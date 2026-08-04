#!/usr/bin/env python3
"""Isolated build_plan test with analysis passed in. Writes .laos/buildplan-bg.log"""

from __future__ import annotations

import pathlib
import subprocess
import sys

LAOS = pathlib.Path(r"F:\projects\laos-v2")
LOG = LAOS / ".laos" / "buildplan-bg.log"
CREATE_NO_WINDOW = 0x08000000


def main() -> int:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    code = (
        "import sys, json\n"
        "sys.path.insert(0, r'F:\\projects\\laos-v2')\n"
        "from laos.plan import planner\n"
        "LOG = __import__('pathlib').Path(r'F:\\projects\\laos-v2\\.laos\\buildplan-bg.log')\n"
        "data = {'project_name': '_x', 'brief': 'app de limpeza 3 abas', 'needs': ['design'], 'deliverables': []}\n"
        "analysis = {'modelo_dados': 'Necessidade(id,nome); Produto(id,nome,capacidade,unidade,preco,nivel_estoque,data_compra,necessidades_cobertas[]) N:N',\n"
        "  'perguntas_abertas': ['gasto medio usa data compra?', 'formula quanto comprar?'],\n"
        "  'regras_negocio': ['necessidade sem produto = nenhum produto estoque>0 cobre', 'recomendacao = estoque<=20%'],\n"
        "  'riscos': ['localStorage limpo perde tudo'],\n"
        "  'criterios_aceite': ['3 abas navegaveis', 'dados persistem']}\n"
        "with LOG.open('a', encoding='utf-8') as f:\n"
        "    f.write('=== launching ===\\n')\n"
        "try:\n"
        "    phases = planner.build_plan(data, analysis)\n"
        "    with LOG.open('a', encoding='utf-8') as f:\n"
        "        f.write('FASES_OK: ' + str(len(phases)) + '\\n')\n"
        "        for p in phases:\n"
        "            f.write(f'fase {p[\"stage\"]} {p[\"name\"]}: {p[\"spec\"][:200]}\\n')\n"
        "        f.write('DONE_OK\\n')\n"
        "except Exception as e:\n"
        "    import traceback\n"
        "    with LOG.open('a', encoding='utf-8') as f:\n"
        "        f.write('ERR ' + type(e).__name__ + ': ' + str(e)[:300] + '\\n')\n"
        "        f.write(traceback.format_exc()[:800] + '\\n')\n"
    )
    proc = subprocess.Popen(
        [sys.executable, "-c", code], cwd=str(LAOS),
        creationflags=CREATE_NO_WINDOW | 0x00000008,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    print(f"LAUNCHED pid={proc.pid}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
