#!/usr/bin/env python3
"""Preflight check for LAOS delivery-reviewer (Stage 0).

Captures 5 categories of mechanical defects that LLM review alone misses:

  1. YAML parse + arithmetic
     - project.yaml must parse
     - conditions_total == sum(condicoes_vinculantes.*)
     - for each *_total / *_count field, the value must match actual count

  2. Deliverable path existence
     - for each entry in `deliverables`, the path must exist relative to
       the project root

  3. Secret scan
     - regex scan of all versioned files (.yaml, .md, .json, .py, .toml)
       for common credential patterns (AKIA, sk_live_, ghp_, api_key=,
       password=, token=). Flags potential leaks.

  4. Cross-reference integrity
     - for each "Art. N" mention in any markdown/yaml under project/,
       verify the Constitution actually has Art. N
     - for each "DA-N" / "DD-N" / "AE-N" / "DR-N" mention, verify the
       condition is catalogued somewhere

  5. Implementation code in LAOS
     - per padroes-entrega.md P0: no .sql / .dax / .pbix / .py / .js / .ts
       under projects/. Only specs/markdown/yaml allowed.

Exit code:
  0  — all checks pass
  1  — one or more BLOCKED findings (orchestrator MUST fix before
       dispatching delivery-reviewer)
  2  — usage error (bad args)

Usage:
  uv run python scripts/preflight_check.py <project_path>

References:
  - Constitution laecon Art. 10 (Detalhamento Metodológico Extremo)
  - LAOS knowledge/padroes-entrega.md P0 items
  - Fagan 1976 IBM Systems Journal 15(3):182-211 (planning stage)
  - IEEE 1028-2008 §6.4 (entry criteria)

Last updated: 2026-06-04 (DA-6 reform of delivery-reviewer).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable

import yaml


# ─── check functions ────────────────────────────────────────────────────────


def check_yaml_arithmetic(project: Path) -> list[str]:
    """Check 1: project.yaml parses and *_total fields match actual counts."""
    errors: list[str] = []
    py = project / "project.yaml"
    if not py.exists():
        return [f"YAML_MISSING: {py}"]

    try:
        data = yaml.safe_load(py.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        return [f"YAML_INVALID: {py} ({e.__class__.__name__}: {e})"]

    if not isinstance(data, dict):
        return [f"YAML_STRUCTURE: {py} (root must be a mapping)"]

    # arithmetic: conditions_total == sum(condicoes_vinculantes.*)
    cap = data.get("capability_status") or {}
    if "conditions_total" in cap:
        cond = data.get("condicoes_vinculantes") or {}
        if not isinstance(cond, dict):
            errors.append(
                f"ARITHMETIC: condicoes_vinculantes must be a mapping, got {type(cond).__name__}"
            )
        else:
            listed = sum(
                len(v) for v in cond.values() if isinstance(v, (list, dict))
            )
            declared = cap["conditions_total"]
            if isinstance(declared, int) and listed != declared:
                errors.append(
                    f"ARITHMETIC_OFF_BY_N: {py.name}: conditions_total={declared} "
                    f"!= sum(condicoes_vinculantes.*)={listed} "
                    f"(off-by-{abs(declared - listed)})"
                )

    # arithmetic: blocking_stable == total (if both present)
    if (
        "conditions_total" in cap
        and "conditions_blocking_stable" in cap
        and cap["conditions_total"] != cap["conditions_blocking_stable"]
    ):
        errors.append(
            f"ARITHMETIC: conditions_total={cap['conditions_total']} != "
            f"conditions_blocking_stable={cap['conditions_blocking_stable']}"
        )

    return errors


def check_deliverable_paths(project: Path) -> list[str]:
    """Check 2: every deliverable path must exist."""
    errors: list[str] = []
    py = project / "project.yaml"
    if not py.exists():
        return errors  # already reported by check_yaml_arithmetic

    try:
        data = yaml.safe_load(py.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return errors  # already reported

    if not isinstance(data, dict):
        return errors

    # deliverables is a list of mappings with `path:` keys
    for d in data.get("deliverables", []) or []:
        if not isinstance(d, dict):
            continue
        path = d.get("path")
        if not path:
            continue
        # resolve relative to LAOS root (parent of projects/_meta/...)
        resolved = _resolve(project, path)
        if not resolved.exists():
            errors.append(f"PATH_MISSING: deliverable {path} -> {resolved}")

    return errors


def check_secrets(project: Path) -> list[str]:
    """Check 3: scan for credential leaks in versioned files."""
    errors: list[str] = []
    # Only scan text-ish files; skip binary
    exts = {".yaml", ".yml", ".md", ".json", ".py", ".toml", ".txt", ".cfg"}
    # Patterns: AWS key, Stripe live, GitHub PAT, generic API key/password/token
    patterns = [
        (r"AKIA[0-9A-Z]{16}", "AWS access key"),
        (r"sk_live_[A-Za-z0-9]{24,}", "Stripe live key"),
        (r"ghp_[A-Za-z0-9]{36}", "GitHub personal access token"),
        (r"gho_[A-Za-z0-9]{36}", "GitHub OAuth token"),
        (r"github_pat_[A-Za-z0-9_]{82}", "GitHub fine-grained PAT"),
        (r"xox[abprs]-[A-Za-z0-9-]{10,}", "Slack token"),
        (r"AIza[0-9A-Za-z_-]{35}", "Google API key"),
        (
            r'(?i)(api_key|apikey|api-key|secret_key|password|token)\s*[:=]\s*["\'][^"\']{12,}["\']',
            "Generic credential in code/config",
        ),
    ]

    for f in project.rglob("*"):
        if not f.is_file() or f.suffix.lower() not in exts:
            continue
        # skip .venv and node_modules
        if any(part in f.parts for part in (".venv", "node_modules", "__pycache__")):
            continue
        try:
            txt = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pat, label in patterns:
            for m in re.finditer(pat, txt):
                # Allow template placeholders like {{API_TOKEN}} or ${API_KEY}
                # (find the surrounding 40 chars)
                start = max(0, m.start() - 20)
                end = min(len(txt), m.end() + 20)
                ctx = txt[start:end].replace("\n", " ")
                if "{{" in ctx or "${" in ctx:
                    continue  # env-var template, not a real secret
                errors.append(
                    f"POSSIBLE_SECRET: {f}:{txt[:m.start()].count(chr(10))+1} "
                    f"matched {label}"
                )
                break  # one finding per file is enough

    return errors


def check_cross_references(project: Path) -> list[str]:
    """Check 4: Constitution article and condition ID mentions must resolve.

    Catalogs considered as ground truth:
      - Any CONSTITUTION.md under the project (for `Art. N` references)
      - Any project.yaml containing `condicoes_vinculantes:` (for DA/DD/AE/DR-N)
      - Any *.md under capability-evolution/ or <capability>-capability/ dirs
        (typically tracking or evolution files)
    """
    errors: list[str] = []
    article_re = re.compile(r"^##\s+Artigo\s+(\d+)\b", re.MULTILINE)
    condition_re = re.compile(r"\b(DA|DD|AE|DR)-(\d+)\b")

    # Build the set of catalog files
    catalog_files: list[Path] = []
    catalog_files.extend(project.rglob("CONSTITUTION.md"))
    for name in ("capability-evolution", "laecon-capability"):
        sub = project / name
        if sub.exists():
            catalog_files.extend(sub.rglob("*.md"))
    for f in project.rglob("*.yaml"):
        try:
            txt = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if "condicoes_vinculantes" in txt:
            catalog_files.append(f)

    # Extract ground-truth sets
    existing_articles: set[int] = set()
    existing_conditions: set[tuple[str, int]] = set()
    for f in catalog_files:
        try:
            txt = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for m in article_re.finditer(txt):
            existing_articles.add(int(m.group(1)))
        for m in condition_re.finditer(txt):
            existing_conditions.add((m.group(1), int(m.group(2))))

    # If we have no catalog at all, we have nothing to cross-ref against.
    if not catalog_files:
        return errors

    # Walk all docs and flag dangling references
    doc_exts = {".md", ".yaml", ".yml", ".txt"}
    for f in project.rglob("*"):
        if not f.is_file() or f.suffix.lower() not in doc_exts:
            continue
        if any(part in f.parts for part in (".venv", "node_modules")):
            continue
        # Skip catalog files themselves (they're the source of truth)
        if f in catalog_files:
            continue
        try:
            txt = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        # Dangling Art. N (only if we have a Constitution catalog)
        if existing_articles:
            for m in re.finditer(r"\bArt\.\s*(\d+)\b", txt):
                n = int(m.group(1))
                if n not in existing_articles:
                    ln = txt[: m.start()].count("\n") + 1
                    errors.append(
                        f"DANGLING_REF: {f}:{ln} references Art. {n} but no "
                        f"Constitution has it (existing: {sorted(existing_articles)})"
                    )

        # Dangling DA-/DD-/AE-/DR-N (only if we have a condition catalog)
        if existing_conditions:
            for m in condition_re.finditer(txt):
                key = (m.group(1), int(m.group(2)))
                if key not in existing_conditions:
                    ln = txt[: m.start()].count("\n") + 1
                    errors.append(
                        f"DANGLING_CONDITION: {f}:{ln} references "
                        f"{key[0]}-{key[1]} but no catalog has it"
                    )

    return errors


def check_no_impl_code(project: Path) -> list[str]:
    """Check 5: no implementation code under projects/.

    Per padroes-entrega.md P0: only specs, contracts, ADRs, knowledge,
    tracking markdown/yaml allowed under projects/. No .sql / .dax /
    .pbix / .py / .js / .ts.
    """
    errors: list[str] = []
    forbidden = {".sql", ".dax", ".pbix", ".py", ".js", ".ts", ".ipynb"}
    # Allowed at the project root (test fixtures, scripts that ARE the
    # project itself). For laecon meta-project, NO code under
    # projects/_meta/. For domain projects, code is in the child repo.
    offenders: list[Path] = []
    for f in project.rglob("*"):
        if not f.is_file() or f.suffix.lower() not in forbidden:
            continue
        if any(part in f.parts for part in (".venv", "node_modules")):
            continue
        offenders.append(f)

    for f in offenders:
        errors.append(f"IMPL_CODE_IN_LAOS: {f} (projects/ holds specs only)")

    return errors


# ─── helpers ────────────────────────────────────────────────────────────────


def _resolve(project: Path, raw_path: str) -> Path:
    """Resolve a deliverable path.

    Convention: paths in project.yaml are relative to LAOS root (the
    directory containing the `projects/` subdir), NOT the project dir.
    So `../laecon/foo` is resolved from LAOS root.
    """
    laos_root = _find_laos_root(project)
    return (laos_root / raw_path).resolve()


def _find_laos_root(start: Path) -> Path:
    """Walk up from `start` until we find the LAOS root (AGENTS.md)."""
    p = start.resolve()
    for ancestor in [p, *p.parents]:
        if (ancestor / "AGENTS.md").exists() and (ancestor / "projects").is_dir():
            return ancestor
    return start.resolve()  # fallback: caller is responsible


# ─── entry point ────────────────────────────────────────────────────────────


def run_all(project: Path) -> tuple[int, list[str]]:
    """Run all checks. Returns (exit_code, list_of_findings)."""
    if not project.exists() or not project.is_dir():
        return 2, [f"USAGE: {project} is not a directory"]

    findings: list[str] = []
    findings += check_yaml_arithmetic(project)
    findings += check_deliverable_paths(project)
    findings += check_secrets(project)
    findings += check_cross_references(project)
    findings += check_no_impl_code(project)

    return (0 if not findings else 1), findings


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="LAOS delivery-reviewer preflight (Stage 0).",
    )
    parser.add_argument(
        "project_path",
        type=Path,
        help="Path to the project directory (e.g. projects/_meta/laecon-capability)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-check headers (useful for CI logs)",
    )
    args = parser.parse_args(argv)

    code, findings = run_all(args.project_path)

    if not args.quiet:
        print(f"Preflight: {args.project_path}")
        print("-" * 60)

    if not findings:
        print("PREFLIGHT_PASS: 0 findings, 5 checks completed.")
        return 0

    for f in findings:
        print(f"BLOCKED: {f}")
    print("-" * 60)
    print(f"PREFLIGHT_BLOCKED: {len(findings)} finding(s). Fix before dispatching delivery-reviewer.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
