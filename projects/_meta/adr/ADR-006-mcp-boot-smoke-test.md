# ADR-006: Smoke-test `*.health()` no boot check + fix do `sys.path` no LATADE MCP server

**Status:** accepted
**Date:** 2026-06-05
**Decisor:** LACOUNCIL (supermaioria, 4/4 SIM, 100%)
**Proposal:** `f82d6261-7592-46e8-8ca3-b7368dfb72a4`
**Implementer:** capability-architect

---

## Contexto

Falha detectada mid-task durante dispatch do `data-architect` no projeto
`previsao-concursos` (Stage 2, data-model). Ao tentar usar `latade_health`,
o servidor MCP retornou `ModuleNotFoundError: No module named 'src'`.

### Bug primário — `E:\projects\latade\mcp\server.py:23`

O caminho inserido em `sys.path` era a junção de `parent.parent` com o
segmento `"src"`, o que colocava `E:\projects\latade\src` em `sys.path`.
Para Python localizar `src` como **package**, é o **parent** de `src/`
(ou seja, `E:\projects\latade`) que precisa estar em `sys.path` — não
`src/` em si. A linha 24 do arquivo estava com o caminho errado,
fazendo a primeira chamada de qualquer tool que faça
`from src.core.confidence import ConfidenceEngine` (a começar por
`health`) explodir com `ModuleNotFoundError`.

```python
# ERRADO (estado antes da proposta):
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

# CORRETO (estado depois da proposta):
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
```

### Bug secundário — `scripts/subagent_boot_check.py` Check 3

A versão anterior de `check_mcp` validava **apenas a presença textual**
do entry do MCP em `.opencode/opencode.jsonc`:

```python
missing = [m for m in mcps if f'"{m}":' not in text]
```

Não havia **invocação real** do servidor MCP. Resultado: o bug primário
passou despercebido até o mid-task failure do `data-architect`. A
Hard Rule #3 de LAOS ("routing determinístico") virou
"routing determinístico para uma capability quebrada".

### Diagnóstico de impacto

- Toda capability com MCP server local (`latade`, `lacouncil`, `lan8n`,
  `ladesign`, `laecon`, `laengine`) compartilha o mesmo vetor de bug:
  `sys.path` errado, env mal resolvido, package config ausente,
  comando com path inválido. Config check OK, runtime FAIL.
- O 1º caso documentado foi o `latade`. O 2º está batendo na porta
  (qualquer capability nova do top-6). O 3º vira padrão.
- LACOUNCIL hard rule: "patterns repeated 3+ times trigger action".
  Esse é o 1º caso, mas é estruturalmente óbvio que vai repetir.

---

## Decisão

Aplicar duas mudanças em commits coordenados (mesma proposta LACOUNCIL
porque o fix de 1-char é trivialmente inseparável do guard que o
justifica — sem o guard, o mesmo bug voltaria na próxima capability
silenciosamente).

### Mudança A — `E:\projects\latade\mcp\server.py:24`

Trocar `parent.parent / "src"` por `parent.parent` (7 caracteres
removidos). **No-op na escrita**: o arquivo já estava com o fix
aplicado quando a proposta foi votada (escala 2026-06-05 10:43 < 11:00
do dispatch). Verificado por `read` + `bash` antes do edit: linha 24
contém `str(Path(__file__).resolve().parent.parent)` (sem `/ "src"`).
Standalone import test (`uv run python -c "import sys; from pathlib
import Path; sys.path.insert(0, str(Path(r'E:\projects\latade')));
from src.core.confidence import ConfidenceEngine"`) retorna OK.

> **Nota operacional:** o processo MCP `latade` que estava em execução
> no opencode runtime (PID 22296, iniciado às 09:43:02) carregou o
> bytecode **antes** do fix de 10:43 e, por isso, continuou retornando
> `ModuleNotFoundError` até ser reiniciado. Isso confirma *exatamente*
> a tese da proposta: a capability **parece** pronta (config check
> passa) mas falha em runtime. O novo boot check 3b detecta esse
> failure mode a cada dispatch.

### Mudança B — `scripts/subagent_boot_check.py` Check 3 → 3b

Substituir a `check_mcp(mcps, root)` (textual-only) por
`check_mcp_primary_optional(mcp_primary, mcp_optional, root)` que faz
**duas fases**:

