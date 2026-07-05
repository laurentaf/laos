#Requires -Version 5.1
<#
.SYNOPSIS
  Git post-merge hook: automatic uv sync after pull/merge.

  Install:
    Copy to .git/hooks/post-merge
    Or run:  .\scripts\setup-hooks.ps1

  This hook runs 'uv sync' silently after every git pull/merge,
  ensuring .venv is always up to date with pyproject.toml + uv.lock.
#>

$root = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent

Write-Host "[post-merge] Sincronizando ambiente..." -ForegroundColor DarkGray

# Stop on first error
$ErrorActionPreference = "Stop"

try {
    Push-Location $root
    uv sync --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[post-merge] uv sync OK" -ForegroundColor DarkGray
    } else {
        Write-Host "[post-merge] [AVISO] uv sync exit code: $LASTEXITCODE" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[post-merge] [ERRO] $_" -ForegroundColor Red
} finally {
    Pop-Location
}
