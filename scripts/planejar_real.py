#!/usr/bin/env python3
"""Real _cmd_planejar on limpeza-casa (actual LLM). Writes .laos/planejar-real.log"""

from __future__ import annotations

import pathlib
import subprocess
import sys

LAOS = pathlib.Path(r"F:\projects\laos-v2")
LOG = LAOS / ".laos" / "planejar-real.log"
CREATE_NO_WINDOW = 0x08000000


def main() -> int:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    code = (
        "import sys\n"
        "sys.path.insert(0, r'F:\\projects\\laos-v2')\n"
        "LOG = __import__('pathlib').Path(r'F:\\projects\\laos-v2\\.laos\\planejar-real.log')\n"
        "from laos.chat import console\n"
        "with LOG.open('a', encoding='utf-8') as f:\n"
        "    f.write('=== launching ===\\n')\n"
        "try:\n"
        "    out = console._cmd_planejar('limpeza-casa', '')\n"
        "    with LOG.open('a', encoding='utf-8') as f:\n"
        "        f.write('OUT:\\n' + out + '\\n')\n"
        "        f.write('DONE_OK\\n')\n"
        "except Exception as e:\n"
        "    import traceback\n"
        "    with LOG.open('a', encoding='utf-8') as f:\n"
        "        f.write('ERR ' + type(e).__name__ + ': ' + str(e)[:400] + '\\n')\n"
        "        f.write(traceback.format_exc()[:800] + '\\n')\n"
    )
    proc = subprocess.Popen(
        [sys.executable, "-c", code], cwd=str(LAOS),
        creationflags=CREATE_NO_WINDOW | 0x00000008,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    print(f"LAUNCHED pid={proc.pid} (ver .laos/planejar-real.log)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
