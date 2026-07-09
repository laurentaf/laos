# Plano: 4 lacouncil infra fixes (2026-07-02)

**Origem:** P2 advisory findings do delivery-reviewer na G4 BASIC sign-off de `d3095fa3`.
**Status:** DRAFT — aguardando aprovação do orchestrator para criar as propostas LACOUNCIL.

## Sumário executivo

| # | Bug | Categoria | Strategy | Acoplamento | LOC | Risk |
|---|-----|-----------|----------|-------------|-----|------|
| 1 | DuckDB em 2 arquivos | workflow | maioria | acoplado com #3 | ~1 linha | low |
| 2 | `automation-engineer` não exposto no `task` tool | knowledge | maioria | independente | ~5 linhas | zero |
| 3 | Lacouncil MCP tools não carregados | registry | maioria | acoplado com #1 | ~3 linhas | low |
| 4 | `lacouncil proposal show` Unicode error Windows | workflow | maioria | independente | ~2 linhas | zero |

**Recomendação de bundling: 2 propostas (A + B).** Ver §"Bundling" abaixo.

---

## Diagnóstico detalhado

### #1 — Lacouncil DuckDB em 2 arquivos

**Sintoma:** Propostas e votos gravados em `lacouncil/src/memoria/lacouncil.duckdb` (default Python) vs `lacouncil/memoria/lacouncil.duckdb` (opencode.jsonc env var). Conteúdo diverge:
- `src/memoria/`: 3 proposals, 11 votes (d3095fa3 está aqui)
- `lacouncil/memoria/`: 2 proposals, 2 votes (DB órfão do opencode.jsonc)

**Causa raiz:** `duckdb_store.py:50`:
```python
_REPO_ROOT = Path(__file__).resolve().parents[2]
```
Arquivo: `lacouncil/src/lacouncil/core/duckdb_store.py`
- `parents[0]` = `lacouncil/src/lacouncil/core/`
- `parents[1]` = `lacouncil/src/lacouncil/`
- `parents[2]` = `lacouncil/src/`
- `parents[3]` = `lacouncil/` (repo root)

Default path = `lacouncil/src/memoria/lacouncil.duckdb`.
opencode.jsonc env var = `lacouncil/memoria/lacouncil.duckdb` (= `parents[3] + memoria/`).

**Fix recomendado:** mudar `parents[2]` → `parents[3]` em `duckdb_store.py`. Segue o padrão dos outros MCPs (latade, lan8n) que colocam a memoria no repo root, não em `src/`.

**Alternativas rejeitadas:**
- Mover opencode.jsonc env var para `lacouncil/src/memoria/...` — violaria a convenção de manter `memoria/` no repo root.
- Symlink — frágil no Windows.

**Files:** `lacouncil/src/lacouncil/core/duckdb_store.py` (1 linha)
**Risk:** low. DB legado `src/memoria/lacouncil.duckdb` permanece como read-only legacy; pode ser removido depois de validar que tudo funciona.
**Categoria:** workflow (lacouncil config) | **Strategy:** maioria

---

### #2 — `automation-engineer` não exposto no `task` tool

**Sintoma:** `task` tool rejeita `subagent_type: "automation-engineer"`:
```
Error: Unknown agent type: automation-engineer is not a valid agent type
```
Mas o agent file `.opencode/agent/automation-engineer.md` existe (verificado via `os.listdir`). WDL gate aceitaria (valida por diretório), mas o `task` tool falha antes de chegar no WDL gate.

**Causa raiz:** Bug no OpenCode — lista hardcoded de `subagent_type` no `task` tool não inclui `automation-engineer`. O agent file está presente e o WDL gate (que valida por diretório em runtime) aceitaria. Mas o `task` tool tem validação própria que rejeita antes.

**Fix recomendado:** Workaround documentado em `.opencode/agent/orchestrator.md` §"Conselho voting". O 4º voto do Conselho é registrado via `chief-engineer` (que está na lista hardcoded) com `voter: "automation-engineer"` no payload da `lacouncil.vote.register` — efeito idêntico no DuckDB, mas bypassa o wall do `task` tool.

