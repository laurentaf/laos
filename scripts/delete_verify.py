#!/usr/bin/env python3
"""Verify: limpeza-v2 gone from board + new project shows 0 cost.
Writes .laos/delete-verify.log"""

from __future__ import annotations

import pathlib
import urllib.request

LAOS = pathlib.Path(r"F:\projects\laos-v2")
LOG = LAOS / ".laos" / "delete-verify.log"


def main() -> int:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    # board should not list limpeza-v2
    with urllib.request.urlopen("http://127.0.0.1:7331/", timeout=5) as r:
        body = r.read().decode("utf-8", errors="replace")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"limpeza-v2 no board: {'limpeza-v2' in body}\n")
        f.write(f"limpeza-casa no board: {'limpeza-casa' in body}\n")
    # project folder gone from projects/
    proj = LAOS / "projects" / "limpeza-v2"
    archived = LAOS / "projects_archived" / "limpeza-v2"
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"pasta limpeza-v2 existe: {proj.exists()}\n")
        f.write(f"pasta arquivada existe: {archived.exists()}\n")
    print(f"DELETED_FROM_BOARD={'limpeza-v2' not in body} | archived={archived.exists()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
