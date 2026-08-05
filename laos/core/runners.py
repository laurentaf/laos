"""LAOS real stage runners — execute a stage via LLM with real cost.

Replaces the demo `costed_runner` for actual work: each stage's `spec`
drives an LLM call (via LiteLLM) that produces a real artifact, and the
response usage is captured so phase costs are REAL, not simulated.

Usage in the pipeline:
    pipe = RunPipeline(project, py, runner=llm_artifact_runner)
"""

from __future__ import annotations

import json
import pathlib
import re
import time
import urllib.request
from typing import Any

LITELLM_URL = "http://localhost:4000/v1/chat/completions"
LITELLM_KEY = "sk-laos-master"
MODEL = "deepseek-v4-flash"
MAX_ATTEMPTS = 3
TIMEOUT_S = 300


def _extract_html(text: str) -> str:
    """Pull the HTML out of the LLM response.

    ONLY accepts output that looks like real HTML (doctype, <html, or
    enough html tags). Reasoning/pseudo-code fragments are rejected so
    the artifact is never garbage.
    """
    # fenced ```html ... ```
    m = re.search(r"```(?:html)?\s*(.*?)```", text, re.S)
    if m:
        cand = m.group(1).strip()
        if _looks_like_html(cand):
            return cand
    # bare: from <!doctype or <html onward
    m = re.search(r"(<!doctype\s+html|<!DOCTYPE\s+HTML|<html[\s>])", text, re.S)
    if m:
        return text[m.start():].strip()
    return ""


def _looks_like_html(cand: str) -> bool:
    """Heuristic: has doctype/html OR at least a handful of html tags."""
    low = cand.lower()
    if "<!doctype" in low or "<html" in low:
        return True
    # count closing tags — real html has many
    tags = re.findall(r"</[a-z][a-z0-9]*>", low)
    return len(tags) >= 5


def llm_artifact_runner(stage: dict[str, Any], ctx: Any) -> dict[str, Any]:
    """Generate the artifact for this stage via LLM.

    The stage dict comes from project.yaml deliverables; the `spec`
    field of each deliverable is the instruction for what to build.
    """
    name = stage.get("name", "?")
    spec = stage.get("spec", stage.get("label", ""))
    stage_num = stage.get("stage", 0)
    project_id = getattr(ctx, "project_id", "?")
    root = getattr(ctx, "_root", None)

    system = (
        "Você é um engenheiro frontend. Gere um ÚNICO arquivo HTML "
        "autossuficiente, em português, com CSS embutido (sem dependência "
        "externa além de fonts opcionais), com JavaScript inline, usando "
        "localStorage para persistência. Interface limpa e funcional. "
        "Responda SOMENTE com o HTML completo — sem explicações antes ou depois."
    )
    prompt = (
        f"Projeto: {project_id} — gestão de produtos de limpeza de casa.\n"
        f"Fase {stage_num} — {name}.\n"
        f"Especificação: {spec}\n\n"
        "Gere o HTML completo desta fase."
    )
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 12000,
        # metadata so Langfuse traces can be attributed per project
        "metadata": {"laos_project": project_id, "laos_phase": stage_num},
    }

    # retry with backoff: OpenCode Go intermittently returns empty content
    # (reasoning consumes the token budget) or times out on long specs.
    last_err: str | None = None
    content = ""
    usage: dict[str, Any] = {}
    for attempt in range(MAX_ATTEMPTS):
        req = urllib.request.Request(
            LITELLM_URL,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {LITELLM_KEY}"},
        )
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
                data = json.loads(resp.read())
                msg = data["choices"][0]["message"]
                content = (msg.get("content") or "").strip()
                if not content:
                    # reasoning models may emit the HTML in reasoning_content
                    content = (msg.get("reasoning_content") or "").strip()
                usage = data.get("usage", {})
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {str(e)[:200]}"
            content = ""
        # validate: usable HTML?
        html_probe = _extract_html(content)
        if html_probe and len(html_probe) >= 100:
            break
        last_err = "empty_artifact: LLM returned no usable HTML"
        if attempt < MAX_ATTEMPTS - 1:
            time.sleep(3 * (attempt + 1))
    else:
        return {"status": "failed", "error_class": "empty_artifact",
                "cost_usd": 0.0, "tokens": 0, "error": last_err}

    html = _extract_html(content)
    # persist to the project artifacts dir (mirror convention)
    if root is None:
        from laos.core import needs

        root = needs._find_laos_root()
    out_dir = root / "projects" / project_id / "artifacts"
    out_dir.mkdir(parents=True, exist_ok=True)
    # artifact path derived from the deliverable's declared artifact when present
    declared = stage.get("artifacts", [])
    if declared:
        rel = declared[0]
        out = root / "projects" / project_id / rel
        out.parent.mkdir(parents=True, exist_ok=True)
    else:
        out = out_dir / f"fase{stage_num}-{name}.html"
    out.write_text(html, encoding="utf-8")

    # real cost from usage
    in_tok = usage.get("prompt_tokens", 0)
    out_tok = usage.get("completion_tokens", 0)
    cost = (in_tok * 0.00000014) + (out_tok * 0.00000028)  # deepseek-v4-flash
    return {"status": "completed", "error_class": None,
            "cost_usd": cost, "tokens": in_tok + out_tok,
            "artifact": str(out), "html_len": len(html)}


