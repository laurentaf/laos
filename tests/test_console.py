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