**Alternativas rejeitadas:**
- Reportar upstream OpenCode — útil mas fora do escopo LAOS.
- Renomear o agent file para `chief-engineer` — confuso, conflita com o `chief-engineer` existente (que é diferente — é evaluator de consensus empírico).

**Files:** `.opencode/agent/orchestrator.md` (knowledge entry, ~5 linhas em §"Conselho voting")
**Risk:** zero — knowledge entry apenas, sem code change.
**Categoria:** knowledge | **Strategy:** maioria

---

### #3 — Lacouncil MCP tools não carregados na sessão

**Sintoma:** `health_check(component="lacouncil")` retorna:
```json
{"status": "degraded", "error": "Binary not found: uv", "latency_ms": 1}
```
E `mcp__lacouncil__*` tools não aparecem na função list do orchestrator. A sessão inteira deste projeto não tem acesso ao lacouncil via MCP — só via CLI ou Python API.

**Causa raiz:** `opencode.jsonc:70-77`:
```json
"lacouncil": {
  "type": "local",
  "command": ["uv", "run", "--directory", "lacouncil", "python", "-m", "lacouncil.mcp.server"],
  "enabled": true,
  "env": {
    "LACOUNCIL_DB_PATH": "{workspaceFolder}\\lacouncil\\memoria\\lacouncil.duckdb"
  }
}
```

O `["uv", "run", ...]` faz com que o subprocess do OpenCode precise resolver `uv` no PATH. Em Windows, o subprocess do OpenCode pode não herdar o PATH completo do user, especialmente quando invocado via hook/plugin. O mesmo padrão NÃO é usado pelos outros MCPs:
- `latade`: `["..\\latade\\.venv\\Scripts\\python", "..\\latade\\mcp_server\\server.py"]`
- `lan8n`: `["..\\lan8n\\.venv\\Scripts\\python", "-m", "lan8n.mcp.server"]`

Ambos usam o Python do venv diretamente, sem o `uv run` indirection.

