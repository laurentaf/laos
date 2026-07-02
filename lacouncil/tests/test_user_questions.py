"""Unit + smoke tests for the Confidence Escalation Ladder.

LACOUNCIL d3095fa3 (workflow / maioria / 4-4 SIM, 2026-07-02).
Test coverage (CEL-IC-3):
  1. test_log_idempotent_on_session_cluster
  2. test_log_validates_cluster_id
  3. test_detect_user_question_patterns_pure_read
  4. test_detect_user_question_patterns_filters_by_scope
  5. test_create_proposal_from_pattern_auto_created
  6. test_migration_idempotent
  7. test_smoke_e2e_ladder

Each test uses a temporary DuckDB (pytest tmp_path fixture) so the
real runtime DB is never touched. The tests run independently and
can be executed in any order.
"""
from __future__ import annotations

import json
import os
import sys
import uuid
from pathlib import Path

import pytest


# Make lacouncil importable when running pytest from the LAOS root.
_LAOS_ROOT = Path(__file__).resolve().parents[1]
_LACOUNCIL_SRC = _LAOS_ROOT / "lacouncil" / "src"
if str(_LACOUNCIL_SRC) not in sys.path:
    sys.path.insert(0, str(_LACOUNCIL_SRC))


# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def tmp_db(tmp_path: Path) -> str:
    """Fresh DuckDB path for the test. Each test gets its own DB."""
    return str(tmp_path / "test_lacouncil.duckdb")


@pytest.fixture
def session_id() -> str:
    return f"sess-{uuid.uuid4()}"


# ──────────────────────────────────────────────────────────────────────────────
# 1. log() idempotency
# ──────────────────────────────────────────────────────────────────────────────


def test_log_idempotent_on_session_cluster(tmp_db: str, session_id: str) -> None:
    """Re-logging the same (session_id, cluster_id) updates, not duplicates."""
    from lacouncil.core import user_questions as uq

    # First log
    uq.log(
        question="Synthetic data?",
        cluster_id="synthetic-data-permission",
        context={"plan_id": "p1", "stage": "data-model"},
        session_id=session_id,
        db_path=tmp_db,
    )

    # Second log with the same (session_id, cluster_id)
    uq.log(
        question="Synthetic data agora?",
        cluster_id="synthetic-data-permission",
        context={"plan_id": "p1", "stage": "data-model", "retry": True},
        session_id=session_id,
        db_path=tmp_db,
    )

    import duckdb
    con = duckdb.connect(tmp_db, read_only=True)
    try:
        rows = con.execute(
            "SELECT COUNT(*) FROM user_questions "
            "WHERE session_id = ? AND cluster_id = ?",
            [session_id, "synthetic-data-permission"],
        ).fetchone()
        assert rows[0] == 1, f"expected 1 row after re-log, got {rows[0]}"

        # The text was updated.
        text = con.execute(
            "SELECT question_text FROM user_questions "
            "WHERE session_id = ? AND cluster_id = ?",
            [session_id, "synthetic-data-permission"],
        ).fetchone()[0]
        assert text == "Synthetic data agora?"
    finally:
        con.close()


# ──────────────────────────────────────────────────────────────────────────────
# 2. log() validates cluster_id
# ──────────────────────────────────────────────────────────────────────────────


def test_log_validates_cluster_id(tmp_db: str, session_id: str) -> None:
    """cluster_id must match kebab-case regex. Bad slugs fail loud."""
    from pydantic import ValidationError

    from lacouncil.core import user_questions as uq
    from lacouncil.core.schemas import UserQuestion

    # Direct model validation: regex fail
    with pytest.raises(ValidationError):
        UserQuestion(
            question_text="x" * 20,
            cluster_id="Bad_Slug",  # uppercase + underscore
            context_json={},
            session_id=session_id,
        )

    # Too short
    with pytest.raises(ValidationError):
        UserQuestion(
            question_text="x" * 20,
            cluster_id="ab",  # < 3 chars
            context_json={},
            session_id=session_id,
        )


# ──────────────────────────────────────────────────────────────────────────────
# 3. detect_user_question_patterns is pure read
# ──────────────────────────────────────────────────────────────────────────────


