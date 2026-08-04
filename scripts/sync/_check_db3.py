"""Check merge with separate remote and output paths."""
import shutil, subprocess
from pathlib import Path

ROOT = Path(r"F:\projects\Laos")
CANONICAL = ROOT / "lacouncil" / "memoria" / "lacouncil.duckdb"
MERGE = ROOT / "scripts" / "sync" / "merge_duckdb.py"

remote_copy = CANONICAL.parent / "lacouncil.REMOTE.duckdb"
output_copy = CANONICAL.parent / "lacouncil.OUTPUT.duckdb"

# Copy canonical to simulate "remote"
shutil.copy2(str(CANONICAL), str(remote_copy))
audit = ROOT / "memoria" / "audit" / "test-merge3.jsonl"

print("Local:", CANONICAL.name)
print("Remote:", remote_copy.name)
print("Output:", output_copy.name)

r = subprocess.run(
    ["uv", "run", "python", str(MERGE),
     "--local", str(CANONICAL),
     "--remote", str(remote_copy),
     "--output", str(output_copy),
     "--audit-log", str(audit)],
    capture_output=True, text=True, cwd=str(ROOT)
)
print("\nSTDOUT:", r.stdout[:1500])
if r.stderr:
    print("STDERR:", r.stderr[:500])
print(f"Exit: {r.returncode}")

# Verify output exists
if output_copy.exists():
    import duckdb
    con = duckdb.connect(str(output_copy), read_only=True)
    for t in ["propostas", "votos", "projetos_registrados"]:
        cnt = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  output.{t}: {cnt} rows")
    con.close()
    output_copy.unlink(missing_ok=True)
else:
    print("Output nao criado!")

remote_copy.unlink(missing_ok=True)
