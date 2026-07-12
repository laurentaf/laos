#!/usr/bin/env python3
"""
run-hidden.py — Entry point CLI para execução 100% silenciosa no Windows.

Uso:
    pythonw scripts/run-hidden.py <comando> [args...]
    pythonw scripts/run-hidden.py uv sync
    pythonw scripts/run-hidden.py git status
    pythonw scripts/run-hidden.py uv run python scripts/preflight_check.py projects/foo

Internamente delega para run_hidden.run() que usa CREATE_NO_WINDOW (0x08000000)
para que NENHUM binário de console (uv, git, python.exe, docker) crie janela.
"""
import sys
from run_hidden import run

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Uso: {sys.argv[0]} <comando> [args...]", file=sys.stderr)
        sys.exit(1)
    sys.exit(run(sys.argv[1:]).returncode)
