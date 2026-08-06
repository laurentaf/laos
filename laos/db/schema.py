"""LAOS durable state schema (DuckDB).

Covers the 9 tables from the Nota-10 plan:

  projects        portfolio overview (the "Trello board" data)
  phases          per-project phases with cost/tokens/errors
  todos           checklist + ToDos per project
  checklist_items padroes-entrega checklist per project
  decisions       pending decisions (user questions to answer)
  deliverables    verification results per deliverable (the "guaranteed check")
  capability_gaps capabilities a project needs but LAOS lacks
  runs            run-level observability (auto-resume state)
  steps           step-level observability

Migration strategy: idempotent CREATE TABLE IF NOT EXISTS, applied via
`apply_schema()`. DuckDB in-memory by default; persisted via LAOS_DB_PATH
env or default path under .laos/.
"""

from __future__ import annotations

import os
from pathlib import Path

import duckdb

# ─── table definitions ───────────────────────────────────────────────

TABLES: dict[str, str] = {
    "projects": """
        CREATE TABLE IF NOT EXISTS projects (
            project_id     VARCHAR PRIMARY KEY,
            name           VARCHAR NOT NULL,
            brief          VARCHAR,
            status         VARCHAR NOT NULL DEFAULT 'not_started',
            created_at     TIMESTAMP DEFAULT current_timestamp,
            last_run_id    VARCHAR,
            ready_to_ship  BOOLEAN DEFAULT FALSE,
            repo_url       VARCHAR
        )
    """,
    "phases": """
        CREATE TABLE IF NOT EXISTS phases (
            project_id  VARCHAR,
            phase       INTEGER,
            name        VARCHAR,
            status      VARCHAR DEFAULT 'pending',
            started_at  TIMESTAMP,
            ended_at    TIMESTAMP,
            cost_usd    DOUBLE DEFAULT 0.0,
            tokens      BIGINT DEFAULT 0,
            errors      INTEGER DEFAULT 0,
            retries     INTEGER DEFAULT 0,
            PRIMARY KEY (project_id, phase)
        )
    """,
    "todos": """
        CREATE TABLE IF NOT EXISTS todos (
            project_id VARCHAR,
            todo_id    VARCHAR,
            text       VARCHAR,
            done       BOOLEAN DEFAULT FALSE,
            source     VARCHAR DEFAULT 'manual',
            PRIMARY KEY (project_id, todo_id)
        )
    """,
    "checklist_items": """
        CREATE TABLE IF NOT EXISTS checklist_items (
            project_id VARCHAR,
            item_id    VARCHAR,
            item       VARCHAR,
            item_type  VARCHAR DEFAULT 'P0',
            done       BOOLEAN DEFAULT FALSE,
            PRIMARY KEY (project_id, item_id)
        )
    """,
    "decisions": """
        CREATE TABLE IF NOT EXISTS decisions (
            project_id    VARCHAR,
            decision_id   VARCHAR,
            question      VARCHAR,
            cluster_id    VARCHAR,
            status        VARCHAR DEFAULT 'pending',
            asked_at      TIMESTAMP DEFAULT current_timestamp,
            decided_at    TIMESTAMP,
            decided_value VARCHAR,
            PRIMARY KEY (project_id, decision_id)
        )
    """,
    "deliverables": """
        CREATE TABLE IF NOT EXISTS deliverables (
            project_id  VARCHAR,
            name        VARCHAR,
            exists_     BOOLEAN DEFAULT FALSE,
            imports_    BOOLEAN DEFAULT FALSE,
            passes_test BOOLEAN DEFAULT FALSE,
            spec_match  BOOLEAN DEFAULT FALSE,
            verified_at TIMESTAMP,
            PRIMARY KEY (project_id, name)
        )
    """,
    "capability_gaps": """
        CREATE TABLE IF NOT EXISTS capability_gaps (
            project_id         VARCHAR,
            need               VARCHAR,
            missing_capability VARCHAR,
            ttl_cycles         INTEGER DEFAULT 2,
            PRIMARY KEY (project_id, need)
        )
    """,
    "chat_messages": """
        CREATE TABLE IF NOT EXISTS chat_messages (
            project_id VARCHAR,
            msg_id     VARCHAR,
            role       VARCHAR,          -- user | assistant | system
            content    VARCHAR,
            ts         TIMESTAMP DEFAULT current_timestamp,
            PRIMARY KEY (project_id, msg_id)
        )
    """,
    "runs": """
        CREATE TABLE IF NOT EXISTS runs (
            run_id       VARCHAR PRIMARY KEY,
            project_id   VARCHAR NOT NULL,
            started_at   TIMESTAMP DEFAULT current_timestamp,
            ended_at     TIMESTAMP,
            status       VARCHAR DEFAULT 'running',  -- running | completed | failed | paused
            cost_usd     DOUBLE DEFAULT 0.0,
            tokens       BIGINT DEFAULT 0,
            duration_s   DOUBLE,
            errors       INTEGER DEFAULT 0,
            retries      INTEGER DEFAULT 0
        )
    """,
    "steps": """
        CREATE TABLE IF NOT EXISTS steps (
            run_id      VARCHAR,
            step_id     VARCHAR,
            ts          TIMESTAMP DEFAULT current_timestamp,
            step_type   VARCHAR,
            agent       VARCHAR,
            status      VARCHAR DEFAULT 'running',
            duration_s  DOUBLE,
            error_class VARCHAR,
            tool        VARCHAR,
            PRIMARY KEY (run_id, step_id)
        )
    """,
}

