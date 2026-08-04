#!/usr/bin/env python3
"""Smoke test on LAOS canonical: doctor + real LLM call + project verify.
Writes .laos/smoke.log"""

from __future__ import annotations

import pathlib

LAOS = pathlib.Path(r"F:\projects\laos-v2")
LOG = LAOS / ".laos" / "smoke.log"


def main() -> int:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    from laos.cli import main as cli_main
    import contextlib
    import io

    results = []

    # 1. doctor
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = cli_main(["doctor"])
    results.append(f"[doctor] exit={code}")

    # 2. real LLM call via LiteLLM
    from laos.core import runners
    import yaml

    py = LAOS / "projects" / "limpeza-casa" / "project.yaml"
    data = yaml.safe_load(py.read_text(encoding="utf-8"))
    stage1 = next(d for d in data["deliverables"] if d["stage"] == 1)

    class _Ctx:
        project_id = "limpeza-casa"
        _root = LAOS

    r = runners.llm_artifact_runner(stage1, _Ctx())
    results.append(f"[llm_fase1] status={r.get('status')} cost=${r.get('cost_usd',0):.6f} "
                   f"tokens={r.get('tokens',0)} artifact={r.get('artifact')}")

    # 3. verify limpeza-casa
    from laos.verify import engine

    vres, vok = engine.verify_project(LAOS, "limpeza-casa")
    results.append(f"[verify] all_ok={vok} ({len(vres)} deliverables)")

    with LOG.open("a", encoding="utf-8") as f:
        f.write("\n".join(results) + "\n")
    print(" | ".join(results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
