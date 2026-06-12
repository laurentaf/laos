# Subagent result contract

**Source:** LACOUNCIL proposal `dbc88097-2ef3-475d-bc10-1ebf76027150`
(aprovada 4/4 SIM, maioria, 2026-06-09)

**Purpose:** Reduce orchestrator context pollution from subagent dispatches.
Every `task` dispatch previously returned full subagent output into the
orchestrator context. After 2-3 rounds, context was 30-40% full from
return values alone. The orchestrator is a coordinator, not a worker —
it needs verdicts, not full results.

## Receipt schema

Every subagent returns ONLY a compact receipt to the orchestrator:

```yaml
status: ok | error          # enum, required
summary: str                # max 2 lines, required — must be actionable
details_path: str           # path to full output file, required
task_id: str                # dispatch task ID (ses_xxx format), required
error_class: str            # optional — only on status: error
```

### Field rules

- **status** — `ok` means the task completed successfully. `error`
  means it failed or was blocked. No other values.
- **summary** — max 2 lines. Must be actionable: state what was
  created/changed/measured, not just "done". See examples below.
- **details_path** — absolute path to the full output file. Always
  under `artifacts/<project>/reviews/<task-id>.md`.
- **task_id** — the dispatch task ID passed in the dispatch payload.
- **error_class** — optional. Values: `timeout`, `auth_failure`,
  `validation_error`, `missing_data`, `mcp_failure`, `permission_denied`.
  Enables the orchestrator to route errors without reading the full file.

## Where detail files go

```
artifacts/<project>/reviews/<task-id>.md
```

- `reviews/` is the subdirectory for full subagent output files.
- `task-id` matches the `task_id` in the receipt.
- The orchestrator reads the receipt, drills into the detail file only
  when needed (error investigation, deeper verification, or user request).

## When the orchestrator drills into details

| Receipt status | Orchestrator action |
|---|---|
| `ok` | Act on summary. Drill into details only if user asks or deeper verification needed. |
| `error` | Always read the detail file. Route based on `error_class` if present. |
| `ok` + `summary` ambiguous | Read the detail file to clarify before proceeding. |

## Summary examples

### Good (actionable)

- `Dashboard wireframe created, 3 pages, 847 lines, artifacts/design/wireframe-v2.html`
- `SQL model spec written: dim_customer grain=customer_id, 4 partition strategies, 2 DQ rules`
- `N8N workflow exported: daily-report-email.json, trigger=schedule, SLA=5min`
- `WDL verdict READY, 3/3 on 3-Q, plan_id=linkedin-content-q3, verified_by=delivery-reviewer`
- `Capability scaffold created: laecon, 17 files, registry updated, BASIC status`
- `Data gap reported: orders_2026q2 missing (API 401), awaiting user decision`

### Bad (not actionable)

- `Done`
- `Task completed successfully`
- `Finished`
- `Working on it`

The summary must allow the orchestrator to decide at a glance whether
to drill in, route elsewhere, or move on.

## Error class routing

The `error_class` field enables fast routing without reading the file:

| error_class | Orchestrator routing |
|---|---|
| `timeout` | Retry with longer timeout or escalate |
| `auth_failure` | Check credentials / ask user |
| `validation_error` | Read details, fix, re-dispatch |
| `missing_data` | Follow Hard Rule #11 (synthetic data protocol) |
| `mcp_failure` | Check MCP health, ask user to restart |
| `permission_denied` | Check permissions / escalate |

## Atomicity

The detail file write must complete BEFORE the receipt is returned.
The orchestrator must never receive a receipt pointing to a non-existent
file.

## §4 — Suficiência não é steering

**Source:** CodeGraph `CLAUDE.md` §"Retrieval performance & dynamic-dispatch
coverage" + `docs/design/agent-codegraph-adoption.md` §P1 (adopted 2026-06-12).

**Doutrina central:** quando um subagente (data-architect, dashboard-designer,
etc.) retorna um output, esse output deve ser **completo o suficiente para
o orchestrator tomar a próxima decisão sem precisar ler arquivos para confirmar.**

Não tente alcançar isso com prompts mais verbosos no lado do caller.
Prompt mais verboso **regressa** wall-clock (CodeGraph validated: wording
variants nunca moveram tool-choice de forma confiável em agentes).
O que realmente funciona é output suficientemente bom que o caller
**naturalmente para**.

**O que significa "suficiente" na prática:**

| Subagente | Output suficiente inclui |
|---|---|
| `data-architect` | Schema completo, sample rows (se relevante), DQ rules documentadas, SQL pronto para executar — **sem** "confirme executando o SQL" |
| `dashboard-designer` | Wireframe HTML funcional, tokens referenciados, breakpoints listados — **sem** "abra o arquivo para ver como ficou" |
| `automation-engineer` | Workflow JSON completo, trigger documentado, SLA definido — **sem** "valide no n8n exportando" |
| `capability-architect` | Scaffold completo (todos os arquivos), registry atualizado, charter escrito — **sem** "confira se os 17 arquivos estão lá" |
| `delivery-reviewer` | Checklist com todos os P0 marcados, cada finding com `file:line` acionável — **sem** "leia o padroes-entrega.md para entender o que passou" |

