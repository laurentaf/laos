"""Schema tests: 9 tables, idempotent migration, verify round-trip."""

from __future__ import annotations

import duckdb

from laos.db import schema


def test_schema_has_10_tables():
    assert len(schema.TABLES) == 10
    assert schema.EXPECTED_TABLES == {
        "projects", "phases", "todos", "checklist_items", "decisions",
        "deliverables", "capability_gaps", "runs", "steps", "chat_messages",
    }


def test_apply_schema_creates_all():
    con = duckdb.connect(":memory:")
    applied = schema.apply_schema(con)
    assert len(applied) == 10
    missing, present = schema.verify_schema(con)
    assert missing == []
    assert len(present) == 10


def test_apply_schema_idempotent():
    con = duckdb.connect(":memory:")
    schema.apply_schema(con)
    applied_again = schema.apply_schema(con)  # no error, no duplicates
    assert len(applied_again) == 10
    missing, _ = schema.verify_schema(con)
    assert missing == []


def test_runs_table_insert_select():
    con = duckdb.connect(":memory:")
    schema.apply_schema(con)
    con.execute(
        "INSERT INTO runs (run_id, project_id, status) VALUES ('r1','p1','running')"
    )
    row = con.execute("SELECT status FROM runs WHERE run_id='r1'").fetchone()
    assert row[0] == "running"


def test_projects_table_insert_select():
    con = duckdb.connect(":memory:")
    schema.apply_schema(con)
    con.execute(
        "INSERT INTO projects (project_id, name, status) VALUES ('p1','P1','not_started')"
    )
    row = con.execute("SELECT status FROM projects WHERE project_id='p1'").fetchone()
    assert row[0] == "not_started"
