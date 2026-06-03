# Takeoff — Sessão LAOS Architecture Review + Fixes
**Data:** 2026-06-03
**Última alteração:** `c631f82` (git push feito)

---

## O que foi descoberto (testado empiricamente)

### MCP Servers — Estado real vs documentação

| Capability | Doc dizia | Realidade testada | Status |
|---|---|---|---|
| **LATADE** | Stub em `capabilities-stubs/latade-mcp/` | Server real em `../latade/mcp/server.py` com 7 tools | ✅ FUNCIONANDO |
| **LAN8N** | Stub | Stub em `capabilities-stubs/lan8n-mcp/server.py` — real não existe | ⚠️ Stub |
| **LADESIGN** | MCP `od mcp serve` ativo | MCP **disabled** — mas skills carregadas via `skills.paths` | ⚠️ Skills ok, MCP off |
| **LACOUNCIL** | Stable, 10 tools | Server real em `../lacouncil/mcp/server.py` | ✅ FUNCIONANDO |
| **LAENGINE** | Stable | Server real em `../laengine/src/laengine/mcp/server.py` | ✅ FUNCIONANDO |
| **context7, exa, github** | Remote MCPs | Todos ativos e testados | ✅ FUNCIONANDO |
| **n8n-community** | Disabled | Disabled (requer n8n local) | ⬜ Aguardando |

### LATADE Confidence Protocol (descoberto em `AGENT_SYSTEM.md`)

O LATADE tem um sistema sofisticado de confiança alinhado com Agreement Matrix:

```
Agreement Matrix:
  KB ✅ + MCP ✅ → HIGH: 0.95  → EXECUTE
  KB ✅ + MCP ❌ → CONFLICT: 0.50 → INVESTIGATE
  KB ✅ + MCP 🤷 → MEDIUM: 0.75 → PROCEED
  KB ❌ + MCP ✅ → MCP_ONLY: 0.85 → PROCEED
  KB ❌ + MCP 🤷 → LOW: 0.50 → ASK_USER

Thresholds:
  CRITICAL: 0.98 → REFUSE
  IMPORTANT: 0.95 → ASK_USER
  STANDARD: 0.90 → PROCEED+DISCLAIMER
  ADVISORY: 0.80 → PROCEED
```

Implementado em `../latade/src/core/confidence.py` — `ConfidenceEngine`.

### Gaps encontrados

1. **README.md**: tabela MCP desatualizada (LATADE source errado, LADESIGN sem nota de skills)
2. **capabilities.yaml**: LATADE inflava `owns` com postgres/databricks/power-bi que não existem
3. **capabilities-stubs/latade-mcp/**: arquivo órfão (não usado)
4. **emperor → lacouncil**: conceito "Emperor" espalhado em 6+ arquivos
5. **LACOUNCIL**: `_load_config()` retornava raw text, não parseava YAML
6. **LACOUNCIL**: pesos em `tally_votes` hardcoded, não usavam `conselho.yaml`
7. **LACOUNCIL**: sem alinhamento com LATADE confidence protocol
8. **`config/conselho.yaml`**: versão 1 com indentação quebrada em `ponderado` e `veto-lacouncil`

---

## Alterações feitas

### LAOS (commit `c631f82`)

| Arquivo | Mudança |
|---|---|
| `README.md` | Tabela MCP corrigida: LATADE source real, LADESIGN skills documentadas, LACOUNCE/LAENGINE adicionados |
| `AGENTS.md` | Emperor → LACOUNCIL em todo lugar, "three pillars" → "five capabilities", tabela atualizada |
| `registry/capabilities.yaml` | LATADE owns: removido postgres/databricks/power-bi; LACOUNCIL tools: todas 10 listadas; LAN8N: nota de stub |
| `capabilities-stubs/latade-mcp/server.py` | DELETADO (órfão) |
| `setup.ps1` | 3 siblings → 5 siblings (LATADE, LAN8N, LADESIGN, LACOUNCIL, LAENGINE) |
| `emperor.yaml` | RENOMEADO para `lacouncil.yaml` |
| `emperor/` | RENOMEADO para `lacouncil/` (propostas/, sdd-template.md) |
| `lacouncil/sdd-template.md` | "Emperor" → "LACOUNCIL" |
| `.opencode/opencode.jsonc` | Comentários atualizados, `../lacouncil/**` adicionado a external_directory |
| `knowledge/stack-decisions.md` | Protocolo venv documentado + Alinhamento LATADE Confidence Protocol |

### LACOUNCIL (repositório `../lacouncil/`)

| Arquivo | Mudança |
|---|---|
| `pyproject.toml` | Adicionado `pyyaml>=6.0` como dependency |
| `config/conselho.yaml` | REESCRITO — version 2, seção `confidence:` com Agreement Matrix, thresholds, modifiers, trust_dynamics |
| `mcp/server.py` | `import yaml`; `_load_config` agora faz `yaml.safe_load()`; `tally_votes` carrega pesos do YAML + trust modulation; novas tools: `update_trust_score`, `get_trust_scores`, `calculate_confidence`; `list_supported_operations` atualizado (14 tools) |

---

## Estado atual verificado

### LAOS Registry
```
latade     domain latade    stable  sql.duckdb, data.engineering, data.modeling, data.quality, docs.technical
lan8n      domain lan8n     stub    automation.n8n, automation.workflows, integration.apis, integration.webhooks
laengine   domain laengine  stable  game.simulation, game.sports-data, game.match-engine, squad, standings
lacouncil  domain lacouncil stable improvement.proposals, voting, investigation, patterns, memory
ladesign   domain ladesign  external design.dashboard, ux-ui, wireframes, systems, decks, presentations, video, images, storytelling
context7   platform context7 external docs.library-lookup, api-reference, code-examples
exa        platform exa      external web.search, crawl, research
github     platform github   external repos, issues, pull-requests, actions, code-search, releases
```

### LACOUNCIL Tools (14 total)
```
health, investigate, create_proposal, get_proposal, register_vote,
tally_votes, update_trust_score, get_trust_scores, calculate_confidence,
implement_proposal, list_proposals, record_project, detect_patterns,
list_supported_operations
```

### LACOUNCIL Config (`conselho.yaml` v2)
- 4 members com weights do YAML
- 5 strategies (unanimidade, supermaioria, maioria, ponderado, veto-lacouncil)
- Confidence section: Agreement Matrix, Thresholds, Modifiers, Trust Dynamics

---

## Ainda pendente / roadmap

### Pode ser feito sem Conselho (direto)

1. **LAN8N real MCP** — implementar `../lan8n/mcp/server.py` (o stub existe mas o real não)
2. **LADESIGN MCP server** — instalar `od` CLI para ativar o MCP server

### Requer Conselho (futuro)

1. **Votação ponderada por trust_score** — ainda não está 100% conectado ao fluxo de registro de voto
2. **`config/fundamentos.yaml` e `salvaguardas.yaml`** — já existem mas não são enforceçados pelo server.py
3. **`update_trust_score` automática** — o fluxo de votação deveria chamar isso após cada voto

---

## Como continuar

```powershell
# Reiniciar opencode para pegar novos arquivos
cd E:\projects\LAOS
opencode

# Se LACOUNCIL estava rodando como subprocess separado, reiniciá-lo também
```

A nova sessão vai carregar automaticamente:
- `AGENTS.md` atualizado
- `knowledge/stack-decisions.md` com venv protocol + LATADE alignment
- `registry/capabilities.yaml` corrigido
- `lacouncil.yaml` (novo arquivo de config)