"""CLI + needs resolution tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from laos import cli
from laos.core import needs


@pytest.fixture()
def laos_root() -> Path:
    """LAOS root is the repo root (AGENTS.md + projects/ present)."""
    return needs._find_laos_root()


def test_doctor_ok(laos_root: Path, monkeypatch):
    monkeypatch.setenv("LAOS_DB_PATH", ":memory:")
    assert cli.cmd_doctor(None) == 0  # type: ignore[arg-type]


def test_projects_lists_contracts(laos_root: Path, monkeypatch, capsys):
    monkeypatch.setenv("LAOS_DB_PATH", ":memory:")
    cli.cmd_projects(None)  # type: ignore[arg-type]
    out = capsys.readouterr().out
    assert "project" in out


def test_resolve_needs_happy(laos_root: Path):
    result = needs.resolve_needs(["data", "dashboard"], laos_root)
    assert result["data"]["primary"] == ["latade"]
    assert result["dashboard"]["primary"] == ["ladesign"]


def test_resolve_needs_missing_fails(laos_root: Path):
    with pytest.raises(KeyError):
        needs.resolve_needs(["not-a-real-need"], laos_root)


def test_primary_capabilities_dedup(laos_root: Path):
    caps = needs.primary_capabilities_for(
        ["data", "etl", "dashboard"], laos_root
    )
    assert "latade" in caps
    assert "ladesign" in caps
    # dedup: latade appears for both data and etl, must appear once
    assert caps.count("latade") == 1