def test_detect_user_question_patterns_pure_read(tmp_db: str) -> None:
    """Pattern detection does NOT create proposals (data-architect #9)."""
    from lacouncil.core import user_questions as uq

    # Log questions across 3 sessions, all in the same cluster.
    # Idempotency: one row per (session_id, cluster_id), so 3 sessions
    # → 3 rows. The re-asks in the same session UPDATE not INSERT
    # (chief-engineer convention).
    cluster = "regime-b-push-approval"
    for sess in ("s1", "s2", "s3"):
        for i in range(2):  # 2 re-asks in the same session
            uq.log(
                question=f"Approve push #{i}?",
                cluster_id=cluster,
                context={"plan_id": f"p{i}", "stage": "build"},
                session_id=sess,
                db_path=tmp_db,
            )

    # Plus 2 questions in a different cluster (different session each)
    for sess in ("s1", "s2"):
        uq.log(
            question="synthetic data permission?",
            cluster_id="synthetic-data-permission",
            context={"plan_id": "p", "stage": "data-model"},
            session_id=sess,
            db_path=tmp_db,
        )

    patterns = uq.detect_user_question_patterns(
        min_occurrences=3, min_confidence=0.5, db_path=tmp_db
    )

    # `regime-b-push-approval` has 3 rows (3 sessions × 1 row each);
    # `synthetic-data-permission` has 2 (below threshold).
    push_patterns = [p for p in patterns if p.cluster_id == cluster]
    assert len(push_patterns) == 1
    top = push_patterns[0]
    assert top.occurrences == 3
    assert top.confidence >= 0.5

    # The function must NOT have created any proposals.
    import duckdb
    con = duckdb.connect(tmp_db, read_only=True)
    try:
        prop_count = con.execute("SELECT COUNT(*) FROM propostas").fetchone()[0]
        assert prop_count == 0, (
            f"detect_user_question_patterns must be pure read; "
            f"propostas has {prop_count} rows but should be 0"
        )
    finally:
        con.close()


# ──────────────────────────────────────────────────────────────────────────────
# 4. detect_user_question_patterns respects scope
# ──────────────────────────────────────────────────────────────────────────────


def test_detect_user_question_patterns_filters_by_scope(tmp_db: str) -> None:
    """When scope is given, only those clusters are inspected."""
    from lacouncil.core import user_questions as uq

    for sess in ("s1", "s2", "s3"):
        uq.log(
            question="Approve push for build?",
            cluster_id="regime-b-push-approval",
            context={"plan_id": "p", "stage": "build"},
            session_id=sess,
            db_path=tmp_db,
        )

    for sess in ("s1", "s2", "s3"):
        uq.log(
            question="Synthetic data permission OK?",
            cluster_id="synthetic-data-permission",
            context={"plan_id": "p", "stage": "data-model"},
            session_id=sess,
            db_path=tmp_db,
        )

    # Scope to only "regime-b-push-approval"
    patterns = uq.detect_user_question_patterns(
        min_occurrences=3, min_confidence=0.5,
        scope=["regime-b-push-approval"],
        db_path=tmp_db,
    )
    assert len(patterns) == 1
    assert patterns[0].cluster_id == "regime-b-push-approval"

    # No scope = both clusters
    patterns_all = uq.detect_user_question_patterns(
        min_occurrences=3, min_confidence=0.5, db_path=tmp_db
    )
    assert len(patterns_all) == 2
    cluster_ids = {p.cluster_id for p in patterns_all}
    assert cluster_ids == {"regime-b-push-approval", "synthetic-data-permission"}


# ──────────────────────────────────────────────────────────────────────────────
# 5. create_proposal_from_pattern: meta.auto_created, no auto-implement
# ──────────────────────────────────────────────────────────────────────────────


def test_create_proposal_from_pattern_auto_created(tmp_db: str) -> None:
    """Created proposal carries meta.auto_created: true; does NOT call implement."""
    from lacouncil.core import user_questions as uq

    # Build a pattern by logging 3 questions
    for sess in ("s1", "s2", "s3"):
        uq.log(
            question="x" * 30,
            cluster_id="missing-context-clarification",
            context={"plan_id": "p", "stage": "discovery"},
            session_id=sess,
            db_path=tmp_db,
        )

    patterns = uq.detect_user_question_patterns(
        min_occurrences=3, min_confidence=0.5, db_path=tmp_db
    )
    assert len(patterns) == 1
    pattern = patterns[0]

    proposal = uq.create_proposal_from_pattern(
        pattern=pattern, autor="orchestrator", db_path=tmp_db
    )

    # Status is pendente (not implementada — Conselho will deliberate)
    from lacouncil.core.schemas import ProposalStatus
    assert proposal.status == ProposalStatus.PENDENTE

    # The implementation dict carries auto_created: true
    assert proposal.implementation is not None
    assert proposal.implementation.get("auto_created") is True
    assert "source_pattern" in proposal.implementation
    assert proposal.implementation["source_pattern"]["cluster_id"] == pattern.cluster_id

    # Verify in DuckDB
    import duckdb
    con = duckdb.connect(tmp_db, read_only=True)
    try:
        row = con.execute(
            "SELECT payload_json, status FROM propostas WHERE proposal_id = ?",
            [proposal.proposal_id],
        ).fetchone()
        assert row is not None
        payload = json.loads(row[0])
        assert payload["status"] == "pendente"
        assert payload["implementation"]["auto_created"] is True
        assert payload["implementation"]["source_pattern"]["cluster_id"] == pattern.cluster_id
    finally:
        con.close()

    # The proposal was NOT auto-implemented (no row in `wdl_signatures`
    # for this proposal_id, no status transition to "implementada").
    con = duckdb.connect(tmp_db, read_only=True)
    try:
        wdl_rows = con.execute(
            "SELECT COUNT(*) FROM wdl_signatures WHERE plan_id = ?",
            [proposal.proposal_id],
        ).fetchone()[0]
        assert wdl_rows == 0, (
            f"create_proposal_from_pattern must not auto-implement; "
            f"wdl_signatures has {wdl_rows} rows for the new proposal"
        )
    finally:
        con.close()


