#!/usr/bin/env pwsh
# setup-hooks.ps1 — Install LAOS git hooks
#
# Usage:
#   .\scripts\setup-hooks.ps1
#
# Installs pre-commit hook for Windows (PowerShell) or Unix (bash)

$ErrorActionPreference = "Stop"

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
# $SCRIPT_DIR = F:\Projetos\Laos\scripts
$REPO_ROOT = Split-Path -Parent $SCRIPT_DIR
# $REPO_ROOT = F:\Projetos\Laos
$HOOKS_DIR = Join-Path $REPO_ROOT ".git\hooks"

# Detect environment
if ($PSVersionTable.Platform -eq "Unix" -or $IsWindows -eq $false -or (Test-Path "/bin/bash")) {
    $HOOK_SOURCE = Join-Path $SCRIPT_DIR "pre-commit"
    $HOOK_TARGET = Join-Path $HOOKS_DIR "pre-commit"
} else {
    # Windows PowerShell
    $HOOK_SOURCE = Join-Path $SCRIPT_DIR "pre-commit.ps1"
    $HOOK_TARGET = Join-Path $HOOKS_DIR "pre-commit"
}

Write-Host "Installing LAOS pre-commit hook..."
Write-Host "  Source: $HOOK_SOURCE"
Write-Host "  Target: $HOOK_TARGET"

if (-not (Test-Path $HOOK_SOURCE)) {
    Write-Host "ERROR: Source hook not found: $HOOK_SOURCE"
    exit 1
}

if (-not (Test-Path $HOOKS_DIR)) {
    Write-Host "ERROR: .git/hooks directory not found. Is this a git repo?"
    exit 1
}

# Backup existing hook if any
if (Test-Path $HOOK_TARGET) {
    $BACKUP = "$HOOK_TARGET.backup.$(Get-Date -Format 'yyyyMMddHHmmss')"
    Write-Host "Backing up existing hook to: $BACKUP"
    Move-Item $HOOK_TARGET $BACKUP
}

# Copy hook
Copy-Item $HOOK_SOURCE $HOOK_TARGET -Force

# Make executable (for Unix/git bash)
if ($PSVersionTable.Platform -eq "Unix" -or (Test-Path "/bin/bash")) {
    chmod +x $HOOK_TARGET 2>$null
}

# Post-merge hook (automatic uv sync after pull)
$POST_SOURCE   = Join-Path $REPO_ROOT "scripts\hooks\post-merge.ps1"
$POST_TARGET   = Join-Path $HOOKS_DIR "post-merge"
$POST_BACKUP   = "$POST_TARGET.backup.$(Get-Date -Format 'yyyyMMddHHmmss')"

if (Test-Path $POST_TARGET) {
    Write-Host "Backing up existing post-merge hook to: $POST_BACKUP"
    Move-Item $POST_TARGET $POST_BACKUP
}
Copy-Item $POST_SOURCE $POST_TARGET -Force
Write-Host "  post-merge hook installed (auto uv sync on git pull)"

Write-Host ""
Write-Host "SUCCESS: hooks installed"
Write-Host "  pre-commit : validates project.yaml before each commit"
Write-Host "  post-merge : auto uv sync after git pull"
Write-Host "To uninstall: Remove-Item .git/hooks/pre-commit, .git/hooks/post-merge"
exit 0