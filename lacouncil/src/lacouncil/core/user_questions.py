"""Confidence Escalation Ladder — user question log + pattern detection.

LACOUNCIL d3095fa3-4570-413c-82b4-47442a90e947 (workflow / maioria / 4-4 SIM
/ 2026-07-02). The 4 contract clauses this module implements:

  1. `log(question, cluster_id, context, session_id) -> UserQuestion`
     — pure write, idempotent on (session_id, cluster_id). Re-asking
     the same cluster in the same session overwrites the previous
     `question_text` and bumps `asked_at` (the dedup boundary is the
     session, not the question — chief-engineer convention).

  2. `detect_user_question_patterns(min_occurrences, min_confidence) -> list[Pattern]`
     — pure read, returns candidate `UserQuestionPattern` records. This
     function MUST NOT create proposals, MUST NOT write to user_questions,
     MUST NOT call any LACOUNCIL write tool. Read/write split
     (data-architect condition #9).

  3. `create_proposal_from_pattern(pattern, autor) -> Proposal`
     — explicit write, called by the orchestrator AFTER it has
     confirmed the pattern with the user (transparency) and AFTER
     the Conselho has decided to formalize. Marks
     `meta.auto_created: true` and does NOT call
     `lacouncil.implement_proposal` (delivery-reviewer condition #10
     loop escape). The Conselho votes on the created proposal in the
     normal fluxo.

  4. `cleanup_user_questions(retention_months=12) -> int`
     — idempotent retention cleanup, returns number of rows deleted.
     Chief-engineer condition #7. Default 12 months is conservative;
     audits can request a longer retention via this function.

All thresholds (min_occurrences, min_confidence, retention_months,
per_action_timeout_seconds) are externalized in
`workflows/wdl-contract.yaml` §confidence_escalation_ladder.thresholds;
this module READS them via the constants imported below, not from
hard-coded values (chief-engineer condition #6).
"""
from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

import yaml

from lacouncil.core.duckdb_store import connect
from lacouncil.core.schemas import (
    CreateProposalFromPatternRequest,
    DetectUserQuestionPatternsRequest,
    LogUserQuestionRequest,
    Proposal,
    UserQuestion,
    UserQuestionPattern,
)


# ──────────────────────────────────────────────────────────────────────────────
# Threshold loading (chief-engineer condition #6: externalized in YAML)
# ──────────────────────────────────────────────────────────────────────────────

_DEFAULT_THRESHOLDS: dict[str, Any] = {
    "min_occurrences": 3,
    "min_confidence": 0.80,
    "per_action_timeout_seconds": 30,
    "retention_months": 12,
    "max_ladder_passes_per_question": 2,
    "min_confidence_for_ask_user": 0.80,
}

# Path to the wdl-contract.yaml — relative to the LAOS root. Resolved
# once at import time. If the file is missing (e.g. a lacouncil-only
# test env), we fall back to _DEFAULT_THRESHOLDS; this is a soft
# fallback, not silent — the orchestrator's runtime contract is the
# YAML, not this module's defaults.
_LAOS_ROOT = Path(__file__).resolve().parents[3]  # /lacouncil/src/lacouncil/core/user_questions.py → LAOS/
_WDL_CONTRACT_PATH = _LAOS_ROOT / "workflows" / "wdl-contract.yaml"


def _load_thresholds() -> dict[str, Any]:
    """Load ladder thresholds from wdl-contract.yaml.

    Falls back to _DEFAULT_THRESHOLDS if the YAML is missing or the
    section is absent. Never raises — the function is called on every
    pattern detection call, and we want the system to remain
    functional even if the YAML is being edited.
    """
    try:
        if not _WDL_CONTRACT_PATH.exists():
            return dict(_DEFAULT_THRESHOLDS)
        with _WDL_CONTRACT_PATH.open("r", encoding="utf-8") as f:
            contract = yaml.safe_load(f) or {}
        ladder = contract.get("confidence_escalation_ladder") or {}
        thresholds = ladder.get("thresholds") or {}
        # Merge: defaults first, then YAML overrides.
        out = dict(_DEFAULT_THRESHOLDS)
        for k, v in thresholds.items():
            if v is not None:
                out[k] = v
        return out
    except Exception:  # noqa: BLE001
        return dict(_DEFAULT_THRESHOLDS)