# ──────────────────────────────────────────────────────────────────────────────
# 6. Migration idempotent
# ──────────────────────────────────────────────────────────────────────────────


def test_migration_idempotent(tmp_db: str) -> None:
    """ensure_schema() can be re-run safely."""
    from lacouncil.core.duckdb_store import connect, ensure_schema

    # First connect() applies the migration.
    con1 = connect(tmp_db)
    con1.close()

    # Second connect() — migration is a no-op (CREATE TABLE IF NOT EXISTS).
    con2 = connect(tmp_db)
    try:
        # Table exists.
        tables = con2.execute("SHOW TABLES").fetchall()
        table_names = {t[0] for t in tables}
        assert "user_questions" in table_names

        # Index exists.
        idx = con2.execute(
            "SELECT index_name FROM duckdb_indexes() "
            "WHERE table_name = 'user_questions'"
        ).fetchall()
        idx_names = {r[0] for r in idx}
        assert "idx_user_questions_cluster_asked" in idx_names

        # Third run — still idempotent.
        ensure_schema(con2)
    finally:
        con2.close()


# ──────────────────────────────────────────────────────────────────────────────
# 7. Smoke test E2E: full ladder workflow
# ──────────────────────────────────────────────────────────────────────────────


def test_smoke_e2e_ladder(tmp_db: str) -> None:
    """End-to-end smoke: log → detect → create_proposal → no auto-implement."""
    from lacouncil.core import user_questions as uq
    from lacouncil.core.schemas import ProposalStatus

    # Phase 1: orchestrator logs 4 questions across 3 sessions.
    cluster = "wdl-defer-block-reason"
    question_text = "DEFER reason is ambiguous; what should I do next?"

    for sess in ("sess-A", "sess-B", "sess-C"):
        uq.log(
            question=question_text,
            cluster_id=cluster,
            context={
                "plan_id": f"plan-{sess}",
                "stage": "discovery",
                "block_reason": "ambiguous_triggers",
            },
            session_id=sess,
            db_path=tmp_db,
        )

    # Phase 2: detect pattern
    patterns = uq.detect_user_question_patterns(
        min_occurrences=3, min_confidence=0.5, db_path=tmp_db
    )
    assert len(patterns) == 1
    assert patterns[0].cluster_id == cluster
    assert patterns[0].occurrences == 3

    # Phase 3: orchestrator (after user consent) creates proposal
    proposal = uq.create_proposal_from_pattern(
        pattern=patterns[0], autor="orchestrator", db_path=tmp_db
    )
    assert proposal.status == ProposalStatus.PENDENTE
    assert proposal.implementation["auto_created"] is True

    # Phase 4: verify Conselho has NOT voted (proposal is pendente)
    import duckdb
    con = duckdb.connect(tmp_db, read_only=True)
    try:
        votes = con.execute(
            "SELECT COUNT(*) FROM votos WHERE proposal_id = ?",
            [proposal.proposal_id],
        ).fetchone()[0]
        assert votes == 0, "Conselho has not voted on the auto-created proposal"
    finally:
        con.close()

    # Phase 5: cleanup (retention) works idempotently
    deleted = uq.cleanup_user_questions(retention_months=12, db_path=tmp_db)
    assert deleted == 0, "no rows older than 12 months in this fresh DB"

    deleted_again = uq.cleanup_user_questions(retention_months=12, db_path=tmp_db)
    assert deleted_again == 0, "second run is idempotent"
