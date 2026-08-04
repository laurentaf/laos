#!/usr/bin/env python3
"""Rename GitHub repos: laos -> laos-legacy, laos-v2 -> laos.

Uses the GitHub REST API (PATCH /repos/{owner}/{repo}).
Token: GITHUB_TOKEN env, or github entry in opencode auth.json.

Writes .laos/rename.log
"""

from __future__ import annotations

import json
import os
import pathlib
import urllib.error
import urllib.request

LOG = pathlib.Path(r"F:\projects\laos-v2\.laos\rename.log")


def _token() -> str | None:
    t = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if t:
        return t
    # try opencode auth.json
    auth = pathlib.Path.home() / ".local/share/opencode/auth.json"
    try:
        data = json.loads(auth.read_text(encoding="utf-8"))
        gh = data.get("github", {})
        return gh.get("key") or gh.get("token")
    except Exception:  # noqa: BLE001
        return None


def rename_repo(owner: str, repo: str, new_name: str) -> str:
    token = _token()
    if not token:
        return "NO_TOKEN"
    req = urllib.request.Request(
        f"https://api.github.com/repos/{owner}/{repo}",
        data=json.dumps({"name": new_name}).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
        },
        method="PATCH",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read())
            return f"OK -> {body.get('full_name')}"
    except urllib.error.HTTPError as e:
        return f"HTTP_{e.code}: {e.read().decode(errors='replace')[:300]}"


def main() -> int:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    steps = [
        ("laurentaf", "laos", "laos-legacy"),
        ("laurentaf", "laos-v2", "laos"),
    ]
    with LOG.open("a", encoding="utf-8") as f:
        for owner, repo, new in steps:
            r = rename_repo(owner, repo, new)
            f.write(f"rename {owner}/{repo} -> {new}: {r}\n")
            print(f"rename {owner}/{repo} -> {new}: {r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
