"""One-shot: move diagnostic/scratch files to _archive before rename.

Only moves files, never deletes. Backup was made in step 1.1.
"""
import shutil, sys, time, subprocess
from pathlib import Path

ROOT = Path(r"F:\projects\Laos")
ARCHIVE = ROOT / "scripts" / "_archive" / "scratch-2026-07-05"
ARCHIVE_SCRIPTS = ARCHIVE / "scripts-src"

# Root-level diagnostic files
ROOT_DIAG = [
    "_check_db.py", "_checklist_body.txt",
    "_diag_final.py", "_diag_laecon.py", "_diag_laengine.py",
    "_diag_mcps.py", "_diag_mcps2.py",
    "_run_laecon_test.py", "_run_laengine_test.py",
    "_temp_read_cv.py", "_tmp_check_boot.py",
    # Temp artifacts
    "0", "in.txt", "tmp_proposal.json",
]

# Scripts that are diagnostic-only (not part of LAOS)
SCRIPTS_DIAG = [
    "_preflight_inline.py", "_test_mcp.py", "_test_mcp_import.py",
    "add-repo-topics.py", "browser.py", "check_sales.py",
    "cleanup.py", "explore_pg.py", "generate_pg_ddl.py",
    "jsonc_sanitize.py", "repro_strip.js",
    "setup_oracle_pg.ps1", "setup_pg.py",
    "start_browser.bat", "update-profile-repo-metadata.py",
    "do_import.py", "export_big.py", "fix_state.py", "run_step.py",
    "extract_all.py", "extract_batch.py", "extract_bg.py",
    "extract_chunks.py", "extract_to_csv.py",
    "fase1_oracle.py",
    "pipeline.py", "pipeline_completo.py",
]


def move_safe(src, dst_dir):
    if not src.exists():
        return False
    dst = dst_dir / src.name
    if dst.exists():
        stamp = time.strftime("%H%M%S")
        dst = dst_dir / f"{src.stem}_{stamp}{src.suffix}"
    shutil.move(str(src), str(dst))
    print(f"  moved {src.relative_to(ROOT)}")
    return True


def main():
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    ARCHIVE_SCRIPTS.mkdir(parents=True, exist_ok=True)

    moved = 0
    print("=== Limpeza de scratch ===")

    # Root-level diag
    print("\nRoot diag:")
    for name in ROOT_DIAG:
        if move_safe(ROOT / name, ARCHIVE):
            moved += 1

    # Weird unicode file
    weird = ROOT / "F\u00ef\u00a7\u00a5ProjetosLaoserr.txt"
    if not weird.exists():
        # Try the git-quoted form
        result = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            capture_output=True, text=True, cwd=str(ROOT)
        )
        for line in result.stdout.split("\n"):
            if "err.txt" in line or "ProjetosLaoserr" in line:
                p = ROOT / line.strip().strip('"')
                if p.exists():
                    if move_safe(p, ARCHIVE):
                        moved += 1

    # $null file
    if move_safe(ROOT / "$null", ARCHIVE):
        moved += 1

    # Scripts diag
    print("\nScripts diag:")
    for name in SCRIPTS_DIAG:
        p = ROOT / "scripts" / name
        if p.exists():
            # Keep my own scripts
            if name in ("_backup_A.py", "_cleanup_scratch.py"):
                continue
            p2 = ARCHIVE / "scripts-src" / name
            if move_safe(p, ARCHIVE_SCRIPTS):
                moved += 1

    # data/extract_summary.txt
    if move_safe(ROOT / "data" / "extract_summary.txt", ARCHIVE):
        moved += 1

    print(f"\nTotal movidos: {moved}")
    print("Nada foi deletado. Restaurar via backup (1.1).")

if __name__ == "__main__":
    main()
