"""Quick test: merge the canonical DuckDB with itself (idempotent)."""
import shutil, subprocess, sys
from pathlib import Path

ROOT = Path(r"F:\projects\Laos")
CANONICAL = ROOT / "lacouncil" / "memoria" / "lacouncil.duckdb"
AUDIT_DIR = ROOT / "memoria" / "audit"
MERGE_SCRIPT = ROOT / "scripts" / "sync" / "merge_duckdb.py"

def main():
    print("=== Teste de merge (A+A = idempotente) ===")
    
    if not CANONICAL.exists():
        print(f"ERRO: DuckDB nao existe em {CANONICAL}")
        sys.exit(1)
    
    sz = CANONICAL.stat().st_size
    print(f"  DuckDB: {CANONICAL.name} ({sz:,} bytes)")
    
    # Create copy as "remote"
    test_copy = CANONICAL.parent / "lacouncil.remote.TEST.duckdb"
    shutil.copy2(str(CANONICAL), str(test_copy))
    print(f"  Copia remota: {test_copy.name}")
    
    # Create audit dir
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    audit_log = AUDIT_DIR / "sync-test-merge.jsonl"
    
    # Run merge
    print(f"  Executando merge...")
    result = subprocess.run([
        "uv", "run", "python", str(MERGE_SCRIPT),
        "--local", str(CANONICAL),
        "--remote", str(test_copy),
        "--output", str(test_copy),
        "--audit-log", str(audit_log),
    ], capture_output=True, text=True, cwd=str(ROOT))
    
    print(f"  Exit code: {result.returncode}")
    if result.stdout:
        # Only last lines
        lines = result.stdout.strip().split("\n")
        for line in lines[-10:]:
            print(f"  {line}")
    if result.stderr:
        print(f"  STDERR: {result.stderr[:300]}")
    
    # Check audit log
    if audit_log.exists():
        with open(audit_log) as f:
            entries = f.readlines()
        print(f"  Audit log: {len(entries)} entradas em {audit_log.name}")
    
    # Dry-run test
    print(f"\n  Teste dry-run...")
    result2 = subprocess.run([
        "uv", "run", "python", str(MERGE_SCRIPT),
        "--local", str(CANONICAL),
        "--remote", str(test_copy),
        "--output", str(CANONICAL.parent / "lacouncil.dry.TEST.duckdb"),
        "--audit-log", str(audit_log),
        "--dry-run",
    ], capture_output=True, text=True, cwd=str(ROOT))
    print(f"  Dry-run exit: {result2.returncode}")
    if result2.stdout:
        lines = result2.stdout.strip().split("\n")
        for line in lines[-5:]:
            print(f"  {line}")
    
    # Cleanup
    test_copy.unlink(missing_ok=True)
    (CANONICAL.parent / "lacouncil.dry.TEST.duckdb").unlink(missing_ok=True)
    print(f"\n  Concluido. Teste de merge OK." if result.returncode == 0 else "\n  Merge FALHOU")
    
    return 0 if result.returncode == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
