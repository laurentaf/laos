"""LAOS core — run pipeline with auto-resume.

Executes the stages declared in a project's project.yaml, persisting
each step to DuckDB. If the process dies mid-run (a step is left in
`running` state), `resume()` marks orphan steps as `interrupted` and
continues from the first non-completed stage — no work is silently lost.

Stage execution is pluggable: the default `runner` is a no-op logger
(dispatch wiring arrives in P2 with the real executor). The pipeline
itself — ordering, persistence, resume semantics — is tested
independently of the executor.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Callable

from laos.db import schema
from laos.core import run_state

# A stage runner: callable(stage: dict, ctx) -> dict.
# Returns {"status": "completed"|"failed", "error_class": str|None,
#          "cost_usd": float, "tokens": int}
StageRunner = Callable[[dict[str, Any], Any], dict[str, Any]]


def noop_runner(stage: dict[str, Any], _ctx: Any) -> dict[str, Any]:
    """Default runner: logs the stage, does not dispatch. (P2 replaces.)"""
    time.sleep(0.05)  # simulate work so mid-run kills are meaningful
    return {"status": "completed", "error_class": None, "cost_usd": 0.0, "tokens": 0}


def costed_runner(stage: dict[str, Any], _ctx: Any) -> dict[str, Any]:
    """Demo runner: reports a cost/token per stage so phase aggregation
    and the board's cost-by-phase have real data to show."""
    cost = 0.001 + 0.0005 * stage.get("stage", 0)
    tokens = 100 + 50 * stage.get("stage", 0)
    return {"status": "completed", "error_class": None,
            "cost_usd": cost, "tokens": tokens}


class RunPipeline:
    """Ordered, resumable execution of a project's stages."""

    def __init__(
        self,
        project_id: str,
        project_yaml: Path,
        runner: StageRunner | None = None,
        con=None,
    ):
        self.project_id = project_id
        self.project_yaml = project_yaml
        self.runner = runner or noop_runner
        self.rs = run_state.RunState(con)
        # expose root for runners (artifact path resolution).
        # project_yaml = <root>/projects/<name>/project.yaml, so root is
        # three levels up: project.yaml -> <name>/ -> projects/ -> <root>/
        self._root = project_yaml.parent.parent.parent

    # ─── public API ───────────────────────────────────────────────

    def run(self, force_new: bool = False) -> str:
        """Run the project. If an incomplete run exists, resume it
        unless force_new is True. Returns the run_id used."""
        existing = self.rs.last_incomplete_run(self.project_id)
        if existing and not force_new:
            self.rs.run_id = existing
            self.rs.project_id = self.project_id
            self._log(f"resuming run {existing}")
        else:
            self.rs.start_run(self.project_id)
            self._log(f"new run {self.rs.run_id}")
        self._execute_stages()
        self.rs.complete_run("completed")
        self._log("run completed")
        return self.rs.run_id or ""

    def resume(self) -> str | None:
        """Resume the last incomplete run for the project. Returns run_id."""
        run_id = self.rs.last_incomplete_run(self.project_id)
        if not run_id:
            return None
        self.rs.run_id = run_id
        self.rs.project_id = self.project_id
        self._execute_stages()
        self.rs.complete_run("completed")
        self._log("run completed (resumed)")
        return run_id

    # ─── stage orchestration ──────────────────────────────────────

    def _stages(self) -> list[dict[str, Any]]:
        import yaml

        data = yaml.safe_load(self.project_yaml.read_text(encoding="utf-8")) or {}
        deliverables = data.get("deliverables", []) or []
        ordered = sorted(
            (d for d in deliverables if isinstance(d, dict) and "stage" in d),
            key=lambda d: d["stage"],
        )
        # carry the full deliverable dict (name/stage/label/spec/artifacts)
        # so real runners (llm_artifact_runner) can produce the artifact.
        return [
            {
                "name": d.get("name", "?"),
                "stage": d.get("stage", 0),
                "label": d.get("label", ""),
                "spec": d.get("spec", d.get("label", "")),
                "artifacts": d.get("artifacts", []) or [],
                "status": d.get("status"),
            }
            for d in ordered
        ]

    def _completed_steps(self) -> set[str]:
        rows = self.con().execute(
            "SELECT step_type FROM steps WHERE run_id=? AND status='completed'",
            [self.rs.run_id],
        ).fetchall()
        return {r[0] for r in rows}

    def _interrupt_orphans(self) -> int:
        """Mark steps still `running` as interrupted (process died mid-step)."""
        cur = self.con()
        orphan_rows = cur.execute(
            "SELECT step_id FROM steps WHERE run_id=? AND status='running'",
            [self.rs.run_id],
        ).fetchall()
        for (step_id,) in orphan_rows:
            cur.execute(
                "UPDATE steps SET status='interrupted', error_class='process_killed' "
                "WHERE step_id=?",
                [step_id],
            )
        return len(orphan_rows)

    def _execute_stages(self) -> None:
        cur = self.con()
        orphans = self._interrupt_orphans()
        if orphans:
            self._log(f"interrupted {orphans} orphan step(s)")
        completed = self._completed_steps()
        for stage in self._stages():
            step_key = f"stage_{stage['stage']}_{stage['name']}"
            if step_key in completed:
                continue
            step_id = self.rs.start_step(step_key, "pipeline", tool=f"stage-{stage['stage']}")
            try:
                result = self.runner(stage, self)
                status = result.get("status", "failed")
                self.rs.end_step(
                    step_id,
                    status,
                    error_class=result.get("error_class"),
                    cost=result.get("cost_usd", 0.0),
                    tokens=result.get("tokens", 0),
                )
                self._log(f"  stage {stage['stage']} {stage['name']}: {status}")
                self._upsert_phase(stage, status, result)
            except Exception as e:  # noqa: BLE001
                self.rs.end_step(step_id, "failed", error_class=type(e).__name__)
                self._upsert_phase(stage, "failed", {})
                self._log(f"  stage {stage['stage']} {stage['name']}: FAILED {e}")
                raise

    def _upsert_phase(self, stage: dict, status: str, result: dict) -> None:
        """Aggregate cost/tokens/errors per (project_id, stage number)."""
        cur = self.con()
        stage_num = stage.get("stage", 0)
        cost = result.get("cost_usd", 0.0) or 0.0
        tokens = result.get("tokens", 0) or 0
        errors = 1 if status == "failed" else 0
        existing = cur.execute(
            "SELECT cost_usd, tokens, errors FROM phases WHERE project_id=? AND phase=?",
            [self.project_id, stage_num],
        ).fetchone()
        if existing:
            cur.execute(
                "UPDATE phases SET cost_usd=?, tokens=?, errors=?, status=?, "
                "ended_at=current_timestamp WHERE project_id=? AND phase=?",
                [existing[0] + cost, existing[1] + tokens, existing[2] + errors,
                 status, self.project_id, stage_num],
            )
        else:
            cur.execute(
                "INSERT INTO phases (project_id, phase, name, status, cost_usd, "
                "tokens, errors, started_at, ended_at) VALUES (?,?,?,?,?,?,?, "
                "current_timestamp, current_timestamp)",
                [self.project_id, stage_num, stage.get("name", "?"), status,
                 cost, tokens, errors],
            )

    # ─── helpers ──────────────────────────────────────────────────

    def _log(self, msg: str) -> None:
        print(f"[laos] {msg}", flush=True)

    def con(self):
        return self.rs.con
