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


def test_console_send_with_action_dropdown(tmp_path, monkeypatch):
    """Dropdown action (/todo) routes to run_command, not the LLM."""
    from fastapi.testclient import TestClient
    from laos.web.app import app
    from laos.db import schema as schema_mod
    import duckdb

    con = duckdb.connect(":memory:")
    schema_mod.apply_schema(con)
    monkeypatch.setattr(schema_mod, "connect", lambda: con)
    monkeypatch.setattr(schema_mod, "db_path", lambda: pathlib.Path(":memory:"))

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

    # if LLM were called, this would fail the test
    from laos.chat import console as chat_mod

    def _should_not_call(pid, msg):
        raise AssertionError("LLM should not be called for dropdown action")

    monkeypatch.setattr(chat_mod, "chat", _should_not_call)

    client = TestClient(app)
    r = client.post("/projects/cproj/console/send",
                    data={"message": "revisar relatorio", "action": "/todo"})
    assert r.status_code == 200
    assert "adicionado" in r.text
    row = con.execute(
        "SELECT text FROM todos WHERE project_id='cproj'").fetchone()
    assert row[0] == "revisar relatorio"


def test_todos_sidebar_add_and_delete(tmp_path, monkeypatch):
    """Sidebar: add via POST /todos/add, delete via POST /todos/<id>/delete."""
    from fastapi.testclient import TestClient
    from laos.web.app import app
    from laos.db import schema as schema_mod
    import duckdb

    con = duckdb.connect(":memory:")
    schema_mod.apply_schema(con)
    monkeypatch.setattr(schema_mod, "connect", lambda: con)
    monkeypatch.setattr(schema_mod, "db_path", lambda: pathlib.Path(":memory:"))

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

    client = TestClient(app)
    # add
    r = client.post("/projects/cproj/todos/add", data={"text": "fazer x"})
    assert r.status_code == 200
    assert "fazer x" in r.text
    row = con.execute(
        "SELECT todo_id FROM todos WHERE project_id='cproj'").fetchone()
    tid = row[0]
    # delete
    r2 = client.post(f"/projects/cproj/todos/{tid}/delete")
    assert r2.status_code == 200
    count = con.execute(
        "SELECT COUNT(*) FROM todos WHERE project_id='cproj'").fetchone()[0]
    assert count == 0


def test_planejar_route_updates_todos_panel(tmp_path, monkeypatch):
    """POST /planejar generates ToDos and returns OOB fragments."""
    from fastapi.testclient import TestClient
    from laos.web.app import app
    from laos.db import schema as schema_mod
    import duckdb

    con = duckdb.connect(":memory:")
    schema_mod.apply_schema(con)
    monkeypatch.setattr(schema_mod, "connect", lambda: con)
    monkeypatch.setattr(schema_mod, "db_path", lambda: pathlib.Path(":memory:"))

    from laos.web import portfolio
    from laos.chat import console as chat_mod
    from laos.plan import planner

    root = tmp_path
    (root / "AGENTS.md").write_text("x", encoding="utf-8")
    proj = root / "projects" / "cproj"
    proj.mkdir(parents=True)
    (proj / "project.yaml").write_text(
        "project_name: cproj\nbrief: x\nneeds: []\ndeliverables: []\n",
        encoding="utf-8")
    monkeypatch.setattr(portfolio.needs_mod, "_find_laos_root", lambda: root)
    monkeypatch.setattr(chat_mod, "_laos_root", lambda: root)
    monkeypatch.setattr(planner.needs_mod, "_find_laos_root", lambda: root)

    # stub planner LLM
    fake_analysis = {"modelo_dados": "x", "perguntas_abertas": [],
                     "regras_negocio": [], "riscos": [], "criterios_aceite": []}
    monkeypatch.setattr(planner, "deep_think", lambda d: fake_analysis)
    monkeypatch.setattr(planner, "build_plan", lambda d, a: [
        {"name": "Fase A", "spec": "spec a", "stage": 1},
        {"name": "Fase B", "spec": "spec b", "stage": 2},
    ])

    client = TestClient(app)
    r = client.post("/projects/cproj/planejar")
    assert r.status_code == 200
    # OOB fragments for both thread and todos panel
    assert "hx-swap-oob" in r.text
    assert "plano gerado" in r.text or "PLANO GERADO" in r.text
    # todos persisted
    rows = con.execute(
        "SELECT text, source FROM todos WHERE project_id='cproj'").fetchall()
    assert len(rows) == 2
    assert all(r[1] == "plano" for r in rows)


def test_extract_json_block_plain():
    from laos.plan.planner import _extract_json_block

    out = _extract_json_block('{"a": 1, "b": ["x"]}')
    assert out == {"a": 1, "b": ["x"]}


def test_extract_json_block_fenced():
    from laos.plan.planner import _extract_json_block

    out = _extract_json_block('```json\n{"a": 1}\n```')
    assert out == {"a": 1}


def test_extract_json_block_with_preamble():
    from laos.plan.planner import _extract_json_block

    out = _extract_json_block('Aqui está a análise:\n{"modelo_dados": "x", "riscos": []}')
    assert out["modelo_dados"] == "x"


def test_extract_json_list():
    from laos.plan.planner import _extract_json_block

    out = _extract_json_block('[{"name": "a", "stage": 1}]', want_list=True)
    assert out == [{"name": "a", "stage": 1}]


def test_deep_think_uses_analysis_structure(monkeypatch):
    """deep_think returns the 5 required keys when LLM responds."""
    from laos.plan import planner

    fake = (
        '{"modelo_dados": "entidades", "perguntas_abertas": ["q1"], '
        '"regras_negocio": ["r1"], "riscos": ["risk1"], '
        '"criterios_aceite": ["c1"]}'
    )
    monkeypatch.setattr(planner, "_llm_json", lambda s, p, m: fake)
    data = {"project_name": "x", "brief": "brief", "needs": ["design"],
            "deliverables": []}
    out = planner.deep_think(data)
    assert set(out.keys()) == {"modelo_dados", "perguntas_abertas",
                               "regras_negocio", "riscos", "criterios_aceite"}


def test_deep_think_prompt_contains_mvp_scope_guard():
    """Regressão: análise profunda de pedido grande deve focar no MVP,
    não no sistema inteiro (quebra em fases razoáveis)."""
    from laos.plan import planner
    import inspect

    src = inspect.getsource(planner.deep_think)
    assert "SÓ o MVP" in src or "só o MVP" in src.lower()
    assert "Não despeje o modelo do sistema inteiro" in src


def test_build_plan_prompt_contains_mvp_iteration_rule():
    """Regressão: build_plan deve planejar o MVP iterável (4-6 fases),
    nunca o sistema inteiro de um pedido amplo."""
    from laos.plan import planner
    import inspect

    src = inspect.getsource(planner.build_plan)
    assert "MVP ITERÁVEL" in src
    assert "fora do escopo desta iteração" in src
    assert "fases do MVP" in src


def test_console_system_prompt_contains_scope_rule():
    """Regressão: o console deve conter respostas grandes (esqueleto MVP
    + oferta de aprofundar) em vez de tentar despejar o sistema inteiro."""
    from laos.chat import console
    import inspect

    src = inspect.getsource(console.chat)
    assert "REGRA DE ESCOPO" in src
    assert "ESQUELETO do MVP" in src
    assert "aprofundada sob pedido" in src
    assert "NUNCA tente" in src