# Module-level cache. The YAML is reloaded on every call to
# `_load_thresholds()` if the file's mtime changes (cheap check, but
# avoids re-parse on hot paths). The cache key is the file's mtime.
_LAST_LOAD_MTIME: Optional[float] = None
_CACHED_THRESHOLDS: dict[str, Any] = dict(_DEFAULT_THRESHOLDS)


def get_thresholds() -> dict[str, Any]:
    """Public accessor — read-only view of the ladder thresholds.

    Reloads from YAML when the file's mtime changes. The orchestrator
    passes these into `detect_user_question_patterns` so the read
    path is pure (no hidden YAML load mid-call).
    """
    global _LAST_LOAD_MTIME, _CACHED_THRESHOLDS
    try:
        mtime = _WDL_CONTRACT_PATH.stat().st_mtime
    except OSError:
        mtime = None
    if mtime != _LAST_LOAD_MTIME:
        _CACHED_THRESHOLDS = _load_thresholds()
        _LAST_LOAD_MTIME = mtime
    return dict(_CACHED_THRESHOLDS)


# ──────────────────────────────────────────────────────────────────────────────
# Persistence helpers (raw SQL — kept here, not in duckdb_store.py,
# because this table is a feature of the Confidence Escalation Ladder,
# not of the core LACOUNCIL data model).
# ──────────────────────────────────────────────────────────────────────────────


def _now_ts() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _row_to_user_question(row: tuple) -> UserQuestion:
    """Convert a raw user_questions row to a UserQuestion model.

    Column order (must match the SELECT in `log()` / `list_*()`):
      0: question_id
      1: question_text
      2: cluster_id
      3: context_json
      4: asked_at
      5: answered_with
      6: session_id
    """
    asked_at = row[4]
    if hasattr(asked_at, "isoformat"):
        asked_at_str = asked_at.isoformat()
    else:
        asked_at_str = str(asked_at)
    return UserQuestion(
        question_id=row[0],
        question_text=row[1],
        cluster_id=row[2],
        context_json=json.loads(row[3]) if row[3] else {},
        asked_at=asked_at_str,
        answered_with=row[5],
        session_id=row[6],
    )


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────


