#!/usr/bin/env python3
"""Force restart :7331 with current code, then probe all routes.
Writes .laos/final-probe.log"""

from __future__ import annotations

import pathlib
import subprocess
import sys
import time
import urllib.request
import urllib.parse

LAOS = pathlib.Path(r"F:\projects\laos-v2")
LOG = LAOS / ".laos" / "final-probe.log"
CREATE_NO_WINDOW = 0x08000000


def kill_7331() -> None:
    r = subprocess.run(["netstat", "-ano"], capture_output=True, text=True,
                       creationflags=CREATE_NO_WINDOW, timeout=30)
    pids = set()
    for line in (r.stdout or "").splitlines():
        if ":7331" in line and "LISTENING" in line:
            parts = line.split()
            if parts:
                pids.add(parts[-1])
    for pid in pids:
        subprocess.run(["taskkill", "/PID", pid, "/F"], capture_output=True,
                       creationflags=CREATE_NO_WINDOW, timeout=15)


def probe(label, url, method="GET", data=None):
    try:
        if method == "POST":
            req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(),
                                         headers={"Content-Type": "application/x-www-form-urlencoded"})
        else:
            req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode("utf-8", errors="replace")
            markers = [m for m in ["Entrega por projeto", "custo total", "duração total",
                                   "console", "enviar", "pronto", "faltando",
                                   "workflow", "banco"] if m in body]
            with LOG.open("a", encoding="utf-8") as f:
                f.write(f"{label}: HTTP {r.status} ({len(body)}B) markers={markers}\n")
            return True
    except Exception as e:  # noqa: BLE001
        with LOG.open("a", encoding="utf-8") as f:
            f.write(f"{label}: ERR {type(e).__name__} {str(e)[:150]}\n")
        return False


def main() -> int:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    kill_7331()
    time.sleep(1)
    logf = open(LAOS / ".laos" / "server.log", "a", encoding="utf-8")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "laos.web.app:app",
         "--host", "127.0.0.1", "--port", "7331"],
        cwd=str(LAOS), creationflags=CREATE_NO_WINDOW | 0x00000008,
        stdout=logf, stderr=logf,
    )
    (LAOS / ".laos" / "server.pid").write_text(str(proc.pid), encoding="utf-8")
    time.sleep(5)
    probe("healthz", "http://127.0.0.1:7331/healthz")
    probe("dashboard", "http://127.0.0.1:7331/dashboard")
    probe("detail", "http://127.0.0.1:7331/projects/limpeza-casa")
    probe("console", "http://127.0.0.1:7331/projects/limpeza-casa/console")
    probe("console-send", "http://127.0.0.1:7331/projects/limpeza-casa/console/send",
          method="POST", data={"message": "teste console"})
    probe("handoff", "http://127.0.0.1:7331/projects/limpeza-casa/handoff")
    print("DONE (see .laos/final-probe.log)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
