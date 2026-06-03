"""Print the active capability registry in a compact table.

Usage:
    uv run python scripts/list_capabilities.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "registry" / "capabilities.yaml"
OPENCODE = ROOT / ".opencode" / "opencode.jsonc"


def _strip_jsonc_comments(text: str) -> str:
    # remove // line comments and /* block comments */; strings untouched
    out = []
    in_string = False
    in_line_comment = False
    in_block_comment = False
    i = 0
    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if in_line_comment:
            if ch == "\n":
                in_line_comment = False
                out.append(ch)
            i += 1
            continue
        if in_block_comment:
            if ch == "*" and nxt == "/":
                in_block_comment = False
                i += 2
                continue
            i += 1
            continue
        if in_string:
            out.append(ch)
            if ch == "\\" and nxt:
                out.append(nxt)
                i += 2
                continue
            if ch == '"':
                in_string = False
            i += 1
            continue
        if ch == "/" and nxt == "/":
            in_line_comment = True
            i += 2
            continue
        if ch == "/" and nxt == "*":
            in_block_comment = True
            i += 2
            continue
        if ch == '"':
            in_string = True
        out.append(ch)
        i += 1
    return "".join(out)


def _load_jsonc(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    return json.loads(_strip_jsonc_comments(text))


def main() -> int:
    caps_doc = yaml.safe_load(REGISTRY.read_text(encoding="utf-8")) or {}
    items = caps_doc.get("capabilities", [])

    print(f"{'ID':<14} {'KIND':<10} {'MCP':<14} {'STATUS':<10} OWNS")
    print("-" * 64)
    for c in items:
        print(
            f"{c.get('id', '?'):<14} "
            f"{c.get('kind', '?'):<10} "
            f"{c.get('mcp_server', '?'):<14} "
            f"{c.get('status', '?'):<10} "
            f"{', '.join(c.get('owns', []))}"
        )

    stubs = [c for c in items if c.get("status") == "stub"]
    if stubs:
        print()
        print("Stubs (promote by creating the real repo and pointing the MCP at it):")
        for s in stubs:
            print(f"  - {s['id']:<14} -> {s.get('promote_to', 'TBD')}")

    if OPENCODE.exists():
        try:
            cfg = _load_jsonc(OPENCODE)
            disabled = [
                name for name, mcp in cfg.get("mcp", {}).items()
                if isinstance(mcp, dict) and mcp.get("enabled") is False
            ]
            if disabled:
                print()
                print("Currently disabled in opencode.jsonc (subagents cannot call these yet):")
                for d in disabled:
                    print(f"  - {d}")
        except Exception as exc:
            print()
            print(f"[warn] could not parse opencode.jsonc to list disabled MCPs: {exc}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
