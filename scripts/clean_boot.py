#!/usr/bin/env python3
"""Kill ALL laos uvicorn processes (by port + by cmdline) then spawn fresh.
Writes .laos/clean-boot.log"""

from __future__ import annotations

import pathlib
import subprocess
import time
import urllib.request

LAOS = pathlib.Path(r"F:\projects\laos-v2")
LOG = LAOS / ".laos" / "clean-boot.log"
CREATE_NO_WINDOW = 0x08000000


def log(msg: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(msg + "\n")


def main() -> int:
    # 1. kill whatever listens on 7331 (with tree)
    r = subprocess.run(["netstat", "-ano"], capture_output=True, text=True,
                       creationflags=CREATE_NO_WINDOW)
    pids = set()
    for l in r.stdout.splitlines():
        if ":7331" in l and "LISTENING" in l:
            pids.add(l.split()[-1])
    for pid in pids:
        k = subprocess.run(["taskkill", "/PID", pid, "/F", "/T"],
                           capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
        log(f"kill {pid}: rc={k.returncode}")
    time.sleep(2)
    # 2. also kill any uvicorn python (cmdline contains laos.web.app)
    r2 = subprocess.run(["wmic", "process", "where",
                         "name='python.exe'", "get", "ProcessId,CommandLine",
                         "/format:csv"], capture_output=True, text=True,
                        creationflags=CREATE_NO_WINDOW)
    for line in (r2.stdout or "").splitlines():
        if "laos.web.app" in line:
            parts = line.split('","')
            pid = parts[-1].strip('"') if parts else ""
            if pid.isdigit():
                subprocess.run(["taskkill", "/PID", pid, "/F", "/T"],
                               capture_output=True, creationflags=CREATE_NO_WINDOW)
                log(f"killed uvicorn {pid}")
    time.sleep(1)
    # 3. confirm port free
    r3 = subprocess.run(["netstat", "-ano"], capture_output=True, text=True,
                        creationflags=CREATE_NO_WINDOW)
    still = [l for l in r3.stdout.splitlines() if ":7331" in l and "LISTENING" in l]
    log(f"after cleanup, 7331: {still or 'FREE'}")
    print(f"CLEAN: 7331 {'still busy' if still else 'FREE'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