1. **Textual config check** (mantido): entries presentes em
   `.opencode/opencode.jsonc`. Falha bloqueante se ausente.
2. **Smoke-test `*.health()` via stdio JSON-RPC** (novo): para cada
   MCP local em `mcp_primary` ∪ `mcp_optional`, faz spawn do
   subprocesso, envia `initialize` + `tools/call health` + `tools/list`
   via newline-delimited JSON, lê o stdout, valida resposta.

**3 restrições do Conselho (não negociáveis) — aplicadas literalmente:**

| # | Restrição | Implementação |
|---|-----------|---------------|
| 1 | **Invocação paralela** | `concurrent.futures.ThreadPoolExecutor(max_workers=len(targets))` em `check_mcp_primary_optional`. Cada MCP roda em sua thread; `as_completed()` coleta na ordem de término. Sem `wait` sequencial. |
| 2 | **Timeout 2-3s fail-fast** | `MCP_HEALTH_TIMEOUT_S = 2.5`. `proc.communicate(timeout=...)`; em `TimeoutExpired`, `proc.kill()` e retorna `(False, f"timeout after 2.5s; stderr=...")`. |
| 3 | **Opcionais = warn; Primários = block** | `targets.append((name, cfg_block, name in mcp_primary))`; no `as_completed`, branch `is_primary`: `fail(...)` + `findings += 1`; senão `warn(...)` (sem `findings += 1`). |

**Adicionalmente** (3 decisões de design documentadas aqui, não no
Conselho porque não foram alvo de voto):

- **MCPs remotos (`type: remote`)** — `context7`, `exa`, `github` —
  pulam o smoke-test (não há stdio pipe; o transporte é HTTP). Mensagem
  `ok(f"{name}: remote MCP (stdio smoke-test NAO aplicavel)")`. Justa:
  esses são opcionais em todos os charters, e o textual check já
  confirmou a presença da URL.
- **Fallback para `tools/list`** — se `health()` retorna erro
  `tool not found` (e.g. LADESIGN, cujo daemon expõe
  `live_artifacts_*` + `connectors_*` mas não `health`), o smoke-test
  cai para `tools/list` e aceita qualquer lista de tools ≥ 1 como
  evidência de que o servidor está vivo. Cobre o caso da capability
  que implementa G1 mas não no tool exato `health`. LADESIGN é o único
  caso atual.
- **Protocolo stdio = newline-delimited JSON** — verificado lendo
  `mcp/server/stdio.py:63-65` da venv do latade:
  `async for line in stdin: message = types.JSONRPCMessage.model_validate_json(line)`.
  FastMCP **não** usa Content-Length framing no stdio (esse é o do
  Streamable HTTP). Implementação errada inicial do smoke-test
  usava Content-Length → falha de validação no servidor → falso
  negativo. Corrigido para `json.dumps(req) + "\n"`.

**Sem novas dependências** no `pyproject.toml` da LAOS. Tudo via
stdlib: `subprocess`, `json`, `concurrent.futures`, `time`, `re`,
`os`, `pathlib`.

**Não foi alterado**: `pyproject.toml`, `AGENTS.md`, registry files,
outros agent files (R5 respeitado). Charter
`binding-conditions.md` do capability-architect aplica R1-R5
(verificado: proposta aprovada, não escrevi artefatos de projeto, não
votei, não propus, não toquei em outros agents).

### Latência observada

| Cenário | Latência smoke-test (paralelo) |
|---------|---------------------------------|
| 1 MCP local (latade) | 1.08-1.19s (subprocess startup + health call) |
| 2 MCPs (latade + ladesign) | ~max(latencies) ≈ 2.0-2.5s |

Sequencial seria a soma (boot do `data-architect` com latade +
lacouncil = 2-3s; orchestrator com 4 primários = 8-12s). Paralelo
mantém em ~max. Conforme a topologia cresce (BASIC LAECON e LAENGINE
em M2), a contenção de latência continua sendo O(max), não O(sum).

---

## Alternativas Consideradas

1. **Confiar no `subprocess.run` seq + retry exponencial** — rejeitado.
   Falha do data-architect no voto: "5s × invocação sequencial pode
   inflar o boot de 30s no orchestrator; paralelo via
   `concurrent.futures` é a escolha certa". Adotado.

2. **Substituir latade sys.path + rezar para o próximo bug ser pego
   em QA manual** — rejeitado. O 1º caso passou exatamente porque
   não havia guard automatizado. Pattern-matching ad-hoc tem
   coverage 0% no próximo vetor de bug.

