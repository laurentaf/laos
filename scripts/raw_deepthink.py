#!/usr/bin/env python3
"""Capture raw deep_think LLM response. Writes .laos/raw-deepthink.log"""

from __future__ import annotations

import pathlib

LAOS = pathlib.Path(r"F:\projects\laos-v2")
LOG = LAOS / ".laos" / "raw-deepthink.log"


def main() -> int:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    from laos.plan import planner

    data = {
        "project_name": "_smoke-deep",
        "brief": "app de controle de despesas pessoais com dashboard e alertas",
        "needs": ["design"],
        "deliverables": [],
    }
    # monkeypatch _llm_json to log raw
    orig = planner._llm_json

    def _logged(system, prompt, max_tokens):
        content = orig(system, prompt, max_tokens)
        with LOG.open("a", encoding="utf-8") as f:
            f.write("=== RAW CONTENT ===\n" + content + "\n")
        return content

    planner._llm_json = _logged
    try:
        analysis = planner.deep_think(data)
        with LOG.open("a", encoding="utf-8") as f:
            f.write("=== PARSED ===\n" + str(analysis)[:2000] + "\n")
        print(f"RAW_OK keys={list(analysis.keys())}")
        return 0
    except Exception as e:  # noqa: BLE001
        with LOG.open("a", encoding="utf-8") as f:
            f.write(f"ERR {type(e).__name__}: {e}\n")
        print(f"RAW_ERR {type(e).__name__}: {e}")
        return 1
    finally:
        planner._llm_json = orig


if __name__ == "__main__":
    raise SystemExit(main())
