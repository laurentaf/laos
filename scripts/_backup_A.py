"""One-shot: backup F:\projects\Laos before rename."""
import sys, subprocess, time
from pathlib import Path

SRC = Path(r"F:\projects\Laos")
DST = Path(f"F:\\backups\\laos-A-pre-sync-{time.strftime('%Y%m%d-%H%M')}")

def main():
    if not SRC.exists():
        print("ERRO: origem", SRC, "nao existe")
        sys.exit(1)

    DST.mkdir(parents=True, exist_ok=True)
    print(f"Backup de {SRC} -> {DST}")

    result = subprocess.run([
        "robocopy", str(SRC), str(DST),
        "/MIR", "/R:2", "/W:3", "/MT:4",
        "/NP", "/NDL", "/NJH", "/NJS"
    ], capture_output=True, text=True)

    if result.returncode >= 8:
        print("robocopy falhou (exit", result.returncode, ")")
        print(result.stderr)
        sys.exit(result.returncode)
    print("robocopy ok (exit", result.returncode, ")")

    # Verify critical files
    for f in ["AGENTS.md", ".gitignore", "pyproject.toml", "lacouncil.duckdb"]:
        p = DST / "memoria" / f if f == "lacouncil.duckdb" else DST / f
        if p.exists():
            print("  ok ", f)
        else:
            print("  AUSENTE ", f)

    # Count files without listing names (avoids Unicode encoding issues)
    total = sum(1 for _ in DST.rglob("*"))
    print(f"\nBackup completo: {total:,} itens em {DST}")

if __name__ == "__main__":
    main()