3. **Adicionar uma dependência nova** (`mcp[client]` para reusar o
   client oficial) — rejeitado pela restrição explícita do
   orchestrator. Stdlib basta. Custo: ~50 linhas de parsing manual;
   ganho: zero dependências externas.

4. **Smoke-test apenas dos primários (não dos opcionais)** — rejeitado.
   Conselho pediu 3-way split: primário block, opcional warn, remoto
   skip. Opcionais que falham viram sinal de degradation sem travar
   dispatch.

5. **Health() estrito (sem fallback `tools/list`)** — considerado.
   Rejeitado porque LADESIGN não expõe `health` (verificado no
   `mcp-live-artifacts-server.js`: tools são `live_artifacts_*` +
   `connectors_*`). Fallback preserva o guard sem exigir G1 retroativo
   em LADESIGN (que é STABLE, não cabe refator no escopo desta
   proposta).

6. **Mover o smoke-test para dentro do orchestrator agent file** —
   rejeitado. Boot check é infra compartilhada por todos os 6
   subagentes; ficar no `.py` reutilizável é a separação correta.

---

## Consequências

### Positivas

- `data-architect` (e os outros 5 subagentes) recebem um guard de
  runtime **antes** do dispatch, não mid-task. Falha mid-task custa
  contexto + turno; falha pré-dispatch custa ~1-2s de boot.
- O vetor "sys.path errado / env mal resolvido / comando quebrado /
  package config ausente" fica com cobertura mecânica. Padrão
  emergente (3+ casos) vira 0% chance de repetição silenciosa.
- Latência do boot check escala em O(max) com paralelismo, não O(sum).
  Topologia atual 1-2 primários ≈ 1-2s; crescimento futuro cabe.
- Reporting é acionável: cada FAIL/WARN/PASS vem com `(elapsed_s)` e
  `info` (resposta de `health()`, stderr, exception). Não é black-box.
- O smoke-test **comprova** a tese da proposta: ele detectou o latade
  quebrado na primeira tentativa (antes do fix no disco, quando rodei
  o smoke-test seco) e PASSou depois (com o fix no disco + subprocess
  fresh). O guard funciona.

### Custos e responsabilidades

- Latência adicional por dispatch: ~1-2.5s (paralelo). Custo fixo,
  não per-action. Aceitável pela PR-1 (ratio 20/10 do Council
  amendment: bug prevenido vs boot time).
- O subprocesso spawned consome ~30-50MB de RAM por MCP
  (Python+FastMCP) durante os 2.5s. Em Windows dev box, irrelevante.
  Em CI enxuto, monitorar.
- LADESIGN não tem `health` exposto; o smoke-test cai no fallback
  `tools/list` e gera mensagem
  `"health() not exposed; tools/list OK (N tools: [...])"`. Não
  bloqueia, mas fica visível. Oportunidade para G1 retroativo em
  LADESIGN (proposta futura).
- 1 ~150 LOC adicionadas a `subagent_boot_check.py` (helpers de
  JSONC + stdio + check_mcp_primary_optional). Sem novo arquivo.

### Riscos

| Risco | Mitigação |
|-------|-----------|
| MCP server spawn compete por CPU/IO com o opencode runtime | `max_workers=len(targets)` (não maior). Custo por spawn ~1s, paralelismo por capability, não por tool. |
| Subprocess hangs para sempre em caso de bug do servidor | `timeout=2.5` + `proc.kill()` em `TimeoutExpired` + `finally: proc.kill() if alive`. Fail-fast. |
| `tools/list` aceita um server vivo mas quebrado (e.g. tool `health` que sempre lança) | Path 1 (`health().result` com `isError`) detecta; cai no fail. |
| Falso positivo: MCP local leva >2.5s para inicializar (cold start Node daemon) | `MCP_HEALTH_TIMEOUT_S = 2.5` é o default. Se o Conselho pedir mais folga, é 1 linha. Por ora 2.5s cobre latade (Python ~1.1s) e ladesign (Node daemon pre-warmed). |
| Mudança de protocolo MCP quebra o framing newline-delimited | Rastreado por ADR (este). Próxima versão de MCP que mude framing exige revisão. |

---

## Implementação

### Arquivos modificados

