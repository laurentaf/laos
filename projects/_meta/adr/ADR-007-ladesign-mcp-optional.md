# ADR-007: Reclassificar LADESIGN MCP smoke-test de PRIMARY para OPTIONAL

**Status:** accepted
**Date:** 2026-06-05
**Decisor:** LACOUNCIL (supermaioria, 4/4 SIM, 100%)
**Proposal:** `ecdc6305-1a81-4ed5-b5ba-34c1cf250dca`
**Implementer:** capability-architect

---

## Contexto

O LADESIGN MCP server (Node/Open Design daemon — `apps/daemon/dist/cli.js`)
não expõe a ferramenta `health()`, diferentemente das capabilities Python
(LATADE, LAN8N, LAECON, LACOUNCIL) que usam FastMCP com `health()` built-in.

O boot check implementado pelo ADR-006 (proposta `f82d6261`) lista
`udesign` como MCP primário no charter do `dashboard-designer`:

```python
# Antes da mudança (subagent_boot_check.py:62-63):
"dashboard-designer": {
    "mcp_primary": ["ladesign"],
    "mcp_optional": ["context7", "exa"],
```

Isso faz o Check 3 (`check_mcp_primary_optional`) tratar `ladesign.health()`
como **PRIMARY (block)**. O resultado: mesmo com a daemon LADESIGN rodando
(Check 2 passa), o smoke-test falha com `unknown tool: health` — bloqueando
o dispatch do `dashboard-designer`.

A LADESIGN daemon expõe outras ferramentas (via fallback `tools/list`):
`live_artifacts_*`, `connectors_*`, `create_artifact`, `start_run`, etc.
O gap é exclusivamente da ferramenta `health()`. O ADR-006 já previu este
cenário e documentou o fallback para `tools/list`, mas o tratamento como
PRIMARY faz com que o smoke-test (que cai no fallback) gere um WARN, não
um FAIL. Contudo, o problema real é que o charter declara `udesign` como
primário, e o código de smoke-test trata primários como BLOCK se `health()`
falha — mesmo com fallback, a lógica de classificação (linha 581-583 do
boot check) só dá WARN para opcionais.

**Impacto:** nenhum projeto com need `dashboard` ou `design` pode ser
despachado via `dashboard-designer` sem passar por este gate. A daemon
está funcional, as tools estão disponíveis, o bloqueio é falso positivo.

### Diagnóstico

- `udesign` é a **única** capability Node-based no ecossistema LAOS.
- Todas as outras (`latade`, `lan8n`, `lacouncil`, `laecon`, `laengine`)
  são Python FastMCP com `health()` built-in.
- O padrão "Node daemon sem endpoint health dedicado" é arquitetural,
  não um bug.
- Check 2 (daemon: ladesign) já verifica `node_modules` + existência
  do diretório, provendo cobertura de liveness equivalente.

---

## Decisão

Mover `udesign` de `mcp_primary` para `mcp_optional` no charter do
`dashboard-designer` em `scripts/subagent_boot_check.py`.

```python
# Depois da mudança (subagent_boot_check.py:62-63):
"dashboard-designer": {
    "mcp_primary": [],
    "mcp_optional": ["ladesign", "context7", "exa"],
}
```

Isso faz com que:
1. **Check 2 (daemon)** continua sendo o guard de liveness da LADESIGN
   — já verifica `node_modules` + diretório, sem falso negativo.
2. **Check 3 (MCP smoke-test)** passa a tratar `udesign.health()` como
   **OPTIONAL (WARN, não BLOCK)**. Se o daemon estiver rodando mas
   `health()` não existir, o boot check gera um aviso não bloqueante.
3. Se o daemon estiver **parado**, Check 2 falha (block). A reclassificação
   não remove cobertura de segurança — apenas corrige o falso positivo.

**Não foi alterado**: a necessidade futura de adicionar `health()` ao
MCP server do LADESIGN continua válida como melhoria (G1 retroativo),
apenas não bloqueia dispatches hoje.

---

