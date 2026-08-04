"""LAOS portfolio — data access layer for the board UI.

Reads project.yaml contracts + DuckDB state and assembles the per-project
view: status, cost by phase, checklist, decisions, gaps, recent runs.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from laos.db import schema
from laos.core import needs as needs_mod


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:  # noqa: BLE001
        data = {}
    return data if isinstance(data, dict) else {}


def _find_laos_root() -> Path:
    return needs_mod._find_laos_root()


def list_projects() -> list[dict[str, Any]]:
    """All projects from projects/*/project.yaml merged with DB state."""
    root = _find_laos_root()
    con = schema.connect()
    out: list[dict[str, Any]] = []
    for pdir in sorted((root / "projects").iterdir()):
        py = pdir / "project.yaml"
        if not py.exists():
            continue
        data = _load_yaml(py)
        name = data.get("project_name", pdir.name)
        row = con.execute(
            "SELECT status, last_run_id, ready_to_ship FROM projects WHERE project_id=?",
            [name],
        ).fetchone()
        db_status = row[0] if row else data.get("status", "not_started")
        ready = bool(row[2]) if row else False
        # aggregate runs for the card
        agg = con.execute(
            "SELECT COALESCE(SUM(cost_usd),0), COALESCE(SUM(tokens),0), "
            "COALESCE(SUM(errors),0), COUNT(*) "
            "FROM runs WHERE project_id=?",
            [name],
        ).fetchone()
        out.append({
            "name": name,
            "display": data.get("display_name", name),
            "brief": data.get("brief", ""),
            "status": db_status,
            "ready_to_ship": ready,
            "last_run_id": row[1] if row else None,
            "needs": data.get("needs", []) or [],
            "path": str(py),
            "cost_usd": agg[0] if agg else 0.0,
            "tokens": agg[1] if agg else 0,
            "errors": agg[2] if agg else 0,
            "run_count": agg[3] if agg else 0,
        })
    return out


def project_detail(project_id: str) -> dict[str, Any] | None:
    root = _find_laos_root()
    py = root / "projects" / project_id / "project.yaml"
    if not py.exists():
        return None
    data = _load_yaml(py)
    con = schema.connect()
    name = data.get("project_name", project_id)

    # status + runs
    prow = con.execute(
        "SELECT status, ready_to_ship FROM projects WHERE project_id=?",
        [name],
    ).fetchone()
    runs = con.execute(
        "SELECT run_id, status, cost_usd, tokens, errors, started_at, ended_at "
        "FROM runs WHERE project_id=? ORDER BY started_at DESC LIMIT 10",
        [name],
    ).fetchall()

    # cost by phase (aggregated by the pipeline)
    phases = con.execute(
        "SELECT phase, name, status, cost_usd, tokens, errors, started_at "
        "FROM phases WHERE project_id=? ORDER BY phase",
        [name],
    ).fetchall()

    # decisions pending
    decisions = con.execute(
        "SELECT decision_id, question, cluster_id, status, asked_at "
        "FROM decisions WHERE project_id=? AND status='pending' ORDER BY asked_at DESC",
        [name],
    ).fetchall()

    # checklist / todos
    todos = con.execute(
        "SELECT todo_id, text, done, source FROM todos WHERE project_id=?",
        [name],
    ).fetchall()

    # gaps
    gaps = con.execute(
        "SELECT need, missing_capability, ttl_cycles FROM capability_gaps "
        "WHERE project_id=?",
        [name],
    ).fetchall()

    # deliverables + verify status
    deliverables = con.execute(
        "SELECT name, exists_, imports_, passes_test, spec_match, verified_at "
        "FROM deliverables WHERE project_id=?",
        [name],
    ).fetchall()

    # ─── Langfuse: LLM cost + trace count for this project ─────────
    lf = _langfuse_stats(name)

    # ─── derived totals ─────────────────────────────────────────────
    total_cost_runs = sum((r[2] or 0) for r in runs)
    total_tokens_runs = sum((r[3] or 0) for r in runs)
    total_errors_runs = sum((r[4] or 0) for r in runs)
    phase_cost = sum((p[3] or 0) for p in phases)
    phase_tokens = sum((p[4] or 0) for p in phases)
    total_done = sum(1 for t in todos if t[2])
    total_todos = len(todos)

    return {
        "name": name,
        "display": data.get("display_name", name),
        "brief": data.get("brief", ""),
        "status": prow[0] if prow else data.get("status", "not_started"),
        "ready_to_ship": bool(prow[1]) if prow else False,
        "needs": data.get("needs", []) or [],
        "capabilities_used": data.get("capabilities_used", {}),
        "repo": data.get("repo", ""),
        "runs": [dict(zip(
            ["run_id", "status", "cost_usd", "tokens", "errors",
             "started_at", "ended_at"], r)) for r in runs],
        "phases": [dict(zip(
            ["phase", "name", "status", "cost_usd", "tokens", "errors",
             "started_at"], p)) for p in phases],
        "decisions": [dict(zip(
            ["decision_id", "question", "cluster_id", "status", "asked_at"],
            d)) for d in decisions],
        "todos": [dict(zip(["todo_id", "text", "done", "source"], t)) for t in todos],
        "gaps": [dict(zip(["need", "missing_capability", "ttl_cycles"], g)) for g in gaps],
        "deliverables": [dict(zip(
            ["name", "exists", "imports", "passes_test", "spec_match",
             "verified_at"], d)) for d in deliverables],
        "langfuse": lf,
        "totals": {
            "cost_runs": total_cost_runs,
            "tokens_runs": total_tokens_runs,
            "errors_runs": total_errors_runs,
            "phase_cost": phase_cost,
            "phase_tokens": phase_tokens,
            "todos_done": total_done,
            "todos_total": total_todos,
        },
    }


def probe_capability_health() -> dict[str, str]:
    """Health of capability MCPs (enabled/disabled in opencode.jsonc)."""
    root = _find_laos_root()
    cfg = root / ".opencode" / "opencode.jsonc"
    if not cfg.exists():
        return {}
    try:
        text = cfg.read_text(encoding="utf-8")
    except OSError:
        return {}
    out: dict[str, str] = {}
    for cap in ["latade", "lan8n", "ladesign", "laecon", "laengine", "lacouncil"]:
        marker = f'"{cap}":'
        idx = text.find(marker)
        if idx == -1:
            out[cap] = "unknown"
            continue
        block = text[idx: idx + 800]
        if '"type": "remote"' in block:
            out[cap] = "ok"
        elif '"enabled": false' in block:
            out[cap] = "disabled"
        else:
            out[cap] = "ok"
    return out


def _langfuse_stats(project_id: str) -> dict[str, Any]:
    """LLM cost + trace count for a project, from Langfuse (degradable)."""
    try:
        import base64
        import json
        import urllib.request

        token = base64.b64encode(
            b"lf_pk_laos_9b8a7c6d5e4f:lf_sk_laos_0f1e2d3c4b5a").decode()
        req = urllib.request.Request(
            "http://localhost:3000/api/public/traces?limit=100",
            headers={"Authorization": f"Basic {token}"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            traces = json.loads(resp.read()).get("data", [])
        # traces from litellm carry no project tag; verify:* traces carry
        # metadata.project_id. We sum costs of litellm traces and count
        # verify traces tagged to this project.
        llm_cost = sum(t.get("totalCost") or 0 for t in traces
                       if "verify:" not in (t.get("name") or ""))
        llm_count = sum(1 for t in traces if "verify:" not in (t.get("name") or ""))
        verify_count = sum(1 for t in traces
                           if (t.get("metadata") or {}).get("project_id") == project_id)
        return {
            "llm_cost_usd": llm_cost,
            "llm_trace_count": llm_count,
            "verify_score_count": verify_count,
            "up": True,
        }
    except Exception:  # noqa: BLE001
        return {"llm_cost_usd": 0.0, "llm_trace_count": 0,
                "verify_score_count": 0, "up": False}
