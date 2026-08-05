#!/usr/bin/env python3
"""Run limpeza-v3 full pipeline with the REAL LLM runner (detached).
Writes .laos/limpeza-v3-run.log"""

from __future__ import annotations

import pathlib
import subprocess
import sys

LAOS = pathlib.Path(r"F:\projects\laos-v2")
LOG = LAOS / ".laos" / "limpeza-v3-run.log"
CREATE_NO_WINDOW = 0x08000000


def main() -> int:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    code = (
        "import sys\n"
        "sys.path.insert(0, r'F:\\projects\\laos-v2')\n"
        "import pathlib\n"
        "LAOS = pathlib.Path(r'F:\\projects\\laos-v2')\n"
        "LOG = LAOS / '.laos' / 'limpeza-v3-run.log'\n"
        "# feedback em tempo real: redireciona stdout para o arquivo de log\n"
        "logf = open(LOG, 'a', encoding='utf-8')\n"
        "sys.stdout = logf\n"
        "sys.stderr = logf\n"
        "print('=== launching v3 ===', flush=True)\n"
        "from laos.core import pipeline, runners\n"
        "py = LAOS / 'projects' / 'limpeza-v3' / 'project.yaml'\n"
        "def router(stage, ctx):\n"
        "    if stage.get('name') == 'app-completo':\n"
        "        return runners.llm_app_runner(stage, ctx)\n"
        "    return runners.llm_artifact_runner(stage, ctx)\n"
        "pipe = pipeline.RunPipeline('limpeza-v3', py, runner=router)\n"
        "run_id = pipe.run(force_new=True)\n"
        "print('RUN_ID=' + str(run_id), flush=True)\n"
        "from laos.db import schema\n"
        "con = schema.connect()\n"
        "rows = con.execute(\"SELECT phase, name, status, cost_usd, tokens, errors FROM phases WHERE project_id='limpeza-v3' ORDER BY phase\").fetchall()\n"
        "print('=== FASES ===', flush=True)\n"
        "for r in rows:\n"
        "    print(f'  fase {r[0]} {r[1]}: {r[2]} ${r[3]:.6f} {r[4]}tok {r[5]}err', flush=True)\n"
    )
    proc = subprocess.Popen(
        [sys.executable, "-c", code], cwd=str(LAOS),
        creationflags=CREATE_NO_WINDOW | 0x00000008,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    print(f"LAUNCHED pid={proc.pid} (ver .laos/limpeza-v3-run.log)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
