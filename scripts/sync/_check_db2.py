"""Check merge error details."""
import shutil, subprocess
from pathlib import Path

ROOT = Path(r"F:\projects\Laos")
CANONICAL = ROOT / "lacouncil" / "memoria" / "lacouncil.duckdb"
MERGE = ROOT / "scripts" / "sync" / "merge_duckdb.py"

test1 = CANONICAL.parent / "lacouncil.TEST_COPY2.duckdb"
shutil.copy2(str(CANONICAL), str(test1))
audit = ROOT / "memoria" / "audit" / "test-merge2.jsonl"

r = subprocess.run(
    ["uv", "run", "python", str(MERGE),
     "--local", str(CANONICAL),
     "--remote", str(test1),
     "--output", str(test1),
     "--audit-log", str(audit)],
    capture_output=True, text=True, cwd=str(ROOT)
)
print("STDOUT:", r.stdout[:1000])
print("STDERR:", r.stderr[:1000])

test1.unlink(missing_ok=True)
