#!/usr/bin/env pwsh
# post-merge.ps1 — LAOS automatic uv sync after git pull/merge
#
# 100% HIDDEN: .NET Process.CreateNoWindow=$true → sem console.
# Roda uv sync sem absolutamente nenhuma janela.
#
# Instalação:
#   .\scripts\setup-hooks.ps1  (copia para .git/hooks/post-merge)

$root = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
$PYTHONW = "$root\.venv\Scripts\pythonw.exe"
$RUNNER = "$root\scripts\run-hidden.py"

if (-not (Test-Path $PYTHONW)) { exit 0 }

# uv sync via run_hidden (CREATE_NO_WINDOW) + pythonw.exe (GUI subsystem)
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $PYTHONW
$psi.Arguments = "`"$RUNNER`" uv sync --quiet"
$psi.UseShellExecute = $false
$psi.CreateNoWindow = $true
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true

try {
    $p = [System.Diagnostics.Process]::Start($psi)
    $p.StandardOutput.ReadToEnd() | Out-Null
    $p.StandardError.ReadToEnd() | Out-Null
    $p.WaitForExit()
} catch {
    # silently ignore post-merge errors
}
