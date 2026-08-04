#!/usr/bin/env python3
"""Full laos plan on limpeza-casa brief (deep think + phases). Writes .laos/fullplan.log"""

from __future__ import annotations

import pathlib
import sys

LAOS = pathlib.Path(r"F:\projects\laos-v2")
LOG = LAOS / ".laos" / "fullplan.log"


def main() -> int:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    from laos.plan import planner

    # project exists with deliverables -> gaps empty -> plan_project returns ready
    # so we call the deep pipeline directly to show the improved plan
    data = {
        "project_name": "_smoke-full",
        "brief": (
            "App HTML autossuficiente (1 arquivo, 3 abas, localStorage) "
            "para gestão doméstica de produtos de limpeza. Aba 1: "
            "necessidades de limpeza (vidro, pia, piso — usuário adiciona "
            "à vontade). Aba 2: produtos comprados/estoque (nome, "
            "capacidade litro/5L/500ml, checkboxes de necessidades que o "
            "produto cobre, quanto pagou, nível de estoque "
            "100/80/60/40/20/0%). Aba 3: dashboard — estoque atual, "
            "necessidades sem produto, gasto médio do mês, quanto comprar "
            "mês que vem."
        ),
        "needs": ["design"],
        "deliverables": [],
    }
    try:
        # log raw responses for debugging
        orig_llm = planner._llm_json

        def _logged(system, prompt, max_tokens):
            content = orig_llm(system, prompt, max_tokens)
            with LOG.open("a", encoding="utf-8") as f:
                f.write(f"=== RAW ({len(content)} chars) ===\n{content[:3000]}\n")
            return content

        planner._llm_json = _logged
        analysis = planner.deep_think(data)
        phases = planner.build_plan(data, analysis)
        with LOG.open("a", encoding="utf-8") as f:
            f.write("=== ANÁLISE (resumo) ===\n")
            f.write(f"perguntas: {len(analysis.get('perguntas_abertas',[]))} | "
                    f"regras: {len(analysis.get('regras_negocio',[]))} | "
                    f"riscos: {len(analysis.get('riscos',[]))}\n")
            for q in (analysis.get("perguntas_abertas") or [])[:5]:
                f.write(f"  ? {q}\n")
            f.write("\n=== FASES FUNDAMENTADAS ===\n")
            for p in phases:
                f.write(f"fase {p['stage']} {p['name']}:\n  {p['spec'][:300]}\n")
        print(f"FULLPLAN_OK: {len(phases)} fases, "
              f"{len(analysis.get('perguntas_abertas',[]))} perguntas")
        return 0
    except Exception as e:  # noqa: BLE001
        with LOG.open("a", encoding="utf-8") as f:
            f.write(f"ERR {type(e).__name__}: {e}\n")
        print(f"FULLPLAN_ERR {type(e).__name__}: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
