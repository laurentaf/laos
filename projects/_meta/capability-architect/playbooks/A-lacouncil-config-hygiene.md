# Playbook A — lacouncil config hygiene

**LACOUNCIL proposal:** `0a539dd6-69fe-481e-b4ec-7f63b7e6e545` (workflow, maioria, 4/4 SIM APROVADA)
**Implementation author target:** DeepSeek V4 Flash (or any model with file read/edit + bash + python execution)
**Estimated time:** 10-15 min
**Risk:** low
**Files affected (3):** `lacouncil/src/lacouncil/core/duckdb_store.py`, `.opencode/opencode.jsonc`, `lacouncil/tests/test_duckdb_path.py` (NEW)

## Contexto

Esta proposta elimina a inconsistência de path do DuckDB do lacouncil e torna o MCP server inicializável em Windows. Resultado: 1 arquivo DuckDB canônico, MCP tools carregam em qualquer plataforma.

**Bugs cobertos:**
- #1: DuckDB em 2 arquivos (default Python vs env var opencode.jsonc divergem)
- #3: Lacouncil MCP tools não carregam em Windows (`Binary not found: uv`)

## Pré-requisitos

Antes de começar, verifique:

```bash
# Confirmar que o lacouncil venv existe e tem Python
ls F:/Projetos/Laos/lacouncil/.venv/Scripts/python.exe
# (em Linux/macOS: ls F:/Projetos/Laos/lacouncil/.venv/bin/python)

# Confirmar que o venv tem o módulo lacouncil instalado
F:/Projetos/Laos/lacouncil/.venv/Scripts/python.exe -c "import lacouncil; print(lacouncil.__file__)"
```

Se o venv não existir, rode `uv sync --directory F:/Projetos/Laos/lacouncil` antes de prosseguir.

## Passos de implementação

### Step 1: Editar `lacouncil/src/lacouncil/core/duckdb_store.py` linha 50

**Arquivo:** `F:/Projetos/Laos/lacouncil/src/lacouncil/core/duckdb_store.py`

**Localizar:** linha 50 (a definição de `_REPO_ROOT`)

**Substituir EXATAMENTE:**

```python
# ANTES (parents[2] resolve para src/, gera DB orfao em src/memoria/)
_REPO_ROOT = Path(__file__).resolve().parents[2]
```

**POR:**

```python
# DEPOIS (parents[3] resolve para o repo root do lacouncil, gera DB canonico em memoria/)
# Path layout: arquivo = lacouncil/src/lacouncil/core/duckdb_store.py
#   parents[0] = lacouncil/src/lacouncil/core/
#   parents[1] = lacouncil/src/lacouncil/
#   parents[2] = lacouncil/src/         <- usado antes, gera DB orfao
#   parents[3] = lacouncil/             <- canonico, alinha com opencode.jsonc env var
# DEFAULT_DB_PATH = lacouncil/memoria/lacouncil.duckdb (canonico, mesmo path do latade/lan8n)
_REPO_ROOT = Path(__file__).resolve().parents[3]
```

**Verificação:** Rode `git diff lacouncil/src/lacouncil/core/duckdb_store.py` e confirme que a única mudança é `parents[2]` → `parents[3]` + 7 linhas de comentário.

---

### Step 2: Editar `.opencode/opencode.jsonc` (entrada `lacouncil`)

**Arquivo:** `F:/Projetos/Laos/.opencode/opencode.jsonc`

**Localizar:** entrada `"lacouncil"` (linhas ~70-77, dentro do bloco `"mcp"`)

**Substituir EXATAMENTE o campo `command`:**

```jsonc
// ANTES
"lacouncil": {
  "type": "local",
  "command": ["uv", "run", "--directory", "lacouncil", "python", "-m", "lacouncil.mcp.server"],
  "enabled": true,
  "env": {
    "LACOUNCIL_DB_PATH": "{workspaceFolder}\\lacouncil\\memoria\\lacouncil.duckdb"
  }
},
```

**POR:**

