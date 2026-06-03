#Requires -Version 5.1
<#
.SYNOPSIS
  Fast-forward sibling capability repos so LAOS sees their latest HEAD.

.DESCRIPTION
  For each of the sibling capability repos (LATADE, LAN8N, LADESIGN) runs
  `git fetch` then `git pull --ff-only`. Aborts the whole run on the first
  failure. Never force-pushes. Never merges.

  Run from the LAOS root.
#>

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$laosRoot  = Split-Path -Parent $scriptDir

$siblings = @("latade", "lan8n", "ladesign")

foreach ($name in $siblings) {
    $path = Join-Path $laosRoot "..\$name"
    if (-not (Test-Path -LiteralPath $path)) {
        Write-Host "[skip] $name not found at $path" -ForegroundColor DarkGray
        continue
    }
    if (-not (Test-Path -LiteralPath (Join-Path $path ".git"))) {
        Write-Host "[skip] $name has no .git (not a clone)" -ForegroundColor DarkGray
        continue
    }
    Write-Host "[fetch] $name" -ForegroundColor Cyan
    Push-Location -LiteralPath $path
    try {
        git fetch --all --prune
        if ($LASTEXITCODE -ne 0) { throw "git fetch failed for $name" }
        git pull --ff-only
        if ($LASTEXITCODE -ne 0) { throw "git pull --ff-only failed for $name (likely divergent history)" }
    }
    finally {
        Pop-Location
    }
    Write-Host "[ok]    $name" -ForegroundColor Green
}

Write-Host ""
Write-Host "Done. Re-run scripts/list_capabilities.py to verify status." -ForegroundColor Green
