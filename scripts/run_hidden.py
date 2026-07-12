#!/usr/bin/env python3
"""
run_hidden.py — Módulo utilitário para execução 100% silenciosa no Windows.

Usa CREATE_NO_WINDOW (0x08000000) para garantir que NENHUMA janela de console
seja criada, mesmo para binários de console (uv, git, docker, python.exe).

Uso como módulo:
    from run_hidden import run, popen
    run(["uv", "sync"])                    # subprocess.run sem console
    popen(["python", "server.py"])          # subprocess.Popen sem console

Uso como script (via pythonw.exe):
    pythonw scripts/run-hidden.py <comando> [args...]
    pythonw scripts/run-hidden.py uv sync
    pythonw scripts/run-hidden.py git status

No Unix, comporta-se como subprocess.run/Popen normal (sem efeito colateral).

Referência: CREATE_NO_WINDOW = 0x08000000
https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags
"""

import os
import subprocess
import sys
from typing import Any

# Windows: flag que suprime COMPLETAMENTE a criação de janela de console.
# Diferente de SW_HIDE (que cria a janela mas a esconde — ainda pisca),
# CREATE_NO_WINDOW diz ao Windows para NÃO alocar um console sequer.
if os.name == "nt":
    _CREATE_NO_WINDOW = 0x08000000
else:
    _CREATE_NO_WINDOW = 0


def run(args: list[str], **kwargs: Any) -> subprocess.CompletedProcess:
    """
    Wrapper para subprocess.run() que nunca cria janela de console no Windows.
    Aceita os mesmos parâmetros que subprocess.run().
    """
    if os.name == "nt":
        kwargs["creationflags"] = kwargs.get("creationflags", 0) | _CREATE_NO_WINDOW
    return subprocess.run(args, **kwargs)


def popen(args: list[str], **kwargs: Any) -> subprocess.Popen:
    """
    Wrapper para subprocess.Popen() que nunca cria janela de console no Windows.
    Aceita os mesmos parâmetros que subprocess.Popen().
    """
    if os.name == "nt":
        kwargs["creationflags"] = kwargs.get("creationflags", 0) | _CREATE_NO_WINDOW
    return subprocess.Popen(args, **kwargs)


if __name__ == "__main__":
    """Uso direto: pythonw scripts/run-hidden.py <comando> [args...]"""
    if len(sys.argv) < 2:
        print(f"Uso: {sys.argv[0]} <comando> [args...]", file=sys.stderr)
        sys.exit(1)

    result = run(sys.argv[1:])
    sys.exit(result.returncode)