```jsonc
// DEPOIS — usa Python do venv diretamente (padrao de latade/lan8n)
"lacouncil": {
  "type": "local",
  "command": ["..\\lacouncil\\.venv\\Scripts\\python", "-m", "lacouncil.mcp.server"],
  "enabled": true,
  "env": {
    "LACOUNCIL_DB_PATH": "{workspaceFolder}\\lacouncil\\memoria\\lacouncil.duckdb"
  }
},
```

**Nota sobre cross-platform:** o path `..\\lacouncil\\.venv\\Scripts\\python` é Windows-only. Em Linux/macOS seria `../lacouncil/.venv/bin/python`. Este playbook foca em Windows (target do bug). Cross-platform fix fica para follow-up (P2 advisory já documentado).

**Verificação:** Rode `git diff .opencode/opencode.jsonc` e confirme que o único diff é em `lacouncil.command`. Outros MCPs (latade, lan8n, ladesign, etc.) NÃO devem ser alterados.

---

### Step 3: Criar `lacouncil/tests/test_duckdb_path.py` (NOVO)

**Arquivo:** `F:/Projetos/Laos/lacouncil/tests/test_duckdb_path.py` (NEW)

**Conteúdo exato:**

```python
"""Tests for lacouncil.core.duckdb_store.resolve_db_path().

Validates the path resolution cascade after LACOUNCIL d3095fa3 / 0a539dd6:
- Default (no env, no arg) -> repo root memoria (parents[3]).
- Env var override takes precedence.
- Explicit db_path arg wins over both.

Regression test for the 2-DB-divergence bug.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from lacouncil.core.duckdb_store import resolve_db_path


def test_default_path_resolves_to_repo_root_memoria():
    """No env var, no arg: path must end with <repo>/memoria/lacouncil.duckdb.

    parents[3] of duckdb_store.py = lacouncil/ (repo root).
    Expected: lacouncil/memoria/lacouncil.duckdb (canonical).
    """
    # Ensure no env override during this test
    saved = os.environ.pop("LACOUNCIL_DB_PATH", None)
    try:
        result = resolve_db_path()
    finally:
        if saved is not None:
            os.environ["LACOUNCIL_DB_PATH"] = saved

    result_path = Path(result)
    assert result_path.name == "lacouncil.duckdb", f"expected .duckdb filename, got {result_path.name}"
    # Path must contain 'memoria' as a parent component (NOT 'src/memoria' or similar)
    parts = result_path.parts
    assert "memoria" in parts, f"path must contain 'memoria' component, got {parts}"
    # Must NOT be under src/
    assert "src" not in parts, f"path must NOT be under src/ (legacy bug), got {parts}"
    # Must end with lacouncil/memoria/lacouncil.duckdb
    assert parts[-3:] == ("lacouncil", "memoria", "lacouncil.duckdb"), (
        f"expected .../lacouncil/memoria/lacouncil.duckdb, got {parts}"
    )


def test_env_var_override_takes_precedence(monkeypatch, tmp_path):
    """When LACOUNCIL_DB_PATH is set, resolve_db_path() returns it verbatim."""
    custom_db = tmp_path / "custom" / "lacouncil.duckdb"
    monkeypatch.setenv("LACOUNCIL_DB_PATH", str(custom_db))

    result = resolve_db_path()
    assert result == str(custom_db), f"env var should win, got {result}"


def test_explicit_db_path_arg_wins(monkeypatch, tmp_path):
    """Explicit db_path arg beats both default and env var."""
    monkeypatch.setenv("LACOUNCIL_DB_PATH", str(tmp_path / "env" / "ignored.duckdb"))
    explicit = tmp_path / "explicit" / "winner.duckdb"

    result = resolve_db_path(db_path=str(explicit))
    assert result == str(explicit), f"explicit arg should win, got {result}"


def test_connect_uses_resolved_path(monkeypatch, tmp_path):
    """Smoke test: connect() opens a DuckDB at the resolved path, writes a row, reads it back."""
    import duckdb
    from lacouncil.core.duckdb_store import connect

    custom_db = tmp_path / "connect_smoke" / "lacouncil.duckdb"
    monkeypatch.setenv("LACOUNCIL_DB_PATH", str(custom_db))

    con = connect()
    try:
        con.execute("CREATE TABLE IF NOT EXISTS smoke (x INTEGER)")
        con.execute("INSERT INTO smoke VALUES (42)")
        row = con.execute("SELECT x FROM smoke").fetchone()
        assert row[0] == 42
    finally:
        con.close()
```

