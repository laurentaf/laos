#!/usr/bin/env python3
"""Investigate limpeza-v2: exists? cost? Writes .laos/investigate-v2.log"""

from __future__ import annotations

import pathlib

LAOS = pathlib.Path(r"F:\projects\laos-v2")
LOG = LAOS / ".laos" / "investigate-v2.log"


def main() -> int:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    proj = LAOS / "projects" / "limpeza-v2"
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"projects dir exists: {proj.exists()}\n")
        py = proj / "project.yaml"
        f.write(f"project.yaml exists: {py.exists()}\n")
        if py.exists():
            f.write("--- project.yaml ---\n" + py.read_text(encoding="utf-8") + "\n")
        if proj.exists():
            f.write("--- files ---\n")
            for p in proj.rglob("*"):
                f.write(f"  {p.relative_to(LAOS)} ({p.stat().st_size}B)\n")

        # DB state
        import duckdb

        try:
            con = duckdb.connect(str(LAOS / ".laos" / "laos.duckdb"), read_only=True)
            runs = con.execute(
                "SELECT run_id, status, cost_usd, tokens, started_at FROM runs "
                "WHERE project_id='limpeza-v2'").fetchall()
            f.write(f"--- runs limpeza-v2 ({len(runs)}) ---\n")
            for r in runs:
                f.write(f"  {r}\n")
            phases = con.execute(
                "SELECT phase, name, status, cost_usd, tokens FROM phases "
                "WHERE project_id='limpeza-v2'").fetchall()
            f.write(f"--- phases limpeza-v2 ({len(phases)}) ---\n")
            for p in phases:
                f.write(f"  {p}\n")
            projrow = con.execute(
                "SELECT status, ready_to_ship FROM projects WHERE project_id='limpeza-v2'"
            ).fetchall()
            f.write(f"--- projects row ---\n  {projrow}\n")
            con.close()
        except Exception as e:  # noqa: BLE001
            f.write(f"DB ERR: {type(e).__name__}: {e}\n")
    print("DONE (see .laos/investigate-v2.log)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
