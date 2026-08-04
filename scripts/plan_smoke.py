#!/usr/bin/env python3
"""Smoke test: laos plan on a real-ish new project. Writes .laos/plan-smoke.log"""

from __future__ import annotations

import pathlib
import sys

LAOS = pathlib.Path(r"F:\projects\laos-v2")
LOG = LAOS / ".laos" / "plan-smoke.log"


def main() -> int:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    from laos.plan import planner

    # create a throwaway project in the real repo (registry lives there)
    proj = LAOS / "projects" / "_smoke-plan"
    proj.mkdir(parents=True, exist_ok=True)
    (proj / "project.yaml").write_text(
        "project_name: _smoke-plan\n"
        "brief: app de controle de despesas pessoais com dashboard e alertas\n"
        "needs: [design]\n"
        "deliverables: []\n",
        encoding="utf-8",
    )
    try:
        result = planner.plan_project("_smoke-plan")
        with LOG.open("a", encoding="utf-8") as f:
            f.write(f"status={result['status']}\n")
            f.write(f"gaps={result['gaps_found']}\n")
            f.write(f"phases={result['phases_proposed']}\n")
            for d in result["contract"].get("deliverables", []) or []:
                f.write(f"  fase {d.get('stage')} {d.get('name')} | {d.get('spec','')[:80]}\n")
        print(f"PLAN_OK status={result['status']} phases={result['phases_proposed']}")
        return 0
    except Exception as e:  # noqa: BLE001
        with LOG.open("a", encoding="utf-8") as f:
            f.write(f"ERR {type(e).__name__}: {e}\n")
        print(f"PLAN_ERR {type(e).__name__}: {e}")
        return 1
    finally:
        import shutil

        shutil.rmtree(proj, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
