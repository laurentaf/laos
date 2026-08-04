"""Merge two LACOUNCIL DuckDBs (local + remote) into a single canonical DB.

PK strategy:
  - UUID PKs (propostas, votos, sessoes_investigacao, wdl_signatures,
    user_questions): dedup by PK, most-recent timestamp wins.
  - SEQUENCE PKs (projetos_registrados, verbetes_conhecimento):
    remap remote IDs to fresh local SEQUENCE values to avoid collision.

Idempotent: running twice with same inputs produces same output.
"""
import argparse, json, sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import duckdb


# ── Schema source of truth ─────────────────────────────────────
# PK column and timestamp column per table (mirrors duckdb_store.py)
TABLES: dict[str, tuple[str, str]] = {
    "propostas":             ("proposal_id", "created_at"),
    "votos":                 ("vote_id",     "cast_at"),
    "sessoes_investigacao":  ("session_id",  "created_at"),
    "wdl_signatures":        ("pre_flight_id", "recorded_at"),
    "user_questions":        ("question_id", "asked_at"),
    # Sequence-backed — special handling needed
    "projetos_registrados":  ("project_id",  "recorded_at"),
    "verbetes_conhecimento": ("verbete_id",  "recorded_at"),
}

SEQUENCE_TABLES = {"projetos_registrados", "verbetes_conhecimento"}


def get_existing_pks(con: duckdb.DuckDBPyConnection, table: str, pk: str) -> set:
    """Return set of existing PK values in a table."""
    try:
        rows = con.execute(f"SELECT {pk} FROM {table}").fetchall()
        return {r[0] for r in rows}
    except Exception:
        return set()


def merge_uuid_table(
    out: duckdb.DuckDBPyConnection,
    local: duckdb.DuckDBPyConnection,
    remote: duckdb.DuckDBPyConnection,
    table: str, pk: str, ts_col: str,
    dry_run: bool = False,
) -> dict:
    """Merge a UUID-PK table: union + dedup by most-recent timestamp."""
    local_rows = local.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    remote_rows = remote.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    if dry_run:
        return {"table": table, "strategy": "uuid_dedup",
                "local": local_rows, "remote": remote_rows, "conflicts": None}

    # Get remote column list
    cols = [d[0] for d in remote.description]

    # Get existing PKs in output
    existing = get_existing_pks(out, table, pk) if local_rows > 0 else set()

    # Insert remote rows, skip if PK exists and is older
    inserted = 0
    skipped = 0
    remote.execute(f"SELECT * FROM {table}")
    for row in remote.fetchall():
        row_dict = dict(zip(cols, row))
        row_pk = row_dict[pk]

        if row_pk in existing:
            # Compare timestamps
            local_ts = out.execute(
                f"SELECT {ts_col} FROM {table} WHERE {pk} = ?", (row_pk,)
            ).fetchone()[0]
            remote_ts = row_dict[ts_col]
            if remote_ts > local_ts:
                # Remote is newer — replace
                out.execute(f"DELETE FROM {table} WHERE {pk} = ?", (row_pk,))
                out.execute(f"INSERT INTO {table} VALUES ({','.join(['?'] * len(cols))})", row)
                skipped += 1
            else:
                # Local is newer — skip
                skipped += 1
        else:
            out.execute(f"INSERT INTO {table} VALUES ({','.join(['?'] * len(cols))})", row)
            inserted += 1
        existing.add(row_pk)

    return {"table": table, "strategy": "uuid_dedup",
            "local": local_rows, "remote": remote_rows,
            "inserted": inserted, "skipped_conflicts": skipped}


