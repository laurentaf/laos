"""
post-merge hook — LAOS auto uv sync after git pull/merge.

Instalado em .git/hooks/post-merge por scripts/setup-hooks.ps1.
100% HIDDEN: executa via pythonw.exe (WINDOWS subsystem, zero console).
"""
import os
import sys
from pathlib import Path


def main() -> int:
    # Hook file is at: .git/hooks/post-merge
    # Repo root is: .git/hooks/../../../
    hook_dir = Path(__file__).resolve().parent          # .git/hooks/
    repo_root = hook_dir.parents[2]                     # LAOS root
    scripts_dir = repo_root / "scripts"
    sys.path.insert(0, str(scripts_dir))
    from run_hidden import run

    result = run(
        ["uv", "sync", "--quiet"],
        capture_output=True, text=True, timeout=60
    )
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