# ─── app runner: big deliverables built in parts ─────────────────────

# Canonical DOM ids shared across the 3 sub-calls. Pinning them prevents
# the LLM from inventing ids that don't match between shell and JS.
APP_IDS = {
    "necessidades": ["novaNecessidade", "addNecessidade", "listaNecessidades"],
    "produtos": ["prodNome", "prodCapacidade", "prodUnidade", "prodPreco",
                 "needsCheck", "prodEstoque", "addProduto", "listaProdutos"],
    "dashboard": ["estoqueAtual", "semProduto", "gastoMes", "sugestaoCompra"],
}


def _llm_part(system: str, prompt: str, max_tokens: int = 6000) -> str:
    """Single LLM call with retry (returns raw text)."""
    last_err: str | None = None
    for attempt in range(MAX_ATTEMPTS):
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": 0.3,
        }
        req = urllib.request.Request(
            LITELLM_URL,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {LITELLM_KEY}"},
        )
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
                d = json.loads(resp.read())
                content = (d["choices"][0]["message"].get("content") or "").strip()
                if not content:
                    content = (d["choices"][0]["message"].get("reasoning_content") or "").strip()
                if content:
                    return content
                last_err = "empty"
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {str(e)[:150]}"
        time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"LLM part failed: {last_err}")


