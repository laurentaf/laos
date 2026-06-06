#!/usr/bin/env python3
"""Idempotent migration: add `wdl_signatures` table to LACOUNCIL DuckDB.

Adds the table backing the WDL v1 contract's signing surface
(`workflows/wdl-contract.yaml` §signing.lts_table).

Per Conselho vote on proposal a4fe9faa (WDL v1): "Signatures stored
in LACOUNCIL DuckDB table `wdl_signatures` (columns: `plan_id, sha256,
contract_version, planner_id, signed_at, verified_by`)."

Schema is idempotent: re-running the migration on a DB that already
has the table is a no-op (CREATE TABLE IF NOT EXISTS). The script
prints a one-line summary of the table's row count + schema so a
human or the preflight `wdl-gate` can confirm migration succeeded.

Usage:
  uv run python scripts/migrate_lacouncil_wdl_signatures.py
  uv run python scripts/migrate_lacouncil_wdl_signatures.py --db-path <custom>

Exit codes:
  0  — migration applied OR table already exists
  1  — migration error (DB unreachable, schema conflict, etc.)
  2  — usage error
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


# Default DB path matches the env var LACOUNCIL_DB_PATH wired into
# .opencode/opencode.jsonc. The DB lives in the lacouncil repo (sibling
# of LAOS), NOT in LAOS itself. Per R1-R5: capability-architect does
# not own the lacouncil repo, so this script is the LAOS-side
# declaration of the schema; the lacouncil repo applies the same
# DDL on its own side via the lacouncil MCP.
DEFAULT_DB_PATH = "../lacouncil/memoria/lacouncil.duckdb"

# Schema. Matches the column set in WDL proposal a4fe9faa §"Output
# (3 signed files)" and wdl-contract.yaml §"signing.lts_columns".
SCHEMA_DDL = """
CREATE TABLE IF NOT EXISTS wdl_signatures (
    plan_id           VARCHAR PRIMARY KEY,
    sha256            VARCHAR NOT NULL,
    contract_version  VARCHAR NOT NULL,
    planner_id        VARCHAR NOT NULL,
    signed_at         TIMESTAMP NOT NULL DEFAULT now(),
    verified_by       VARCHAR NOT NULL
);
"""

# Indexes for the typical access patterns:
#   - lookup by plan_id (PRIMARY KEY covers it)
#   - audit by verified_by (delivery-reviewer self-verifies today;
#     future cross-validators may include orchestrator, capability-architect)
#   - audit by signed_at for "most recent N plans"
SCHEMA_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_wdl_signer ON wdl_signatures(verified_by);",
    "CREATE INDEX IF NOT EXISTS idx_wdl_signed_at ON wdl_signatures(signed_at);",
]


def run_migration(db_path: Path) -> tuple[int, str]:
    """Apply the migration. Returns (exit_code, summary)."""
    if not db_path.exists():
        return 1, f"DB_PATH_MISSING: {db_path} (does the lacouncil repo exist?)"

    # Import duckdb locally so the script is importable in environments
    # where duckdb is not on sys.path. The laecon venv has duckdb, so
    # `uv run python ...` from the LAOS root (with its own venv that
    # does not have duckdb) would fail; the operator should run from
    # ../lacouncil or with a venv that has duckdb installed.
    try:
        import duckdb  # type: ignore
    except ImportError:
        return 1, (
            "DUCKDB_NOT_AVAILABLE: this script requires duckdb. "
            "Run from ../lacouncil (which has duckdb in its venv) "
            "or install duckdb in the calling venv. "
            "Ex: ..\\lacouncil\\.venv\\Scripts\\python scripts/migrate_lacouncil_wdl_signatures.py"
        )

    try:
        con = duckdb.connect(str(db_path))
    except Exception as e:
        return 1, f"DB_CONNECT_FAILED: {db_path} ({type(e).__name__}: {e})"

    try:
        # CREATE TABLE IF NOT EXISTS + CREATE INDEX IF NOT EXISTS are
        # idempotent in DuckDB. Re-running the migration is safe.
        for stmt in [SCHEMA_DDL, *SCHEMA_INDEXES]:
            con.execute(stmt)

        # Confirm shape. If the table pre-existed with a different
        # schema, this would catch it.
        cols = con.execute("DESCRIBE wdl_signatures").fetchall()
        col_names = [c[0] for c in cols]
        expected = ["plan_id", "sha256", "contract_version",
                    "planner_id", "signed_at", "verified_by"]
        missing = [c for c in expected if c not in col_names]
        if missing:
            return 1, f"SCHEMA_MISMATCH: missing columns {missing} (have: {col_names})"

        row_count = con.execute("SELECT COUNT(*) FROM wdl_signatures").fetchone()[0]
        summary = (
            f"OK: wdl_signatures migration applied. "
            f"db={db_path} cols={col_names} rows={row_count}"
        )
        return 0, summary
    except Exception as e:
        return 1, f"MIGRATION_FAILED: {type(e).__name__}: {e}"
    finally:
        try:
            con.close()
        except Exception:
            pass


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Idempotent DuckDB migration: add wdl_signatures table to LACOUNCIL DB."
    )
    p.add_argument(
        "--db-path",
        type=Path,
        default=Path(DEFAULT_DB_PATH),
        help=f"Path to lacouncil.duckdb (default: {DEFAULT_DB_PATH})",
    )
    args = p.parse_args(argv)

    code, summary = run_migration(args.db_path)
    print(summary)
    return code


if __name__ == "__main__":
    sys.exit(main())
