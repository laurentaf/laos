"""Check DuckDBs and test merge idempotency."""
import shutil, subprocess
from pathlib import Path

ROOT = Path(r"F:\projects\Laos")
CANONICAL = ROOT / "lacouncil" / "memoria" / "lacouncil.duckdb"
MERGE = ROOT / "scripts" / "sync" / "merge_duckdb.py"

# 1. Check canonical DB
if not CANONICAL.exists():
    print("ERRO: Canonical DuckDB nao encontrado")
    exit(1)

sz = CANONICAL.stat().st_size
print(f"Canonical: {sz:,} bytes")

# 2. List tables via duckdb
import duckdb
con = duckdb.connect(str(CANONICAL), read_only=True)
tables = con.execute(
    "SELECT table_name FROM information_schema.tables WHERE table_schema='main'"
).fetchall()
for t in tables:
    cnt = con.execute(f"SELECT COUNT(*) FROM {t[0]}").fetchone()[0]
    print(f"  {t[0]}: {cnt} rows")
con.close()

# 3. Test merge: copy DB, merge copy with original
test1 = CANONICAL.parent / "lacouncil.TEST_COPY.duckdb"
shutil.copy2(str(CANONICAL), str(test1))
audit = ROOT / "memoria" / "audit" / "test-merge.jsonl"

r = subprocess.run(
    ["uv", "run", "python", str(MERGE),
     "--local", str(CANONICAL),
     "--remote", str(test1),
     "--output", str(test1),
     "--audit-log", str(audit)],
    capture_output=True, text=True, cwd=str(ROOT)
)
print(f"\nMerge exit={r.returncode}")
for line in r.stdout.strip().split("\n")[-8:]:
    print(f"  {line}")
test1.unlink(missing_ok=True)
print("Teste completo.")
