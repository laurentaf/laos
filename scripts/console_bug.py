#!/usr/bin/env python3
"""Test console send route via TestClient. Writes .laos/console-bug.log"""

from __future__ import annotations

import pathlib

LOG = pathlib.Path(r"F:\projects\laos-v2\.laos\console-bug.log")


def main() -> int:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    from fastapi.testclient import TestClient
    from laos.web.app import app
    from laos.db import schema as schema_mod
    import duckdb

    # isolate DB in memory
    con = duckdb.connect(":memory:")
    schema_mod.apply_schema(con)
    schema_mod.connect = lambda: con

    client = TestClient(app)
    # need a project to exist (console requires portfolio.project_detail)
    import pathlib as pl
    from laos.web import portfolio

    root = pl.Path(r"F:\projects\laos-v2")
    # ensure project.yaml exists (it does in the real repo)

    r1 = client.get("/projects/limpeza-casa/console")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"GET console: {r1.status_code}\n")
    # monkeypatch chat to avoid LLM call
    from laos.chat import console as chat_mod

    chat_mod.chat = lambda pid, msg: "REPLY_OK"

    r2 = client.post(
        "/projects/limpeza-casa/console/send",
        data={"message": "teste"},
    )
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"POST send: {r2.status_code}\n")
        f.write(f"body: {r2.text[:300]}\n")
    print(f"GET={r1.status_code} POST={r2.status_code}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
