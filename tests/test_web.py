"""P3: portfolio board — FastAPI routes smoke tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from laos.db import schema
from laos.web.app import app


client = TestClient(app)


def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_board_renders():
    r = client.get("/")
    assert r.status_code == 200
    body = r.text
    assert "LAOS Control Plane" in body
    assert "Novo projeto" in body


def test_board_has_project_columns():
    r = client.get("/")
    assert "Não iniciado" in r.text
    assert "Planejando" in r.text
    assert "Rodando" in r.text
    assert "Aguardando decisão" in r.text
    assert "Pronto para shipar" in r.text


def test_project_detail_renders():
    # any existing project.yaml contract
    from laos.web import portfolio

    projects = portfolio.list_projects()
    assert projects, "no projects found to test detail"
    r = client.get(f"/projects/{projects[0]['name']}")
    assert r.status_code == 200
    assert "Brief" in r.text


def test_new_project_redirects(tmp_path, monkeypatch):
    from laos.web import portfolio

    root = tmp_path
    (root / "AGENTS.md").write_text("x", encoding="utf-8")
    (root / "projects").mkdir()
    monkeypatch.setattr(portfolio.needs_mod, "_find_laos_root", lambda: root)

    r = client.post("/projects/new", data={"project_name": "test-board-proj"},
                    follow_redirects=False)
    assert r.status_code in (303, 302)
    created = root / "projects" / "test-board-proj" / "project.yaml"
    assert created.exists()


def test_set_status_updates_db(tmp_path, monkeypatch):
    import duckdb

    from laos.web import portfolio
    from laos.db import schema as schema_mod

    root = tmp_path
    (root / "AGENTS.md").write_text("x", encoding="utf-8")
    (root / "projects").mkdir()
    monkeypatch.setattr(portfolio.needs_mod, "_find_laos_root", lambda: root)

    con = duckdb.connect(":memory:")
    schema_mod.apply_schema(con)
    monkeypatch.setattr(schema_mod, "connect", lambda: con)
    monkeypatch.setattr(schema, "connect", lambda: con)
    con.execute(
        "INSERT INTO projects (project_id, name, status) VALUES ('test-board-proj','x','not_started')"
    )
    r = client.post("/projects/test-board-proj/status",
                    data={"status": "running"}, follow_redirects=False)
    assert r.status_code in (303, 302)
    row = con.execute(
        "SELECT status FROM projects WHERE project_id='test-board-proj'"
    ).fetchone()
    assert row[0] == "running"


def test_decide_decision_updates_db(tmp_path, monkeypatch):
    import duckdb

    from laos.web import portfolio
    from laos.db import schema as schema_mod

    root = tmp_path
    (root / "AGENTS.md").write_text("x", encoding="utf-8")
    (root / "projects").mkdir()
    monkeypatch.setattr(portfolio.needs_mod, "_find_laos_root", lambda: root)

    con = duckdb.connect(":memory:")
    schema_mod.apply_schema(con)
    monkeypatch.setattr(schema_mod, "connect", lambda: con)
    monkeypatch.setattr(schema, "connect", lambda: con)
    con.execute(
        "INSERT INTO decisions (project_id, decision_id, question, cluster_id, status) "
        "VALUES ('test-board-proj','d1','seguir?','generic','pending')"
    )
    r = client.post("/projects/test-board-proj/decisions/d1/decide",
                    data={"decided_value": "y"}, follow_redirects=False)
    assert r.status_code in (303, 302)
    row = con.execute(
        "SELECT status, decided_value FROM decisions WHERE decision_id='d1'"
    ).fetchone()
    assert row[0] == "decided"
    assert row[1] == "y"


def test_toggle_todo_updates_db(tmp_path, monkeypatch):
    import duckdb

    from laos.web import portfolio
    from laos.db import schema as schema_mod

    root = tmp_path
    (root / "AGENTS.md").write_text("x", encoding="utf-8")
    (root / "projects").mkdir()
    monkeypatch.setattr(portfolio.needs_mod, "_find_laos_root", lambda: root)

    con = duckdb.connect(":memory:")
    schema_mod.apply_schema(con)
    monkeypatch.setattr(schema_mod, "connect", lambda: con)
    monkeypatch.setattr(schema, "connect", lambda: con)
    con.execute(
        "INSERT INTO todos (project_id, todo_id, text, done) "
        "VALUES ('test-board-proj','t1','fazer algo', false)"
    )
    r = client.post("/projects/test-board-proj/todos/t1/toggle",
                    follow_redirects=False)
    assert r.status_code in (303, 302)
    row = con.execute(
        "SELECT done FROM todos WHERE todo_id='t1'"
    ).fetchone()
    assert row[0] is True


def test_project_action_verify_returns_html(tmp_path, monkeypatch):
    """verify action streams output back on the page."""
    from laos.web import portfolio

    root = tmp_path
    (root / "AGENTS.md").write_text("x", encoding="utf-8")
    proj = root / "projects" / "vproj"
    proj.mkdir(parents=True)
    (proj / "project.yaml").write_text(
        "project_name: vproj\n"
        "deliverables:\n"
        "  - name: good-sql\n    label: Modelo\n    stage: 1\n"
        "    artifacts: [artifacts/data/schema-gold.sql]\n",
        encoding="utf-8",
    )
    (proj / "artifacts/data/schema-gold.sql").parent.mkdir(parents=True)
    (proj / "artifacts/data/schema-gold.sql").write_text(
        "CREATE TABLE gold AS SELECT 1;", encoding="utf-8")
    monkeypatch.setattr(portfolio.needs_mod, "_find_laos_root", lambda: root)
    import laos.verify.engine as eng

    monkeypatch.setattr(eng.schema, "connect", schema.connect)

    r = client.post("/projects/vproj/actions", data={"action": "verify"})
    assert r.status_code == 200
    assert "VERIFY" in r.text or "deliverable" in r.text or "OK" in r.text


def test_dashboard_renders(tmp_path, monkeypatch):
    """Executive dashboard: KPIs + attention + health."""
    from laos.web import portfolio

    root = tmp_path
    (root / "AGENTS.md").write_text("x", encoding="utf-8")
    proj = root / "projects" / "vproj"
    proj.mkdir(parents=True)
    (proj / "project.yaml").write_text(
        "project_name: vproj\nneeds: [data]\ndeliverables: []\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(portfolio.needs_mod, "_find_laos_root", lambda: root)

    r = client.get("/dashboard")
    assert r.status_code == 200
    assert "Dashboard executivo" in r.text
    assert "custo acumulado" in r.text
