#!/usr/bin/env pwsh
# setup-hooks.ps1 — Install LAOS git hooks (100% hidden, zero console)
#
# Instala hooks Python que rodam via pythonw.exe (WINDOWS subsystem).
# NENHUM PowerShell ou cmd.exe é usado — zero flash de console.
#
# Usage:
#   .\scripts\setup-hooks.ps1

$ErrorActionPreference = "Stop"

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$REPO_ROOT = Split-Path -Parent $SCRIPT_DIR
$HOOKS_DIR = Join-Path $REPO_ROOT ".git\hooks"

if (-not (Test-Path $HOOKS_DIR)) {
    Write-Host "ERROR: .git/hooks directory not found. Is this a git repo?"
    exit 1
}

$PYTHONW = "$REPO_ROOT\.venv\Scripts\pythonw.exe"
if (-not (Test-Path $PYTHONW)) {
    Write-Host "WARNING: pythonw.exe not found at $PYTHONW"
    Write-Host "Hooks will be installed but may not execute until pythonw is available."
}

# ─── Pre-commit hook ─────────────────────────────────────────
$PRE_SOURCE = Join-Path $SCRIPT_DIR "pre-commit.hook.py"
$PRE_TARGET = Join-Path $HOOKS_DIR "pre-commit"

if (Test-Path $PRE_TARGET) {
    $BACKUP = "$PRE_TARGET.backup.$(Get-Date -Format 'yyyyMMddHHmmss')"
    Write-Host "Backing up existing hook to: $BACKUP"
    Move-Item $PRE_TARGET $BACKUP
}

# Copy the hook and prepend the pythonw shebang (absolute path for git's CreateProcess)
$shebang = "#!$PYTHONW"
$content = Get-Content $PRE_SOURCE -Raw
$shebang + "`n" + $content | Set-Content $PRE_TARGET -NoNewline
Write-Host "  pre-commit hook installed: $PRE_TARGET"
Write-Host "    Interpreter: $PYTHONW (WINDOWS subsystem, zero console)"

# ─── Post-merge hook ──────────────────────────────────────────
$POST_SOURCE = Join-Path $SCRIPT_DIR "post-merge.hook.py"
$POST_TARGET = Join-Path $HOOKS_DIR "post-merge"

if (Test-Path $POST_TARGET) {
    $BACKUP = "$POST_TARGET.backup.$(Get-Date -Format 'yyyyMMddHHmmss')"
    Write-Host "Backing up existing post-merge hook to: $BACKUP"
    Move-Item $POST_TARGET $BACKUP
}

$content = Get-Content $POST_SOURCE -Raw
$shebang + "`n" + $content | Set-Content $POST_TARGET -NoNewline
Write-Host "  post-merge hook installed: $POST_TARGET"
Write-Host "    Interpreter: $PYTHONW (WINDOWS subsystem, zero console)"

Write-Host ""
Write-Host "SUCCESS: hooks installed (100% hidden)"
Write-Host "  pre-commit : validates project.yaml via pythonw.exe (no console)"
Write-Host "  post-merge : auto uv sync via run_hidden.run() (CREATE_NO_WINDOW)"
Write-Host "To uninstall: Remove-Item .git/hooks/pre-commit, .git/hooks/post-merge"
exit 0
