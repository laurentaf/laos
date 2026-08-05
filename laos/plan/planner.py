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


# ─── 3. deep thinking (passada 1) ────────────────────────────────────


def _llm_json(system: str, prompt: str, max_tokens: int) -> str:
    """Call the LLM and return raw content, with retry on empty response."""
    import time

    last_err: Exception | None = None
    for attempt in range(3):
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
        }
        req = urllib.request.Request(
            LITELLM_URL,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {LITELLM_KEY}"},
        )
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                data_resp = json.loads(resp.read())
                msg = data_resp["choices"][0]["message"]
                content = (msg.get("content") or "").strip()
                if not content:
                    # deepseek reasoning models may put the JSON in
                    # reasoning_content when content budget is exhausted
                    content = (msg.get("reasoning_content") or "").strip()
            if content:
                return content
            last_err = ValueError("LLM retornou conteúdo vazio")
        except Exception as e:  # noqa: BLE001
            last_err = e
        time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"LLM falhou após 3 tentativas: {last_err}")


def _extract_json_block(content: str, want_list: bool = False):
    """Extract a JSON object or array from an LLM response robustly."""
    import re

    raw = content.strip()
    # try direct parse first (clean JSON)
    try:
        return json.loads(raw)
    except Exception:  # noqa: BLE001
        pass
    # fenced ```json ... ```
    m = re.search(r"```(?:json)?\s*(\{.*?\}|\{.*\}|\[.*?\])\s*```", raw, re.S)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:  # noqa: BLE001
            pass
    # first balanced { ... } or [ ... ]
    opener = "[" if want_list else "{"
    closer = "]" if want_list else "}"
    start = raw.find(opener)
    if start == -1:
        raise ValueError("LLM não retornou JSON")
    depth = 0
    in_str = False
    esc = False
    end = None
    for i in range(start, len(raw)):
        c = raw[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
            continue
        if c == '"':
            in_str = True
        elif c == opener:
            depth += 1
        elif c == closer:
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end is None:
        raise ValueError("JSON não balanceado")
    return json.loads(raw[start:end])


def deep_think(data: dict[str, Any]) -> dict[str, Any]:
    """Passada 1: razão sobre o projeto ANTES de propor fases.

    Responde as decisões que o brief não cobre: modelo de dados,
    perguntas abertas, regras de negócio, riscos, critérios de aceite.
    """
    brief = data.get("brief", "")
    needs = data.get("needs", []) or []
    try:
        caps = needs_mod.primary_capabilities_for(needs)
    except KeyError:
        caps = []
    system = (
        "Você é um arquiteto de software senior. Responda com JSON EXATO. "
        "NÃO raciocine em voz alta: vá direto ao JSON, conciso e específico. "
        "Forma obrigatória: "
        '{"modelo_dados": "...", "perguntas_abertas": ["..."], '
        '"regras_negocio": ["..."], "riscos": ["..."], '
        '"criterios_aceite": ["..."]}. '
        "modelo_dados: entidades/relações/campos em texto curto. "
        "perguntas_abertas: 3-6 itens que o brief não responde e afetam "
        "implementação. regras_negocio: 3-6 heurísticas/cálculos explícitos. "
        "riscos: 3-5 concretos. criterios_aceite: 3-6 testáveis. "
        "ESCOPO: se o pedido for GRANDE (um sistema completo, uma "
        "plataforma tipo YouTube), analise SÓ o MVP iterável — o "
        "conjunto mínimo de entidades e regras que sustenta a primeira "
        "entrega. Não despeje o modelo do sistema inteiro."
    )
    prompt = (
        f"Brief: {brief}\n"
        f"Needs: {needs}\n"
        f"Capabilities: {caps}\n\n"
        "Analise profundamente e responda o JSON."
    )
    content = _llm_json(system, prompt, 8000)
    try:
        analysis = _extract_json_block(content)
        if isinstance(analysis, dict):
            return analysis
    except Exception:  # noqa: BLE001
        pass
    # fallback: reasoning contains the full analysis as prose — structure it
    return {
        "modelo_dados": content[:1500],
        "perguntas_abertas": ["(ver reasoning completo no log — JSON cortado)"],
        "regras_negocio": [content[1500:3500]],
        "riscos": [content[3500:5500]],
        "criterios_aceite": ["(JSON final truncado pelo limite de tokens — "
                             "aumentar max_tokens ou simplificar o prompt)"],
        "_raw": content,
    }


# ─── 3b. build phase plan (passada 2, fundamentada) ──────────────────


def build_plan(data: dict[str, Any], analysis: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Propose the phase breakdown (LLM) given brief + deep analysis."""
    brief = data.get("brief", "")
    needs = data.get("needs", []) or []
    try:
        caps = needs_mod.primary_capabilities_for(needs)
    except KeyError:
        caps = []
    system = (
        "Você é um planejador de engenharia. Dado o brief, a análise "
        "profunda (modelo de dados, perguntas abertas, regras, riscos, "
        "critérios) e as capabilities, proponha a decomposição em FASES "
        "ordenadas (3 a 8 fases) para o MVP ITERÁVEL — nunca o sistema "
        "inteiro. REGRAS:\n"
        "  - Se o brief for GRANDE ('um sistema tipo YouTube', 'uma "
        "  plataforma completa'), planeje SÓ o MVP: as fases que "
        "  entregam a versão mínima útil e iterável. Features além do "
        "  MVP são mencionadas como 'fora do escopo desta iteração', "
        "  NÃO como fases.\n"
        "  - FASE 0 SEMPRE: fundação do projeto — criar/validar "
        "  project.yaml com brief REAL, especificação (SDD: "
        "  spec/constitution.md, spec/todo.md, contract.md), harness "
        "  de teste, e verificar quais agentes/MCPs existem (latade, "
        "  ladesign, lan8n, laecon) em vez de inventar stack. Se o "
        "  projeto já tem isso, diga 'já existe' e pule.\n"
        "  - PROJETO CURTO (brief de 1-2 frases, 1-2 entidades): "
        "  DETALHE mais — cada fase com spec concreta (o que faz, "
        "  campos, botões, telas). Não seja genérico; um app de "
        "  limpeza tem fases como 'Aba Produtos: cadastro com nome, "
        "  quantidade, validade' e não 'implementar módulo de "
        "  produtos'.\n"
        "  - Cada fase deve caber numa chamada: 1 artefato entregável "
        "  razoável (uma tela, um CRUD, um módulo) — não um subsistema "
        "  inteiro.\n"
        "  - CADA fase deve: endereçar uma parte concreta do modelo de "
        "  dados OU resolver uma pergunta aberta OU implementar uma "
        "  regra de negócio — não repetir o brief.\n"
        "  - Inclua nas specs as decisões da análise que fundamentam a "
        "  fase.\n"
        "Responda SOMENTE com JSON válido: "
        '[{"name": "...", "spec": "...", "artifacts": ["..."], "stage": N}, ...]'
    )
    prompt = (
        f"Brief: {brief}\n"
        f"Needs: {needs}\n"
        f"Capabilities primárias: {caps}\n\n"
        f"--- ANÁLISE PROFUNDA ---\n{json.dumps(analysis, ensure_ascii=False, indent=2)}\n\n"
        "Proponha as fases. Se o brief for curto, detalhe cada fase "
        "com campos/telas/ações concretas. A fase 0 é sempre a "
        "fundação (yaml/SDD/harness/agentes). Cada fase: stage "
        "numerado (1..N), name, spec detalhada em português "
        "FUNDAMENTADA na análise (mencione a entidade/regra/risco que "
        "resolve), artifacts com path sob artifacts/<subdir>/."
    )
    content = _llm_json(system, prompt, 12000)
    phases = _extract_json_block(content, want_list=True)
    if not isinstance(phases, list):
        raise ValueError("LLM retornou fases não-lista")
    for i, p in enumerate(phases):
        p["stage"] = i + 1
        p["status"] = "pending"
    return phases


# ─── 4. write back ──────────────────────────────────────────────────


def apply_plan(data: dict[str, Any], phases: list[dict[str, Any]],
               analysis: dict[str, Any] | None = None) -> dict[str, Any]:
    """Merge the proposed phases + analysis into the contract and save."""
    root = _laos_root()
    project_id = data.get("project_name")
    py = root / "projects" / project_id / "project.yaml"
    data["deliverables"] = phases
    if analysis:
        data["planning"] = analysis
    data["status"] = "planned"
    py.write_text(
        "# Gerado por laos plan\n" + yaml.safe_dump(data, allow_unicode=True,
                                                    sort_keys=False),
        encoding="utf-8",
    )
    return data


# ─── entry ──────────────────────────────────────────────────────────


def plan_project(project_id: str, brief: str | None = None) -> dict[str, Any]:
    """Run the planning phase (deep think + decompose). Returns the
    final contract + gaps found."""
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
        # passada 1: pensar; passada 2: decompor fundamentado
        analysis = deep_think(data)
        phases = build_plan(data, analysis)
        data = apply_plan(data, phases, analysis)
        return {"project_id": project_id, "gaps_found": gaps,
                "phases_proposed": len(phases), "contract": data,
                "analysis": analysis, "status": "planned"}
    return {"project_id": project_id, "gaps_found": [],
            "phases_proposed": len(data.get("deliverables", []) or []),
            "contract": data, "status": "ready"}
