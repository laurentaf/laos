#Requires -Version 5.1 -RunAsAdministrator
<#
.SYNOPSIS
  Replace root memoria/ with a junction to lacouncil/memoria/.

.DESCRIPTION
  After a reboot, existing handles on memoria/ are released and this
  script can replace the directory with a junction. Run ONCE after
  reboot (and after the SMB share has been recreated).

  After this, both the sync infrastructure and the LACOUNCIL MCP
  server see the same DuckDB file — no divergence.

.EXAMPLE
  .\scripts\sync\fix-memoria-junction.ps1
#>

$ErrorActionPreference = "Stop"

$LAOS    = Resolve-Path "$PSScriptRoot\..\.."
$TARGET  = "$LAOS\lacouncil\memoria"
$LINK    = "$LAOS\memoria"

Write-Host "=== Fix memoria junction ===" -ForegroundColor Cyan
Write-Host "  Link:   $LINK"
Write-Host "  Target: $TARGET"

# 1. Verify target exists
if (-not (Test-Path $TARGET)) {
    Write-Error "Target lacouncil/memoria nao encontrado: $TARGET"
    exit 1
}

# 2. Remove SMB share (admin needed)
Write-Host "[1/3] Removendo SMB share temporariamente..." -ForegroundColor Yellow
Get-SmbShare -Name LAOS_STATE -ErrorAction SilentlyContinue | Remove-SmbShare -Force
Write-Host "  SMB share removed."

# 3. Backup audit dir from current memoria/ if any
Write-Host "[2/3] Preparando junction..." -ForegroundColor Yellow
$auditBackup = "$env:TEMP\memoria-audit-backup"
if (Test-Path "$LINK\audit") {
    Remove-Item $auditBackup -Recurse -Force -ErrorAction SilentlyContinue
    Copy-Item "$LINK\audit" $auditBackup -Recurse -Force
    Write-Host "  audit backed up to $auditBackup"
}

# Remove the directory (should work post-reboot)
Remove-Item $LINK -Force -Recurse
Write-Host "  Root memoria/ removed."

# Create junction
New-Item -ItemType Junction -Path $LINK -Target $TARGET -Force | Out-Null
Write-Host "  Junction created: memoria -> lacouncil/memoria"

# 4. Recreate SMB share
Write-Host "[3/3] Recriando SMB share..." -ForegroundColor Yellow
New-SmbShare -Name LAOS_STATE `
    -Path $LINK `
    -FullAccess "$env:USERNAME" `
    -Description "LAOS state sync (DuckDB + audit + .env)"
Set-SmbShare -Name LAOS_STATE -EncryptData $true

# Verify
$share = Get-SmbShare -Name LAOS_STATE
Write-Host ""
Write-Host "=== Resultado ===" -ForegroundColor Green
$share | Select-Object Name, Path, Description | Format-Table
Write-Host ""
Write-Host "Testando conteudo via UNC..."
try {
    Get-ChildItem "\\localhost\LAOS_STATE" | Select-Object Name, Length | Format-Table
} catch {
    Write-Host "  (aguarde alguns segundos e tente novamente)"
}
Write-Host ""
Write-Host "Done." -ForegroundColor Green
