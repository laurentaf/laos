#!/usr/bin/env python3
"""Verify limpeza-casa has plan ToDos. Writes .laos/planejar-verify.log"""

from __future__ import annotations

import pathlib

LAOS = pathlib.Path(r"F:\projects\laos-v2")
LOG = LAOS / ".laos" / "planejar-verify.log"


def main() -> int:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    import duckdb

    con = duckdb.connect(str(LAOS / ".laos" / "laos.duckdb"), read_only=True)
    rows = con.execute(
        "SELECT text, done, source FROM todos WHERE project_id='limpeza-casa'"
    ).fetchall()
    con.close()
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"todos limpeza-casa: {len(rows)}\n")
        for r in rows:
            f.write(f"  [{('x' if r[1] else ' ')}] {r[0][:80]} ({r[2]})\n")
    print(f"TODOS={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
