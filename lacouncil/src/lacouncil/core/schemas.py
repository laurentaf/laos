"""Pydantic v2 schemas for the LACOUNCIL data model.

These models are the **canonical shape** of every record persisted to
DuckDB. They are imported by `duckdb_store.py`, `voting.py`, and the MCP
binding. Any change to a field name is a breaking change requiring a DuckDB
migration (see Art. 1 da CONSTITUTION).
"""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# ──────────────────────────────────────────────────────────────────────────────
# Enums
# ──────────────────────────────────────────────────────────────────────────────


class ProposalStatus(str, Enum):
    """Lifecycle of a proposal inside LACOUNCIL.

    Pendente → em_votacao → (aprovada OR rejeitada) → implementada (only if aprovada)
    """

    PENDENTE = "pendente"
    EM_VOTACAO = "em_votacao"
    APROVADA = "aprovada"
    REJEITADA = "rejeitada"
    IMPLEMENTADA = "implementada"
    CANCELADA = "cancelada"


class Estrategia(str, Enum):
    """Voting strategies (Art. 5 da CONSTITUTION)."""

    UNANIMIDADE = "unanimidade"
    SUPERMAIORIA = "supermaioria"
    MAIORIA = "maioria"


class VoteValue(str, Enum):
    """Individual vote cast by a Conselho member.

    ABSTENCAO counts as ausência for quorum (Art. 3 §2).
    """

    SIM = "sim"
    NAO = "nao"
    ABSTENCAO = "abstencao"


class Category(str, Enum):
    """The class of structural change a proposal is about.

    Used for routing + approver choice. The Conselho's threshold (Art. 5)
    follows the category:
    - FUNDAMENTOS: unanimidade (e.g., AGENTS.md)
    - REGISTRY:    supermaioria (e.g., registry/*.yaml)
    - WORKFLOW:    maioria (e.g., workflows/*.yaml)
    - KNOWLEDGE:   maioria (e.g., knowledge/*.md)
    - CAPABILITY:  supermaioria (new class of capability)
    - ADVISORY:    maioria
    """

    FUNDAMENTOS = "fundamentos"
    REGISTRY = "registry"
    WORKFLOW = "workflow"
    KNOWLEDGE = "knowledge"
    CAPABILITY = "capability"
    ADVISORY = "advisory"
    OTHER = "other"


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────


def _utc_now_iso() -> str:
    """Always-UTC ISO-8601 with second precision."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _canonical_json(payload: dict[str, Any]) -> str:
    """Serialize a dict deterministically (Jason Kinsky canonical JSON).

    Used to compute the proposal signature (Art. 4 §1).
    """
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


_SHA256_HEX = re.compile(r"^[a-f0-9]{64}$")


# ──────────────────────────────────────────────────────────────────────────────
# Domain models
# ──────────────────────────────────────────────────────────────────────────────


class InvestigationResult(BaseModel):
    """Output of `lacouncil.investigate`.

    The 5-Whys + Fishbone analyses + the inferred root causes. Session-scoped:
    each `investigate` call returns one of these and stores it under
    `session_id` for linking to subsequent proposals (Art. 4 §2).
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    gap: str
    five_whys: list[str] = Field(default_factory=list)
    fishbone: dict[str, list[str]] = Field(default_factory=dict)
    root_causes: list[str] = Field(default_factory=list)
    proposed_action: Optional[str] = None
    created_at: str = Field(default_factory=_utc_now_iso)


class Proposal(BaseModel):
    """A structural-change proposal registered for Conselho deliberation.

    After `tally_votes` succeeds, `status` progresses to APROVADA or
    REJEITADA. `implementation` carries post-acceptance metadata.

    Mutations follow CONSTITUTION Art. 1: a closed proposal is immutable;
    superseding changes require OBRR (open-by-record-replace).
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    proposal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    titulo: str = Field(min_length=10, max_length=200)
    descricao: str = Field(min_length=30)
    categoria: Category = Category.OTHER
    estrategia: Estrategia = Estrategia.MAIORIA
    autor: str  # agente-id (e.g., "orchestrator", "data-architect")
    contexto: str  # why this proposal exists now
    mudanca: str   # what changes
    impacto: str = ""  # expected impact (positive + risk)
    alternativas: str = ""  # alternatives considered (with rationale)
    created_at: str = Field(default_factory=_utc_now_iso)
    created_by_session: Optional[str] = None  # investigation.session_id

    # Set after deliberation (Art. 5 + 6)
    status: ProposalStatus = ProposalStatus.PENDENTE
    tally_summary: Optional[dict[str, Any]] = None  # populated by tally_votes
    implementation: Optional[dict[str, Any]] = None  # populated by implement_proposal

    # Updated alongside status transitions
    closed_at: Optional[str] = None
    signature: Optional[str] = None  # sha256-canonical-json

    @field_validator("descricao", "contexto", "mudanca")
    @classmethod
    def _non_trivial_strings(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 10:
            raise ValueError("descricao / contexto / mudanca precisa de pelo menos 10 chars")
        return v

    @model_validator(mode="after")
    def _signature_must_match(self) -> "Proposal":
        if self.signature is not None and not _SHA256_HEX.match(self.signature):
            raise ValueError("signature deve ser SHA-256 hex (64 chars)")
        return self


class Vote(BaseModel):
    """A single Conselho vote attached to a proposal.

    Stored in DuckDB with `proposal_id` as FK; one vote per (proposal, voter).
    """

    model_config = ConfigDict(extra="forbid")

    vote_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    proposal_id: str
    voter: str  # agent-id
    voto: VoteValue
    justificativa: str = Field(min_length=0, max_length=2000, default="")
    cast_at: str = Field(default_factory=_utc_now_iso)


class TallyResult(BaseModel):
    """Result of the voting strategy on a proposal.

    The Conselho compares `passed` against `status` to decide transition.
    """

    proposal_id: str
    passed: bool
    strategy: Estrategia
    votes: dict[str, int]  # {"sim": int, "nao": int, "abstencao": int}
    total: int
    ratio: float  # sim / max(total, 1)
    threshold: float
    new_status: ProposalStatus
    notes: str = ""
    computed_at: str = Field(default_factory=_utc_now_iso)


class Project(BaseModel):
    """Workspace-level project metadata (recorded by orchestrator on close)."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    project_id: Optional[str] = None  # set by DuckDB autoincrement
    project_slug: str = Field(pattern=r"^[a-z][a-z0-9_-]{1,80}$")
    scope: str
    capabilities_used: list[str] = Field(default_factory=list)
    deliverable_summary: str
    follow_up: str = ""
    follows_pattern: Optional[str] = None  # canonical bucket name
    recorded_at: str = Field(default_factory=_utc_now_iso)


