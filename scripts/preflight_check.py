#!/usr/bin/env python3
"""Preflight check for LAOS delivery-reviewer (Stage 0).

Captures 6 categories of mechanical defects that LLM review alone misses:

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

6. WDL preflight gate (proposals a4fe9faa + 7fd94c1a, supermaioria 4/4).

Adaptive scaling tiers (CodeGraph KB, 2026-06-12):
  Project complexity is classified into three tiers based on deliverable count.
  Higher tiers run more thorough sub-checks. Invariant: a larger tier
  never applies a LESS thorough check than a smaller tier.

  | Tier | Deliverables | Checks 4 (cross-ref) | Checks 6 (WDL) |
  |------|-------------|----------------------|-----------------|
  | M0   | < 5         | skip (advisory only)  | skip (advisory)|
  | M1   | 5–15        | full                 | standard        |
  | M2   | > 15        | full + ADR deep-check| full + bypass  |

  Reference: CodeGraph docs/design/agent-codegraph-adoption.md §P1
  "Adapt the tool to the agent" + adaptive-explore-sizing.md.
  Implemented in get_project_tier() and scaled_*() wrappers.

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
  - WDL v1 contract: workflows/wdl-contract.yaml (pinned wdl_version: 1)
  - Capability-architect binding conditions G10 (WDL implementation)
    and G11 (Charter P0 implementation)
  - Fagan 1976 IBM Systems Journal 15(3):182-211 (planning stage)
  - IEEE 1028-2008 §6.4 (entry criteria)

Last updated: 2026-06-06 (WDL v1 rollout — added sub-check 6 `wdl-gate`).
"""
from __future__ import annotations

import argparse
import datetime as _dt
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


# ─── Check 6: WDL preflight gate (proposals a4fe9faa + 7fd94c1a) ──
# WDL v1 sub-check: 4 sub-criteria (DR-2 of the Charter P0 proposal).
# Reference: workflows/wdl-contract.yaml §enforcement.prefight.sub_criteria
# and §enforcement.post_delivery.p0_cite_schema.
#
# This check runs against the LAOS project mirror at projects/<name>/.
# It is a meta-audit for projects whose plan_id was emitted by
# workflow-decomposer. For meta-projects (no plan_id yet, e.g. the
# wdl-rollout meta-project itself), the check reports INFO-only and
# does not block — analogous to the sub-check `skeleton` meta-audit
# skip pattern in subagent_boot_check.py.

# We need the LAOS-rooted child-repo view. The contract says files
# live at artifacts/wdl/<plan-id>/verdict.yaml. The LAOS mirror is
# at projects/<name>/; the child repo mirrors the same tree.
# The orchestrator's manifest declares the active plan_id. We read
# it from the project's project.yaml (if present) under
# `wdl: { active_plan_id: ... }` OR from a sibling manifest file
# `projects/<name>/.wdl-manifest.yaml`. If neither is present, the
# sub-check reports a soft "no plan_id declared" finding (advisory
# only — not blocking, but signals that the project has not yet
# entered the WDL pre-dispatch flow).

# We need the LAOS-rooted child-repo view. The contract says files
# live at artifacts/wdl/<plan-id>/verdict.yaml. The LAOS mirror is
# at projects/<name>/; the child repo mirrors the same tree.

# Adaptive scaling: classify project by complexity tier (M0/M1/M2).
# Tier is determined by deliverable count. Higher tiers get deeper checks.
# Invariant: M2 gets at least as thorough checks as M1, which gets at
# least as thorough as M0. This mirrors CodeGraph's getExploreOutputBudget
# rule: "a larger tier must never get a smaller maxCharsPerFile than a
# smaller tier."

# ─── Project tier classification ─────────────────────────────────────────────
# Tier thresholds. Adjust if LAOS patterns shift (e.g., more complex
# workflows emerge). The tier is advisory — checks emit guidance, not
# blocking errors, for the tier gap between what was run and what would
# have run in a higher tier.

