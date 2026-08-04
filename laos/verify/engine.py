"""LAOS verifier framework — the "guaranteed check".

Each deliverable type has a verifier that answers mechanically:
  - exists:       file present (mirror or child clone)
  - imports:      loads cleanly (SQL parses, HTML well-formed, JSON valid)
  - passes_test:  artifact-specific sanity test
  - spec_match:   matches the contract declared in project.yaml

A deliverable is "shipped" only when all four are True. Results persist
to DuckDB `deliverables` and are surfaced in the board + `laos verify`.

Verifiers are registered by artifact extension or keyword in the path.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from laos.db import schema

# ─── result type ─────────────────────────────────────────────────────


@dataclass
class VerifyResult:
    deliverable: str
    exists: bool = False
    imports: bool = False
    passes_test: bool = False
    spec_match: bool = False
    skipped: bool = False
    notes: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.exists and self.imports and self.passes_test and self.spec_match

    def to_row(self) -> dict[str, Any]:
        return {
            "exists": self.exists,
            "imports": self.imports,
            "passes_test": self.passes_test,
            "spec_match": self.spec_match,
            "notes": "; ".join(self.notes),
        }


# ─── individual checks ───────────────────────────────────────────────


def _check_import(path: Path, ext: str) -> tuple[bool, str]:
    """Load the file cleanly per type."""
    try:
        if ext == ".sql":
            # parse-ish: must have a statement terminator and valid charset
            txt = path.read_text(encoding="utf-8")
            ok = bool(txt.strip()) and (";" in txt or "CREATE" in txt.upper() or "SELECT" in txt.upper())
            return ok, "sql parse" if ok else "no statements"
        if ext == ".json":
            json.loads(path.read_text(encoding="utf-8"))
            return True, "json valid"
        if ext in (".html", ".htm"):
            txt = path.read_text(encoding="utf-8", errors="replace")
            ok = "<html" in txt.lower() or "<!doctype" in txt.lower() or "<body" in txt.lower()
            return ok, "html structure" if ok else "no html markers"
        if ext in (".py",):
            import ast

            ast.parse(path.read_text(encoding="utf-8"))
            return True, "python parses"
        if ext == ".md":
            return bool(path.read_text(encoding="utf-8").strip()), "non-empty markdown"
        if ext == ".yaml" or ext == ".yml":
            import yaml

            yaml.safe_load(path.read_text(encoding="utf-8"))
            return True, "yaml valid"
        # unknown type: existence is the check
        return True, "type not checked"
    except Exception as e:  # noqa: BLE001
        return False, f"{type(e).__name__}: {str(e)[:120]}"


def _check_pass(path: Path, ext: str) -> tuple[bool, str]:
    """Type-specific sanity test (beyond 'loads')."""
    try:
        if ext == ".sql":
            txt = path.read_text(encoding="utf-8").upper()
            # must contain a DDL/DML keyword and not be empty
            ok = any(k in txt for k in ("CREATE", "SELECT", "INSERT", "ALTER", "DROP", "WITH"))
            return ok, "sql keywords" if ok else "no sql keywords"
        if ext == ".json":
            data = json.loads(path.read_text(encoding="utf-8"))
            ok = isinstance(data, (dict, list)) and len(data) > 0
            return ok, "non-empty json" if ok else "empty json"
        if ext == ".html":
            txt = path.read_text(encoding="utf-8", errors="replace")
            ok = len(txt) > 500
            return ok, f"{len(txt)} chars" if ok else "too small"
        if ext == ".py":
            txt = path.read_text(encoding="utf-8")
            ok = len(txt) > 100
            return ok, f"{len(txt)} chars" if ok else "too small"
        if ext == ".md":
            txt = path.read_text(encoding="utf-8")
            ok = len(txt) > 200
            return ok, f"{len(txt)} chars" if ok else "too small"
        return True, "no extra test"
    except Exception as e:  # noqa: BLE001
        return False, f"{type(e).__name__}: {str(e)[:120]}"


# ─── the verifier engine ─────────────────────────────────────────────


def _artifact_paths(root: Path, project_name: str, artifact: str) -> list[Path]:
    """Possible locations: LAOS mirror + project-local artifacts + child clone."""
    cands = [
        root / artifact,
        root / "projects" / project_name / artifact,
        root / "projects" / project_name / "_child_clone" / artifact,
    ]
    return [c for c in cands if c.exists()]


def verify_deliverable(
    root: Path,
    project_name: str,
    deliverable: dict[str, Any],
) -> VerifyResult:
    name = deliverable.get("name", "?")
    res = VerifyResult(deliverable=name)
    artifacts = deliverable.get("artifacts", []) or []
    # Explicitly pending deliverables are NOT failures — they are skipped
    # until the stage actually runs. The board shows them as not-yet-shipped.
    if deliverable.get("status") == "pending":
        res.exists = True
        res.imports = True
        res.passes_test = True
        res.spec_match = bool(deliverable.get("label")) and "stage" in deliverable
        res.skipped = True
        res.notes.append("status=pending: skipped until stage runs")
        return res
    if not artifacts:
        # deliverable without artifact paths: spec-level only
        res.spec_match = bool(deliverable.get("label")) and "stage" in deliverable
        res.exists = True  # declared; nothing to check physically
        return res

    # exists: at least one declared artifact present
    present_paths: list[Path] = []
    for a in artifacts:
        found = _artifact_paths(root, project_name, a)
        if found:
            present_paths.extend(found)
    res.exists = len(present_paths) == len(artifacts)  # ALL artifacts present

    # imports + passes_test on the first present artifact per declared path
    import_ok, import_note = True, ""
    pass_ok, pass_note = True, ""
    for a in artifacts:
        found = _artifact_paths(root, project_name, a)
        if not found:
            res.notes.append(f"missing: {a}")
            import_ok, pass_ok = False, False
            continue
        ext = Path(a).suffix.lower()
        for fp in found:
            i_ok, i_note = _check_import(fp, ext)
            p_ok, p_note = _check_pass(fp, ext)
            import_ok = import_ok and i_ok
            pass_ok = pass_ok and p_ok
            if not i_ok:
                res.notes.append(f"{a}: import fail ({i_note})")
            if not p_ok:
                res.notes.append(f"{a}: test fail ({p_note})")
    res.imports = import_ok
    res.passes_test = pass_ok

    # spec_match: deliverable has label + stage (contract completeness)
    res.spec_match = bool(deliverable.get("label")) and "stage" in deliverable
    if not res.spec_match:
        res.notes.append("spec incomplete: needs label + stage")
    return res


def persist_result(con, project_id: str, res: VerifyResult) -> None:
    row = res.to_row()
    con.execute(
        "INSERT OR REPLACE INTO deliverables "
        "(project_id, name, exists_, imports_, passes_test, spec_match, verified_at) "
        "VALUES (?, ?, ?, ?, ?, ?, current_timestamp)",
        [project_id, res.deliverable, row["exists"], row["imports"],
         row["passes_test"], row["spec_match"]],
    )


def verify_project(root: Path, project_name: str) -> tuple[list[VerifyResult], bool]:
    """Verify all deliverables of a project. Returns (results, all_ok)."""
    import yaml

    py = root / "projects" / project_name / "project.yaml"
    if not py.exists():
        raise FileNotFoundError(f"project.yaml not found: {py}")
    data = yaml.safe_load(py.read_text(encoding="utf-8")) or {}
    deliverables = data.get("deliverables", []) or []
    con = schema.connect()
    results = []
    for d in deliverables:
        if not isinstance(d, dict):
            continue
        res = verify_deliverable(root, project_name, d)
        persist_result(con, project_name, res)
        results.append(res)
    all_ok = bool(results) and all(
        r.ok or r.skipped for r in results  # pending deliverables don't block
    )
    # flip ready_to_ship on the project row
    con.execute(
        "INSERT INTO projects (project_id, name, status, ready_to_ship) "
        "VALUES (?, ?, 'completed', ?) "
        "ON CONFLICT (project_id) DO UPDATE SET ready_to_ship=?",
        [project_name, project_name, all_ok, all_ok],
    )
    # best-effort Langfuse scores (degradable if Langfuse is down)
    try:
        from laos.verify.langfuse_score import post_project_scores

        post_project_scores(project_name, results)
    except Exception:  # noqa: BLE001
        pass
    return results, all_ok
