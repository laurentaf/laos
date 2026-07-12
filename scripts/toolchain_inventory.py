#!/usr/bin/env python3
"""
toolchain_inventory.py — Inventaria runtimes, gerenciadores de pacote,
containers e tools disponíveis no workspace.

Executado pelo orchestrator no início de cada ciclo de projeto (antes
de needs resolution). O output alimenta as decisões de stack durante
o planning (Fase 1 de knowledge/discover-before-build.md).

Exit 0 = inventário completo; exit 1 = erro fatal.
Saída: JSON no stdout + (opcional) arquivo em artifacts/toolchain.json.

Uso:
  uv run python scripts/toolchain_inventory.py
  uv run python scripts/toolchain_inventory.py --project-name foo
  uv run python scripts/toolchain_inventory.py --output artifacts/toolchain.json
"""

import argparse
import json
import os
import shutil
import subprocess  # kept for exception types (TimeoutExpired, FileNotFoundError)
import sys
from pathlib import Path

# Importa run_hidden.run() que usa CREATE_NO_WINDOW (0x08000000) no Windows
# para que NENHUM binário de console crie janela visível.
from run_hidden import run as _hidden_run


def check_command(cmd: str) -> dict:
    """Check if a command is available and return its version."""
    path = shutil.which(cmd)
    if not path:
        return {"available": False, "path": None, "version": None}

    version = None
    for flag in ["--version", "-v", "-version", "version"]:
        try:
            r = _hidden_run(
                [cmd, flag],
                capture_output=True, text=True, timeout=10
            )
            output = (r.stdout + r.stderr).strip()
            if output and len(output) < 500:
                version = output.split("\n")[0][:200]
                break
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            continue

    return {"available": True, "path": path, "version": version}


def check_docker_containers() -> list:
    """List running Docker containers."""
    try:
        r = _hidden_run(
            ["docker", "ps", "--format", "{{.Names}}\t{{.Image}}\t{{.Status}}"],
            capture_output=True, text=True, timeout=10
        )
        if r.returncode != 0:
            return []
        containers = []
        for line in r.stdout.strip().split("\n"):
            if line:
                parts = line.split("\t")
                containers.append({
                    "name": parts[0] if len(parts) > 0 else "?",
                    "image": parts[1] if len(parts) > 1 else "?",
                    "status": parts[2] if len(parts) > 2 else "?",
                })
        return containers
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return []


def check_docker_images() -> list:
    """List local Docker images (top 20)."""
    try:
        r = _hidden_run(
            ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}\t{{.Size}}"],
            capture_output=True, text=True, timeout=10
        )
        if r.returncode != 0:
            return []
        images = []
        for line in r.stdout.strip().split("\n")[:20]:
            if line:
                parts = line.split("\t")
                images.append({
                    "image": parts[0] if len(parts) > 0 else "?",
                    "size": parts[1] if len(parts) > 1 else "?",
                })
        return images
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return []


def find_venvs(workspace: str = "E:/projects") -> list:
    """Find existing .venv directories in the workspace."""
    venvs = []
    workspace_path = Path(workspace)
    if not workspace_path.exists():
        return venvs

    for project_dir in workspace_path.iterdir():
        if not project_dir.is_dir() or project_dir.name.startswith("."):
            continue
        venv_dir = project_dir / ".venv"
        if venv_dir.exists():
            # Check if it has a python executable
            python_candidates = [
                venv_dir / "Scripts" / "python.exe",  # Windows
                venv_dir / "bin" / "python",           # Unix
            ]
            python_path = None
            for p in python_candidates:
                if p.exists():
                    python_path = str(p)
                    break

            # Check if pyproject.toml exists
            has_pyproject = (project_dir / "pyproject.toml").exists()

            venvs.append({
                "project": project_dir.name,
                "path": str(venv_dir),
                "python": python_path,
                "has_pyproject": has_pyproject,
            })

    return venvs


def find_project_configs(workspace: str = "E:/projects") -> list:
    """Find pyproject.toml and package.json in workspace projects."""
    configs = []
    workspace_path = Path(workspace)
    if not workspace_path.exists():
        return configs

    for project_dir in workspace_path.iterdir():
        if not project_dir.is_dir() or project_dir.name.startswith("."):
            continue

        pyproject = project_dir / "pyproject.toml"
        package_json = project_dir / "package.json"
        docker_compose = project_dir / "docker-compose.yaml"
        docker_compose_yml = project_dir / "docker-compose.yml"

        entry = {"project": project_dir.name}
        if pyproject.exists():
            entry["pyproject"] = str(pyproject)
        if package_json.exists():
            entry["package_json"] = str(package_json)
        if docker_compose.exists() or docker_compose_yml.exists():
            entry["docker_compose"] = str(
                docker_compose if docker_compose.exists() else docker_compose_yml
            )

        if len(entry) > 1:  # has at least one config
            configs.append(entry)

    return configs


def main():
    parser = argparse.ArgumentParser(description="Toolchain inventory")
    parser.add_argument("--project-name", help="Project name for context")
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument("--workspace", default="E:/projects", help="Workspace root")
    args = parser.parse_args()

    # Runtimes
    runtimes = {}
    runtime_cmds = {
        "python": "python",
        "python3": "python3",
        "uv": "uv",
        "node": "node",
        "npm": "npm",
        "npx": "npx",
        "pnpm": "pnpm",
        "java": "java",
        "go": "go",
        "rustc": "rustc",
        "cargo": "cargo",
        "gcc": "gcc",
        "g++": "g++",
        "dotnet": "dotnet",
    }
    for name, cmd in runtime_cmds.items():
        result = check_command(cmd)
        if result["available"]:
            runtimes[name] = result

    # Package managers
    package_managers = {}
    pm_cmds = {
        "uv": "uv",
        "pip": "pip",
        "npm": "npm",
        "pnpm": "pnpm",
        "cargo": "cargo",
        "winget": "winget",
    }
    for name, cmd in pm_cmds.items():
        result = check_command(cmd)
        if result["available"]:
            package_managers[name] = result

    # Docker
    docker_available = shutil.which("docker") is not None
    docker_containers = check_docker_containers() if docker_available else []
    docker_images = check_docker_images() if docker_available else []

    # Workspace scan
    venvs = find_venvs(args.workspace)
    project_configs = find_project_configs(args.workspace)

    inventory = {
        "workspace": args.workspace,
        "project": args.project_name,
        "runtimes": runtimes,
        "package_managers": package_managers,
        "docker": {
            "available": docker_available,
            "running_containers": docker_containers,
            "local_images": docker_images,
        },
        "workspace_venvs": venvs,
        "workspace_configs": project_configs,
        "summary": {
            "primary_language": None,
            "primary_package_manager": None,
            "has_docker": docker_available,
            "active_containers": len(docker_containers),
            "projects_with_venvs": len(venvs),
        },
    }

    # Determine primary language (first available in preference order)
    lang_preference = ["python", "node", "java", "go", "rustc", "gcc"]
    for lang in lang_preference:
        if lang in runtimes:
            inventory["summary"]["primary_language"] = lang
            break

    # Determine primary package manager
    pm_preference = ["uv", "pip", "npm", "pnpm", "cargo"]
    for pm in pm_preference:
        if pm in package_managers:
            inventory["summary"]["primary_package_manager"] = pm
            break

    # Output
    output_json = json.dumps(inventory, indent=2, ensure_ascii=False)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output_json, encoding="utf-8")
        print(f"Inventory written to {args.output}", file=sys.stderr)

    print(output_json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