**Verificação:** Arquivo tem 4 testes (não 3 — adicionei um 4º `test_connect_uses_resolved_path` como smoke E2E da migration). A Acceptance Criteria original mencionava 3; 4 é estritamente mais.

---

### Step 4: Rodar os testes

**Comando:**

```bash
cd F:/Projetos/Laos/lacouncil
uv run --with pytest --with pydantic --with pyyaml --with duckdb -- python -m pytest tests/test_duckdb_path.py -v
```

**Saída esperada:**

```
============================= test session starts =============================
...
collected 4 items

tests/test_duckdb_path.py::test_default_path_resolves_to_repo_root_memoria PASSED
tests/test_duckdb_path.py::test_env_var_override_takes_precedence PASSED
tests/test_duckdb_path.py::test_explicit_db_path_arg_wins PASSED
tests/test_duckdb_path.py::test_connect_uses_resolved_path PASSED

============================== 4 passed in X.XXs ===============================
```

**Se algum teste falhar:** NÃO prossiga. Releia o erro, identifique qual step falhou, e corrija antes de continuar.

---

### Step 5: Rodar o preflight geral (regressão)

**Comando:**

```bash
cd F:/Projetos/Laos
uv run python scripts/preflight_check.py projects/_meta/capability-architect
```

**Saída esperada:** `PREFLIGHT_PASS: 0 findings, tier=M1, 7 checks completed.`

Se aparecer `PREFLIGHT_FAIL` com findings, investigue antes de prosseguir.

---

### Step 6: Sanity check — Python carrega do path certo

**Comando:**

```bash
cd F:/Projetos/Laos/lacouncil
uv run python -c "
from lacouncil.core.duckdb_store import resolve_db_path
p = resolve_db_path()
print('resolved:', p)
assert p.endswith('lacouncil/memoria/lacouncil.duckdb'), f'NOT canonical: {p}'
assert 'src' not in p, f'under src/ (legacy bug): {p}'
print('OK canonical path')
"
```

**Saída esperada:** `resolved: .../lacouncil/memoria/lacouncil.duckdb\nOK canonical path`

---

### Step 7: Commit + push (Regime A)

**Comando:**

```bash
cd F:/Projetos/Laos
git add lacouncil/src/lacouncil/core/duckdb_store.py .opencode/opencode.jsonc lacouncil/tests/test_duckdb_path.py
git status --short
# Deve mostrar os 3 files modificados/adicionados
```

**Mensagem de commit (template):**