def llm_app_runner(stage: dict[str, Any], ctx: Any) -> dict[str, Any]:
    """Build the full 3-tab app in 3 smaller LLM calls with pinned ids.

    Part 1: HTML+CSS shell (3 tabs, empty sections, pinned ids)
    Part 2: JS for tabs 1+2 (necessidades + produtos CRUD)
    Part 3: JS for tab 3 (dashboard)
    Then compose into a single index.html.
    """
    name = stage.get("name", "?")
    spec = stage.get("spec", "")
    project_id = getattr(ctx, "project_id", "?")
    root = getattr(ctx, "_root", None)
    if root is None:
        from laos.core import needs

        root = needs._find_laos_root()

    ids_n = ", ".join(APP_IDS["necessidades"])
    ids_p = ", ".join(APP_IDS["produtos"])
    ids_d = ", ".join(APP_IDS["dashboard"])

    # ── part 1: shell ────────────────────────────────────────────────
    shell_sys = (
        "Você gera HTML+CSS. Responda SOMENTE com o HTML completo de um "
        "app de gestão de produtos de limpeza: 3 abas (Necessidades, "
        "Produtos, Dashboard), sections vazias com os ids EXATOS pedidos, "
        "CSS embutido (fundo #f5f5f4, cards brancos, botão verde #16a34a, "
        "font system-ui), <script> vazio no fim. Sem frameworks, sem CDN. "
        "Português."
    )
    shell_prompt = (
        f"Spec: {spec[:600]}\n\n"
        "Gere o HTML shell. Use EXATAMENTE estes ids:\n"
        f"  Aba Necessidades: {ids_n}\n"
        f"  Aba Produtos: {ids_p}\n"
        f"  Aba Dashboard: {ids_d}\n"
        "Estrutura: <button class='tab' data-tab='...'> para navegar, "
        "<section id='tab-...' class='tab-content'> para cada aba. "
        "O <script> deve ficar vazio (o JS vem depois)."
    )
    shell_html = _extract_html(_llm_part(shell_sys, shell_prompt))
    if not shell_html:
        return {"status": "failed", "error_class": "empty_artifact",
                "cost_usd": 0.0, "tokens": 0}

    # ── part 2: JS abas 1+2 ───────────────────────────────────────────
    js12_sys = (
        "Você gera JavaScript puro (ES6) para um app de gestão de produtos "
        "de limpeza. Responda SOMENTE com o JS dentro de <script>...</script> "
        "(sem HTML). Use os ids exatos. localStorage chaves "
        "limpeza_necessidades e limpeza_produtos. Português, sem frameworks."
    )
    js12_prompt = (
        "Implemente o JS das Abas 1 e 2:\n"
        "Aba Necessidades (ids: " + ids_n + "): adicionar necessidade "
        "(campo + botão), listar com remover, persistir localStorage.\n"
        "Aba Produtos (ids: " + ids_p + "): formulário (nome, capacidade+"
        "unidade ml/L, preço, checkboxes das necessidades vindas do "
        "localStorage, estoque 100-0%), lista com barra de estoque colorida "
        "e remover, persistir localStorage.\n"
        "Navegação entre abas: cliques nos buttons .tab mostram a section "
        "correspondente.\n"
        "Retorne o JS completo."
    )
    js12 = _extract_script(_llm_part(js12_sys, js12_prompt))

    # ── part 3: JS dashboard ──────────────────────────────────────────
    js3_sys = (
        "Você gera JavaScript puro (ES6) para o dashboard de um app de "
        "gestão de produtos de limpeza. Responda SOMENTE com o JS dentro "
        "de <script>...</script> (sem HTML). Use os ids exatos. "
        "localStorage chaves limpeza_necessidades e limpeza_produtos. "
        "Português, sem frameworks."
    )
    js3_prompt = (
        "Implemente o JS do Dashboard (ids: " + ids_d + "):\n"
        "  estoqueAtual: lista produtos com nome, capacidade e % (barra).\n"
        "  semProduto: necessidades sem nenhum produto com estoque>0.\n"
        "  gastoMes: soma preços de produtos com dataCompra no mês atual, R$.\n"
        "  sugestaoCompra: produtos estoque<=40% e necessidades descobertas, "
        "'repor X'.\n"
        "Recalcula ao mostrar a aba. Retorne o JS completo."
    )
    js3 = _extract_script(_llm_part(js3_sys, js3_prompt))

    # ── compose ───────────────────────────────────────────────────────
    js_all = f"\n// --- abas 1+2 ---\n{js12}\n// --- dashboard ---\n{js3}\n"

    # inject JS: prefer before </body>, else into any <script ...>
    if "</body>" in shell_html.lower():
        full = shell_html.lower().replace(
            "</body>", f"<script>{js_all}</script></body>", 1)
        # restore original casing of the body tag
        full = full.replace("</body>", "</body>", 1)
    elif re.search(r"<script[^>]*>", shell_html, re.S):
        full = re.sub(
            r"<script[^>]*>(.*?)</script>", f"<script>{js_all}</script>",
            shell_html, count=1, flags=re.S,
        )
    else:
        full = shell_html + f"<script>{js_all}</script>"

    # validate the composed artifact: real HTML + non-trivial JS
    if not _looks_like_html(full) or len(js_all.strip()) < 200:
        return {"status": "failed", "error_class": "incomplete_artifact",
                "cost_usd": 0.0, "tokens": 0,
                "error": f"composed app too small ({len(full)}B)"}

    # persist
    declared = stage.get("artifacts", [])
    if declared:
        out = root / "projects" / project_id / declared[0]
        out.parent.mkdir(parents=True, exist_ok=True)
    else:
        out_dir = root / "projects" / project_id / "artifacts"
        out_dir.mkdir(parents=True, exist_ok=True)
        out = out_dir / f"fase{stage.get('stage',0)}-{name}.html"
    out.write_text(full, encoding="utf-8")
    return {"status": "completed", "error_class": None,
            "cost_usd": 0.0, "tokens": 0,
            "artifact": str(out), "html_len": len(full)}


def _extract_script(text: str) -> str:
    """Pull JS out of the LLM response (fenced or bare <script>)."""
    m = re.search(r"```(?:js|javascript)?\s*(.*?)```", text, re.S)
    if m:
        return m.group(1).strip()
    m = re.search(r"<script[^>]*>(.*?)</script>", text, re.S)
    if m:
        return m.group(1).strip()
    return text.strip()
