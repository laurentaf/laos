#Requires -Version 5.1 -RunAsAdministrator
<#
.SYNOPSIS
  Registra tarefa agendada para sync automático a cada 15 minutos.

.DESCRIPTION
  Cria uma tarefa no Windows Task Scheduler que roda sync-state.ps1
  periodicamente. Roda em background, não exibe janela.

.PARAMETER RemoteDrive
  Letra do drive mapeado para o remoto (ex.: Y).

.PARAMETER Direction
  "pull" ou "push". Default: pull.

.PARAMETER TaskName
  Nome da tarefa no scheduler. Default: "LAOS-Sync-State-A" (ou B).

.EXAMPLE
  # Em A
  .\install-sync-task.ps1 -RemoteDrive Y -Direction pull
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$RemoteDrive,

    [ValidateSet("pull", "push")]
    [string]$Direction = "pull",

    [string]$TaskName = "LAOS-Sync-State-A"
)

$ErrorActionPreference = "Stop"
$laosRoot = Resolve-Path "$PSScriptRoot\..\.."

Write-Host "=== Instalando tarefa: $TaskName ===" -ForegroundColor Cyan

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument @"
-NoProfile -ExecutionPolicy Bypass -File "$laosRoot\scripts\sync\sync-state.ps1" -RemoteDrive $RemoteDrive -Direction $Direction
"@

$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
    -RepetitionInterval (New-TimeSpan -Minutes 15) `
    -RepetitionDuration (New-TimeSpan -Days 3650)

$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -RunLevel Limited

Register-ScheduledTask -TaskName $TaskName `
    -Action $action -Trigger $trigger -Principal $principal `
    -Settings (New-ScheduledTaskSettingsSet `
        -StartWhenAvailable -DontStopIfGoingOnBatteries -AllowStartIfOnBatteries `
        -Hidden -DisallowHardTerminate `
    ) -Force

Write-Host "  Task $TaskName registrada." -ForegroundColor Green
Write-Host "  Trigger: a cada 15 min (primeira execucao em 1 min)"
Write-Host ""

# Validar
$task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($task) {
    Write-Host "  Task: $($task.TaskName) — State: $($task.State)"
} else {
    Write-Warning "  Nao foi possivel validar a tarefa."
}

Write-Host "Done." -ForegroundColor Green
