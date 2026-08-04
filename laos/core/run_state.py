"""LAOS core — run state machine (auto-resume).

Tracks runs and steps in DuckDB. A run is `running` until explicitly
completed or failed. On restart, `laos resume` reads the last persisted
step and continues from there — no work is silently lost.
"""

from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone

from laos.db import schema


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _duration_since(ts) -> float:
    """Seconds from a DuckDB timestamp to now. Handles str/datetime."""
    if ts is None:
        return 0.0
    try:
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        return max(0.0, (now - ts).total_seconds())
    except Exception:  # noqa: BLE001
        return 0.0


class RunState:
    """Durable run/step tracking over DuckDB."""

    def __init__(self, con=None):
        self.con = con if con is not None else schema.connect()
        self.run_id: str | None = None
        self.project_id: str | None = None

    # ─── run lifecycle ────────────────────────────────────────────

    def start_run(self, project_id: str) -> str:
        self.run_id = f"run_{uuid.uuid4().hex[:12]}"
        self.project_id = project_id
        self.con.execute(
            "INSERT INTO runs (run_id, project_id, status) VALUES (?, ?, 'running')",
            [self.run_id, project_id],
        )
        self.con.execute(
            "UPDATE projects SET status='running', last_run_id=? WHERE project_id=?",
            [self.run_id, project_id],
        )
        return self.run_id

    def complete_run(self, status: str = "completed") -> None:
        assert self.run_id
        row = self.con.execute(
            "SELECT cost_usd, tokens, errors, retries, started_at "
            "FROM runs WHERE run_id=?",
            [self.run_id],
        ).fetchone()
        cost, tokens, errors, retries = row[0], row[1], row[2], row[3]
        started = row[4]
        duration = _duration_since(started)
        self.con.execute(
            "UPDATE runs SET status=?, ended_at=current_timestamp, "
            "duration_s=?, cost_usd=?, tokens=?, errors=?, retries=? "
            "WHERE run_id=?",
            [status, duration, cost, tokens, errors, retries, self.run_id],
        )
        self.con.execute(
            "UPDATE projects SET status=? WHERE project_id=?",
            ["completed" if status == "completed" else "failed", self.project_id],
        )

    # ─── step lifecycle ───────────────────────────────────────────

    def start_step(self, step_type: str, agent: str, tool: str = "") -> str:
        assert self.run_id
        step_id = f"{self.run_id}_{step_type}_{int(time.time()*1000)}"
        self.con.execute(
            "INSERT INTO steps (run_id, step_id, step_type, agent, status, tool) "
            "VALUES (?, ?, ?, ?, 'running', ?)",
            [self.run_id, step_id, step_type, agent, tool],
        )
        return step_id

    def end_step(
        self,
        step_id: str,
        status: str,
        error_class: str | None = None,
        cost: float = 0.0,
        tokens: int = 0,
    ) -> None:
        # compute real duration from the step's ts
        ts_row = self.con.execute(
            "SELECT ts FROM steps WHERE step_id=?", [step_id],
        ).fetchone()
        duration = _duration_since(ts_row[0]) if ts_row else 0.0
        self.con.execute(
            "UPDATE steps SET status=?, error_class=?, "
            "duration_s=? WHERE step_id=?",
            [status, error_class, duration, step_id],
        )
        if status == "failed":
            self.con.execute(
                "UPDATE runs SET errors = errors + 1 WHERE run_id=?",
                [self.run_id],
            )
        if cost or tokens:
            self.con.execute(
                "UPDATE runs SET cost_usd = cost_usd + ?, tokens = tokens + ? "
                "WHERE run_id=?",
                [cost, tokens, self.run_id],
            )

    # ─── resume / inspection ──────────────────────────────────────

    def last_incomplete_run(self, project_id: str) -> str | None:
        row = self.con.execute(
            "SELECT run_id FROM runs WHERE project_id=? AND status='running' "
            "ORDER BY started_at DESC LIMIT 1",
            [project_id],
        ).fetchone()
        return row[0] if row else None

    def last_step_of(self, run_id: str) -> dict | None:
        row = self.con.execute(
            "SELECT step_id, step_type, agent, status, tool FROM steps "
            "WHERE run_id=? ORDER BY ts DESC LIMIT 1",
            [run_id],
        ).fetchone()
        if not row:
            return None
        return {
            "step_id": row[0],
            "step_type": row[1],
            "agent": row[2],
            "status": row[3],
            "tool": row[4],
        }

    def run_summary(self, run_id: str) -> dict:
        row = self.con.execute(
            "SELECT run_id, project_id, status, cost_usd, tokens, duration_s, "
            "errors, retries, started_at, ended_at FROM runs WHERE run_id=?",
            [run_id],
        ).fetchone()
        if not row:
            raise KeyError(f"run not found: {run_id}")
        cols = [
            "run_id", "project_id", "status", "cost_usd", "tokens",
            "duration_s", "errors", "retries", "started_at", "ended_at",
        ]
        return dict(zip(cols, row))
