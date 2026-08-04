"""Planner tests: gap analysis, scaffold, apply_plan, console send fix."""

from __future__ import annotations

import pathlib

import pytest

from laos.plan import planner


def test_gap_analysis_empty_contract():
    gaps = planner.gap_analysis({"project_name": "x", "brief": "", "needs": [], "deliverables": []})
    assert any("brief" in g for g in gaps)
    assert any("needs" in g for g in gaps)
    assert any("deliverables" in g for g in gaps)


def test_gap_analysis_complete_contract():
    data = {
        "project_name": "x",
        "brief": "app de limpeza com 3 abas",
        "needs": ["design"],
        "deliverables": [
            {"name": "aba1", "label": "Aba 1", "stage": 1, "spec": "spec 1",
             "artifacts": ["artifacts/a.html"]},
        ],
    }
    gaps = planner.gap_analysis(data)
    assert gaps == []


def test_gap_analysis_missing_spec_and_stage():
    data = {
        "project_name": "x",
        "brief": "app de limpeza com 3 abas",
        "needs": ["design"],
        "deliverables": [
            {"name": "aba1", "artifacts": ["a.html"]},  # sem label E sem spec
        ],
    }
    gaps = planner.gap_analysis(data)
    assert any("sem spec" in g for g in gaps)
    assert any("sem stage" in g for g in gaps)


def test_scaffold_from_brief():
    data = planner.scaffold_from_brief("novo-proj", "sistema de notas")
    assert data["project_name"] == "novo-proj"
    assert data["brief"] == "sistema de notas"
    assert data["needs"] == []
    assert data["status"] == "planning"


def test_apply_plan_writes_contract(tmp_path, monkeypatch):
    proj = tmp_path / "projects" / "pproj"
    proj.mkdir(parents=True)
    py = proj / "project.yaml"
    py.write_text("project_name: pproj\nbrief: x\nneeds: [design]\ndeliverables: []\n",
                  encoding="utf-8")
    monkeypatch.setattr(planner.needs_mod, "_find_laos_root", lambda: tmp_path)

    data = {"project_name": "pproj", "brief": "x", "needs": ["design"],
            "deliverables": []}
    phases = [{"name": "f1", "spec": "spec1", "artifacts": ["artifacts/f1.html"], "stage": 1}]
    result = planner.apply_plan(data, phases)
    assert result["status"] == "planned"
    saved = py.read_text(encoding="utf-8")
    assert "f1" in saved
    assert "spec1" in saved


def test_console_send_returns_html(tmp_path, monkeypatch):
    """Regression: console send had missing request arg (bug fix)."""
    from fastapi.testclient import TestClient
    from laos.web.app import app
    from laos.db import schema as schema_mod
    import duckdb

    con = duckdb.connect(":memory:")
    schema_mod.apply_schema(con)
    monkeypatch.setattr(schema_mod, "connect", lambda: con)
    monkeypatch.setattr(schema_mod, "db_path", lambda: pathlib.Path(":memory:"))

    # project must exist
    from laos.web import portfolio

    root = tmp_path
    (root / "AGENTS.md").write_text("x", encoding="utf-8")
    proj = root / "projects" / "cproj"
    proj.mkdir(parents=True)
    (proj / "project.yaml").write_text(
        "project_name: cproj\nbrief: x\nneeds: []\ndeliverables: []\n",
        encoding="utf-8")
    monkeypatch.setattr(portfolio.needs_mod, "_find_laos_root", lambda: root)
    monkeypatch.setattr(portfolio.schema, "connect", lambda: con)

    # avoid LLM call
    from laos.chat import console as chat_mod

    monkeypatch.setattr(chat_mod, "chat", lambda pid, msg: "RESP")

    client = TestClient(app)
    r = client.post("/projects/cproj/console/send", data={"message": "ola"})
    assert r.status_code == 200
    assert "RESP" in r.text
