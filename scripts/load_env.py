"""LAOS environment loader.

Reads .env.local first (machine-specific paths), then .env.shared
(shared API keys). Shared keys override local if same key name.

Usage:
    from scripts.load_env import load_env
    load_env()

Or:
    uv run python -m scripts.load_env  # prints current env state
"""
import os
from pathlib import Path
from typing import Optional

_LAOS_ROOT: Optional[Path] = None

def laos_root() -> Path:
    global _LAOS_ROOT
    if _LAOS_ROOT is None:
        # This file is at <root>/scripts/load_env.py
        _LAOS_ROOT = Path(__file__).resolve().parents[1]
    return _LAOS_ROOT

def load_env() -> None:
    """Load .env.local then .env.shared into os.environ (setdefault).

    Priority (lowest to highest):
        1. OS environment vars (never overridden)
        2. .env.local (machine-specific paths)
        3. .env.shared (shared API keys)
    """
    root = laos_root()
    for fname in (".env.local", ".env.shared"):
        path = root / fname
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k, v = k.strip(), v.strip().strip('"').strip("'")
            # setdefault: OS env var wins, .env overrides if not set
            os.environ.setdefault(k, v)

def dump() -> dict[str, str]:
    """Return all LAOS-related env vars currently set."""
    load_env()
    keys = {
        "LATADE_DB_PATH", "LACOUNCIL_DB_PATH",
        "N8N_API_URL", "N8N_API_KEY",
        "CONTEXT7_API_KEY", "GITHUB_TOKEN",
        "LAOS_WORKSPACE",
    }
    return {k: v for k, v in os.environ.items() if k in keys and v}

if __name__ == "__main__":
    load_env()
    print("=== LAOS env ===")
    for k, v in sorted(dump().items()):
        if "KEY" in k and v:
            v = f"{v[:4]}...{v[-4:]}"
        print(f"  {k}={v or '(empty)'}")
    print(f"  root={laos_root()}")