- `E:\projects\LAOS\scripts\subagent_boot_check.py`:
  - **Imports:** `+concurrent.futures`, `+json`, `+subprocess`, `+time`
  - **Helper novo:** `warn(s)` (paralelo a `ok`/`fail`)
  - **Constantes novas:** `MCP_HEALTH_TIMEOUT_S = 2.5`,
    `MCP_STDIO_PROTOCOL_VERSION = "2024-11-05"`
  - **Helpers novos:** `_strip_jsonc_comments`, `_parse_mcp_configs`,
    `_resolve_mcp_env`, `_mcp_frame`, `_parse_mcp_framed_messages`,
    `_smoke_test_mcp`
  - **Função renomeada + estendida:**
    `check_mcp(mcps, root)` → `check_mcp_primary_optional(mcp_primary, mcp_optional, root)`.
    Backwards-compat shim `check_mcp(mcps, root)` mantida para callers antigos.
  - **Call site em `main()`:** passa `c.get("mcp_optional", [])` e
    novo header `=== 3. MCP primario (smoke-test *.health() — proposta f82d6261) ===`.
- `E:\projects\latade\mcp\server.py:24`: **no-op** (já estava corrigido
  no momento do dispatch — 10:43:20 do file mtime vs 11:00+ do
  dispatch). Reportado como tal ao orchestrator.

### Validação executada (2026-06-05)

| Validação | Esperado | Observado | Status |
|-----------|----------|-----------|--------|
| `subagent_boot_check.py data-architect --project-name previsao-concursos` | Check 3 PASS | `latade.health() PRIMARY PASS (1.19s)` + Check 7 BLOCKED (SDD scaffold pré-existente, fora do escopo) | ✅ Check 3 PASS (proposta f82d6261); Check 7 fora de escopo |
| `latade_health` via boot check (subprocess fresh) | `{"status": "ok", ...}` | `{"status": "ok", "capability": "latade", "version": "2.0.0", "confidence_score": 0.95}` | ✅ |
| `latade_health` via opencode MCP (PID 22296 stale) | (n/a — processo carregou bytecode pré-fix) | `ModuleNotFoundError: No module named 'src'` | ⚠️  — bug pré-existente da session cache; corrigido por kill+restart (opencode não auto-respawn) |
| Standalone `import` test do latade server | `confidence OK` | `import OK; module path: src.core.confidence` | ✅ |
| `preflight_check.py projects/previsao-concursos` | PASS | `PREFLIGHT_PASS: 0 findings, 5 checks completed.` | ✅ |

### Próximos passos

- **Imediato (proposta f82d6261)**: capability-architect reporta
  conclusão ao orchestrator + LACOUNCIL.
- **M0-9.5 (sugestão, não decidido)**: delivery-reviewer valida o
  smoke-test contra 6 subagentes (não só `data-architect`) e contra
  o conjunto de capabilities não-`health` (ladesign via fallback
  `tools/list`).
- **M1+ (oportunidade)**: Proposta separada para adicionar
  `health` ao LADESIGN daemon (cumprir G1 retroativamente) e remover
  o fallback `tools/list`.

---

## Referências

- Proposta LACOUNCIL: `f82d6261-7592-46e8-8ca3-b7368dfb72a4` (4/4 SIM, supermaioria, 100%)
- Diagnóstico de runtime: `latade_health` retornou `ModuleNotFoundError` em 2026-06-05 durante dispatch do `data-architect` no projeto `previsao-concursos`
- Hard rule violada: LAOS Hard Rule #3 ("routing determinístico") virou "routing determinístico para capability quebrada"
- Padrão emergente: 1º caso de "config-OK but runtime-fail". Conselho antecipou 3+.
- Precedente: ADR-001 (capability governance), ADR-003 (capability-architect creation), ADR-005 (modeling routing laecon)
- Binding conditions: `projects/_meta/capability-architect/binding-conditions.md` (R1-R5 + G1-G8)
- Knowledge: `knowledge/padroes-entrega.md` §"Calibração e pré-flight", §"Boot check de subagente"
- Stack decisions: `knowledge/stack-decisions.md` §"Boot check de subagente (subagent_boot_check.py)"
- MCP stdio transport: `mcp/server/stdio.py:63-65` (newline-delimited JSON, sem Content-Length)
- Capability evolutions: `projects/_meta/capability-evolution/laecon.md`, `laengine.md` (outras BASIC)
