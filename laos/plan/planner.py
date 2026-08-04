"""LAOS plan — scaled planning phase.

Turns a rough project.yaml (or just a brief) into a complete, runnable
plan: resolves needs -> capabilities, detects gaps, builds the expected
workflow (phases in order with specs), and when the user approves, writes
the full project.yaml and offers to run.

Flow:
  1. read project.yaml (or scaffold from brief)
  2. resolve_needs -> capabilities (deterministic routing)
  3. gap analysis: deliverables without spec, needs without capability,
     phases without order, missing artifacts paths
  4. build phase plan (LLM-assisted: given the brief + capabilities,
     propose the phase breakdown and per-phase specs)
  5. write back project.yaml (complete)
  6. user approves -> run pipeline
"""

from __future__ import annotations

import json
import pathlib
import urllib.request
import uuid
from typing import Any

import yaml

from laos.core import needs as needs_mod

LITELLM_URL = "http://localhost:4000/v1/chat/completions"
LITELLM_KEY = "sk-laos-master"
MODEL = "deepseek-v4-flash"


def _laos_root() -> pathlib.Path:
    return needs_mod._find_laos_root()


# ─── 1. read/scaffold ───────────────────────────────────────────────


def load_contract(project_id: str) -> dict[str, Any]:
    root = _laos_root()
    py = root / "projects" / project_id / "project.yaml"
    if not py.exists():
        raise FileNotFoundError(
            f"{py} não existe. Crie o contrato com `laos plan {project_id}` "
            f"e um brief, ou use a rota de novo projeto no painel."
        )
    data = yaml.safe_load(py.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


def scaffold_from_brief(project_id: str, brief: str) -> dict[str, Any]:
    """Create a minimal contract from a brief (for brand-new projects)."""
    return {
        "project_name": project_id,
        "display_name": project_id.replace("-", " ").title(),
        "brief": brief,
        "needs": [],
        "deliverables": [],
        "status": "planning",
    }


# ─── 2. gap analysis (deterministic) ────────────────────────────────


def gap_analysis(data: dict[str, Any]) -> list[str]:
    """Detect gaps in the contract. Returns human-readable findings."""
    gaps: list[str] = []
    needs = data.get("needs", []) or []
    dels = data.get("deliverables", []) or []
    brief = data.get("brief", "")

    if not brief or len(brief) < 10:
        gaps.append("brief ausente ou curto demais (precisa descrever o projeto)")
    if not needs:
        gaps.append("needs vazio — o roteamento needs→capabilities não tem entrada")
    else:
        try:
            needs_mod.resolve_needs(needs)
        except KeyError as e:
            gaps.append(str(e))
    if not dels:
        gaps.append("deliverables vazio — nenhuma fase definida")
    else:
        missing_spec = [d.get("name") for d in dels
                        if not d.get("spec") and not d.get("label")]
        if missing_spec:
            gaps.append(f"deliverables sem spec: {missing_spec}")
        no_stage = [d.get("name") for d in dels if "stage" not in d]
        if no_stage:
            gaps.append(f"deliverables sem stage (ordem): {no_stage}")
        no_artifact = [d.get("name") for d in dels
                       if not d.get("artifacts") and d.get("status") != "pending"]
        if no_artifact:
            gaps.append(f"deliverables sem path de artifact: {no_artifact}")
    return gaps


# ─── 3. build phase plan (LLM-assisted) ──────────────────────────────


def build_plan(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Propose the phase breakdown (LLM) given brief + capabilities."""
    brief = data.get("brief", "")
    needs = data.get("needs", []) or []
    try:
        caps = needs_mod.primary_capabilities_for(needs)
    except KeyError:
        caps = []
    system = (
        "Você é um planejador de engenharia. Dado o brief de um projeto "
        "e as capabilities disponíveis, proponha a decomposição em FASES "
        "ordenadas (3 a 6 fases). Para cada fase: name curto, spec clara "
        "(o que construir e qual o artefato), e artifact path. "
        "Responda SOMENTE com JSON válido: "
        '[{"name": "...", "spec": "...", "artifacts": ["..."], "stage": N}, ...]'
    )
    prompt = (
        f"Brief: {brief}\n"
        f"Needs: {needs}\n"
        f"Capabilities primárias: {caps}\n\n"
        "Proponha as fases. Cada fase deve ter stage numerado (1..N), "
        "name, spec detalhada em português, e artifacts com path sob "
        "artifacts/<subdir>/."
    )
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 4000,
    }
    req = urllib.request.Request(
        LITELLM_URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {LITELLM_KEY}"},
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data_resp = json.loads(resp.read())
        content = data_resp["choices"][0]["message"]["content"]

    # extract JSON from the response
    import re

    m = re.search(r"\[.*\]", content, re.S)
    if not m:
        raise ValueError("LLM não retornou JSON de fases válido")
    phases = json.loads(m.group(0))
    if not isinstance(phases, list):
        raise ValueError("LLM retornou fases não-lista")
    # ensure stage ordering
    for i, p in enumerate(phases):
        p["stage"] = i + 1
        p["status"] = "pending"
    return phases


# ─── 4. write back ──────────────────────────────────────────────────


def apply_plan(data: dict[str, Any], phases: list[dict[str, Any]]) -> dict[str, Any]:
    """Merge the proposed phases into the contract and save."""
    root = _laos_root()
    project_id = data.get("project_name")
    py = root / "projects" / project_id / "project.yaml"
    data["deliverables"] = phases
    data["status"] = "planned"
    py.write_text(
        "# Gerado por laos plan\n" + yaml.safe_dump(data, allow_unicode=True,
                                                    sort_keys=False),
        encoding="utf-8",
    )
    return data


# ─── entry ──────────────────────────────────────────────────────────


def plan_project(project_id: str, brief: str | None = None) -> dict[str, Any]:
    """Run the planning phase. Returns the final contract + gaps found."""
    try:
        data = load_contract(project_id)
    except FileNotFoundError:
        if not brief:
            raise
        data = scaffold_from_brief(project_id, brief)
        root = _laos_root()
        (root / "projects" / project_id).mkdir(parents=True, exist_ok=True)
        (root / "projects" / project_id / "project.yaml").write_text(
            yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )

    gaps = gap_analysis(data)
    if gaps:
        # if the contract is incomplete, build the plan from brief
        phases = build_plan(data)
        data = apply_plan(data, phases)
        return {"project_id": project_id, "gaps_found": gaps,
                "phases_proposed": len(phases), "contract": data,
                "status": "planned"}
    return {"project_id": project_id, "gaps_found": [],
            "phases_proposed": len(data.get("deliverables", []) or []),
            "contract": data, "status": "ready"}
