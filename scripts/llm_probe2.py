#!/usr/bin/env python3
"""Minimal LLM call probe — is content empty consistently? Writes .laos/llm-probe2.log"""

from __future__ import annotations

import json
import pathlib
import urllib.request

LOG = pathlib.Path(r"F:\projects\laos-v2\.laos\llm-probe2.log")


def main() -> int:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    for i, prompt in enumerate([
        "Reply with exactly: pong",
        'Responda exatamente com este JSON: {"a": 1}',
        "Qual é 2+2? Responda só o número.",
    ]):
        payload = {
            "model": "deepseek-v4-flash",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 100,
        }
        req = urllib.request.Request(
            "http://localhost:4000/v1/chat/completions",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json",
                     "Authorization": "Bearer sk-laos-master"},
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                d = json.loads(resp.read())
                content = d["choices"][0]["message"].get("content", "")
                reasoning = d["choices"][0]["message"].get("reasoning_content", "")
                usage = d.get("usage", {})
                with LOG.open("a", encoding="utf-8") as f:
                    f.write(f"[{i}] content={len(content)}B reasoning={len(reasoning)}B "
                            f"usage={usage}\n")
        except Exception as e:  # noqa: BLE001
            with LOG.open("a", encoding="utf-8") as f:
                f.write(f"[{i}] ERR {type(e).__name__}: {str(e)[:200]}\n")
    print("DONE (see .laos/llm-probe2.log)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