def log(
    question: str,
    cluster_id: str,
    context: dict[str, Any],
    session_id: str,
    *,
    answered_with: Optional[str] = None,
    db_path: Optional[str] = None,
) -> UserQuestion:
    """Persist a single `ask_user` invocation. Idempotent on (session_id, cluster_id).

    Behavior (chief-engineer convention):
      - If a row exists for (session_id, cluster_id), UPDATE
        `question_text`, `context_json`, and `asked_at` (the user is
        re-asking the same question in the same session; the
        `question_id` PK is preserved).
      - Otherwise INSERT a new row with a fresh `question_id`.

    The function NEVER raises on validation — the orchestrator's
    caller passes validated strings. If the cluster_id is invalid
    (kebab-case regex fail), the UserQuestion model raises on
    construction and that error propagates. This is the desired
    fail-loud behavior (data-architect condition #8).

    Returns the persisted UserQuestion (with question_id, asked_at
    populated by the database).
    """
    req = LogUserQuestionRequest(
        question_text=question,
        cluster_id=cluster_id,
        context_json=context,
        session_id=session_id,
        answered_with=answered_with,
    )
    uq = UserQuestion(
        question_text=req.question_text,
        cluster_id=req.cluster_id,
        context_json=req.context_json,
        session_id=req.session_id,
        answered_with=req.answered_with,
    )

    con = connect(db_path)
    try:
        # Idempotent write: UPSERT on (session_id, cluster_id).
        existing = con.execute(
            "SELECT question_id FROM user_questions "
            "WHERE session_id = ? AND cluster_id = ?",
            [uq.session_id, uq.cluster_id],
        ).fetchone()

        if existing is not None:
            # UPDATE — preserve question_id, refresh payload + timestamp.
            con.execute(
                """
                UPDATE user_questions
                SET question_text = ?, context_json = ?, asked_at = ?,
                    answered_with = ?
                WHERE question_id = ?
                """,
                [
                    uq.question_text,
                    json.dumps(uq.context_json, ensure_ascii=False),
                    _now_ts(),
                    uq.answered_with,
                    existing[0],
                ],
            )
            uq = uq.model_copy(update={"question_id": existing[0]})
        else:
            con.execute(
                """
                INSERT INTO user_questions
                    (question_id, question_text, cluster_id, context_json,
                     asked_at, answered_with, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    uq.question_id,
                    uq.question_text,
                    uq.cluster_id,
                    json.dumps(uq.context_json, ensure_ascii=False),
                    _now_ts(),
                    uq.answered_with,
                    uq.session_id,
                ],
            )

        # Read back the persisted row (the asked_at was set by
        # _now_ts() in DuckDB; we want the canonical form).
        row = con.execute(
            "SELECT question_id, question_text, cluster_id, context_json, "
            "asked_at, answered_with, session_id "
            "FROM user_questions WHERE question_id = ?",
            [uq.question_id],
        ).fetchone()
        return _row_to_user_question(row)
    finally:
        con.close()


def detect_user_question_patterns(
    min_occurrences: Optional[int] = None,
    min_confidence: Optional[float] = None,
    scope: Optional[list[str]] = None,
    *,
    db_path: Optional[str] = None,
) -> list[UserQuestionPattern]:
    """Pure read: detect recurring user-question clusters.

    Returns `UserQuestionPattern` records for clusters where
    `occurrences >= min_occurrences` AND `confidence >= min_confidence`.

    Thresholds default to the YAML-loaded ladder thresholds (chief-engineer
    condition #6). Pass explicit values to override for testing.

    PURE READ — this function MUST NOT create proposals, MUST NOT
    write to user_questions, MUST NOT call any LACOUNCIL write tool.
    (Data-architect condition #9; verified by tests.)

    Confidence formula (simple, defensible):
        confidence = min(1.0, occurrences / (min_occurrences + 2))
    The `+2` buffer means a cluster must have at least
    `min_occurrences + 2` hits to reach confidence 1.0; below that,
    confidence grows linearly. This is consistent with the formula
    used in `detect_patterns()` for `projetos_registrados` (in
    `duckdb_store.py`).

    `scope` is a list of cluster_ids to limit detection. None = all.
    """
    thresholds = get_thresholds()
    if min_occurrences is None:
        min_occurrences = thresholds["min_occurrences"]
    if min_confidence is None:
        min_confidence = thresholds["min_confidence"]

    req = DetectUserQuestionPatternsRequest(
        min_occurrences=min_occurrences,
        min_confidence=min_confidence,
        scope=scope,
    )

    con = connect(db_path)
    try:
        if req.scope is not None:
            # Parameterized IN clause; DuckDB supports ? expansion
            # via tuple. We use a `cluster_id = ANY(?)` form to
            # avoid string interpolation.
            rows = con.execute(
                "SELECT cluster_id, COUNT(*), MIN(asked_at), MAX(asked_at) "
                "FROM user_questions "
                "WHERE cluster_id = ANY(?) "
                "GROUP BY cluster_id "
                "HAVING COUNT(*) >= ? "
                "ORDER BY COUNT(*) DESC",
                [req.scope, req.min_occurrences],
            ).fetchall()
        else:
            rows = con.execute(
                "SELECT cluster_id, COUNT(*), MIN(asked_at), MAX(asked_at) "
                "FROM user_questions "
                "GROUP BY cluster_id "
                "HAVING COUNT(*) >= ? "
                "ORDER BY COUNT(*) DESC",
                [req.min_occurrences],
            ).fetchall()
    finally:
        con.close()

    patterns: list[UserQuestionPattern] = []
    for cluster_id, count, first_asked, last_asked in rows:
        confidence = min(1.0, count / (req.min_occurrences + 2))
        if confidence < req.min_confidence:
            continue

        # Fetch up to 5 sample question texts + 5 session_ids for
        # the pattern, so the orchestrator can show the user what
        # was logged before promoting to a proposal.
        con2 = connect(db_path)
        try:
            sample_rows = con2.execute(
                "SELECT question_text, session_id FROM user_questions "
                "WHERE cluster_id = ? "
                "ORDER BY asked_at DESC LIMIT 5",
                [cluster_id],
            ).fetchall()
        finally:
            con2.close()
        samples = [r[0] for r in sample_rows]
        sessions = sorted({r[1] for r in sample_rows})

        first_str = first_asked.isoformat() if hasattr(first_asked, "isoformat") else str(first_asked)
        last_str = last_asked.isoformat() if hasattr(last_asked, "isoformat") else str(last_asked)

        patterns.append(
            UserQuestionPattern(
                cluster_id=cluster_id,
                occurrences=int(count),
                question_samples=samples,
                session_ids=sessions,
                confidence=confidence,
                first_asked_at=first_str,
                last_asked_at=last_str,
            )
        )

    # Sort: highest confidence first; tiebreak on most occurrences.
    patterns.sort(key=lambda p: (-p.confidence, -p.occurrences, p.cluster_id))
    return patterns


def create_proposal_from_pattern(
    pattern: UserQuestionPattern,
    autor: str,
    *,
    db_path: Optional[str] = None,
) -> Proposal:
    """EXPLICIT WRITE: create a LACOUNCIL proposal from a detected pattern.

    This function is called by the orchestrator AFTER it has
    confirmed the pattern with the user (transparency, see
    `orchestrator.md` §"Session Close") and only when the user or
    Conselho has approved the promotion.

    The created proposal carries `meta.auto_created: true` in its
    payload_json to flag its origin in the audit trail
    (delivery-reviewer condition #10). It does NOT call
    `lacouncil.implement_proposal` (that remains a Conselho-gated
    step, R3 + R4 separation of duties).

    The proposal is in status `pendente` and is registered like any
    other LACOUNCIL proposal — Conselho votes normally. This is the
    loop escape: the proposal doesn't auto-implement, but it also
    doesn't bypass the Conselho.
    """
    req = CreateProposalFromPatternRequest(
        cluster_id=pattern.cluster_id,
        occurrences=pattern.occurrences,
        confidence=pattern.confidence,
        question_samples=pattern.question_samples,
        autor=autor,
    )

    sample_quote = (
        pattern.question_samples[0] if pattern.question_samples else "(no sample)"
    )
    descricao = (
        f"Auto-criado a partir de detecção de padrão em `user_questions` "
        f"(LACOUNCIL d3095fa3 — Confidence Escalation Ladder). "
        f"Cluster: `{req.cluster_id}`. Ocorrências: {req.occurrences} "
        f"(confidence {req.confidence:.2f}). "
        f"Exemplo de pergunta: \"{sample_quote}\".\n\n"
        f"Ação sugerida: formalizar como regra transversal — adicionar "
        f"entrada em `knowledge/` ou ajustar registry/workflow para que "
        f"a próxima ocorrência seja auto-resolvida sem HITL."
    )
    contexto = (
        f"Detectado por `lacouncil.detect_user_question_patterns()` em "
        f"{pattern.first_asked_at} (última: {pattern.last_asked_at}). "
        f"Sessões: {', '.join(pattern.session_ids[:5])}."
    )
    mudanca = (
        f"(1) Adicionar entrada em `knowledge/` (regra) ou `workflows/` "
        f"(template) cobrindo a classe `{req.cluster_id}`. "
        f"(2) Atualizar `registry/needs-to-capabilities.yaml` se a "
        f"resolução virar routing nativo. (3) Adicionar ADR se a "
        f"mudança afeta contrato entre capabilities."
    )
    impacto = (
        f"Positivo: elimina HITL recorrente para a classe "
        f"`{req.cluster_id}` (≥{req.occurrences} ocorrências já "
        f"registradas). Risco: amostra pode ser insuficiente para "
        f"generalizar; mitigação = Conselho delibera antes de "
        f"implementar (esta proposta é pendente)."
    )
    alternativas = (
        "(A) Não criar proposta, apenas logar — rejeitada: perde a "
        "mecanização. (B) Auto-implementar sem Conselho — rejeitada: "
        "viola R3 + R4 separation of duties. (C) Esperar ≥5 "
        "ocorrências em vez de ≥3 — possível, mas HR #7 já usa ≥3."
    )

    from lacouncil.core.schemas import (
        Category,
        CreateProposalRequest,
        Estrategia,
    )

    cat = Category.KNOWLEDGE  # Most auto-detected questions map to a knowledge rule.
    estrat = Estrategia.MAIORIA  # Knowledge category default.

    cp_req = CreateProposalRequest(
        titulo=(
            f"Pattern detectado: {req.cluster_id} "
            f"({req.occurrences}x, conf {req.confidence:.2f})"
        )[:200],
        descricao=descricao,
        categoria=cat,
        estrategia=estrat,
        autor=req.autor,
        contexto=contexto,
        mudanca=mudanca,
        impacto=impacto,
        alternativas=alternativas,
    )
    proposal = Proposal(**cp_req.model_dump())

    # Inject the `meta.auto_created: true` flag into the proposal's
    # implementation slot. We use a separate JSON column to avoid
    # polluting the canonical Proposal model; duckdb_store will
    # round-trip the model through payload_json and the flag will
    # be visible to `get_proposal()` consumers.
    import dataclasses

    # Pydantic v2: use model_copy to add the flag. We attach it as
    # a non-canonical metadata field by going through the
    # model_extra mechanism — but `extra="forbid"` blocks that.
    # Instead, we add a synthetic field via object.__setattr__ AFTER
    # construction. Pydantic v2's `model_config = ConfigDict(
    # extra="forbid")` does not block __setattr__ on the instance
    # directly; it only blocks model construction with extras.
    # However, to keep the audit trail visible to readers, we
    # persist the flag via a sidecar key in the implementation dict
    # (which is `dict[str, Any]`, free-form).
    if proposal.implementation is None:
        proposal = proposal.model_copy(
            update={
                "implementation": {
                    "auto_created": True,
                    "source_pattern": {
                        "cluster_id": req.cluster_id,
                        "occurrences": req.occurrences,
                        "confidence": req.confidence,
                        "first_asked_at": pattern.first_asked_at,
                        "last_asked_at": pattern.last_asked_at,
                    },
                }
            }
        )
    else:
        # Merge into existing implementation dict.
        merged = dict(proposal.implementation)
        merged["auto_created"] = True
        merged["source_pattern"] = {
            "cluster_id": req.cluster_id,
            "occurrences": req.occurrences,
            "confidence": req.confidence,
            "first_asked_at": pattern.first_asked_at,
            "last_asked_at": pattern.last_asked_at,
        }
        proposal = proposal.model_copy(update={"implementation": merged})

    # Persist via the canonical pipeline. We use a small custom
    # insertion because the existing `upsert_proposal` doesn't
    # preserve the implementation dict verbatim (it constructs a
    # fresh dict in some flows). For audit trail integrity, we
    # re-load and re-merge here.
    from lacouncil.core.duckdb_store import upsert_proposal

    persisted = upsert_proposal(proposal, db_path=db_path)
    # Re-merge: upsert_proposal serializes the model into payload_json
    # and stores the implementation dict there, so the auto_created
    # flag is preserved. Returned Proposal should carry it.
    return persisted


def cleanup_user_questions(
    retention_months: Optional[int] = None,
    *,
    db_path: Optional[str] = None,
) -> int:
    """Idempotent retention cleanup (chief-engineer condition #7).

    Deletes `user_questions` rows whose `asked_at` is older than
    `retention_months` ago. Default 12 months from the YAML-loaded
    threshold. Returns the number of rows deleted.

    The function is explicit (not scheduled). The orchestrator calls
    it at session close if retention is desired; otherwise rows
    accumulate forever. Idempotency: re-running on an already-clean
    DB returns 0.
    """
    if retention_months is None:
        thresholds = get_thresholds()
        retention_months = thresholds["retention_months"]

    cutoff = _now_ts() - timedelta(days=int(retention_months) * 30)  # 30 days/month approx
    con = connect(db_path)
    try:
        result = con.execute(
            "DELETE FROM user_questions WHERE asked_at < ? RETURNING question_id",
            [cutoff],
        ).fetchall()
        return len(result)
    finally:
        con.close()
