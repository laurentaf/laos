#!/usr/bin/env python3
"""Find remaining 500s via TestClient. Writes .laos/err-find.log"""

from __future__ import annotations

import pathlib

LOG = pathlib.Path(r"F:\projects\laos-v2\.laos\err-find.log")


def main() -> int:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    from fastapi.testclient import TestClient
    from laos.web.app import app

    client = TestClient(app)
    paths = ["/dashboard", "/projects/limpeza-casa", "/projects/limpeza-casa/handoff",
             "/projects/limpeza-casa/console"]
    with LOG.open("a", encoding="utf-8") as f:
        for p in paths:
            try:
                r = client.get(p)
                f.write(f"{p}: {r.status_code}\n")
            except Exception as e:  # noqa: BLE001
                f.write(f"{p}: EXC {type(e).__name__}: {str(e)[:200]}\n")
    print("DONE (see .laos/err-find.log)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