EXPECTED_TABLES = set(TABLES.keys())


def _all_tables() -> list[str]:
    return sorted(TABLES.keys())


def db_path() -> Path:
    """Resolve the DuckDB path: LAOS_DB_PATH env or .laos/laos.duckdb."""
    env = os.environ.get("LAOS_DB_PATH")
    if env:
        return Path(env)
    root = Path(__file__).resolve().parent.parent.parent
    return root / ".laos" / "laos.duckdb"


def connect() -> duckdb.DuckDBPyConnection:
    """Open a DuckDB connection, applying schema idempotently."""
    path = db_path()
    if str(path) != ":memory:":
        path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(path))
    apply_schema(con)
    _track_write(con)
    return con


# ─── write-connection registry ─────────────────────────────────────────
# DuckDB is single-process-writer: while the server holds ANY open write
# connection, a run subprocess (separate process) can't open the file.
# We track every write connection so /run can close them all before
# launching the subprocess. Reads use connect_readonly (no registry).

_open_writes: set[duckdb.DuckDBPyConnection] = set()


def _track_write(con: duckdb.DuckDBPyConnection) -> None:
    try:
        _open_writes.add(con)
    except Exception:  # noqa: BLE001
        pass


def close_all_writes() -> int:
    """Close every tracked write connection. Returns count closed.

    Call BEFORE launching a run subprocess so it can open the file.
    Idempotent; untracked connections (test mocks) are untouched.
    """
    n = 0
    for con in list(_open_writes):
        try:
            con.close()
            n += 1
        except Exception:  # noqa: BLE001
            pass
        _open_writes.discard(con)
    return n


def connect_readonly() -> duckdb.DuckDBPyConnection:
    """Open a read-only DuckDB connection (no writer lock).

    The panel and other readers use this so they don't collide with the
    writer (pipeline). Reads never need the write lock.
    """
    path = db_path()
    if str(path) == ":memory:":
        return connect()
    if not path.exists():
        return connect()  # first run: create it
    try:
        return duckdb.connect(str(path), read_only=True)
    except Exception:  # noqa: BLE001
        return connect()


def apply_schema(con: duckdb.DuckDBPyConnection) -> list[str]:
    """Apply all tables idempotently. Returns names of applied tables."""
    applied: list[str] = []
    for name, ddl in TABLES.items():
        con.execute(ddl)
        applied.append(name)
    return applied


def verify_schema(con: duckdb.DuckDBPyConnection) -> tuple[list[str], list[str]]:
    """Return (missing_tables, present_tables). Empty missing = PASS."""
    present_rows = con.execute("SHOW TABLES").fetchall()
    present = {r[0] for r in present_rows}
    missing = sorted(EXPECTED_TABLES - present)
    return missing, sorted(present)