**Anti-pattern que nunca funciona:** no orchestrator prompt, escrever
"always prefer latade_execute_sql over reading files" ou similar.
O orchestrator vai ignorar. O subagente não vai mudar de comportamento.
O tool vai continuar retornando output incompleto.

**O que funciona:** fazer o tool output ser tão bom que ler mais é
redundante. Para cada tool, pergunte: "o caller consegue tomar a decisão
só com este output, ou vai precisar ler algo?" Se a segunda, o output
é insuficiente — e a resposta não é "melhore o prompt", é
"melhore o tool".

**Teste:** rode `knowledge/eval-methodology.md` com e sem a mudança.
Se o arm "com" tem menos `mcp__*` calls E menos `Read` pelo orchestrator,
o output ficou mais suficiente.

## §5 — Erros em formato de sucesso

**Source:** CodeGraph `docs/design/agent-codegraph-adoption.md` §P1
"Errors teach abandonment" (adopted 2026-06-12).

**Regra:** todo `isError: true` é uma mensagem de **"pare de tentar"**.
Uma ou duas respostas com `isError: true` no início de uma sessão e o
agent para completamente de usar o tool — mesmo quando o tool
funcionaria bem para queries subsequentes.

**Classificação de condições:**

| Condição | Resposta correta | isError? |
|---|---|---|
| Segurança: path traversal tentado | `isError: true` com mensagem de recusa | **SIM** — Security refusal |
| Segurança: segredos detectados | `isError: true` | **SIM** — Security |
| Tool genuinamente quebrado (crash, panic) | `isError: true` com retry hint | **SIM** — genuine malfuncion |
| Projeto não indexado | `status: ok + "não indexado ainda, rode `codegraph init` primeiro"` | **NÃO** — esperado/recuperável |
| Símbolo não encontrado | `status: ok + listagem do que existe (você quis dizer X?)` | **NÃO** — esperado/recuperável |
| Arquivo não no índice | `status: ok + `file not indexed: <path>. Read it directly.` | **NÃO** — esperado/recuperável |
| Workspace vazio (sem .codegraph/) | `tools/list` retorna [] + 2 linhas "inactive" | **NÃO** — ausência é o sinal |
| Dados insuficientes para processar | `status: ok + guidance` de como obter os dados | **NÃO** — esperado/recuperável |

**Padrão de resposta esperada/recuperável (success-shaped error):**

```yaml
# Projeto não indexado
status: ok
summary: "Projeto não indexado — codegraph serve não encontra .codegraph/"
details_path: ""
task_id: ""
# O caller sabe o que fazer (não é erro, é estado)

# Símbolo não encontrado — sugira alternativas
status: ok
summary: "Symbol 'FooBar' não encontrado. Encontrados: FooBarService (3 calls), fooBar (variable). Quer explorar um destes?"
details_path: ""
task_id: ""

# Arquivo não no índice
status: ok
summary: "src/auth.py não está no índice. O arquivo existe em disco — leia diretamente ou rode codegraph sync."
details_path: ""
task_id: ""
```

**O que NÃO fazer nunca:**
```yaml
# ERRADO — o caller não sabe o que fazer
status: error
summary: "Symbol not found"

# ERRADO — isError para condição esperada
isError: true
message: "Symbol not found"

# ERRADO — isError para condição recuperável
isError: true
message: "execute_sql failed: table not found. Run load_csv_to_bronze first."
```

**A regra prática:** se o caller pode fazer algo concreto sobre o
problema (rodar init, read arquivo diretamente, corrigir input), é
`status: ok + guidance`. Só é `isError` quando o caller **não pode
fazer nada** além de parar de tentar ou escalar.

** delivery-reviewer valida isso?** Sim — P0-21 em `padroes-entrega.md`
valida que cada tool response segue esta regra.

## Examples

### Successful dispatch

```yaml
status: ok
summary: "Dim customer model spec written: grain=customer_id, 12 columns, 2 partition strategies, 3 DQ rules"
details_path: "E:/projects/myproject/artifacts/reviews/ses_abc123.md"
task_id: "ses_abc123"
```

### Failed dispatch

```yaml
status: error
summary: "Latade MCP returned 401 on execute_sql; credentials missing in .env"
details_path: "E:/projects/myproject/artifacts/reviews/ses_def456.md"
task_id: "ses_def456"
error_class: "auth_failure"
```

### Blocked dispatch (missing data)

```yaml
status: error
summary: "orders_2026q2 table empty (0 rows); cannot build sales model without real data"
details_path: "E:/projects/myproject/artifacts/reviews/ses_ghi789.md"
task_id: "ses_ghi789"
error_class: "missing_data"
```