TIER_M0_MAX = 5    # <  TIER_M0_MAX  → M0 (micro)
TIER_M1_MAX = 15   # <  TIER_M1_MAX  → M1 (small-medium)
                    # >= TIER_M1_MAX  → M2 (large)

def get_project_tier(project: Path) -> str:
    """Classify project into M0 / M1 / M2 by deliverable count.

    Returns "M0", "M1", or "M2". M2 is the most thorough.
    """
    py = project / "project.yaml"
    if not py.exists():
        return "M0"

    try:
        data = yaml.safe_load(py.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return "M0"

    if not isinstance(data, dict):
        return "M0"

    deliverables = data.get("deliverables", []) or []
    count = len(deliverables) if isinstance(deliverables, list) else 0

    if count < TIER_M0_MAX:
        return "M0"
    elif count < TIER_M1_MAX:
        return "M1"
    else:
        return "M2"


VERDICT_YAML_REL = "artifacts/wdl"   # relative to project root
MANIFEST_REL = ".wdl-manifest.yaml"  # sibling file at project root
PLANNING_AGENT_IDS = {"workflow-decomposer"}  # self-attest forbidden


def _parse_iso8601(s: str) -> _dt.datetime | None:
    """Parse an ISO-8601 timestamp; return None on failure. Accepts
    the `Z` suffix and naive timestamps. Used for anti-backdating
    comparison (user_confirmed_at >= dispatch_at).
    """
    if not isinstance(s, str) or not s:
        return None
    # Python's fromisoformat in 3.11+ accepts the 'Z' suffix; for
    # earlier versions, normalize.
    s_norm = s.replace("Z", "+00:00")
    try:
        return _dt.datetime.fromisoformat(s_norm)
    except ValueError:
        return None


def check_wdl_gate(project: Path) -> list[str]:
    """Check 6: WDL preflight gate (proposal 7fd94c1a DR-2).

    4 sub-criteria:
      (a) verdict.yaml exists at child-repo path
      (b) verified_by countersigned (populated, not equal to the
          planning subagent — cross-validator requirement)
      (c) plan_id matches active project (manifest's plan_id ==
          verdict's plan_id)
      (d) bypass validity (if wdl_bypass: orchestrator_override
          declared, ALL of:
          (i) user_confirmed_at >= dispatch_at
          (ii) manifest_entry references the bypass
          (iii) user message logged verbatim OR user_confirmed_at
                strictly after dispatch_at by >= 1 second
          If wdl_bypass absent → no further check; the WDL gate is
          the happy path.

    Reference: workflows/wdl-contract.yaml §enforcement.prefight.

    Meta-audit skip: if the project has no `wdl.active_plan_id` and
    no `.wdl-manifest.yaml`, the check reports an advisory finding
    (NOT blocking). This covers meta-projects and the wdl-rollout
    rollout meta-project itself, which are not project dispatches
    and therefore not subject to the WDL gate.
    """
    errors: list[str] = []
    py = project / "project.yaml"
    if not py.exists():
        # Meta-audit skip: no project.yaml → not a project dispatch.
        return errors

    # Read the orchestrator's manifest. Two surfaces, in order:
    #   1. project.yaml `wdl: { active_plan_id, wdl_bypass, ... }`
    #   2. .wdl-manifest.yaml sibling file
    try:
        proj_data = yaml.safe_load(py.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        proj_data = {}
    if not isinstance(proj_data, dict):
        proj_data = {}

    wdl_block = proj_data.get("wdl") if isinstance(proj_data.get("wdl"), dict) else {}

    manifest_path = project / MANIFEST_REL
    manifest = {}
    if manifest_path.exists():
        try:
            manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            manifest = {}
        if not isinstance(manifest, dict):
            manifest = {}

    # The effective manifest merges project.yaml's wdl: block (lower
    # precedence) and the .wdl-manifest.yaml sibling (higher
    # precedence — the orchestrator's runtime manifest).
    def _get(key: str, default=None):
        return manifest.get(key, wdl_block.get(key, default))

    active_plan_id = _get("active_plan_id")
    wdl_bypass = _get("wdl_bypass")  # None | "orchestrator_override"
    user_confirmed_at_raw = _get("user_confirmed_at")
    dispatch_at_raw = _get("dispatch_at")
    manifest_entry = _get("manifest_entry")

    if not active_plan_id:
        # Meta-audit / pre-WDL project: no plan_id declared.
        # Advisory only (not blocking). This is the WDL counterpart
        # to the subagent_boot_check.py meta-audit skip pattern.
        # We emit an INFO line but return no errors.
        # (Callers distinguish via the WDL_GATE_INFO prefix.)
        # NOTE: We append to errors list with a special prefix so
        # the run_all can split blocking vs advisory. Simpler: use
        # a separate channel. Here, we just return [] (no block).
        return errors

    # Sub-criterion (a): verdict.yaml exists at child-repo path.
    verdict_path = project / VERDICT_YAML_REL / active_plan_id / "verdict.yaml"
    if not verdict_path.exists():
        errors.append(
            f"WDL_GATE_A: verdict.yaml ausente em {verdict_path}. "
            f"Fix: workflow-decomposer deve produzir "
            f"artifacts/wdl/{active_plan_id}/verdict.yaml antes de "
            f"qualquer dispatch de especialista."
        )
        return errors  # subsequent sub-criteria need the file

    # Load verdict.yaml.
    try:
        verdict_data = yaml.safe_load(verdict_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        errors.append(
            f"WDL_GATE_A: verdict.yaml invalido em {verdict_path} "
            f"({type(e).__name__}: {e})"
        )
        return errors
    if not isinstance(verdict_data, dict):
        errors.append(
            f"WDL_GATE_A: verdict.yaml root nao e' mapping em {verdict_path}"
        )
        return errors

    # Sub-criterion (a cont.): the verdict has a `state` field and it
    # is one of the three valid states.
    state = verdict_data.get("state")
    if state not in {"READY", "DEFER", "ESCALATE"}:
        errors.append(
            f"WDL_GATE_A: verdict.state invalido: {state!r} "
            f"(esperado READY | DEFER | ESCALATE)"
        )

    # Sub-criterion (b): verified_by countersigned.
    verified_by = verdict_data.get("verified_by")
    planner_id = verdict_data.get("planner_id")
    if not verified_by:
        errors.append(
            "WDL_GATE_B: verified_by ausente no verdict. "
            "Fix: cross-validator (delivery-reviewer em bootstrap) "
            "deve countersign antes do orchestrator despachar."
        )
    elif planner_id and verified_by == planner_id:
        # Self-attested: same agent planned AND verified. P0 cite.
        errors.append(
            f"WDL_GATE_B: verified_by == planner_id ({verified_by!r}); "
            f"self-attested verdict. Fix: cross-validator deve ser "
            f"agente_id != planner_id."
        )
    elif verified_by in PLANNING_AGENT_IDS:
        # The planning agent "self-verified" — same anti-pattern.
        errors.append(
            f"WDL_GATE_B: verified_by == planning subagent "
            f"({verified_by!r}); self-attested verdict."
        )

    # Sub-criterion (c): plan_id matches active project.
    verdict_plan_id = verdict_data.get("plan_id")
    if verdict_plan_id != active_plan_id:
        errors.append(
            f"WDL_GATE_C: verdict.plan_id ({verdict_plan_id!r}) != "
            f"manifest.active_plan_id ({active_plan_id!r})."
        )

    # Sub-criterion (d): bypass validity.
    if wdl_bypass == "orchestrator_override":
        # (d-i) user_confirmed_at >= dispatch_at (anti-backdating)
        if not user_confirmed_at_raw:
            errors.append(
                "WDL_GATE_D: wdl_bypass=orchestrator_override declarado "
                "mas user_confirmed_at ausente no manifest."
            )
        if not dispatch_at_raw:
            errors.append(
                "WDL_GATE_D: wdl_bypass=orchestrator_override declarado "
                "mas dispatch_at ausente no manifest."
            )
        if user_confirmed_at_raw and dispatch_at_raw:
            uc = _parse_iso8601(str(user_confirmed_at_raw))
            da = _parse_iso8601(str(dispatch_at_raw))
            if uc is None:
                errors.append(
                    f"WDL_GATE_D: user_confirmed_at malformado: "
                    f"{user_confirmed_at_raw!r}"
                )
            elif da is None:
                errors.append(
                    f"WDL_GATE_D: dispatch_at malformado: "
                    f"{dispatch_at_raw!r}"
                )
            elif uc < da:
                errors.append(
                    f"WDL_GATE_D: bypass backdated "
                    f"(user_confirmed_at={user_confirmed_at_raw} < "
                    f"dispatch_at={dispatch_at_raw}); DR-1 anti-backdating."
                )
            elif (uc - da).total_seconds() < 1 and not manifest_entry:
                # Same minute as first dispatch AND no verbatim
                # user message in manifest → suspect.
                errors.append(
                    f"WDL_GATE_D: bypass timestamp within 1s of first "
                    f"dispatch (user_confirmed_at={user_confirmed_at_raw}, "
                    f"dispatch_at={dispatch_at_raw}) and no manifest_entry. "
                    f"DR-1: confirmation treated as suspect unless user "
                    f"message is logged verbatim in manifest."
                )
        # (d-ii) manifest_entry references the bypass
        if not manifest_entry:
            errors.append(
                "WDL_GATE_D: wdl_bypass declarado mas manifest_entry "
                "ausente (sem trecho verbatim da mensagem do usuario)."
            )

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


def run_all(project: Path) -> tuple[int, list[str], str]:
    """Run all checks. Returns (exit_code, list_of_findings, tier).

    tier is "M0", "M1", or "M2" — determines scaling depth for checks 4 and 6.
    """
    if not project.exists() or not project.is_dir():
        return 2, [f"USAGE: {project} is not a directory"], "M0"

    findings: list[str] = []
    tier = get_project_tier(project)

    findings += check_yaml_arithmetic(project)
    findings += check_deliverable_paths(project)
    findings += check_secrets(project)

    # Check 4 (cross-ref): M0 → advisory only (no blocking findings)
    cross_ref_errors = check_cross_references(project)
    if tier == "M0":
        for f in cross_ref_errors:
            findings.append(f"ADVISORY: {f}")  # non-blocking for M0
    else:
        findings += cross_ref_errors

    findings += check_no_impl_code(project)

    # Check 6 (WDL gate): M0 → skip entirely; M1 → standard; M2 → full
    if tier == "M0":
        findings.append(
            f"ADVISORY_WDL: project tier M0 (<{TIER_M0_MAX} deliverables) — "
            f"WDL preflight gate skipped. Run `workflow-decomposer` manually "
            f"if project will scale to M1+."
        )
    else:
        findings += check_wdl_gate(project)

    return (0 if not findings else 1), findings, tier


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

    code, findings, tier = run_all(args.project_path)

    if not args.quiet:
        print(f"Preflight: {args.project_path}")
        print(f"Tier: {tier} "
              f"({'<5' if tier=='M0' else '5-15' if tier=='M1' else '>15'} deliverables)")
        print("-" * 60)

    if not findings:
        print(f"PREFLIGHT_PASS: 0 findings, tier={tier}, 6 checks completed.")
        return 0

    # blocking vs advisory
    blocking = [f for f in findings if not f.startswith("ADVISORY")]
    advisory = [f for f in findings if f.startswith("ADVISORY")]

    for f in blocking:
        print(f"BLOCKED: {f}")
    for f in advisory:
        print(f"{f}")

    print("-" * 60)
    if blocking:
        print(f"PREFLIGHT_BLOCKED: {len(blocking)} blocking, {len(advisory)} advisory. Fix blocking before dispatch.")
    else:
        print(f"PREFLIGHT_PASS: {len(advisory)} advisory finding(s), 0 blocking. Pass.")
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
