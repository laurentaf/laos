#!/usr/bin/env python3
"""
delivery-hook.py — Pre-commit validation for LAOS projects

Runs delivery-reviewer against a project's project.yaml before git commit.
Blocks commit if validation fails.

Usage:
    python scripts/delivery-hook.py [--check <path>] [--verbose]

Exit codes:
    0 = PASS (validation successful)
    1 = FAIL (validation failed)
    2 = SKIP (no project.yaml found, or not a LAOS project)
"""

import sys
import argparse
from pathlib import Path


def find_project_yaml(start_path: Path = Path.cwd()) -> Path | None:
    """Walk up from start_path to find .laos-project or project.yaml."""
    # Try current directory
    for pattern in ["project.yaml", ".laos-project"]:
        p = start_path / pattern
        if p.exists():
            return p

    # Walk up
    current = start_path
    for _ in range(10):  # Max 10 levels up
        for pattern in ["project.yaml", ".laos-project"]:
            p = current / pattern
            if p.exists():
                return p
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def run_validation(project_path: Path, verbose: bool = False) -> bool:
    """
    Run delivery-reviewer validation.
    This invokes the delivery-reviewer subagent via task tool.
    For CLI-only operation, we do basic checks here.
    """
    import yaml

    try:
        with open(project_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Basic YAML validation
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            print(f"FAIL: {project_path} is not valid YAML: {e}")
            return False

        # Check required fields in project.yaml
        if project_path.name == "project.yaml":
            required = ["name", "needs", "deliverables", "repo"]
            missing = [f for f in required if f not in data]
            if missing:
                print(f"FAIL: project.yaml missing required fields: {missing}")
                return False

        # Check deliverables exist
        if "deliverables" in data:
            # Find repo root by looking for .git or known files
            repo_root = project_path.parent
            for _ in range(10):
                if (repo_root / ".git").exists() or (repo_root / "AGENTS.md").exists():
                    break
                parent = repo_root.parent
                if parent == repo_root:
                    break
                repo_root = parent

            # Paths are relative to repo root
            missing_deliverables = []

            for d in data["deliverables"]:
                if isinstance(d, dict):
                    deliverable_path = repo_root / d["path"]
                else:
                    deliverable_path = repo_root / d

                if not deliverable_path.exists():
                    missing_deliverables.append(str(deliverable_path))

            if missing_deliverables:
                print(f"FAIL: Missing deliverables:")
                for md in missing_deliverables:
                    print(f"  - {md}")
                return False

        print(f"PASS: {project_path} validated successfully")
        return True

    except Exception as e:
        print(f"FAIL: Unexpected error validating {project_path}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="LAOS delivery validation pre-commit hook"
    )
    parser.add_argument(
        "--check",
        type=str,
        default=None,
        help="Path to project.yaml to validate",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print verbose output",
    )
    args = parser.parse_args()

    # Find project.yaml
    if args.check:
        project_path = Path(args.check)
        if not project_path.exists():
            print(f"SKIP: {project_path} does not exist")
            sys.exit(2)
    else:
        project_path = find_project_yaml()
        if project_path is None:
            print("SKIP: No project.yaml or .laos-project found")
            sys.exit(2)

    if args.verbose:
        print(f"Validating: {project_path}")

    # Run validation
    if run_validation(project_path, verbose=args.verbose):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()