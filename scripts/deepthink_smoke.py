#!/usr/bin/env python3
"""Smoke: deep_think + build_plan on the limpeza-casa brief (real LLM).
Writes .laos/deepthink.log"""

from __future__ import annotations

import pathlib
import sys

LAOS = pathlib.Path(r"F:\projects\laos-v2")
LOG = LAOS / ".laos" / "deepthink.log"


def main() -> int:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    from laos.plan import planner

    data = {
        "project_name": "_smoke-deep",
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
        analysis = planner.deep_think(data)
        phases = planner.build_plan(data, analysis)
        with LOG.open("a", encoding="utf-8") as f:
            f.write("=== ANÁLISE PROFUNDA ===\n")
            f.write(f"modelo_dados: {analysis.get('modelo_dados','')}\n\n")
            f.write("perguntas_abertas:\n")
            for q in analysis.get("perguntas_abertas", []):
                f.write(f"  ? {q}\n")
            f.write("regras_negocio:\n")
            for r in analysis.get("regras_negocio", []):
                f.write(f"  • {r}\n")
            f.write("riscos:\n")
            for r in analysis.get("riscos", []):
                f.write(f"  ⚠ {r}\n")
            f.write("criterios_aceite:\n")
            for c in analysis.get("criterios_aceite", []):
                f.write(f"  ✓ {c}\n")
            f.write("\n=== FASES ===\n")
            for p in phases:
                f.write(f"fase {p['stage']} {p['name']}:\n  {p['spec'][:250]}\n")
        print(f"DEEP_OK: {len(phases)} fases, {len(analysis.get('perguntas_abertas',[]))} perguntas")
        return 0
    except Exception as e:  # noqa: BLE001
        with LOG.open("a", encoding="utf-8") as f:
            f.write(f"ERR {type(e).__name__}: {e}\n")
        print(f"DEEP_ERR {type(e).__name__}: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
