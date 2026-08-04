#!/usr/bin/env python3
"""Probe: does deepseek-v4-flash with max_tokens 8000 return JSON in content?
Writes .laos/json-probe.log"""

from __future__ import annotations

import json
import pathlib
import urllib.request

LOG = pathlib.Path(r"F:\projects\laos-v2\.laos\json-probe.log")


def main() -> int:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "model": "glm-5.2",
        "messages": [
            {"role": "system", "content": "Responda exatamente com JSON válido: {\"a\": 1}"},
            {"role": "user", "content": "gere o json"},
        ],
        "max_tokens": 8000,
    }
    req = urllib.request.Request(
        "http://localhost:4000/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer sk-laos-master"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        d = json.loads(resp.read())
        msg = d["choices"][0]["message"]
        content = msg.get("content", "")
        reasoning = msg.get("reasoning_content", "")
        usage = d.get("usage", {})
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"content={len(content)}B: {content[:200]!r}\n")
        f.write(f"reasoning={len(reasoning)}B: {reasoning[:200]!r}\n")
        f.write(f"usage={usage}\n")
    print(f"content={len(content)}B reasoning={len(reasoning)}B")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
