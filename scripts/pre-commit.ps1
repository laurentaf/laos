#!/usr/bin/env pwsh
# pre-commit.ps1 — LAOS delivery validation hook (Windows PowerShell)
#
# Usage:
#   Move this file to .git/hooks/pre-commit (no extension)
#   Or run: .\scripts\setup-hooks.ps1 to install automatically

$ErrorActionPreference = "Stop"

$REPO_ROOT = Split-Path -Parent $PSScriptRoot
$SCRIPT = "$REPO_ROOT\scripts\delivery-hook.py"

# Find project.yaml in current directory or parent directories
$PROJECT_YAML = $null
$CHECK_DIR = Get-Location

for ($i = 0; $i -lt 10; $i++) {
    $TEST_PATH = Join-Path $CHECK_DIR "project.yaml"
    if (Test-Path $TEST_PATH) {
        $PROJECT_YAML = $TEST_PATH
        break
    }
    $CHECK_DIR = Split-Path -Parent $CHECK_DIR
    if ($CHECK_DIR -eq $null) { break }
}

if ($PROJECT_YAML -eq $null) {
    Write-Host "SKIP: No project.yaml found"
    exit 0
}

Write-Host "Validating: $PROJECT_YAML"

# Run delivery-hook.py
$RESULT = & python $SCRIPT --check $PROJECT_YAML

if ($LASTEXITCODE -eq 0) {
    Write-Host "PASS: Validation successful"
    exit 0
} elseif ($LASTEXITCODE -eq 2) {
    Write-Host "SKIP: No project to validate"
    exit 0
} else {
    Write-Host "FAIL: Validation failed - commit blocked"
    Write-Host "Fix the issues above and try again"
    exit 1
}