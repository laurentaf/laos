"""Tests for lacouncil.core.duckdb_store.resolve_db_path().

Validates the path resolution cascade after LACOUNCIL 0a539dd6:
- Default (no env, no arg) -> repo root memoria (parents[3]).
- Env var override takes precedence.
- Explicit db_path arg wins over both.

Regression test for the 2-DB-divergence bug.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from lacouncil.core.duckdb_store import resolve_db_path


def test_default_path_resolves_to_repo_root_memoria():
    """No env var, no arg: path must end with <repo>/memoria/lacouncil.duckdb.
    parents[3] of duckdb_store.py = lacouncil/ (repo root).
    Expected: lacouncil/memoria/lacouncil.duckdb.
    """
    saved = os.environ.pop("LACOUNCIL_DB_PATH", None)
    try:
        result = resolve_db_path()
    finally:
        if saved is not None:
            os.environ["LACOUNCIL_DB_PATH"] = saved

    result_path = Path(result)
    assert result_path.name == "lacouncil.duckdb"
    parts = result_path.parts
    assert "memoria" in parts, f"path must contain 'memoria', got {parts}"
    assert "src" not in parts, f"path must NOT be under src/ (legacy bug), got {parts}"
    assert parts[-3:] == ("lacouncil", "memoria", "lacouncil.duckdb")


def test_env_var_override_takes_precedence(monkeypatch, tmp_path):
    """When LACOUNCIL_DB_PATH is set, resolve_db_path() returns it."""
    custom_db = tmp_path / "custom" / "lacouncil.duckdb"
    monkeypatch.setenv("LACOUNCIL_DB_PATH", str(custom_db))
    assert resolve_db_path() == str(custom_db)


def test_explicit_db_path_arg_wins(monkeypatch, tmp_path):
    """Explicit db_path arg beats both default and env var."""
    monkeypatch.setenv("LACOUNCIL_DB_PATH", str(tmp_path / "env" / "ignored.duckdb"))
    explicit = tmp_path / "explicit" / "winner.duckdb"
    assert resolve_db_path(db_path=str(explicit)) == str(explicit)


def test_connect_uses_resolved_path(monkeypatch, tmp_path):
    """Smoke test: connect() opens DuckDB at resolved path, writes/reads back."""
    from lacouncil.core.duckdb_store import connect

    custom_db = tmp_path / "connect_smoke" / "lacouncil.duckdb"
    monkeypatch.setenv("LACOUNCIL_DB_PATH", str(custom_db))

    con = connect()
    try:
        con.execute("CREATE TABLE IF NOT EXISTS smoke (x INTEGER)")
        con.execute("INSERT INTO smoke VALUES (42)")
        row = con.execute("SELECT x FROM smoke").fetchone()
        assert row[0] == 42
    finally:
        con.close()
