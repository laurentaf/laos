#!/usr/bin/env python3
"""Debug _langfuse_stats filtering. Writes .laos/lf-filter.log"""

from __future__ import annotations

import pathlib

LAOS = pathlib.Path(r"F:\projects\laos-v2")
LOG = LAOS / ".laos" / "lf-filter.log"


def main() -> int:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    from laos.web import portfolio

    fake_traces = [
        {"name": "litellm-acompletion", "totalCost": 0.5,
         "metadata": {"laos_project": "other-proj"}},
        {"name": "litellm-acompletion", "totalCost": 0.3,
         "metadata": {"laos_project": "mine"}},
        {"name": "litellm-acompletion", "totalCost": 9.9, "metadata": None},
    ]
    import json

    class _Resp:
        def read(self):
            return json.dumps({"data": fake_traces}).encode()

    def _fake_open(req, timeout=5):
        return _Resp()

    portfolio.urllib.request.urlopen = _fake_open
    stats = portfolio._langfuse_stats("mine")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"stats={stats}\n")
    print(f"stats={stats}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
