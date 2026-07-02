"""LACOUNCIL MCP server — stdio FastMCP binding using base mcp.server.Server.

Migrated from FastMCP (required fastmcp package which conflicted with pydantic
version constraints) to base mcp.server.Server for compatibility with mcp>=1.27.

Exposed tools (per registry/capabilities.yaml):
    G1 (mandatory):   health, list_supported_operations
    Proposal lifecycle: create_proposal, get_proposal, list_proposals,
                       tally_votes
    Voting:           register_vote
    Implementation:   implement_proposal
    Pattern:          record_project, detect_patterns
    Investigation:    investigate
    Confidence Ladder (d3095fa3, 2026-07-02):
                       log_user_question,
                       detect_user_question_patterns,
                       create_proposal_from_pattern,
                       cleanup_user_questions
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import asyncio
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from lacouncil import __version__, __status__
from lacouncil.core import user_questions as __user_questions
from lacouncil.core.duckdb_store import (
    connect,
    detect_patterns as _detect_patterns,
    get_proposal as __get_proposal,
    list_projects,
    list_proposals as __list_proposals,
    record_project as __record_project,
    register_vote as __register_vote,
    upsert_proposal,
)
from lacouncil.core.voting import tally_votes as __tally_votes
from lacouncil.core.investigation import build_prompt_for_investigation

# ──────────────────────────────────────────────────────────────────────────────
# MCP Server (base mcp.server.Server)
# ──────────────────────────────────────────────────────────────────────────────

server = Server("lacouncil")

TOOL_FUNCTIONS: dict[str, Any] = {}
TOOL_DEFINITIONS: list[Tool] = []


def _make_tool(name: str, description: str, properties: dict, required: list[str]) -> Tool:
    return Tool(name=name, description=description,
                inputSchema={"type": "object", "properties": properties, "required": required})


def _health() -> dict[str, Any]:
    try:
        con = connect()
        row = con.execute("SELECT 1 AS ok").fetchone()
        con.close()
        ping_ok = row[0] == 1 if row else False
    except Exception as exc:
        ping_ok = False
        reason = str(exc)
    else:
        reason = None
    return {"status": "ok" if ping_ok else "degraded", "version": __version__,
            "server_status": __status__, "db_reachable": ping_ok, "reason": reason}


def _list_supported_operations() -> list[str]:
    return [
        "health", "list_supported_operations", "investigate", "create_proposal",
        "get_proposal", "list_proposals", "register_vote", "tally_votes",
        "implement_proposal", "record_project", "detect_patterns",
        # Confidence Escalation Ladder (LACOUNCIL d3095fa3, 2026-07-02)
        "log_user_question", "detect_user_question_patterns",
        "create_proposal_from_pattern", "cleanup_user_questions",
    ]


def _investigate(gap: str) -> dict:
    return {
        "prompt": build_prompt_for_investigation(gap),
        "note": "Feed prompt output to LLM, then call persist_investigation separately.",
    }


def _create_proposal(
    titulo: str, descricao: str, autor: str, contexto: str, mudanca: str,
    impacto: str = "", alternativas: str = "", categoria: str = "outro",
    estrategia: str = "maioria",
) -> dict:
    from lacouncil.core.schemas import Category, CreateProposalRequest, Estrategia, Proposal
    req = CreateProposalRequest(
        titulo=titulo, descricao=descricao, autor=autor, contexto=contexto,
        mudanca=mudanca, impacto=impacto, alternativas=alternativas,
        categoria=Category(categoria.lower()), estrategia=Estrategia(estrategia.lower()),
    )
    proposal = Proposal(**req.model_dump())
    return upsert_proposal(proposal).model_dump(mode="json")


def _get_proposal(proposal_id: str) -> dict | None:
    result = __get_proposal(proposal_id)
    return result.model_dump(mode="json") if result else None


def _list_proposals(status: str | None = None, limit: int = 50) -> list[dict]:
    from lacouncil.core.schemas import ProposalStatus
    ps = ProposalStatus(status.lower()) if status else None
    rows = __list_proposals(status=ps, limit=limit)
    return [r.model_dump(mode="json") for r in rows]


def _register_vote(proposal_id: str, voter: str, voto: str, justificativa: str = "") -> dict:
    from lacouncil.core.schemas import RegisterVoteRequest, Vote, VoteValue
    req = RegisterVoteRequest(
        proposal_id=proposal_id, voter=voter, voto=VoteValue(voto.lower()),
        justificativa=justificativa,
    )
    vote = Vote(**req.model_dump())
    return __register_vote(vote).model_dump(mode="json")


def _tally_votes(proposal_id: str, notes: str = "", strategy: str = "maioria") -> dict:
    from lacouncil.core.schemas import Estrategia
    return __tally_votes(proposal_id, Estrategia(strategy), notes=notes).model_dump()


def _implement_proposal(
    proposal_id: str, applied_at: str, commit_sha: str | None = None,
    files_changed: list[str] | None = None, notes: str = "",
) -> dict:
    from lacouncil.core.schemas import ImplementRequest
    req = ImplementRequest(
        proposal_id=proposal_id, applied_at=applied_at,
        commit_sha=commit_sha, files_changed=files_changed or [], notes=notes,
    )
    proposal = __get_proposal(proposal_id)
    if not proposal:
        return {"error": f"proposal {proposal_id} not found"}
    proposal.implementation = {"applied_at": applied_at, "commit_sha": commit_sha,
                               "files_changed": files_changed or [], "notes": notes}
    return upsert_proposal(proposal).model_dump(mode="json")


def _record_project(
    project_slug: str, scope: str, capabilities_used: list[str],
    deliverable_summary: str, follow_up: str = "", follows_pattern: str | None = None,
) -> dict:
    from lacouncil.core.schemas import RecordProjectRequest, ProjectRecord
    req = RecordProjectRequest(
        project_slug=project_slug, scope=scope, capabilities_used=capabilities_used,
        deliverable_summary=deliverable_summary, follow_up=follow_up,
        follows_pattern=follows_pattern,
    )
    record = ProjectRecord(**req.model_dump())
    return __record_project(record).model_dump(mode="json")


def __detect_patterns_tool(min_occurrences: int = 3, scope: list[str] | None = None) -> list[dict]:
    rows = _detect_patterns(min_occurrences=min_occurrences, scope=scope)
    return [dict(r) for r in rows]


# ──────────────────────────────────────────────────────────────────────────────
# Confidence Escalation Ladder tools (LACOUNCIL d3095fa3, 2026-07-02)
# ──────────────────────────────────────────────────────────────────────────────
# These tools back the orchestrator's `ask_user` instrumentation
# (see .opencode/agent/orchestrator.md §"User Question Logging").
# Read/write split (data-architect condition #9): log + create_proposal_from
# are writes; detect_user_question_patterns is pure read. The split is
# visible in the function naming (`__` prefix on internal helpers).
# ──────────────────────────────────────────────────────────────────────────────


def _log_user_question(
    question_text: str,
    cluster_id: str,
    context_json: dict[str, Any],
    session_id: str,
    answered_with: str | None = None,
) -> dict:
    """Log a single ask_user invocation. Idempotent on (session_id, cluster_id).

    Per chief-engineer convention: re-asking the same cluster in the same
    session UPDATEs the row (preserves question_id, refreshes text/timestamp).
    """
    uq = __user_questions.log(
        question=question_text,
        cluster_id=cluster_id,
        context=context_json,
        session_id=session_id,
        answered_with=answered_with,
    )
    return uq.model_dump(mode="json")


def _detect_user_question_patterns(
    min_occurrences: int | None = None,
    min_confidence: float | None = None,
    scope: list[str] | None = None,
) -> list[dict]:
    """Pure read: detect recurring user-question clusters.

    Returns list of `UserQuestionPattern` records. MUST NOT create
    proposals (data-architect condition #9).
    """
    patterns = __user_questions.detect_user_question_patterns(
        min_occurrences=min_occurrences,
        min_confidence=min_confidence,
        scope=scope,
    )
    return [p.model_dump(mode="json") for p in patterns]


def _create_proposal_from_pattern(
    cluster_id: str,
    occurrences: int,
    confidence: float,
    question_samples: list[str] | None = None,
    autor: str = "orchestrator",
) -> dict:
    """Explicit write: create a LACOUNCIL proposal from a pattern.

    The orchestrator calls this AFTER the user has approved promotion
    (transparency, see orchestrator.md §"Session Close"). The created
    proposal carries `meta.auto_created: true` and stays in status
    `pendente` — does NOT auto-implement (delivery-reviewer condition
    #10 loop escape). Conselho votes normally.
    """
    from lacouncil.core.schemas import UserQuestionPattern

    pattern = UserQuestionPattern(
        cluster_id=cluster_id,
        occurrences=occurrences,
        confidence=confidence,
        question_samples=question_samples or [],
    )
    proposal = __user_questions.create_proposal_from_pattern(
        pattern=pattern, autor=autor
    )
    return proposal.model_dump(mode="json")


def _cleanup_user_questions(retention_months: int | None = None) -> dict:
    """Idempotent retention cleanup. Returns count of rows deleted."""
    deleted = __user_questions.cleanup_user_questions(
        retention_months=retention_months
    )
    return {"deleted_rows": deleted, "retention_months": retention_months}


# Build tool registry from function signatures
TOOL_FUNCTIONS = {
    "health": _health,
    "list_supported_operations": _list_supported_operations,
    "investigate": _investigate,
    "create_proposal": _create_proposal,
    "get_proposal": _get_proposal,
    "list_proposals": _list_proposals,
    "register_vote": _register_vote,
    "tally_votes": _tally_votes,
    "implement_proposal": _implement_proposal,
    "record_project": _record_project,
    "detect_patterns": __detect_patterns_tool,
    # Confidence Escalation Ladder (LACOUNCIL d3095fa3, 2026-07-02)
    "log_user_question": _log_user_question,
    "detect_user_question_patterns": _detect_user_question_patterns,
    "create_proposal_from_pattern": _create_proposal_from_pattern,
    "cleanup_user_questions": _cleanup_user_questions,
}

TOOL_DEFINITIONS = [
    _make_tool("health", "Liveness + DuckDB connectivity check", {}, []),
    _make_tool("list_supported_operations", "List all MCP tool names", {}, []),
    _make_tool("investigate", "Return structured LLM prompt for 5-Whys + Fishbone analysis",
               {"gap": {"type": "string"}}, ["gap"]),
    _make_tool("create_proposal", "Register a new structural-change proposal",
               {"titulo": {"type": "string"}, "descricao": {"type": "string"},
                "autor": {"type": "string"}, "contexto": {"type": "string"},
                "mudanca": {"type": "string"}, "impacto": {"type": "string"},
                "alternativas": {"type": "string"}, "categoria": {"type": "string"},
                "estrategia": {"type": "string"}},
               ["titulo", "descricao", "autor", "contexto", "mudanca"]),
    _make_tool("get_proposal", "Fetch a single proposal by ID",
               {"proposal_id": {"type": "string"}}, ["proposal_id"]),
    _make_tool("list_proposals", "List proposals with optional status filter",
               {"status": {"type": "string"}, "limit": {"type": "integer"}}, []),
    _make_tool("register_vote", "Register a vote from a Conselho member",
               {"proposal_id": {"type": "string"}, "voter": {"type": "string"},
                "voto": {"type": "string"}, "justificativa": {"type": "string"}},
               ["proposal_id", "voter", "voto"]),
    _make_tool("tally_votes", "Compute the tally for a proposal and update status",
               {"proposal_id": {"type": "string"}, "notes": {"type": "string"}}, ["proposal_id"]),
    _make_tool("implement_proposal", "Record that an approved proposal was implemented",
               {"proposal_id": {"type": "string"}, "applied_at": {"type": "string"},
                "commit_sha": {"type": "string"}, "files_changed": {"type": "array", "items": {"type": "string"}},
                "notes": {"type": "string"}}, ["proposal_id", "applied_at"]),
    _make_tool("record_project", "Record a completed project for pattern detection",
               {"project_slug": {"type": "string"}, "scope": {"type": "string"},
                "capabilities_used": {"type": "array", "items": {"type": "string"}},
                "deliverable_summary": {"type": "string"}, "follow_up": {"type": "string"},
                "follows_pattern": {"type": "string"}},
               ["project_slug", "scope", "capabilities_used", "deliverable_summary"]),
    _make_tool("detect_patterns", "Detect recurring patterns across registered projects",
               {"min_occurrences": {"type": "integer"}, "scope": {"type": "array", "items": {"type": "string"}}}, []),
    # Confidence Escalation Ladder (LACOUNCIL d3095fa3, 2026-07-02)
    _make_tool(
        "log_user_question",
        "Log an orchestrator ask_user invocation. Idempotent on (session_id, cluster_id).",
        {
            "question_text": {"type": "string"},
            "cluster_id": {"type": "string"},
            "context_json": {"type": "object"},
            "session_id": {"type": "string"},
            "answered_with": {"type": "string"},
        },
        ["question_text", "cluster_id", "context_json", "session_id"],
    ),
    _make_tool(
        "detect_user_question_patterns",
        "Pure read: detect recurring user-question clusters (>= min_occurrences, confidence >= min_confidence).",
        {
            "min_occurrences": {"type": "integer"},
            "min_confidence": {"type": "number"},
            "scope": {"type": "array", "items": {"type": "string"}},
        },
        [],
    ),
    _make_tool(
        "create_proposal_from_pattern",
        "Explicit write: create a LACOUNCIL proposal from a detected pattern. Status starts pendente; does NOT auto-implement.",
        {
            "cluster_id": {"type": "string"},
            "occurrences": {"type": "integer"},
            "confidence": {"type": "number"},
            "question_samples": {"type": "array", "items": {"type": "string"}},
            "autor": {"type": "string"},
        },
        ["cluster_id", "occurrences", "confidence"],
    ),
    _make_tool(
        "cleanup_user_questions",
        "Idempotent retention cleanup. Returns deleted row count.",
        {"retention_months": {"type": "integer"}},
        [],
    ),
]


@server.list_tools()
async def list_tools() -> list[Tool]:
    return TOOL_DEFINITIONS


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    fn = TOOL_FUNCTIONS.get(name)
    if fn is None:
        return [TextContent(type="text", text=f'{{"error": "unknown tool: {name}"}}')]
    try:
        result = fn(**arguments)
    except TypeError as exc:
        return [TextContent(type="text", text=f'{{"error": "argument error: {exc}"}}')]
    return [TextContent(type="text", text=str(result))]


async def run_mcp():
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


def main(transport: str = "stdio") -> None:
    """Launch the MCP server. Default transport is stdio."""
    asyncio.run(run_mcp())


if __name__ == "__main__":
    main()