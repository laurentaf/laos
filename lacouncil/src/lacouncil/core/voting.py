"""Voting strategies for the Conselho.

The Conselho applies one of three strategies (per category, see CONSTITUTION Art. 5):

  - UNANIMIDADE  (100% dos votos válidos = SIM)              # FUNDAMENTOS
  - SUPERMAIORIA (>=75% dos votos válidos = SIM)              # REGISTRY/CAPABILITY
  - MAIORIA      (>50% dos votos válidos = SIM)               # WORKFLOW/KNOWLEDGE/ADVISORY

ABSTENCAO **não** conta como voto válido (viability 100% requires presente). This
matches the LAOS convention that abstention = "I have no authoritative opinion"
and should not push a proposal through.

A proposal **passes** (status -> APROVADA) iff:
  - threshold-met AND
  - quorum-met (>=1 SIM vote present) AND
  - no negative "veto" condition (e.g., unanimous supermajority loss).

Otherwise the proposal is REJEITADA (or CANCELADA if quorum fails before any vote).
"""

from __future__ import annotations

from typing import Iterable

from lacouncil.core.schemas import Estrategia, ProposalStatus, TallyResult
from lacouncil.core.duckdb_store import votes_for

# ──────────────────────────────────────────────────────────────────────────────
# Thresholds
# ──────────────────────────────────────────────────────────────────────────────


_STRATEGY_THRESHOLDS: dict[Estrategia, float] = {
    Estrategia.UNANIMIDADE: 1.00,
    Estrategia.SUPERMAIORIA: 0.75,
    Estrategia.MAIORIA: 0.50,  # strict majority; >50% per spec
}


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────


def compute_tally(
    votes: dict[str, int],
    strategy: Estrategia,
    *,
    proposal_id: str,
    notes: str = "",
) -> TallyResult:
    """Compute TallyResult for a proposal given raw vote counts.

    Args:
        votes: {"sim": int, "nao": int, "abstencao": int}.
        strategy: which estrategia the Conselho applies to this proposal.
        proposal_id: for inclusion in the result record.
        notes: optional commentary.

    Returns:
        TallyResult with passed/threshold/ratio/etc. Caller mutates the
        proposal status based on `passed` and `new_status`.
    """
    sim = votes.get("sim", 0)
    nao = votes.get("nao", 0)
    abst = votes.get("abstencao", 0)

    valid_total = sim + nao  # abstentions excluded
    total = sim + nao + abst

    # Quorum: requires at least 1 SIM vote to pass (no silent "all-NAO" wins).
    quorum_met = sim >= 1
    threshold = _STRATEGY_THRESHOLDS[strategy]

    ratio = (sim / valid_total) if valid_total > 0 else 0.0
    passed = quorum_met and ratio >= threshold and ratio > 0.0

    new_status = ProposalStatus.APROVADA if passed else ProposalStatus.REJEITADA

    if valid_total == 0:
        new_status = ProposalStatus.PENDENTE  # no votes cast -> still TBD
        notes = (notes + " | " if notes else "") + "no votes cast"

    return TallyResult(
        proposal_id=proposal_id,
        passed=passed,
        strategy=strategy,
        votes={"sim": sim, "nao": nao, "abstencao": abst},
        total=total,
        ratio=ratio,
        threshold=threshold,
        new_status=new_status,
        notes=notes,
    )


def tally_votes(
    proposal_id: str,
    strategy: Estrategia,
    *,
    db_path: str | None = None,
    notes: str = "",
) -> TallyResult:
    """Read votes from DuckDB and compute a tally for `proposal_id`.

    Convenience layer that bridges duckdb_store.votes_for → compute_tally.
    The MCP server (mcp/server.py) calls this directly.
    """
    counts = votes_for(proposal_id, db_path=db_path)
    return compute_tally(counts, strategy, proposal_id=proposal_id, notes=notes)


def explain_strategy(strategy: Estrategia) -> dict[str, object]:
    """Diagnostic helper: what does this strategy mean in this Conselho?"""
    return {
        "name": strategy.value,
        "threshold_pct": int(_STRATEGY_THRESHOLDS[strategy] * 100),
        "abstencao_counts": False,
        "quorum": ">=1 SIM vote required",
        "voting_required_for_categories": _CATEGORY_DEFAULTS_USED,
    }


# Internal: which categories default to which estrategia when the proposer picks "maioria".
_CATEGORY_DEFAULTS_USED: dict[str, Estrategia] = {
    "fundamentos": Estrategia.UNANIMIDADE,
    "registry": Estrategia.SUPERMAIORIA,
    "workflow": Estrategia.MAIORIA,
    "knowledge": Estrategia.MAIORIA,
    "capability": Estrategia.SUPERMAIORIA,
    "advisory": Estrategia.MAIORIA,
    "other": Estrategia.MAIORIA,
}


def default_strategy_for_category(category: str) -> Estrategia:
    """Resolve the default estrategia for a Category string (CONSTITUTION Art. 5).

    The orchestrator calls this when a proposal omits an explicit estrategia.
    """
    return _CATEGORY_DEFAULTS_USED.get(category.lower(), Estrategia.MAIORIA)