**Fix recomendado:** Mudar `command` para:
```json
"command": ["..\\lacouncil\\.venv\\Scripts\\python", "-m", "lacouncil.mcp.server"]
```
E aproveitar para corrigir o `LACOUNCIL_DB_PATH` env var para o path canônico (após o fix de #1):
```json
"LACOUNCIL_DB_PATH": "{workspaceFolder}\\lacouncil\\memoria\\lacouncil.duckdb"
```
(Este path JÁ é o que o env var diz; é o DEFAULT_DB_PATH do Python que está errado. Após #1, os dois convergem.)

**Files:** `.opencode/opencode.jsonc` (1 entry, ~3 linhas)
**Risk:** low. Requer restart do OpenCode para efeito. Validar que o lacouncil venv existe em `F:\Projetos\Laos\lacouncil\.venv\` (verificado durante d3095fa3 — `uv sync` rodou OK).

**Caveat:** Se o restart não for suficiente, pode ser que o OpenCode tenha um cache de MCP tools que precisa ser limpo. Workaround: kill all opencode processes, restart session.

**Categoria:** registry (opencode.jsonc) | **Strategy:** maioria

---

### #4 — `lacouncil proposal show` Unicode error no Windows

**Sintoma:** Ao rodar `lacouncil proposal show <id>` no console Windows (cp1252):
```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2265' in position 711
```

**Causa raiz:** Rich console (usado pelo CLI Typer) no Windows default não usa UTF-8 para o stdout. Quando a proposta tem chars não-ASCII (ex: `≥` que aparece no campo `impacto` quando escrito sem escape), o encoding cp1252 falha.

**Fix recomendado:** Adicionar `sys.stdout.reconfigure(encoding="utf-8")` no topo de `__main__.py` (após `from __future__ import annotations` e antes de `import typer`). Python 3.7+ tem `reconfigure` em `TextIOBase`. Idiomático e zero-risk.

**Alternativas rejeitadas:**
- Setar `PYTHONIOENCODING=utf-8` no env var do opencode.jsonc — funciona, mas só quando invocado via OpenCode; quando invocado via `uv run` direto ou via shell, não pega.
- `Console(file=sys.stdout, legacy_windows=False)` em Rich — não é kwarg válido; `legacy_windows` está em `Console`, mas tem outras implicações.
- Reescrever todas as strings para ASCII — perde informação.

**Files:** `lacouncil/src/lacouncil/__main__.py` (2 linhas adicionadas)
**Risk:** zero. Apenas força encoding no stdout; resto do comportamento inalterado.
**Categoria:** workflow (CLI) | **Strategy:** maioria

---

## Acoplamentos

```
#1 (DB path) ←──── acoplado ────→ #3 (MCP command)
            Ambos tocam o path
            canônico do DuckDB.
            Fix em #1 antes de
            #3 (ou no mesmo
            batch) garante que
            MCP e Python usem
            o mesmo arquivo.

#2 (knowledge) ── independente ── #4 (CLI encoding)
```

**Implicação:** #1 e #3 devem ser implementados na mesma proposta (Proposta A). #2 e #4 podem ser separados (Proposta B) ou unificados (independem entre si).

---

## Bundling — 3 opções analisadas

### Opção A: 2 propostas (RECOMENDADA)

| Proposta | Categoria | Strategy | Cobre | Acoplamento |
|---|---|---|---|---|
| **A: lacouncil config hygiene** | workflow | maioria | #1, #3 | DB path + MCP command |
| **B: lacouncil CLI/UX hygiene** | workflow | maioria | #2, #4 | Knowledge + CLI fix |

**Vantagens:**
- Categoria coerente em cada proposta (workflow para ambos)
- Acoplamentos respeitados
- 2 ciclos Conselho → capability-architect → delivery-reviewer (paralelizáveis se necessário)
- Cada uma é simples o suficiente para passar em um único round

**Estimativa:** 30-45 min total (cada proposta é ~3 files change, 2-3 unit tests, 1 acceptance criteria cada)

### Opção B: 4 propostas separadas

**Vantagens:** máxima granularidade, cada bug isolado.
**Desvantagens:** burocracia 4× maior sem benefício prático; Conselho delibera 4× sobre o mesmo assunto.

### Opção C: 1 proposta consolidada

**Vantagens:** 1 ciclo único.
**Desvantagens:** mistura categoria (workflow + knowledge + registry não é workflow puro); complica o acceptance criteria.

### Decisão: **Opção A**.

---

## Acceptance criteria

### Proposta A: lacouncil config hygiene (#1 + #3)

- [ ] **AC-A1:** `lacouncil/src/lacouncil/core/duckdb_store.py` tem `_REPO_ROOT = Path(__file__).resolve().parents[3]` (com comentário explicando o porquê)
- [ ] **AC-A2:** `.opencode/opencode.jsonc` lacouncil `command` é `["..\\lacouncil\\.venv\\Scripts\\python", "-m", "lacouncil.mcp.server"]` (sem `uv run`)
- [ ] **AC-A3:** `.opencode/opencode.jsonc` lacouncil `env.LACOUNCIL_DB_PATH` é `"{workspaceFolder}\\lacouncil\\memoria\\lacouncil.duckdb"` (canônico, alinhado com #1)
- [ ] **AC-A4:** Após OpenCode restart, `health_check(component="lacouncil")` retorna `status: "ok"` (não `degraded`)
- [ ] **AC-A5:** Após OpenCode restart, `mcp__lacouncil__*` tools (health, list_supported_operations, investigate, create_proposal, get_proposal, list_proposals, register_vote, tally_votes, implement_proposal, record_project, detect_patterns, log_user_question, detect_user_question_patterns, create_proposal_from_pattern) aparecem na função list do orchestrator
- [ ] **AC-A6:** Unit test em `lacouncil/tests/test_duckdb_path.py` confirma `resolve_db_path()` retorna o path canônico em 3 cenários: (a) sem env var, (b) com env var override, (c) com `db_path` arg explícito

### Proposta B: lacouncil CLI/UX hygiene (#2 + #4)

- [ ] **AC-B1:** `.opencode/agent/orchestrator.md` §"Conselho voting" tem nota: "automation-engineer agent type não está exposto no `task` tool desta sessão. Workaround: dispatch via `chief-engineer` com voter string `automation-engineer` no payload da `lacouncil.vote.register`. Mesmo efeito no DuckDB; preserva integridade do log do Conselho."
- [ ] **AC-B2:** `lacouncil/src/lacouncil/__main__.py` tem `sys.stdout.reconfigure(encoding="utf-8")` no topo (após `from __future__ import annotations`)
- [ ] **AC-B3:** `lacouncil proposal show d3095fa3-4570-413c-82b4-47442a90e947` não falha com `UnicodeEncodeError` quando stdout é Windows-cp1252 (subprocess test)
- [ ] **AC-B4:** Smoke test E2E: dispatch do Conselho (4 subagents, 1 deles via `chief-engineer` workaround) termina com tally 4/4 sem NAO

---

## Plano de execução

### Sequência

```
T+0   Orchestrator cria Proposta A (Python API)
T+2   Orchestrator cria Proposta B (Python API)
T+4   Orchestrator convoca Conselho para A (4 dispatches em paralelo)
T+8   Conselho A delibera → tally → APROVADA (esperado)
T+10  Orchestrator convoca Conselho para B (4 dispatches em paralelo)
T+14  Conselho B delibera → tally → APROVADA (esperado)
T+16  capability-architect implementa A
T+22  capability-architect implementa B (paralelo com A se independente)
T+25  delivery-reviewer G4 BASIC para A → APPROVED (esperado)
T+27  delivery-reviewer G4 BASIC para B → APPROVED (esperado)
T+30  Commit A + push origin/main (Regime A)
T+32  Commit B + push origin/main (Regime A)
T+35  Propostas marcadas como implementada no DuckDB
```

**Total estimado: 30-45 min.**

### Paralelização

- A e B podem rodar em paralelo (são propostas independentes, capability-architect e delivery-reviewer são stateless através de propostas).
- Mas para evitar race conditions no `.opencode/opencode.jsonc` (se A e B tocam o mesmo arquivo), serializar.
- A e B NÃO tocam o mesmo arquivo (A: `duckdb_store.py` + `opencode.jsonc`; B: `__main__.py` + `orchestrator.md`). Paralelizável.

### Riscos e mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| OpenCode restart não carrega novo MCP config | low | high (A fica sem efeito) | Documentar no commit que restart é manual; commit inclui nota de release |
| `parents[3]` resolve para path errado em algum contexto | very low | medium | Unit test cobre 3 cenários; smoke test pós-deploy |
| Workaround #2 conflita com fix upstream futuro do OpenCode | medium | low | Knowledge entry cita issue upstream (se reportado); workaround é trivial de reverter |
| Reconfigure stdout quebra em Python < 3.7 | zero | zero | LAOS requires-python = ">=3.11" (per pyproject.toml) |
| `lacouncil.mcp.server` não tem entry point com `__main__` | low | medium | Verificado: `server.py:249-250` tem `if __name__ == "__main__": main()` |

---

## G8 STABLE coupling com d3095fa3

A re-validação G8 de d3095fa3 está due 2026-08-01 (30d). Estas 2 propostas (A + B) podem ser re-validadas na mesma janela. Sugestão: adicionar este plano como sub-projeto de "lacouncil infra evolution" com G8 due 2026-08-01 também, e re-validar tudo junto.

---

## Pré-requisitos antes de executar

- [ ] Orchestrator confirma que o user aprova Opção A (2 propostas, maioria, workflow)
- [ ] Orchestrator confirma que o restart do OpenCode após #3 é aceitável (pode ser feito pelo user)

## Não-objetivos (out of scope)

- Não vou tocar nos untracked files de debug (`_diag_*.py`, `tmp_proposal.json`, etc.) — esses são lixos de sessões anteriores.
- Não vou alterar `projects/_meta/readme-improvement/*` ou `.opencode/plugins/laos-infra.ts` (mudanças pré-existentes não relacionadas).
- Não vou propor mudar a categoria ou strategy — maioria está correto para ambos.

---

## Próximo passo

Orchestrator: revisar este plano, ajustar bundling se necessário, e dar luz verde para criar as 2 propostas LACOUNCIL.
