"""Delete/archive project + langfuse attribution tests."""

from __future__ import annotations

import duckdb
import pytest

from laos.db import schema as schema_mod
from laos.web import portfolio


@pytest.fixture()
def env(tmp_path, monkeypatch):
    root = tmp_path
    (root / "AGENTS.md").write_text("x", encoding="utf-8")
    proj = root / "projects" / "del-proj"
    proj.mkdir(parents=True)
    (proj / "project.yaml").write_text(
        "project_name: del-proj\nbrief: x\nneeds: []\ndeliverables: []\n",
        encoding="utf-8")
    con = duckdb.connect(":memory:")
    schema_mod.apply_schema(con)
    monkeypatch.setattr(portfolio.needs_mod, "_find_laos_root", lambda: root)
    monkeypatch.setattr(portfolio.schema, "connect", lambda: con)
    # seed DB state
    con.execute(
        "INSERT INTO projects (project_id, name, status) VALUES ('del-proj','del-proj','running')"
    )
    con.execute(
        "INSERT INTO runs (run_id, project_id, status) VALUES ('r1','del-proj','completed')"
    )
    con.execute(
        "INSERT INTO steps (run_id, step_id, step_type, agent, status) "
        "VALUES ('r1','s1','stage','x','completed')"
    )
    con.execute(
        "INSERT INTO phases (project_id, phase, name, status) VALUES ('del-proj',1,'f','completed')"
    )
    return root, con


def test_delete_removes_db_and_archives(tmp_path, monkeypatch, env):
    root, con = env
    result = portfolio.delete_project("del-proj", archive_dir="projects_archived")
    # DB state gone
    assert con.execute("SELECT COUNT(*) FROM runs WHERE project_id='del-proj'").fetchone()[0] == 0
    assert con.execute("SELECT COUNT(*) FROM steps WHERE run_id='r1'").fetchone()[0] == 0
    assert con.execute("SELECT COUNT(*) FROM phases WHERE project_id='del-proj'").fetchone()[0] == 0
    assert con.execute("SELECT COUNT(*) FROM projects WHERE project_id='del-proj'").fetchone()[0] == 0
    # folder moved to archive
    assert not (root / "projects" / "del-proj").exists()
    assert (root / "projects_archived" / "del-proj" / "project.yaml").exists()
    assert result["db_tables"]


def test_delete_without_archive_deletes_folder(tmp_path, monkeypatch, env):
    root, con = env
    portfolio.delete_project("del-proj")  # no archive_dir -> remove folder
    assert not (root / "projects" / "del-proj").exists()


def test_langfuse_stats_filters_by_project(monkeypatch):
    """Traces without laos_project tag must NOT count toward a project."""
    fake_traces = [
        {"name": "litellm-acompletion", "totalCost": 0.5,
         "metadata": {"laos_project": "other-proj"}},
        {"name": "litellm-acompletion", "totalCost": 0.3,
         "metadata": {"laos_project": "mine"}},
        {"name": "litellm-acompletion", "totalCost": 9.9, "metadata": None},  # untagged
    ]
    import json

    class _Resp:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return json.dumps({"data": fake_traces}).encode()

    def _fake_open(req, timeout=5):
        return _Resp()

    monkeypatch.setattr(portfolio.urllib.request, "urlopen", _fake_open)
    stats = portfolio._langfuse_stats("mine")
    assert stats["llm_cost_usd"] == pytest.approx(0.3)
    assert stats["llm_trace_count"] == 1
