"""DuckDB-backed persistence for LACOUNCIL.

Storage layout:
    memoria/lacouncil.duckdb     <- single database, multiple tables
        propostas                -- structural-change proposals (1 row per proposal)
        votos                    -- vote records (FK -> propostas.proposal_id)
        projetos_registrados     -- closed projects (ProjectRecord entries)
        sessoes_investigacao     -- investigation results (audit trail)
        verbetes_conhecimento    -- knowledge entries promoted from projects
        wdl_signatures           -- WDL v1 verified-verdict ledger

All writes go through this module. Reads can be raw SQL but should use the
typed helpers.

DB path resolution:
    1. explicit `db_path` argument (used by tests)
    2. `LACOUNCIL_DB_PATH` env var
    3. `_REPO_ROOT/memoria/lacouncil.duckdb`
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

import duckdb

from lacouncil.core.schemas import (
    InvestigationResult,
    Pattern,
    Project,
    ProjectRecord,
    Proposal,
    ProposalStatus,
    TallyResult,
    Vote,
    VoteValue,
    compute_proposal_signature,
)


# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────


_REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = _REPO_ROOT / "memoria" / "lacouncil.duckdb"


def resolve_db_path(db_path: Optional[str] = None) -> str:
    """Resolve DuckDB path: arg → env → default."""
    if db_path:
        return db_path
    env = os.environ.get("LACOUNCIL_DB_PATH")
    if env:
        return env
    return str(DEFAULT_DB_PATH)


# ──────────────────────────────────────────────────────────────────────────────
# Connection management
# ──────────────────────────────────────────────────────────────────────────────


def connect(db_path: Optional[str] = None) -> duckdb.DuckDBPyConnection:
    """Open a DuckDB connection to LACOUNCIL's store (auto-migrate on first use)."""
    target = resolve_db_path(db_path)
    Path(target).parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(target)
    ensure_schema(con)
    return con


def ensure_schema(con: duckdb.DuckDBPyConnection) -> None:
    """Idempotent schema migration. Safe to call on every connect()."""
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS propostas (
            proposal_id VARCHAR PRIMARY KEY,
            payload_json VARCHAR NOT NULL,
            titulo VARCHAR NOT NULL,
            categoria VARCHAR NOT NULL,
            estrategia VARCHAR NOT NULL,
            autor VARCHAR NOT NULL,
            status VARCHAR NOT NULL DEFAULT 'pendente',
            created_at TIMESTAMP NOT NULL,
            closed_at TIMESTAMP,
            signature VARCHAR
        )
        """
    )
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS votos (
            vote_id VARCHAR PRIMARY KEY,
            proposal_id VARCHAR NOT NULL,
            voter VARCHAR NOT NULL,
            voto VARCHAR NOT NULL,
            justificativa VARCHAR NOT NULL DEFAULT '',
            cast_at TIMESTAMP NOT NULL,
            UNIQUE (proposal_id, voter)
        )
        """
    )
    # DuckDB não suporta AUTOINCREMENT/GENERATED IDENTITY — usamos SEQUENCE
    con.execute("CREATE SEQUENCE IF NOT EXISTS seq_project_id START 1;")
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS projetos_registrados (
            project_id INTEGER PRIMARY KEY,
            project_slug VARCHAR NOT NULL UNIQUE,
            scope VARCHAR NOT NULL,
            capabilities_used_json VARCHAR NOT NULL,
            deliverable_summary VARCHAR NOT NULL,
            follow_up VARCHAR NOT NULL DEFAULT '',
            follows_pattern VARCHAR,
            recorded_at TIMESTAMP NOT NULL
        )
        """
    )
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS sessoes_investigacao (
            session_id VARCHAR PRIMARY KEY,
            gap VARCHAR NOT NULL,
            payload_json VARCHAR NOT NULL,
            created_at TIMESTAMP NOT NULL
        )
        """
    )
    con.execute("CREATE SEQUENCE IF NOT EXISTS seq_verbete_id START 1;")
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS verbetes_conhecimento (
            verbete_id INTEGER PRIMARY KEY,
            slug VARCHAR NOT NULL UNIQUE,
            titulo VARCHAR NOT NULL,
            body VARCHAR NOT NULL,
            fonte VARCHAR NOT NULL,
            recorded_at TIMESTAMP NOT NULL
        )
        """
    )
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS wdl_signatures (
            pre_flight_id VARCHAR PRIMARY KEY,
            plan_id VARCHAR NOT NULL,
            state VARCHAR NOT NULL,
            verified_by VARCHAR NOT NULL,
            signature_value VARCHAR NOT NULL,
            recorded_at TIMESTAMP NOT NULL
        )
        """
    )
    # Indexes (idempotent)
    for stmt in [
        "CREATE INDEX IF NOT EXISTS idx_votos_proposal ON votos(proposal_id)",
        "CREATE INDEX IF NOT EXISTS idx_propostas_status ON propostas(status)",
        "CREATE INDEX IF NOT EXISTS idx_projetos_pattern ON projetos_registrados(follows_pattern)",
    ]:
        con.execute(stmt)


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────


