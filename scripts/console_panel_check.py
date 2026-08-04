#!/usr/bin/env python3
"""Verify console page renders todos panel. Writes .laos/console-panel.log"""

from __future__ import annotations

import pathlib
import urllib.request

LAOS = pathlib.Path(r"F:\projects\laos-v2")
LOG = LAOS / ".laos" / "console-panel.log"


def main() -> int:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(
            "http://127.0.0.1:7331/projects/limpeza-casa/console", timeout=6) as r:
        body = r.read().decode("utf-8", errors="replace")
    markers = [m for m in ["ToDos do projeto", "adicionar", "planejar fases",
                           "todos-panel", "action-select", "conversar"] if m in body]
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"HTTP 200 ({len(body)}B)\n")
        f.write(f"markers: {markers}\n")
    print(f"CONSOLE_PANEL_OK markers={markers}")
    return 0 if markers else 1


if __name__ == "__main__":
    raise SystemExit(main())
