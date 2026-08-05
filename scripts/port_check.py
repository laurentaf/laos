#!/usr/bin/env python3
"""Who is on :7331. Writes .laos/port-check.log"""

from __future__ import annotations

import pathlib
import subprocess
import urllib.request

LAOS = pathlib.Path(r"F:\projects\laos-v2")
LOG = LAOS / ".laos" / "port-check.log"
CREATE_NO_WINDOW = 0x08000000


def main() -> int:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(["netstat", "-ano"], capture_output=True, text=True,
                       creationflags=CREATE_NO_WINDOW)
    with LOG.open("a", encoding="utf-8") as f:
        for l in r.stdout.splitlines():
            if ":7331" in l and "LISTENING" in l:
                f.write("LISTEN: " + l + "\n")
        try:
            with urllib.request.urlopen("http://127.0.0.1:7331/healthz", timeout=3) as resp:
                f.write(f"HEALTH {resp.status}\n")
        except Exception as e:  # noqa: BLE001
            f.write(f"HEALTH_ERR {type(e).__name__}: {str(e)[:100]}\n")
    print("DONE (see .laos/port-check.log)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
