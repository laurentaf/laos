#Requires -Version 5.1
<#
.SYNOPSIS
  Install Tailscale (if missing) and capture VPN credentials for sync.

.DESCRIPTION
  1. Install Tailscale via winget
  2. Tailscale up (opens browser for auth)
  3. Capture IP, hostname, and MagicDNS suffix
  4. Creates F:\projects\ (which will be needed anyway)

  Run as Administrator.
#>

$ErrorActionPreference = "Stop"

Write-Host "=== Tailscale setup ===" -ForegroundColor Cyan

# 1. Install if missing
$ts = Get-Command "tailscale.exe" -ErrorAction SilentlyContinue
if (-not $ts) {
    Write-Host "[1/4] Installing Tailscale via winget..." -ForegroundColor Yellow
    winget install --id Tailscale.Tailscale --accept-source-agreements --accept-package-agreements
    if ($LASTEXITCODE -ne 0) { throw "winget install falhou" }
    Write-Host "  installed."
} else {
    Write-Host "[1/4] Tailscale already installed at $($ts.Source)" -ForegroundColor Yellow
}

# 2. Create F:\projects\ (needed for the rename)
Write-Host "[2/4] Creating F:\projects... (placeholder for LAOS)" -ForegroundColor Yellow
New-Item -ItemType Directory -Path "F:\projects" -Force | Out-Null
Write-Host "  F:\projects ready."

# 3. Tailscale up
Write-Host "[3/4] Running tailscale up..." -ForegroundColor Yellow
Write-Host "  A browser will open for authentication."
Write-Host "  Log in with your Google/Microsoft/GitHub account."
& "$env:ProgramFiles\Tailscale\tailscale.exe" up

# 4. Capture credentials
Write-Host "[4/4] Capturing Tailscale credentials..." -ForegroundColor Yellow
$tsStatus = & "$env:ProgramFiles\Tailscale\tailscale.exe" status --json 2>$null
$tsIP     = & "$env:ProgramFiles\Tailscale\tailscale.exe" ip -4
$tsHost   = $env:COMPUTERNAME
$mdns     = $null
try {
    $mdns = $tsStatus | ConvertFrom-Json | Select -ExpandProperty MagicDNSSuffix
} catch { }

Write-Host ""
Write-Host "=== Credenciais para o prompt B ===" -ForegroundColor Green
Write-Host "Hostname de A:     $tsHost"
Write-Host "Tailscale IP de A: $tsIP"
if ($mdns) {
    Write-Host "MagicDNS suffix:   $mdns"
    Write-Host "A via MagicDNS:    $tsHost.$mdns"
}
Write-Host ""
Write-Host "Para gerar auth key (necessária para B):"
Write-Host "  1. Acesse https://login.tailscale.com/admin/settings/keys"
Write-Host "  2. Generate auth key -> Reusable -> tag:laos-sync"
Write-Host "  3. Copie a chave (tskey-auth-...) e inclua no prompt B como TAILSCALE_AUTH_KEY"
Write-Host ""
Write-Host "Para verificar conectividade com B depois que ele instalar:"
Write-Host "  tailscale ping <B_HOSTNAME>"

# 5. Create a JSON with the credentials for reuse
$creds = @{
    hostname = $tsHost
    tailscale_ip = $tsIP
    magicdns_suffix = $mdns
    machine = "A"
    captured_at = (Get-Date).ToString("o")
} | ConvertTo-Json
Set-Content -Path "F:\projects\LAOS\.tailscale-creds.json" -Value $creds
Write-Host ""
Write-Host "Credenciais salvas em F:\projects\LAOS\.tailscale-creds.json" -ForegroundColor DarkGray
Write-Host "Done." -ForegroundColor Green