def merge_sequence_table(
    out: duckdb.DuckDBPyConnection,
    local: duckdb.DuckDBPyConnection,
    remote: duckdb.DuckDBPyConnection,
    table: str, pk: str, ts_col: str,
    dry_run: bool = False,
) -> dict:
    """Merge a SEQUENCE-PK table: remap remote IDs to new local SEQUENCE."""
    local_rows = local.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    remote_rows = remote.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    if dry_run:
        return {"table": table, "strategy": "sequence_remap",
                "local": local_rows, "remote": remote_rows,
                "remap_needed": remote_rows}

    cols = [d[0] for d in remote.description]
    existing = get_existing_pks(out, table, pk) if local_rows > 0 else set()

    # Get max existing ID
    max_id = out.execute(f"SELECT COALESCE(MAX({pk}), 0) FROM {table}").fetchone()[0]

    inserted = 0
    skipped = 0

    remote.execute(f"SELECT * FROM {table}")
    for row in remote.fetchall():
        row_dict = dict(zip(cols, row))
        old_pk = row_dict[pk]

        if old_pk in existing:
            # Conflict: compare timestamps
            local_ts = out.execute(
                f"SELECT {ts_col} FROM {table} WHERE {pk} = ?", (old_pk,)
            ).fetchone()[0]
            remote_ts = row_dict[ts_col]
            if remote_ts > local_ts:
                out.execute(f"DELETE FROM {table} WHERE {pk} = ?", (old_pk,))
                new_pk = max_id + 1
                max_id = new_pk
                new_row = [new_pk if c == pk else v for c, v in zip(cols, row)]
                out.execute(
                    f"INSERT INTO {table} VALUES ({','.join(['?'] * len(cols))})",
                    new_row
                )
                skipped += 1
            else:
                skipped += 1
        else:
            new_pk = max_id + 1
            max_id = new_pk
            new_row = [new_pk if c == pk else v for c, v in zip(cols, row)]
            out.execute(
                f"INSERT INTO {table} VALUES ({','.join(['?'] * len(cols))})",
                new_row
            )
            inserted += 1

    return {"table": table, "strategy": "sequence_remap",
            "local": local_rows, "remote": remote_rows,
            "inserted": inserted, "skipped_conflicts": skipped}


def main():
    parser = argparse.ArgumentParser(description="Merge two LACOUNCIL DuckDBs")
    parser.add_argument("--local", required=True, help="Local DuckDB path")
    parser.add_argument("--remote", required=True, help="Remote DuckDB path (PULL from)")
    parser.add_argument("--output", required=True, help="Output DuckDB path")
    parser.add_argument("--audit-log", default=None, help="Append-only audit log path")
    parser.add_argument("--dry-run", action="store_true", help="Rehearse without writing")
    args = parser.parse_args()

    local_path = Path(args.local)
    remote_path = Path(args.remote)
    out_path = Path(args.output)

    # Validate inputs
    if not local_path.exists() and not args.dry_run:
        print(f"Local DB {local_path} nao existe. Criando vazio...", file=sys.stderr)
        duckdb.connect(str(out_path)).close()
        # Still need to copy remote into output
        import shutil
        if remote_path.exists():
            shutil.copy2(str(remote_path), str(out_path))
        print("merge: output = remote (local estava vazio)")
        return

    if not remote_path.exists():
        print("Remote DB nao existe. Nada a mergear.", file=sys.stderr)
        return

    # Open connections
    local = duckdb.connect(str(local_path), read_only=True)
    remote = duckdb.connect(str(remote_path), read_only=True)

    if args.dry_run:
        out = None
    else:
        # Start from local's state
        import shutil
        shutil.copy2(str(local_path), str(out_path))
        out = duckdb.connect(str(out_path))

    print(f"Merge: local={local_path.name} + remote={remote_path.name} -> {out_path.name}")
    results = []

    for table, (pk, ts_col) in TABLES.items():
        try:
            if table in SEQUENCE_TABLES:
                result = merge_sequence_table(
                    out, local, remote, table, pk, ts_col,
                    dry_run=args.dry_run
                )
            else:
                result = merge_uuid_table(
                    out, local, remote, table, pk, ts_col,
                    dry_run=args.dry_run
                )
            results.append(result)
            if result.get("inserted", 0) > 0 or result.get("skipped_conflicts", 0) > 0:
                print(f"  {table}: +{result.get('inserted',0)} inserted, "
                      f"{result.get('skipped_conflicts',0)} skipped/conflicts")
            else:
                print(f"  {table}: unchanged")
        except Exception as e:
            print(f"  {table}: ERRO - {e}", file=sys.stderr)
            results.append({"table": table, "error": str(e)})

    local.close()
    remote.close()
    if out:
        out.close()

    # Audit
    if args.audit_log:
        audit_path = Path(args.audit_log)
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "ts": datetime.now().isoformat(),
            "event": "merge_complete",
            "data": {
                "local": str(local_path),
                "remote": str(remote_path),
                "output": str(out_path),
                "results": results,
                "dry_run": args.dry_run,
            }
        }
        with open(audit_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    # Summary
    total_inserted = sum(r.get("inserted", 0) for r in results)
    total_skipped = sum(r.get("skipped_conflicts", 0) for r in results)
    print(f"\nResumo: {total_inserted} registros inseridos, {total_skipped} conflitos resolvidos")

    if args.dry_run:
        print("(dry-run — nada foi escrito)")


if __name__ == "__main__":
    main()