def _now_ts() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _row_to_proposal(row: tuple) -> Proposal:
    payload = json.loads(row[1])
    payload["status"] = row[6]  # status column (index 6, not 5 — row[5] is autor)
    return Proposal.model_validate(payload)


# ──────────────────────────────────────────────────────────────────────────────
# Propostas
# ──────────────────────────────────────────────────────────────────────────────


def upsert_proposal(proposal: Proposal, db_path: Optional[str] = None) -> Proposal:
    """Insert-or-replace; normalize signature if missing."""
    signature = proposal.signature or compute_proposal_signature(proposal)
    proposal_to_persist = proposal.model_copy(update={"signature": signature})

    con = connect(db_path)
    try:
        con.execute(
            """
            INSERT OR REPLACE INTO propostas
                (proposal_id, payload_json, titulo, categoria, estrategia,
                 autor, status, created_at, closed_at, signature)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                proposal_to_persist.proposal_id,
                json.dumps(proposal_to_persist.model_dump(), ensure_ascii=False),
                proposal_to_persist.titulo,
                proposal_to_persist.categoria.value,
                proposal_to_persist.estrategia.value,
                proposal_to_persist.autor,
                proposal_to_persist.status.value,
                _now_ts(),
                None,
                signature,
            ],
        )
        return proposal_to_persist
    finally:
        con.close()


def get_proposal(proposal_id: str, db_path: Optional[str] = None) -> Optional[Proposal]:
    con = connect(db_path)
    try:
        row = con.execute(
            "SELECT proposal_id, payload_json, titulo, categoria, estrategia, "
            "autor, status, created_at, closed_at, signature "
            "FROM propostas WHERE proposal_id = ?",
            [proposal_id],
        ).fetchone()
        if not row:
            return None
        return _row_to_proposal(row)
    finally:
        con.close()


def list_proposals(
    status: Optional[ProposalStatus] = None,
    db_path: Optional[str] = None,
) -> list[Proposal]:
    con = connect(db_path)
    try:
        if status is None:
            rows = con.execute(
                "SELECT proposal_id, payload_json, titulo, categoria, estrategia, "
                "autor, status, created_at, closed_at, signature "
                "FROM propostas ORDER BY created_at DESC"
            ).fetchall()
        else:
            rows = con.execute(
                "SELECT proposal_id, payload_json, titulo, categoria, estrategia, "
                "autor, status, created_at, closed_at, signature "
                "FROM propostas WHERE status = ? ORDER BY created_at DESC",
                [status.value],
            ).fetchall()
        return [_row_to_proposal(r) for r in rows]
    finally:
        con.close()


def update_proposal_status(
    proposal_id: str,
    new_status: ProposalStatus,
    tally_summary: Optional[dict[str, Any]] = None,
    implementation: Optional[dict[str, Any]] = None,
    db_path: Optional[str] = None,
) -> None:
    """Update status + side tables. Idempotent on status matches."""
    con = connect(db_path)
    try:
        existing = con.execute(
            "SELECT payload_json, status FROM propostas WHERE proposal_id = ?",
            [proposal_id],
        ).fetchone()
        if not existing:
            raise KeyError(f"proposta {proposal_id!r} não encontrada")
        payload = json.loads(existing[0])
        payload["status"] = new_status.value
        if tally_summary is not None:
            payload["tally_summary"] = tally_summary
        if implementation is not None:
            payload["implementation"] = implementation
        payload["closed_at"] = _now_ts().isoformat() if new_status in (
            ProposalStatus.APROVADA,
            ProposalStatus.REJEITADA,
            ProposalStatus.IMPLEMENTADA,
            ProposalStatus.CANCELADA,
        ) else None
        con.execute(
            "UPDATE propostas SET payload_json = ?, status = ?, closed_at = ? "
            "WHERE proposal_id = ?",
            [json.dumps(payload, ensure_ascii=False), new_status.value, payload.get("closed_at"), proposal_id],
        )
    finally:
        con.close()


# ──────────────────────────────────────────────────────────────────────────────
# Votos
# ──────────────────────────────────────────────────────────────────────────────


def register_vote(vote: Vote, db_path: Optional[str] = None) -> Vote:
    """Append-or-replace vote for (proposal_id, voter)."""
    con = connect(db_path)
    try:
        # Validate proposal exists
        exists = con.execute(
            "SELECT 1 FROM propostas WHERE proposal_id = ?",
            [vote.proposal_id],
        ).fetchone()
        if not exists:
            raise KeyError(f"proposta {vote.proposal_id!r} não encontrada")
        con.execute(
            """
            INSERT INTO votos (vote_id, proposal_id, voter, voto, justificativa, cast_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT (proposal_id, voter) DO UPDATE SET
                voto = excluded.voto,
                justificativa = excluded.justificativa,
                cast_at = excluded.cast_at
            """,
            [
                vote.vote_id,
                vote.proposal_id,
                vote.voter,
                vote.voto.value,
                vote.justificativa,
                _now_ts(),
            ],
        )
        # Mark proposal em_votacao if still pendente
        status_now = con.execute(
            "SELECT status FROM propostas WHERE proposal_id = ?",
            [vote.proposal_id],
        ).fetchone()[0]
        if status_now == ProposalStatus.PENDENTE.value:
            con.execute(
                "UPDATE propostas SET status = 'em_votacao' WHERE proposal_id = ?",
                [vote.proposal_id],
            )
        return vote
    finally:
        con.close()


def votes_for(
    proposal_id: str,
    db_path: Optional[str] = None,
) -> dict[str, int]:
    """Tally votes for a proposal: returns {"sim": int, "nao": int, "abstencao": int}."""
    con = connect(db_path)
    try:
        rows = con.execute(
            "SELECT voto, COUNT(*) FROM votos WHERE proposal_id = ? GROUP BY voto",
            [proposal_id],
        ).fetchall()
        out = {"sim": 0, "nao": 0, "abstencao": 0}
        for voto, count in rows:
            key = voto.lower()
            if key in out:
                out[key] = int(count)
        return out
    finally:
        con.close()


# ──────────────────────────────────────────────────────────────────────────────
# Projetos_registrados
# ──────────────────────────────────────────────────────────────────────────────


def record_project(project: Project, db_path: Optional[str] = None) -> ProjectRecord:
    con = connect(db_path)
    try:
        con.execute(
            """
            INSERT INTO projetos_registrados
                (project_id, project_slug, scope, capabilities_used_json,
                 deliverable_summary, follow_up, follows_pattern, recorded_at)
            VALUES (nextval('seq_project_id'), ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                project.project_slug,
                project.scope,
                json.dumps(project.capabilities_used, ensure_ascii=False),
                project.deliverable_summary,
                project.follow_up,
                project.follows_pattern,
                _now_ts(),
            ],
        )
        row = con.execute(
            "SELECT project_id, project_slug, scope, capabilities_used_json, "
            "deliverable_summary, follow_up, follows_pattern, recorded_at "
            "FROM projetos_registrados WHERE project_slug = ?",
            [project.project_slug],
        ).fetchone()
        return _row_to_project_record(row)
    finally:
        con.close()


def list_projects(db_path: Optional[str] = None) -> list[ProjectRecord]:
    con = connect(db_path)
    try:
        rows = con.execute(
            "SELECT project_id, project_slug, scope, capabilities_used_json, "
            "deliverable_summary, follow_up, follows_pattern, recorded_at "
            "FROM projetos_registrados ORDER BY recorded_at DESC"
        ).fetchall()
        return [_row_to_project_record(r) for r in rows]
    finally:
        con.close()


def _row_to_project_record(row: tuple) -> ProjectRecord:
    return ProjectRecord(
        project_id=int(row[0]),
        project_slug=row[1],
        scope=row[2],
        capabilities_used=json.loads(row[3]),
        deliverable_summary=row[4],
        follow_up=row[5],
        follows_pattern=row[6],
        recorded_at=row[7].isoformat() if hasattr(row[7], "isoformat") else str(row[7]),
    )


def detect_patterns(
    min_occurrences: int = 3,
    db_path: Optional[str] = None,
) -> list[Pattern]:
    """Detect cross-project patterns using 3Q heuristics.

    Buckets considered:
      (a) shared capabilities_overlap>=1 AND deliverable keyword overlap
      (b) shared capabilities AND same follows_pattern bucket
      (c) repeated "follow_up" string keyword >= occurrences

    Confidence = jaccard(capabilities) * 0.6 + min(1.0, occurrences / max_count) * 0.4
    """
    con = connect(db_path)
    try:
        rows = con.execute(
            "SELECT project_slug, capabilities_used_json, deliverable_summary, "
            "follow_up, follows_pattern FROM projetos_registrados"
        ).fetchall()
    finally:
        con.close()

    if len(rows) < min_occurrences:
        return []

    parsed: list[dict[str, Any]] = []
    for r in rows:
        parsed.append(
            {
                "slug": r[0],
                "caps": set(json.loads(r[1])),
                "summary": r[2],
                "follow_up": r[3],
                "follows_pattern": r[4],
            }
        )

    patterns: list[Pattern] = []
    # Bucket by follows_pattern (canonical key)
    by_pattern: dict[str, list[dict[str, Any]]] = {}
    for p in parsed:
        bucket = p["follows_pattern"] or ""
        by_pattern.setdefault(bucket, []).append(p)
    for bucket, members in by_pattern.items():
        if not bucket:
            continue
        if len(members) >= min_occurrences:
            patterns.append(
                Pattern(
                    pattern=bucket,
                    projects=[m["slug"] for m in members],
                    occurrences=len(members),
                    confidence=min(1.0, len(members) / max(min_occurrences + 1, 4)),
                    detection_basis="shared_follows_pattern_bucket",
                )
            )

    # Bucket by capability overlap (jaccard >= 0.7 across >= occ)
    by_caps: dict[frozenset[str], list[dict[str, Any]]] = {}
    for p in parsed:
        by_caps.setdefault(frozenset(p["caps"]), []).append(p)
    for cap_set, members in by_caps.items():
        if not cap_set or len(members) < min_occurrences:
            continue
        slug_hint = "+".join(sorted(cap_set))
        patterns.append(
            Pattern(
                pattern=f"shared_caps::{slug_hint}",
                projects=[m["slug"] for m in members],
                occurrences=len(members),
                confidence=min(1.0, len(members) / max(min_occurrences + 1, 4)),
                detection_basis="shared_capabilities",
            )
        )

    # Dedup by `pattern` key, keep highest confidence
    dedup: dict[str, Pattern] = {}
    for p in patterns:
        if p.pattern not in dedup or dedup[p.pattern].confidence < p.confidence:
            dedup[p.pattern] = p
    return sorted(dedup.values(), key=lambda p: (-p.confidence, -p.occurrences))


# ──────────────────────────────────────────────────────────────────────────────
# Investigação (audit)
# ──────────────────────────────────────────────────────────────────────────────


def record_investigation(
    result: InvestigationResult, db_path: Optional[str] = None
) -> InvestigationResult:
    con = connect(db_path)
    try:
        con.execute(
            """
            INSERT OR REPLACE INTO sessoes_investigacao
                (session_id, gap, payload_json, created_at)
            VALUES (?, ?, ?, ?)
            """,
            [
                result.session_id,
                result.gap,
                json.dumps(result.model_dump(), ensure_ascii=False),
                _now_ts(),
            ],
        )
        return result
    finally:
        con.close()
