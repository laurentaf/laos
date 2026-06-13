# Tool Permission Model

> **Proveniência:** Oracle 2Care §Tool Permission Model (mesmo autor, Laurent).
> LACOUNCIL proposal `3473c12b` (aprovada 4/4 SIM, 2026-06-12).

## Princípio central — "Knives in the kitchen"

> Agents use knives that are already in the kitchen.
> No permission needed.
> Only when a cook needs a new tool (blowtorch) does the chef (user) decide if we buy one.

Um agente não deveria instalar ou configurar uma tool que já existe
no workspace. Isso inclui: tool no PATH, venv já sincronizado,
container já rodando, dependência já instalada no venv.

## Tabela de Permissão de Tools

| Categoria | Permissão | Regra | Exemplo |
|-----------|-----------|-------|---------|
| **Tool existente no workspace** | `allow` | Agente USA direto, sem instalação | `python` no PATH, `uv` já no venv, `docker` no PATH |
| **Tool já no venv do capability repo** | `allow` | Usar `uv run python` dentro do venv | scikit-learn no venv latade |
| **Container já rodando** | `allow` | Conectar direto, não criar novo | n8n via `docker ps` |
| **Tool nova (não existe em nenhuma camada)** | `ask` | Orchestrator pergunta ao usuário antes de instalar | Nova lib Python, CLI não disponível |
| **Nova capability (MCP server novo)** | `ask` | Registro via LACOUNCIL proposal, não improviso | Adicionar novo repo em registry |

## Camadas de existência (ordem de prioridade)

Para determinar se uma tool "existe" e pode ser usada sem pedir:

```
Layer 1: Tool no PATH do sistema         → allow
Layer 2: Tool no workspace (E:/projects) → prefer (evitar setup)
Layer 3: Venv já sincronizado            → allow (uv sync atualiza)
Layer 4: Container já rodando            → allow (docker ps)
Layer 5: Dependência já no venv          → allow (pip list)
Layer 6: Tool não existe em nenhuma      → ask antes de instalar
```

## Relação com outras regras LAOS

### discover-before-build (§knowledge/discover-before-build.md)

A tabela de permissão de tools é a **formalização explícita** do
princípio discover-before-build. A hierarquia de 6 camadas acima
é o mapa concreto do que significa "já existe".

| discover-before-build | Tool permission model |
|----------------------|----------------------|
| Inventariar runtimes antes de sugerir | Layer 1: PATH check |
| Verificar venv antes de sync | Layer 3: venv check |
| Checar containers antes de subir | Layer 4: container check |
| Dependência já instalada | Layer 5: venv deps check |
| Só então instalar | Layer 6: ask |

### Hard Rule #9 (venv path policy)

A política de venv (Hard Rule #9) é um caso específico desta tabela:
venv dentro de `E:/projects/**` é in-scope automático; fora é `ask`.

### subagent_boot_check.py (5 dimensões)

O boot check valida venv/daemon/MCP/paths/env mas **não** cobre
a check de "tool já existe no PATH" (Layer 1). Isso é coberto
pela Fase 2 do discover-before-build, que o subagente executa
durante o trabalho — não no boot check.

### Hard Rule #11 (synthetic data)

O modo per-ask para dados sintéticos mapeia para Layer 6:
"tool/situação nova que não existe → ask". A diferença é que
dados sintéticos têm uma regra específica (per-ask default = NÃO)
enquanto tools novas têm uma regra geral (per-ask = autorizo
com justificativa).

## Anti-pattern: "tool installation sem checagem"

```
Anti-pattern: Agente instala Docker Desktop quando já existe
no PATH (Get-Command docker retorna resultado).

Por que é ruim:
- Download desnecessário (~500MB)
- Conflito de versão se já existe
- Duplicação de serviço na máquina
- Viola a doutrina "sufficiency > steering"

Correção: Cascata de checagem (Layers 1-5) antes de instalar.
Se qualquer Layer retorna "existe" → USAR, não instalar.
```

## Quando "ask" se aplica na prática

O agente **não** precisa pedir permissão quando:

- A tool está em qualquer Layer 1-5 (existe no workspace)
- A install é uma atualização menor de algo já existente (`uv sync`)
- O usuário pediu explicitamente "instale X"

O agente **precisa pedir** quando:

- Nenhuma das Layers 1-5 se aplica
- É a primeira vez que a capability precisa de uma tool
- A install alteraria o ambiente de forma permanente
  (nova lib no venv, novo CLI global, novo container)

## Script de validação (opor

Para checar se uma tool está em alguma Layer antes de propor instalação:

```bash
# Tool pre-existence check (exausta todas as 6 camadas)
check_tool_exists() {
  local tool="$1"
  # Layer 1: PATH
  if command -v "$tool" >/dev/null 2>&1; then
    echo "EXISTS: Layer1-PATH → allow"
    return 0
  fi
  # Layer 2: workspace tools dir
  if [[ -f "E:/tools/$tool" ]] || [[ -f "E:/projects/**/tools/$tool" ]]; then
    echo "EXISTS: Layer2-workspace → allow"
    return 0
  fi
  # Layer 3-5: checados pelo subagent_boot_check.py + discover-before-build
  # Layer 6: não existe
  echo "NOTFOUND: Layer6 → ask before install"
  return 1
}
```

Este script live em `scripts/check-tool-existence.sh` (mesmo padrão
de `child-repo-hooks.sh`). Pode ser chamado no briefing do subagente
como validação pré-dispatched.

## Histórico

- 2026-06-12 — Criado via LACOUNCIL `3473c12b` (adção de 3 padrões Oracle 2Care)