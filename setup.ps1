# LAOS first-run setup.
#
# Usage (from LAOS root):
#   pwsh .\setup.ps1

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
Set-Location -LiteralPath $root

Write-Host "=== LAOS setup ===" -ForegroundColor Cyan
Write-Host "Root: $root"
Write-Host ""

# 1. Local Python venv via uv
Write-Host "[1/3] Creating local .venv via uv sync..." -ForegroundColor Yellow
uv sync
if ($LASTEXITCODE -ne 0) { throw "uv sync failed" }

# 2. .env* files from templates
Write-Host ""
Write-Host "[2/3] .env files..." -ForegroundColor Yellow

# .env (legacy, for opencode.jsonc compat)
if (Test-Path -LiteralPath ".env") {
    Write-Host "  .env exists, leaving alone."
} else {
    Copy-Item -LiteralPath ".env.example" -Destination ".env"
    Write-Host "  created .env from .env.example - fill in N8N_API_KEY when ready."
}

# .env.local (machine-specific paths)
if (Test-Path -LiteralPath ".env.local") {
    Write-Host "  .env.local exists, leaving alone."
} else {
    if (Test-Path -LiteralPath "env-local-template.txt") {
        Copy-Item -LiteralPath "env-local-template.txt" -Destination ".env.local"
        Write-Host "  created .env.local from env-local-template.txt - adjust paths for this machine."
    }
}

# .env.shared (shared API keys, sync'd between machines)
if (Test-Path -LiteralPath ".env.shared") {
    Write-Host "  .env.shared exists, leaving alone."
} else {
    if (Test-Path -LiteralPath "env-shared-template.txt") {
        Copy-Item -LiteralPath "env-shared-template.txt" -Destination ".env.shared"
        Write-Host "  created .env.shared from env-shared-template.txt - fill in API keys."
    }
}

Write-Host "  Run 'uv run python scripts/load_env.py' to verify env vars."

# 3. Sibling capability sanity check
Write-Host ""
Write-Host "[3/3] Sibling capability repos..." -ForegroundColor Yellow
$siblings = @(
    @{ name = "LATADE";    path = "..\latade" },
    @{ name = "LAN8N";     path = "..\lan8n" },
    @{ name = "LADESIGN";  path = "..\ladesign" },
    @{ name = "LACOUNCIL"; path = "..\lacouncil" },
    @{ name = "LAENGINE";  path = "..\laengine" }
)
foreach ($s in $siblings) {
    if (Test-Path -LiteralPath $s.path) {
        Write-Host ("  OK    {0,-12}  -> {1}" -f $s.name, (Resolve-Path $s.path))
    } else {
        Write-Host ("  MISS  {0,-12}  expected at {1}" -f $s.name, $s.path) -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Done." -ForegroundColor Green
Write-Host "Next: launch opencode from this folder."
Write-Host "  cd $root"
Write-Host "  opencode"