class ProjectRecord(BaseModel):
    """Public record returned by `record_project` — same data, plus id."""

    project_id: int
    project_slug: str
    scope: str
    capabilities_used: list[str]
    deliverable_summary: str
    follow_up: str
    follows_pattern: Optional[str]
    recorded_at: str


class Pattern(BaseModel):
    """Cross-project recurring pattern detected by `detect_patterns`."""

    model_config = ConfigDict(extra="forbid")

    pattern: str  # canonical normalized string
    projects: list[str] = Field(default_factory=list)  # project_slugs
    occurrences: int
    confidence: float = Field(ge=0.0, le=1.0)
    detection_basis: str  # e.g., "shared_capabilities" or "shared_deliverable_keyword"
    detected_at: str = Field(default_factory=_utc_now_iso)


# ──────────────────────────────────────────────────────────────────────────────
# Lightweight request models (used by MCP tool inputs)
# ──────────────────────────────────────────────────────────────────────────────


class CreateProposalRequest(BaseModel):
    """Input shape for the `create_proposal` MCP tool."""

    model_config = ConfigDict(extra="forbid")

    titulo: str
    descricao: str
    categoria: Category = Category.OTHER
    estrategia: Estrategia = Estrategia.MAIORIA
    autor: str
    contexto: str
    mudanca: str
    impacto: str = ""
    alternativas: str = ""
    created_by_session: Optional[str] = None


class RegisterVoteRequest(BaseModel):
    """Input shape for `register_vote`."""

    model_config = ConfigDict(extra="forbid")

    proposal_id: str
    voter: str
    voto: VoteValue
    justificativa: str = ""


class TallyRequest(BaseModel):
    """Input shape for `tally_votes` (proposal_id only)."""

    model_config = ConfigDict(extra="forbid")

    proposal_id: str
    notes: str = ""


class ImplementRequest(BaseModel):
    """Input shape for `implement_proposal`."""

    model_config = ConfigDict(extra="forbid")

    proposal_id: str
    applied_at: str  # ISO-8601
    commit_sha: Optional[str] = None
    files_changed: list[str] = Field(default_factory=list)
    notes: str = ""


class RecordProjectRequest(BaseModel):
    """Input shape for `record_project`."""

    model_config = ConfigDict(extra="forbid")

    project_slug: str = Field(pattern=r"^[a-z][a-z0-9_-]{1,80}$")
    scope: str
    capabilities_used: list[str]
    deliverable_summary: str
    follow_up: str = ""
    follows_pattern: Optional[str] = None


class DetectPatternsRequest(BaseModel):
    """Input shape for `detect_patterns`."""

    model_config = ConfigDict(extra="forbid")

    min_occurrences: int = 3
    scope: Optional[list[str]] = None  # limit by category


# ──────────────────────────────────────────────────────────────────────────────
# Signature helper
# ──────────────────────────────────────────────────────────────────────────────


def compute_proposal_signature(proposal: Proposal) -> str:
    """SHA-256 of canonical-JSON encoding of the proposal (Art. 4 §1).

    Fields excluded from the signature: signature itself, status transitions,
    tally/implementation metadata. The signature is bound to the original
    payload; mutations invalidate it (Art. 1 §1).
    """
    payload = proposal.model_dump()
    payload.pop("signature", None)
    payload.pop("status", None)
    payload.pop("closed_at", None)
    payload.pop("tally_summary", None)
    payload.pop("implementation", None)
    import hashlib

    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
