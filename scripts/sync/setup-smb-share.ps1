#Requires -Version 5.1 -RunAsAdministrator
<#
.SYNOPSIS
  Cria SMB share LAOS_STATE para sync entre A e B.

.DESCRIPTION
  Expõe a pasta memoria/lacouncil.duckdb (e .env) como share de rede.
  O acesso é criptografado via Tailscale (WireGuard).

  Deve ser executado em A e em B (cada máquina expõe seu próprio state).

.EXAMPLE
  .\setup-smb-share.ps1  # Cria share com nome LAOS_STATE
#>

$ErrorActionPreference = "Stop"

$LAOS   = Resolve-Path "$PSScriptRoot\..\.."
$SHARE  = "LAOS_STATE"
$MEMORIA = "$LAOS\memoria"

Write-Host "=== SMB Share setup ===" -ForegroundColor Cyan
Write-Host "  Share:     $SHARE"
Write-Host "  Caminho:   $MEMORIA"
Write-Host "  Maquina:   $env:COMPUTERNAME"

# Ensure directory exists
New-Item -ItemType Directory -Path $MEMORIA\audit -Force | Out-Null

# Create share
if (Get-SmbShare -Name $SHARE -ErrorAction SilentlyContinue) {
    Write-Host "[aviso] Share $SHARE ja existe. Recriando..." -ForegroundColor Yellow
    Remove-SmbShare -Name $SHARE -Force
}

New-SmbShare -Name $SHARE `
    -Path $MEMORIA `
    -FullAccess "$env:USERNAME" `
    -Description "LAOS state sync (DuckDB + audit + .env)"

Write-Host "[ok] Share $SHARE criado" -ForegroundColor Green

# Enable SMB encryption (recommended for potential Tailscale CGNAT path)
Set-SmbShare -Name $SHARE -EncryptData $true
Write-Host "[ok] SMB encryption ativada" -ForegroundColor Green

# Verify
$share = Get-SmbShare -Name $SHARE
Write-Host ""
Write-Host "=== Resultado ===" -ForegroundColor Cyan
$share | Select-Object Name, Path, Description | Format-Table

Write-Host ""
Write-Host "Mapeamento na outra maquina (B):"
Write-Host "  net use Y: \\$env:COMPUTERNAME\$SHARE"
Write-Host ""
Write-Host "Credenciais: mesmas do usuario Windows $env:USERNAME"
Write-Host ""
Write-Host "[!] Apos reboot, rode fix-memoria-junction.ps1 (Admin) para"
Write-Host "    substituir memoria/ por um junction apontando para"
Write-Host "    lacouncil/memoria/. Assim sync e MCP veem o mesmo DuckDB."
Write-Host "    Script: .\scripts\sync\fix-memoria-junction.ps1"
Write-Host "Done." -ForegroundColor Green
