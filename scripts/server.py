#!/usr/bin/env python3
"""Start the LAOS portfolio board server (windowless background).

Usage:
  python scripts/server.py start   # start uvicorn on :7331, write pid
  python scripts/server.py stop    # kill by pid
  python scripts/server.py status  # is it up?

Logs: .laos/server.log
"""

from __future__ import annotations

import pathlib
import subprocess
import sys
import time
import urllib.request

LAOS_ROOT = pathlib.Path(r"F:\projects\laos-v2")
LOG = LAOS_ROOT / ".laos" / "server.log"
PIDFILE = LAOS_ROOT / ".laos" / "server.pid"
PORT = 7331
CREATE_NO_WINDOW = 0x08000000


def _log(msg: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")


def _probe() -> bool:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/healthz", timeout=3):
            return True
    except Exception:  # noqa: BLE001
        return False


def start() -> int:
    if _probe():
        _log("already running")
        print("SERVER_ALREADY_UP")
        return 0
    logf = LOG.open("a", encoding="utf-8")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "laos.web.app:app",
         "--host", "127.0.0.1", "--port", str(PORT)],
        cwd=str(LAOS_ROOT),
        creationflags=CREATE_NO_WINDOW | 0x00000008,
        stdout=logf, stderr=logf,
    )
    PIDFILE.write_text(str(proc.pid), encoding="utf-8")
    _log(f"started pid={proc.pid}")
    for _ in range(20):
        if _probe():
            _log("healthy")
            print(f"SERVER_UP pid={proc.pid} http://127.0.0.1:{PORT}")
            return 0
        time.sleep(0.5)
    _log("started but not healthy yet")
    print(f"SERVER_STARTING pid={proc.pid}")
    return 0


def stop() -> int:
    if not PIDFILE.exists():
        print("SERVER_NOT_RUNNING")
        return 0
    pid = int(PIDFILE.read_text(encoding="utf-8").strip())
    try:
        import os

        os.kill(pid, 9)
    except Exception as e:  # noqa: BLE001
        _log(f"kill failed: {e}")
    PIDFILE.unlink(missing_ok=True)
    _log("stopped")
    print("SERVER_STOPPED")
    return 0


def status() -> int:
    up = _probe()
    print("SERVER_UP" if up else "SERVER_DOWN")
    if up:
        print(f"URL: http://127.0.0.1:{PORT}")
    return 0 if up else 1


def main(argv: list[str]) -> int:
    cmd = argv[0] if argv else "status"
    handlers = {"start": start, "stop": stop, "status": status}
    h = handlers.get(cmd)
    if not h:
        print(f"unknown: {cmd}")
        return 2
    return h()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
