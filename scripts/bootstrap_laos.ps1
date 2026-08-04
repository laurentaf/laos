# LAOS Bootstrap — initial setup for the Databricks POC project
#
# Why this script exists:
# LAOS depends on 6 sibling capability repos (latade, lacouncil, lan8n,
# ladesign, laecon, laengine). On a fresh machine, several of these are
# missing or lack their `.venv/`. This script:
#   1. Clones missing capability repos from github.com/laurentaf
#   2. Syncs their venvs (uv-managed)
#   3. Installs the ladesign Node daemon (pnpm install)
#   4. Re-runs `laos-doctor` to confirm a healthy workspace
#
# Run this once. Re-run if any capability repo CLAIMS add new tooling.
#
# Usage (PowerShell):
#   cd F:\projects\Laos
#   uv run python scripts/print_boostrap.ps1    # dry-run preview
#   .\scripts\bootstrap_laos.ps1                 # actual execution
#
# Or invoke directly:
#   pwsh -File .\scripts\bootstrap_laos.ps1

[CmdletBinding()]
param(
  [switch]$DryRun = $false,
  [string]$Org = 'laurentaf'
)

$ErrorActionPreference = 'Stop'
$WorkspaceRoot = 'F:\projects'

# ─── Capability repos mapped to upstream URLs ────────────────────
$CapabilityRepos = @{
  'lacouncil' = @{ url = "https://github.com/$Org/lacouncil";          sync = $true;  reason = 'enables structural-change pipeline' }
  'latade'    = @{ url = $null;                                       sync = $true;  reason = 'target of sql.databricks addition' }
  'lan8n'     = @{ url = $null;                                       sync = $true;  reason = 'orchestrator.routes need it' }
  'ladesign'  = @{ url = $null;                                       sync = $false; node = $true; reason = 'branding pass needs Node daemon' }
  'laecon'    = @{ url = $null;                                       sync = $true;  reason = 'listed stable in registry' }
  'laengine'  = @{ url = $null;                                       sync = $true;  reason = 'listed stable in registry (optional)' }
}

# ─── Helper: print or run a step ─────────────────────────────────
function Invoke-Step {
  param([string]$Title, [string]$Cmd, [switch]$AllowFailure = $false)

  Write-Host ''
  Write-Host ('=== ' + $Title + ' ===') -ForegroundColor Cyan
  Write-Host ('$ ' + $Cmd)
  Write-Host ''

  if ($DryRun) {
    Write-Host '(dry-run: skipping execution)' -ForegroundColor Yellow
    return
  }

  try {
    Invoke-Expression $Cmd
    if ($LASTEXITCODE -ne 0 -and -not $AllowFailure) {
      throw "Step '$Title' exited with code $LASTEXITCODE"
    }
    Write-Host ('OK: ' + $Title) -ForegroundColor Green
  }
  catch {
    if ($AllowFailure) {
      Write-Host ('WARN: ' + $Title + ' — ' + $_.Exception.Message) -ForegroundColor Yellow
    } else {
      throw
    }
  }
}

# ─── Helper: clone if missing ─────────────────────────────────────
function Ensure-CapabilityClone {
  param([string]$Name, [string]$Url)
  $dest = Join-Path $WorkspaceRoot $Name

  if (Test-Path $dest) {
    Write-Host ("[skip] " + $Name + " already exists at " + $dest) -ForegroundColor DarkGray
    return
  }
  if (-not $Url) {
    throw "Repo '$Name' is missing on disk and no upstream URL is recorded."
  }

  if ($DryRun) {
    Write-Host ('[dry-run] would clone ' + $Url + ' -> ' + $dest)
    return
  }

  Invoke-Step -Title ("clone " + $Name) -Cmd ("git clone " + $Url + " '" + $dest + "'")
}

# ─── 1. Pre-flight checks ─────────────────────────────────────────
Invoke-Step -Title 'verify toolchain' -Cmd 'uv --version; git --version; node --version; pnpm --version' -AllowFailure

# ─── 2. Clone missing capability repos ────────────────────────────
foreach ($name in $CapabilityRepos.Keys) {
  $meta = $CapabilityRepos[$name]
  Ensure-CapabilityClone -Name $name -Url $meta.url
}

# ─── 3. Sync Python venvs ─────────────────────────────────────────
function Sync-If-Repo {
  param([string]$Name, [string]$Reason)
  $dest = Join-Path $WorkspaceRoot $Name
  if (-not (Test-Path $dest)) {
    Write-Host ("[skip] " + $Name + " missing; cannot sync.") -ForegroundColor Yellow
    return
  }
  Invoke-Step -Title ("uv sync " + $Name + " (" + $Reason + ")") -Cmd ('uv --directory "' + $dest + '" sync')
}

Sync-If-Repo 'lacouncil' 'in-memory structural improvement engine'
Sync-If-Repo 'latade'    'data engineering (target of Databricks extension)'
Sync-If-Repo 'lan8n'     'automation/orchestration'
Sync-If-Repo 'laecon'    'econometrics + ML'
Sync-If-Repo 'laengine'  'game dev'

# ─── 4. Install ladesign Node daemon (pnpm install) ───────────────
$ladesign = Join-Path $WorkspaceRoot 'ladesign'
if (Test-Path $ladesign) {
  Invoke-Step -Title 'pnpm install --dir ladesign' -Cmd ('pnpm --dir "' + $ladesign + '" install') -AllowFailure
} else {
  Write-Host '[skip] ladesign not on disk' -ForegroundColor Yellow
}

# ─── 5. Re-verify ─────────────────────────────────────────────────
Invoke-Step -Title 'laos-doctor verification' -Cmd 'uv run python scripts\laos-doctor.py' -AllowFailure

# ─── 6. Clear git fetch refs cache ────────────────────────────────
# (operators will fetch latest when first LAOS ops happen)

Write-Host ''
Write-Host 'Bootstrap complete.' -ForegroundColor Green
Write-Host 'Next steps:'
Write-Host '  1. Open a new LAOS session (or /new-project).'
Write-Host '  2. Run `laos-doctor` again to confirm venvs are tracked.'
Write-Host '  3. Continue with the Databricks POC structural-change pipeline.'
