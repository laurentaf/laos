#!/usr/bin/env python3
"""Launch fullplan smoke detached (LLM retries can take minutes).
Writes .laos/fullplan-bg.log"""

from __future__ import annotations

import pathlib
import subprocess
import sys

LAOS = pathlib.Path(r"F:\projects\laos-v2")
LOG = LAOS / ".laos" / "fullplan-bg.log"
CREATE_NO_WINDOW = 0x08000000


def main() -> int:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    code = (
        "import sys\n"
        "sys.path.insert(0, r'F:\\projects\\laos-v2')\n"
        "from laos.plan import planner\n"
        "LOG = __import__('pathlib').Path(r'F:\\projects\\laos-v2\\.laos\\fullplan-bg.log')\n"
        "data = {\n"
        "  'project_name': '_smoke-full',\n"
        "  'brief': ('App HTML autossuficiente (1 arquivo, 3 abas, localStorage) para gestao domestica de produtos de limpeza. Aba 1: necessidades de limpeza (vidro, pia, piso). Aba 2: produtos comprados/estoque (nome, capacidade litro/5L/500ml, checkboxes de necessidades que o produto cobre, quanto pagou, nivel de estoque 100/80/60/40/20/0%). Aba 3: dashboard - estoque atual, necessidades sem produto, gasto medio do mes, quanto comprar mes que vem.'),\n"
        "  'needs': ['design'],\n"
        "  'deliverables': [],\n"
        "}\n"
        "with LOG.open('a', encoding='utf-8') as f:\n"
        "    f.write('=== launching ===\\n')\n"
        "try:\n"
        "    import laos.plan.planner as P\n"
        "    orig = P._llm_json\n"
        "    def _logged(system, prompt, max_tokens):\n"
        "        c = orig(system, prompt, max_tokens)\n"
        "        with LOG.open('a', encoding='utf-8') as f:\n"
        "            f.write('=== RAW deep_think (' + str(len(c)) + ' chars) ===\\n' + c[:4000] + '\\n')\n"
        "        return c\n"
        "    P._llm_json = _logged\n"
        "    analysis = P.deep_think(data)\n"
        "    phases = P.build_plan(data, analysis)\n"
        "    with LOG.open('a', encoding='utf-8') as f:\n"
        "        f.write('PERGUNTAS: ' + str(len(analysis.get('perguntas_abertas',[]))) + '\\n')\n"
        "        for q in analysis.get('perguntas_abertas', [])[:6]:\n"
        "            f.write('  ? ' + q + '\\n')\n"
        "        f.write('FASES: ' + str(len(phases)) + '\\n')\n"
        "        for p in phases:\n"
        "            f.write(f'fase {p[\"stage\"]} {p[\"name\"]}: {p[\"spec\"][:250]}\\n')\n"
        "        f.write('DONE_OK\\n')\n"
        "except Exception as e:\n"
        "    import traceback\n"
        "    with LOG.open('a', encoding='utf-8') as f:\n"
        "        f.write('ERR ' + type(e).__name__ + ': ' + str(e)[:500] + '\\n')\n"
        "        f.write(traceback.format_exc()[:1000] + '\\n')\n"
    )
    proc = subprocess.Popen(
        [sys.executable, "-c", code], cwd=str(LAOS),
        creationflags=CREATE_NO_WINDOW | 0x00000008,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    print(f"LAUNCHED pid={proc.pid} (ver .laos/fullplan-bg.log)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