## Alternativas Consideradas

1. **Adicionar `health()` ao daemon LADESIGN agora** — rejeitado. A
   LADESIGN daemon é STABLE, e adicionar uma tool nova requer proposta
   própria + votação do Conselho. A proposta atual tem escopo limitado
   a desbloquear o dispatch.

2. **Manter `udesign` como PRIMARY e alterar a lógica de classificação
   do smoke-test** — rejeitado. A lógica atual (primário=block,
   opcional=warn) é consistente com a semântica do Conselho desde o
   ADR-006. Alterá-la para acomodar um caso específico quebra o contrato
   e afeta todos os subagentes.

3. **Manter o status quo** — rejeitado. Bloqueia o `dashboard-designer`
   indefinidamente. Violação de P0: nenhum projeto visual pode ser
   despachado.

4. **Remover `udesign` completamente do charter** — rejeitado. A
   capability continua sendo a primária para design; apenas o smoke-test
   health() não é aplicável. Check 2 + tools/list ainda cobrem.

---

## Consequências

### Positivas

- `dashboard-designer` passa a ser despachável. Check 3: `udesign.health()
  OPTIONAL WARN` (não block). Check 2: `daemon OK` (block se parado).
- Nenhuma perda de segurança: Check 2 continua protegendo, e as tools
  da LADESIGN são validadas em runtime (não em boot check).
- Precedente para outras capabilities Node-based no futuro: se um
  MCP server não expõe `health()`, o padrão é `mcp_optional` + `daemon`
  check, não forçar `mcp_primary`.

### Custos e responsabilidades

- O `dashboard-designer` perde o guard contra "daemon vivo mas tool
  health quebrada". Mitigação: Check 2 já verifica `node_modules/`.
  O fallback `tools/list` no smoke-test (OPTIONAL WARN) ainda alerta.
- Futuramente, adicionar `health()` ao LADESIGN é a correção definitiva.
  Quando isso acontecer, mover de volta para `mcp_primary`.

### Riscos

| Risco | Mitigação |
|-------|-----------|
| LADESIGN daemon rodando mas MCP server quebrado (outra tool falha) | Check 2 (daemon) + Check 6 (external_directory) + dispatch real capturam. Smoke-test OPTIONAL com WARN alerta. |
| Capacidade Node-based futura herda o mesmo falso positivo | Documentado neste ADR como precedente. Novas capabilities Node-based devem declarar `mcp_optional` + `daemon` se não tiverem `health()`. |

---

## Implementação

### Arquivos modificados

- `E:\projects\LAOS\scripts\subagent_boot_check.py`: 1 diff, 2 linhas.
  Seção `"dashboard-designer": {`:
  - `mcp_primary`: `["ladesign"]` → `[]`
  - `mcp_optional`: `["context7", "exa"]` → `["ladesign", "context7", "exa"]`

### Validação executada (2026-06-05)

| Validação | Esperado | Observado |
|-----------|----------|-----------|
| `uv run python scripts/subagent_boot_check.py dashboard-designer --project-name previsao-concursos --project-root E:\projects\LAOS` | Exit 0 (PASS) | Check 3: `ladesign.health() OPTIONAL WARN` + demais checks PASS |

---

## Referências

- Proposta LACOUNCIL: `ecdc6305-1a81-4ed5-b5ba-34c1cf250dca` (4/4 SIM, supermaioria, 100%)
- ADR-006: Smoke-test `*.health()` (proposta `f82d6261`) — implementou Check 3 com fallback `tools/list` e classificação primary/optional
- ADR-003: Criação do capability-architect (vinculação de G1-G8)
- G1 (Observability contract): expor `health` + `list_supported_operations`. LADESIGN não cumpre G1 hoje; este ADR reconhece o gap como melhoria futura, não bloqueio.
- Binding conditions: `projects/_meta/capability-architect/binding-conditions.md` (R1-R5 + G1-G8)
- Stack decisions: `knowledge/stack-decisions.md` §"Boot check de subagente (subagent_boot_check.py)"