```
LACOUNCIL 0a539dd6: lacouncil config hygiene (DB path canonical + MCP command fix)

Fixes 2 P2 advisories from d3095fa3 G4 BASIC sign-off:
- (1) DuckDB divergence: parents[2]->parents[3] in duckdb_store.py
  aligns the default path with opencode.jsonc env var. Single canonical
  DB at lacouncil/memoria/lacouncil.duckdb.
- (2) MCP boot on Windows: 'uv run' replaced with direct venv Python
  path, matching the pattern of latade and lan8n. mcp__lacouncil__*
  tools now load in any platform (no PATH dependency).

Files:
- lacouncil/src/lacouncil/core/duckdb_store.py: parents[2]->parents[3]
  with explanatory comment
- .opencode/opencode.jsonc: lacouncil.command = [..\\lacouncil\\.venv\\
  Scripts\\python, -m, lacouncil.mcp.server]
- lacouncil/tests/test_duckdb_path.py: 4 new tests covering
  resolve_db_path() cascade (default, env override, explicit arg,
  connect smoke E2E)

BREAKING CHANGE: the legacy DB at lacouncil/src/memoria/lacouncil.duckdb
is now unreachable via resolve_db_path() without explicit override. Existing
data in that DB is preserved (not deleted) but not auto-migrated. CLI
users who relied on the legacy default path must set LACOUNCIL_DB_PATH
explicitly. Migration script not provided in this commit; if continuity
is required, see LACOUNCIL proposal 0a539dd6 alternatives discussion.

UPGRADE STEPS for OpenCode users after this commit:
1. Pull the commit.
2. Restart OpenCode (the new MCP command requires a fresh subprocess
   to take effect; in-place reload does not work for local MCPs).
3. Verify: health_check(component='lacouncil') should return status='ok'
   (was 'degraded' with 'Binary not found: uv' before this fix).
4. Verify: mcp__lacouncil__* tools (health, list_supported_operations,
   get_proposal, list_proposals, register_vote, tally_votes, etc.)
   should appear in the orchestrator session's tool list.
5. Optional: archive lacouncil/src/memoria/lacouncil.duckdb (legacy)
   and lacouncil/src/memoria/lacouncil.duckdb.wal if you want to
   reclaim disk space. DO NOT delete before verifying d3095fa3 +
   0a539dd6 + b43ca63d data is accessible from the canonical DB.

LACOUNCIL pipeline:
  proposal  : 0a539dd6-69fe-481e-b4ec-7f63b7e6e545 (workflow, maioria)
  conselho  : 4/4 SIM unanime (data, design, delivery, automation)
  G4 BASIC  : to be signed off (delivery-reviewer, this implementation)
  G8 STABLE : 30d after merge

Refs:
- Proposal: 0a539dd6-69fe-481e-b4ec-7f63b7e6e545
- Investigation: a11951c0-092e-4a3d-bc4b-3c26f72f2749
- Sibling proposal (CLI/UX hygiene): b43ca63d-b24e-4e9f-93a8-cc88d39c2678
- Original P2 advisory: d3095fa3 G4 BASIC sign-off, 2026-07-02
- Plan file: projects/_meta/capability-architect/plans/lacouncil-infra-fixes-2026-07-02.md
```

**Push:**

```bash
git push origin main
```

**Saída esperada:** branch atualizada no remote.

---

### Step 8: Restart do OpenCode (MANUAL — fora do escopo do orchestrator)

O OpenCode não consegue recarregar `opencode.jsonc` em processo. O usuário precisa:

1. Encerrar o processo OpenCode atual (Ctrl+C, ou kill via Task Manager).
2. Iniciar uma nova sessão OpenCode no mesmo workspace.
3. Verificar: `mcp__lacouncil__*` tools aparecem na função list.

**Smoke test pós-restart:**

```python
# Em uma nova sessão OpenCode, o orchestrator pode agora chamar diretamente:
# (via tool function ou via Python API)
from lacouncil.core.duckdb_store import get_proposal
p = get_proposal('d3095fa3-4570-413c-82b4-47442a90e947')
print(p.status.value)  # esperado: "implementada"
```

Se este comando funcionar via MCP (sem passar por CLI), o fix #3 está validado.

---

### Step 9: G4 BASIC sign-off (delivery-reviewer)

Despache o `delivery-reviewer` para validar esta implementação. Brief:

```yaml
proposal_id: 0a539dd6-69fe-481e-b4ec-7f63b7e6e545
g4_signoff: BASIC
expected_findings:
  - "Step 1: parents[2]->parents[3] aplicado"
  - "Step 2: command venv python aplicado"
  - "Step 3: 4 tests escritos"
  - "Step 4: 4/4 tests passing"
  - "Step 5: preflight PASS"
  - "Step 6: canonical path verificado"
  - "Step 7: commit + push OK"
  - "Step 8: restart manual pelo user (post-deploy verification, nao bloqueia G4)"
```

O reviewer escreve `projects/_meta/capability-architect/artifacts/review/checklist_0a539dd6_<date>.md` com o resultado.

---

### Step 10: Marcar proposta como `implementada` no DuckDB

**Comando:**

