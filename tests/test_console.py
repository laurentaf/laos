"""Console tests: slash commands mutate DB, context builds, chat falls back."""

from __future__ import annotations

import duckdb
import pytest

from laos.chat import console


@pytest.fixture()
def con(monkeypatch):
    c = duckdb.connect(":memory:")
    from laos.db import schema as schema_mod

    schema_mod.apply_schema(c)
    monkeypatch.setattr(schema_mod, "connect", lambda: c)
    monkeypatch.setattr(console.schema, "connect", lambda: c)
    return c


def test_add_todo_via_command(con):
    out = console.run_command("p1", "/todo revisar relatorio")
    assert "adicionado" in out
    row = con.execute(
        "SELECT text, source FROM todos WHERE project_id='p1'").fetchone()
    assert row[0] == "revisar relatorio"
    assert row[1] == "console"


def test_unknown_command_returns_help_hint(con):
    out = console.run_command("p1", "/naoexiste x")
    assert "comando desconhecido" in out
    assert "/help" in out


def test_fases_empty(con):
    assert console.run_command("p1", "/fases") == "sem fases"


def test_status_changes(con):
    console.run_command("p1", "/status planning")
    row = con.execute(
        "SELECT status FROM projects WHERE project_id='p1'").fetchone()
    assert row[0] == "planning"


def test_decidir_adds_pending(con):
    console.run_command("p1", "/decidir subir repos agora?")
    row = con.execute(
        "SELECT status FROM decisions WHERE project_id='p1'").fetchone()
    assert row[0] == "pending"


def test_project_context_includes_status(con):
    con.execute(
        "INSERT INTO projects (project_id, name, status) VALUES ('p1','P1','running')"
    )
    ctx = console.project_context("p1")
    assert "p1" in ctx
    assert "running" in ctx
    assert "## Fases" in ctx


def test_save_and_recent_messages(con):
    console.save_message("p1", "user", "ola")
    console.save_message("p1", "assistant", "oi")
    msgs = console.recent_messages("p1")
    assert len(msgs) == 2
    assert msgs[0]["role"] == "user"
    assert msgs[1]["role"] == "assistant"


def test_handle_routes_slash_vs_llm(con, monkeypatch):
    # slash goes to command
    out = console.handle("p1", "/todo item")
    assert "adicionado" in out
    # non-slash would call LLM; patch chat to avoid network
    monkeypatch.setattr(console, "chat", lambda pid, msg: "LLM_FAKE")
    out2 = console.handle("p1", "o que vem depois?")
    assert out2 == "LLM_FAKE"


def test_chat_uses_moderate_temperature(con, monkeypatch):
    """Temperature back to moderate (0.6) so planning keeps creativity."""
    import json
    import urllib.request

    captured = {}

    class _Resp:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return json.dumps({"choices": [{"message": {"content": "ok"}}]}).encode()

    def _fake_open(req, timeout=120):
        captured["payload"] = json.loads(req.data.decode())
        return _Resp()

    monkeypatch.setattr(urllib.request, "urlopen", _fake_open)
    console.chat("p1", "pergunta criativa")
    assert captured["payload"]["temperature"] == 0.6


def test_planejar_creates_todos(tmp_path, monkeypatch, con):
    """/planejar gera fases e registra cada uma como ToDo (source=plano)."""
    from laos.plan import planner

    root = tmp_path
    (root / "AGENTS.md").write_text("x", encoding="utf-8")
    proj = root / "projects" / "plan-proj"
    proj.mkdir(parents=True)
    (proj / "project.yaml").write_text(
        "project_name: plan-proj\nbrief: app simples\ndeliverables: []\n",
        encoding="utf-8")
    monkeypatch.setattr(console, "_laos_root", lambda: root)
    monkeypatch.setattr(planner.needs_mod, "_find_laos_root", lambda: root)
    # stub LLM: deep_think + build_plan
    fake_analysis = {"modelo_dados": "x", "perguntas_abertas": [],
                     "regras_negocio": [], "riscos": [], "criterios_aceite": []}
    monkeypatch.setattr(planner, "deep_think", lambda d: fake_analysis)
    monkeypatch.setattr(planner, "build_plan", lambda d, a: [
        {"name": "Fase A", "spec": "spec a", "stage": 1},
        {"name": "Fase B", "spec": "spec b", "stage": 2},
    ])
    out = console.run_command("plan-proj", "/planejar")
    assert "PLANO GERADO" in out
    assert "2" in out
    rows = con.execute(
        "SELECT text, source FROM todos WHERE project_id='plan-proj'"
    ).fetchall()
    assert len(rows) == 2
    assert rows[0][1] == "plano"
    assert "Fase A" in rows[0][0]


def test_todo_del_removes_individual(con):
    console.run_command("p1", "/todo primeiro")
    console.run_command("p1", "/todo segundo")
    out = console.run_command("p1", "/todo-del segundo")
    assert "removido" in out
    rows = con.execute(
        "SELECT text FROM todos WHERE project_id='p1'").fetchall()
    assert len(rows) == 1
    assert rows[0][0] == "primeiro"


def test_todos_lists(con):
    console.run_command("p1", "/todo um")
    console.run_command("p1", "/todo dois")
    out = console.run_command("p1", "/todos")
    assert "um" in out
    assert "dois" in out


def test_chat_cache_returns_same_answer_twice(con):
    """Consistency: same prompt -> same answer, no second LLM call."""
    import json
    import urllib.request

    calls = {"n": 0}

    class _Resp:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            calls["n"] += 1
            body = json.dumps({
                "choices": [{"message": {"content": "RESPOSTA_ESTAVEL"}}]
            })
            return body.encode()

    def _fake_open(req, timeout=120):
        return _Resp()

    orig = urllib.request.urlopen
    urllib.request.urlopen = _fake_open
    try:
        # first call: user saved by route, then handle() -> LLM
        console.save_message("p1", "user", "mesma pergunta")
        r1 = console.handle("p1", "mesma pergunta")
        console.save_message("p1", "assistant", r1)
        # second identical prompt: should hit cache, NOT call LLM again
        console.save_message("p1", "user", "mesma pergunta")
        r2 = console.handle("p1", "mesma pergunta")
        console.save_message("p1", "assistant", r2)
        assert r1 == "RESPOSTA_ESTAVEL"
        assert r2 == "RESPOSTA_ESTAVEL"
        assert r1 == r2
        assert calls["n"] == 1  # LLM called only once
    finally:
        urllib.request.urlopen = orig
