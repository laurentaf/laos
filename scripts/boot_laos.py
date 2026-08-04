#!/usr/bin/env python3
"""Start LAOS canonical: observability check + panel. Writes .laos/boot.log"""

from __future__ import annotations

import pathlib
import subprocess
import sys
import time
import urllib.request

LAOS = pathlib.Path(r"F:\projects\laos-v2")
LOG = LAOS / ".laos" / "boot.log"
CREATE_NO_WINDOW = 0x08000000


def probe(url: str, timeout: float = 4) -> str:
    try:
        with urllib.request.urlopen(url, timeout=timeout):
            return "UP"
    except Exception as e:  # noqa: BLE001
        return f"DOWN({type(e).__name__})"


def start_panel() -> str:
    """Start uvicorn on :7331 detached; return pid."""
    logf = open(LAOS / ".laos" / "server.log", "a", encoding="utf-8")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "laos.web.app:app",
         "--host", "127.0.0.1", "--port", "7331"],
        cwd=str(LAOS), creationflags=CREATE_NO_WINDOW | 0x00000008,
        stdout=logf, stderr=logf,
    )
    return str(proc.pid)


def main() -> int:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append(f"Langfuse :3000 -> {probe('http://localhost:3000/api/public/health')}")
    lines.append(f"LiteLLM  :4000 -> {probe('http://localhost:4000/health/liveliness')}")
    panel_up = probe("http://127.0.0.1:7331/healthz") == "UP"
    if not panel_up:
        pid = start_panel()
        time.sleep(4)
        panel_up = probe("http://127.0.0.1:7331/healthz") == "UP"
        lines.append(f"painel :7331 -> startado (pid {pid}) -> {probe('http://127.0.0.1:7331/healthz')}")
    else:
        lines.append("painel :7331 -> UP (já rodando)")
    with LOG.open("a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(" | ".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
