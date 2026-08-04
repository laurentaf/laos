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
import urllib.request
from typing import Any

LITELLM_URL = "http://localhost:4000/v1/chat/completions"
LITELLM_KEY = "sk-laos-master"
MODEL = "deepseek-v4-flash"


def _extract_html(text: str) -> str:
    """Pull the HTML out of the LLM response (fenced or bare)."""
    m = re.search(r"```(?:html)?\s*(.*?)```", text, re.S)
    if m:
        return m.group(1).strip()
    # bare: if it looks like html, take from <!doctype or <html onward
    m = re.search(r"(<!doctype\s+html|<!DOCTYPE\s+HTML|<html)", text)
    if m:
        return text[m.start():].strip()
    return text.strip()


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
    }
    req = urllib.request.Request(
        LITELLM_URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {LITELLM_KEY}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read())
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
    except Exception as e:  # noqa: BLE001
        return {"status": "failed", "error_class": type(e).__name__,
                "cost_usd": 0.0, "tokens": 0, "error": str(e)[:200]}

    html = _extract_html(content)
    if not html or len(html) < 100:
        return {"status": "failed", "error_class": "empty_artifact",
                "cost_usd": 0.0, "tokens": 0, "error": "LLM returned no usable HTML"}
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
