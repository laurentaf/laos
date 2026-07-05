#Requires -Version 5.1
<#
.SYNOPSIS
  Sincroniza state LAOS (DuckDB, .env.shared, lacouncil.yaml) entre A e B.

.DESCRIPTION
  Orquestrador de sync bidirecional sobre SMB via Tailscale.
  Faz lock → pull → merge DuckDB → sync .env.shared → push → audit.

  Idempotente: rodar 2x seguidas = mesmo resultado.

.PARAMETER RemoteDrive
  Letra do drive mapeado para o remoto (ex.: Y:\ para A->B, Z:\ para B->A).

.PARAMETER Direction
  "pull" (remoto → local) ou "push" (local → remoto). Default: pull.

.PARAMETER NoPush
  Se presente, só faz pull (não push). Útil para validar antes de subir.

.EXAMPLE
  .\sync-state.ps1 -RemoteDrive Y -Direction pull
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$RemoteDrive,

    [ValidateSet("pull", "push")]
    [string]$Direction = "pull",

    [switch]$NoPush
)

$ErrorActionPreference = "Stop"

$LAOS      = Resolve-Path "$PSScriptRoot\..\.."
$LOG_DIR   = "$LAOS\memoria\audit"
$LOG       = "$LOG_DIR\sync.jsonl"
$LOCK      = "$LAOS\memoria\.sync.lock"

# Ensure directories
New-Item -ItemType Directory -Path $LOG_DIR -Force | Out-Null

function Write-Audit {
    param($Event, $Data)
    $entry = @{
        ts      = (Get-Date).ToString("o")
        event   = $Event
        machine = $env:COMPUTERNAME
        data    = $Data
    } | ConvertTo-Json -Compress
    Add-Content -Path $LOG -Value $entry
}

function Get-Timestamp { Get-Date -Format "yyyy-MM-dd HH:mm:ss" }

Write-Host "=== LAOS sync ===" -ForegroundColor Cyan
Write-Host "  Machine:   $env:COMPUTERNAME"
Write-Host "  Direction: $Direction"
Write-Host "  Remote:    ${RemoteDrive}:"
Write-Host "  LAOS:      $LAOS"
Write-Host "  Started:   $(Get-Timestamp)"

# 1. Lock
if (Test-Path $LOCK) {
    Write-Warning "Sync ja em andamento (lock: $LOCK). Abortando."
    exit 1
}
New-Item -ItemType File -Path $LOCK -Force | Out-Null
Write-Audit -Event "sync_started" -Data @{ direction = $Direction }

try {
    # 2. Validate remote connectivity
    $remoteBase = "${RemoteDrive}:\"
    if (-not (Test-Path $remoteBase)) {
        throw "Drive remoto ${RemoteDrive}: nao acessivel. Verifique VPN/net use."
    }
    Write-Host "[ok] Conexao remota via ${RemoteDrive}:" -ForegroundColor Green

    # 3. If pull: copy remote state to local staging area
    if ($Direction -eq "pull") {
        Write-Host "[pull] DuckDB remoto -> local..." -ForegroundColor Yellow
        $remoteDuck = "${RemoteDrive}:\lacouncil.duckdb"
        $localDuck  = "$LAOS\memoria\lacouncil.duckdb"
        $stagingDuck = "$LAOS\memoria\remote.duckdb"

        if (Test-Path $remoteDuck) {
            Copy-Item $remoteDuck $stagingDuck -Force
            Write-Host "[pull] DuckDB copied ($remoteDuck -> $stagingDuck)"

            # Merge
            Write-Host "[merge] Unindo DuckDBs..." -ForegroundColor Yellow
            $result = uv run python "$LAOS\scripts\sync\merge_duckdb.py" `
                --local $localDuck --remote $stagingDuck `
                --output $localDuck --audit-log $LOG
            Write-Host "[merge] $result"
        } else {
            Write-Warning "DuckDB remoto nao encontrado em $remoteDuck. Pulando."
        }

        # Pull .env.shared
        $remoteEnv = "${RemoteDrive}:\..\.env.shared"
        if (Test-Path $remoteEnv) {
            Copy-Item $remoteEnv "$LAOS\.env.shared" -Force
            Write-Host "[pull] .env.shared sincronizado"
        }

        # Pull lacouncil.yaml
        $remoteYaml = "${RemoteDrive}:\..\lacouncil.yaml"
        if (Test-Path $remoteYaml) {
            Copy-Item $remoteYaml "$LAOS\lacouncil.yaml" -Force
            Write-Host "[pull] lacouncil.yaml sincronizado"
        }

        Write-Audit -Event "sync_pull_complete" @{ }
        Write-Host "[ok] Pull concluido" -ForegroundColor Green
    }

    # 4. If push (or after pull if NoPush is off): local -> remote
    if ($Direction -eq "push" -or (-not $NoPush)) {
        Write-Host "[push] Local -> remoto..." -ForegroundColor Yellow

        $remoteDuckDir = "${RemoteDrive}:\"
        $localDuck  = "$LAOS\memoria\lacouncil.duckdb"

        if (Test-Path $localDuck) {
            Copy-Item $localDuck $remoteDuckDir -Force
            Write-Host "[push] DuckDB enviado"
        }

        # Push .env.shared (only if exists)
        if (Test-Path "$LAOS\.env.shared") {
            Copy-Item "$LAOS\.env.shared" "${RemoteDrive}:\..\.env.shared" -Force
            Write-Host "[push] .env.shared enviado"
        }

        Write-Audit -Event "sync_push_complete" @{ }
        Write-Host "[ok] Push concluido" -ForegroundColor Green
    }

    Write-Host ""
    Write-Host "=== Sync concluido: $(Get-Timestamp) ===" -ForegroundColor Green

} catch {
    Write-Audit -Event "sync_failed" @{ error = $_.Exception.Message }
    Write-Error "Falha no sync: $_"
    exit 1
} finally {
    Remove-Item $LOCK -Force -ErrorAction SilentlyContinue
}
