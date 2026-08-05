#!/usr/bin/env python3
"""Deterministic server launcher: kill :7331, spawn uvicorn, wait health.
Writes .laos/boot-deterministic.log"""

from __future__ import annotations

import pathlib
import subprocess
import sys
import time
import urllib.request

LAOS = pathlib.Path(r"F:\projects\laos-v2")
LOG = LAOS / ".laos" / "boot-deterministic.log"
PIDFILE = LAOS / ".laos" / "server.pid"
CREATE_NO_WINDOW = 0x08000000


def log(msg: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(msg + "\n")


def kill_port() -> None:
    r = subprocess.run(["netstat", "-ano"], capture_output=True, text=True,
                       creationflags=CREATE_NO_WINDOW)
    pids = set()
    for l in r.stdout.splitlines():
        if ":7331" in l and "LISTENING" in l:
            pids.add(l.split()[-1])
    for pid in pids:
        subprocess.run(["taskkill", "/PID", pid, "/F", "/T"],
                       capture_output=True, creationflags=CREATE_NO_WINDOW)
        log(f"killed {pid}")
    time.sleep(1)


def probe() -> bool:
    try:
        with urllib.request.urlopen("http://127.0.0.1:7331/healthz", timeout=2):
            return True
    except Exception:  # noqa: BLE001
        return False


def main() -> int:
    kill_port()
    logf = open(LAOS / ".laos" / "server.log", "a", encoding="utf-8")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "laos.web.app:app",
         "--host", "127.0.0.1", "--port", "7331"],
        cwd=str(LAOS), creationflags=CREATE_NO_WINDOW | 0x00000008,
        stdout=logf, stderr=logf,
    )
    PIDFILE.write_text(str(proc.pid), encoding="utf-8")
    log(f"spawned pid={proc.pid}")
    for _ in range(30):
        if probe():
            log(f"healthy pid={proc.pid}")
            print(f"SERVER_READY pid={proc.pid}")
            return 0
        time.sleep(0.5)
    log("NOT healthy")
    print("SERVER_TIMEOUT")
    return 1


if __name__ == "__main__":
    sys.exit(main())
