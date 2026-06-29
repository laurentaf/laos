"""Investigation module — 5-Whys + Fishbone analyses for LACOUNCIL.

Implements the methods `lacouncil.investigate(gap)` exposes to the orchestrator.
The investigation is a **trace document** connecting a known gap to candidate
root causes and a recommended next action.

Strategy:
  1. Construct a structured 5-Whys prompt (each Why builds on the previous).
  2. Construct a Fishbone (Ishikawa) with 6 standard heads:
        method, machine, measurement, manpower, material, milieu
        (mapped to LAOS context: latade pipeline, capability tool surface,
         DQ metrics, agent autonomy, data sources, runtime/config).
  3. The orchestrator's LLM is the source of truth for the textual answers.
     This module **shapes** the analysis — it persists what the LLM says.
  4. Detect_patterns() cross-references against projetos_registrados to
     suggest if the gap is recurring (3+ occurrences rule per AGENTS.md HR #7).

This module DOES NOT call out to an LLM. It is **pure Python** that takes the
LLM-generated content (`five_whys: list[str]`, `fishbone: dict[str, list[str]]`,
`root_causes: list[str]`) and persists a session-scoped InvestigationResult.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from lacouncil.core.duckdb_store import connect
from lacouncil.core.schemas import InvestigationResult


# ──────────────────────────────────────────────────────────────────────────────
# Templates — the structural defaults; the LLM fills in the strings.
# ──────────────────────────────────────────────────────────────────────────────


FISHBONE_HEADS: tuple[str, ...] = (
    "method",       # process/pipeline (e.g., data-model, contract.md)
    "machine",      # tooling/compute (MCP servers, registry, venv)
    "measurement",  # DQ / KPI / observability (test coverage, run metrics)
    "manpower",     # agent autonomy / orchestration routing
    "material",     # data sources / inputs (real data vs synthetic)
    "milieu",       # runtime / config / permission policy
)


def default_fishbone_template(gap: str) -> dict[str, list[str]]:
    """Produce an empty fishbone scaffold the LLM fills in.

    Returns one bullet per head = "—". Caller mutates.
    """
    return {head: ["—"] for head in FISHBONE_HEADS}


def default_5_whys_template(gap: str) -> list[str]:
    """Empty 5-Whys ladder; caller fills in."""
    return ["—"] * 5


def build_prompt_for_investigation(gap: str) -> str:
    """Construct the LLM-facing prompt for a 5-Whys + Fishbone analysis.

    The orchestrator copies the output into its own prompt context, the LLM
    returns JSON, and the orchestrator feeds the JSON back into
    `persist_investigation()`.
    """
    return f"""\
Detecte a causa raiz do seguinte gap (ausência ou falha observada) na
plataforma LAOS:

  gap: {gap}

Aplique **5-Whys** (Why? ladder for 5 levels) e **Fishbone (Ishikawa)**
com os 6 cabeçalhos padrão ({", ".join(FISHBONE_HEADS)}).

Responda em JSON estrito (sem markdown, sem texto extra):

{{
  "five_whys": [
    "1. Why #1 (literal)",
    "...Why #2-5 cada um aprofundando o anterior..."
  ],
  "fishbone": {{
    "method": ["item1", "item2"],
    ...
  }},
  "root_causes": ["Causa raiz 1", "Causa raiz 2"],
  "proposed_action": "Próxima ação sugerida (1-2 frases)"
}}
"""


# ──────────────────────────────────────────────────────────────────────────────
# Persistence
# ──────────────────────────────────────────────────────────────────────────────


def persist_investigation(result: InvestigationResult, db_path: Optional[str] = None) -> InvestigationResult:
    """Persist the InvestigationResult to DuckDB (sessoes_investigacao table).

    Idempotent on session_id (replace if exists).
    """
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
                _result_to_json(result),
                datetime.now(timezone.utc).replace(microsecond=0),
            ],
        )
    finally:
        con.close()
    return result


def get_investigation(session_id: str, db_path: Optional[str] = None) -> Optional[InvestigationResult]:
    """Retrieve a prior investigation by session_id (for linking to proposals)."""
    con = connect(db_path)
    try:
        row = con.execute(
            "SELECT session_id, gap, payload_json FROM sessoes_investigacao WHERE session_id = ?",
            [session_id],
        ).fetchone()
        if not row:
            return None
        # The full payload lives in payload_json with the structural fields.
        import json
        payload = json.loads(row[2])
        return InvestigationResult.model_validate(payload)
    finally:
        con.close()


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────


def _result_to_json(result: InvestigationResult) -> str:
    import json
    return json.dumps(result.model_dump(), ensure_ascii=False, sort_keys=True)


def link_to_proposal(
    session_id: str,
    proposal_id: str,
    db_path: Optional[str] = None,
) -> None:
    """Bind a session_id to a proposal so subsequent `get_proposal` can show context."""
    from lacouncil.core.duckdb_store import get_proposal, upsert_proposal

    p = get_proposal(proposal_id, db_path=db_path)
    if p is None:
        raise KeyError(f"proposta {proposal_id!r} não encontrada")
    upsert_proposal(
        p.model_copy(update={"created_by_session": session_id}),
        db_path=db_path,
    )
