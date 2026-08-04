"""P1: auto-resume — kill mid-run, resume continues without redoing work."""

from __future__ import annotations

import duckdb
import pytest

from laos.core import pipeline
from laos.core import run_state


def _project_yaml(tmp_path):
    py = tmp_path / "project.yaml"
    py.write_text(
        "project_name: test-proj\n"
        "deliverables:\n"
        "  - name: a\n    stage: 1\n"
        "  - name: b\n    stage: 2\n"
        "  - name: c\n    stage: 3\n",
        encoding="utf-8",
    )
    return py


def _steps_of(con, run_id: str) -> list[tuple]:
    return con.execute(
        "SELECT step_type, status FROM steps WHERE run_id=? ORDER BY ts",
        [run_id],
    ).fetchall()


def test_full_run_completes_all_stages(tmp_path):
    con = duckdb.connect(":memory:")
    from laos.db import schema

    schema.apply_schema(con)
    py = _project_yaml(tmp_path)
    pipe = pipeline.RunPipeline("test-proj", py, con=con)
    run_id = pipe.run()
    steps = _steps_of(con, run_id)
    assert len(steps) == 3
    assert all(s[1] == "completed" for s in steps)
    summary = pipe.rs.run_summary(run_id)
    assert summary["status"] == "completed"


def test_kill_mid_run_then_resume_continues(tmp_path):
    """Runner dies on stage 2. Resume must NOT redo stage 1, must finish 2+3."""
    con = duckdb.connect(":memory:")
    from laos.db import schema

    schema.apply_schema(con)
    py = _project_yaml(tmp_path)

    calls: list[str] = []

    def killer(stage, ctx):
        calls.append(stage["name"])
        if stage["name"] == "b":
            # simulate process death: raise KeyboardInterrupt mid-step
            raise KeyboardInterrupt("simulated kill")
        return {"status": "completed", "error_class": None, "cost_usd": 0.0, "tokens": 0}

    pipe = pipeline.RunPipeline("test-proj", py, runner=killer, con=con)
    with pytest.raises(KeyboardInterrupt):
        pipe.run()

    # after "kill": run is still running, step b is an orphan (still 'running')
    run_id = pipe.rs.run_id
    assert run_id
    steps = _steps_of(con, run_id)
    statuses = {s[0]: s[1] for s in steps}
    assert statuses["stage_1_a"] == "completed"
    assert statuses["stage_2_b"] == "running"  # orphan mark: process died mid-step

    # resume with a healthy runner: redo only b, then c
    def healthy(stage, ctx):
        calls.append(stage["name"])
        return {"status": "completed", "error_class": None, "cost_usd": 0.0, "tokens": 0}

    pipe2 = pipeline.RunPipeline("test-proj", py, runner=healthy, con=con)
    resumed_id = pipe2.resume()
    assert resumed_id == run_id  # same run, not a new one

    steps = _steps_of(con, run_id)
    statuses = {s[0]: s[1] for s in steps}
    assert statuses["stage_1_a"] == "completed"   # not redone
    assert statuses["stage_2_b"] == "completed"   # redone after resume
    assert statuses["stage_3_c"] == "completed"
    # the orphan b was marked interrupted before being redone
    assert any(s[0] == "stage_2_b" and s[1] == "interrupted" for s in steps)
    # a ran once total; b ran twice (killed + resumed); c ran once
    assert calls.count("a") == 1
    assert calls.count("b") == 2
    assert calls.count("c") == 1


def test_resume_with_no_incomplete_returns_none(tmp_path):
    con = duckdb.connect(":memory:")
    from laos.db import schema

    schema.apply_schema(con)
    py = _project_yaml(tmp_path)
    pipe = pipeline.RunPipeline("test-proj", py, con=con)
    assert pipe.resume() is None


def test_force_new_starts_fresh_run(tmp_path):
    con = duckdb.connect(":memory:")
    from laos.db import schema

    schema.apply_schema(con)
    py = _project_yaml(tmp_path)
    pipe = pipeline.RunPipeline("test-proj", py, con=con)
    first = pipe.run()
    second = pipe.run(force_new=True)
    assert first != second


def test_phases_aggregate_cost_tokens(tmp_path):
    """costed_runner -> phases table has per-phase cost/tokens for the board."""
    con = duckdb.connect(":memory:")
    from laos.db import schema

    schema.apply_schema(con)
    py = _project_yaml(tmp_path)
    pipe = pipeline.RunPipeline("test-proj", py, runner=pipeline.costed_runner, con=con)
    pipe.run()

    phases = con.execute(
        "SELECT phase, cost_usd, tokens FROM phases WHERE project_id='test-proj' "
        "ORDER BY phase"
    ).fetchall()
    # 3 stages; each costed_runner reports 0.001 + 0.0005*stage
    assert len(phases) == 3
    assert phases[0][1] == pytest.approx(0.001 + 0.0005 * 1)
    assert phases[1][1] == pytest.approx(0.001 + 0.0005 * 2)
    assert phases[2][1] == pytest.approx(0.001 + 0.0005 * 3)