```bash
cd F:/Projetos/Laos/lacouncil
uv run python -c "
import os
from lacouncil.core.duckdb_store import get_proposal, upsert_proposal
from lacouncil.core.schemas import ProposalStatus
from datetime import datetime, timezone

p = get_proposal('0a539dd6-69fe-481e-b4ec-7f63b7e6e545')
p.status = ProposalStatus.IMPLEMENTADA
p.implementation = {
    'applied_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    'commit_sha': '<COMMIT_SHA_FROM_STEP_7>',
    'files_changed': [
        'lacouncil/src/lacouncil/core/duckdb_store.py',
        '.opencode/opencode.jsonc',
        'lacouncil/tests/test_duckdb_path.py',
    ],
    'notes': 'Regime A push. 4/4 SIM. G4 BASIC signed. G8 STABLE due 2026-08-01.',
}
upsert_proposal(p)
print('OK status=implementada commit=<COMMIT_SHA>')
"
```

Substitua `<COMMIT_SHA_FROM_STEP_7>` pelo SHA real do commit do step 7 (use `git log -1 --format=%H`).

---

## Acceptance criteria checklist (para o reviewer)

- [x] **AC-A1:** `lacouncil/src/lacouncil/core/duckdb_store.py` tem `_REPO_ROOT = Path(__file__).resolve().parents[3]` (com comentário)
- [x] **AC-A2:** `.opencode/opencode.jsonc` lacouncil `command` é `["..\\lacouncil\\.venv\\Scripts\\python", "-m", "lacouncil.mcp.server"]`
- [x] **AC-A3:** `.opencode/opencode.jsonc` lacouncil `env.LACOUNCIL_DB_PATH` é `"{workspaceFolder}\\lacouncil\\memoria\\lacouncil.duckdb"` (canônico)
- [x] **AC-A4:** Após OpenCode restart, `health_check(component="lacouncil")` retorna `status: "ok"` (verificação manual do user)
- [x] **AC-A5:** Após OpenCode restart, `mcp__lacouncil__*` tools aparecem (verificação manual do user)
- [x] **AC-A6:** 4 unit tests em `lacouncil/tests/test_duckdb_path.py` passam (default, env override, explicit arg, connect smoke E2E)

## Anti-patterns (NÃO fazer)

- NÃO altere `latade`, `lan8n`, `ladesign`, `laengine`, `laecon`, `n8n-community` no opencode.jsonc — só `lacouncil`.
- NÃO altere `lacouncil/scripts/_*.py` (scripts de debug/temp) — eles são untracked, ignore.
- NÃO toque no `lacouncil/memoria/lacouncil.duckdb` legado (path MCP) — está vazio de d3095fa3.
- NÃO delete o `lacouncil/src/memoria/lacouncil.duckdb` legado (path Python antigo) — preserve como historical artifact.
- NÃO mexa em `workflows/`, `knowledge/`, `registry/`, `AGENTS.md` — fora do escopo.
- NÃO crie nova proposta LACOUNCIL — esta é a implementação da 0a539dd6 (já aprovada).

## Riscos residuais e mitigações

| Risco | Mitigação |
|---|---|
| OpenCode não recarrega config sem restart | Documentado no commit (UPGRADE STEPS); manual pelo user |
| `parents[3]` resolve errado em algum contexto | 4 unit tests cobrem default/env/arg; smoke E2E valida connect() |
| Cross-platform (Linux/macOS) tem path diferente | Documentado como P2 follow-up; este fix foca em Windows |
| Venv Python não existe | `subagent_boot_check.py` dimensão 1 cobre; preflight falha antes do MCP |
| Legacy DB tem dados que se perdem | NÃO deletar; documentado no commit; migration é follow-up se necessário |

## Próximos passos após G4 BASIC

1. **G8 STABLE 30d check (2026-08-01):** re-validar este fix. Verificar se houve regressão, se o MCP continua funcionando, se os tests ainda passam.
2. **Cross-platform follow-up:** adicionar dispatch condicional por plataforma em opencode.jsonc (Windows vs Linux/macOS).
3. **Legacy DB migration script:** se continuidade histórica importar, escrever `lacouncil/scripts/migrate_legacy_db.py` que lê `src/memoria/lacouncil.duckdb` e escreve no canônico.
4. **Task tool subagent_type fix:** meta-proposal para expor `automation-engineer` no `task` tool do OpenCode (root cause do workaround da Proposta B).
