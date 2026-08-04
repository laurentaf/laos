#!/usr/bin/env pwsh
# pre-commit.ps1 — LAOS delivery validation hook (Windows PowerShell)
#
# 100% HIDDEN: .NET Process.CreateNoWindow=$true (CREATE_NO_WINDOW).
# Dupla camada: pythonw.exe (GUI subsystem) + run_hidden.run() (CREATE_NO_WINDOW).
# NENHUMA janela de console é criada, mesmo em tela cheia.
#
# Instalação:
#   .\scripts\setup-hooks.ps1  (copia para .git/hooks/pre-commit)

$ErrorActionPreference = "Stop"

$REPO_ROOT = Split-Path -Parent $PSScriptRoot
$PYTHONW = "$REPO_ROOT\.venv\Scripts\pythonw.exe"
$RUNNER = "$REPO_ROOT\scripts\run-hidden.py"
$SCRIPT = "$REPO_ROOT\scripts\delivery-hook.py"

if (-not (Test-Path $PYTHONW)) {
    exit 0
}

# Find project.yaml
$PROJECT_YAML = $null
$CHECK_DIR = Get-Location
for ($i = 0; $i -lt 10; $i++) {
    $TEST_PATH = Join-Path $CHECK_DIR "project.yaml"
    if (Test-Path $TEST_PATH) {
        $PROJECT_YAML = $TEST_PATH
        break
    }
    $CHECK_DIR = Split-Path -Parent $CHECK_DIR
}
if (-not $PROJECT_YAML) { exit 0 }

# 100% hidden: .NET ProcessStartInfo com CreateNoWindow=$true
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $PYTHONW
$psi.Arguments = "`"$RUNNER`" `"$SCRIPT`" --check `"$PROJECT_YAML`""
$psi.UseShellExecute = $false
$psi.CreateNoWindow = $true
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true

try {
    $p = [System.Diagnostics.Process]::Start($psi)
    $output = $p.StandardOutput.ReadToEnd()
    $err = $p.StandardError.ReadToEnd()
    $p.WaitForExit()
    $exitCode = $p.ExitCode
} catch {
    $output = ""
    $err = $_.Exception.Message
    $exitCode = 1
}

if ($output) { Write-Host $output }
if ($err) { Write-Host $err }
exit $exitCode
