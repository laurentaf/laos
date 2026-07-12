"""
pre-commit hook — LAOS delivery validation.

Instalado em .git/hooks/pre-commit por scripts/setup-hooks.ps1.
100% HIDDEN: executa via pythonw.exe (WINDOWS subsystem, zero console).
"""
import os
import sys
from pathlib import Path


def find_project_yaml(start: Path) -> Path | None:
    for parent in [start, *start.parents]:
        candidate = parent / "project.yaml"
        if candidate.exists():
            return candidate
        if parent.parent == parent:
            break
    return None


def main() -> int:
    # Hook file is at: .git/hooks/pre-commit
    # Repo root is: .git/hooks/../../../
    hook_dir = Path(__file__).resolve().parent          # .git/hooks/
    repo_root = hook_dir.parents[2]                     # LAOS root (3 levels up)
    scripts_dir = repo_root / "scripts"
    runner = scripts_dir / "run-hidden.py"
    script = scripts_dir / "delivery-hook.py"

    if not script.exists() or not runner.exists():
        return 0

    project_yaml = find_project_yaml(Path.cwd())
    if not project_yaml:
        return 0

    # Use run_hidden.run() para que subprocessos usem CREATE_NO_WINDOW
    sys.path.insert(0, str(scripts_dir))
    from run_hidden import run

    result = run(
        [sys.executable, str(script), "--check", str(project_yaml)],
        capture_output=True, text=True
    )
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
