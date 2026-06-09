# ADR-010: Hard Rule #11 — Sem dados sintéticos sem permissão explícita do usuário

**Status:** accepted
**Date:** 2026-06-07
**Decisor:** Orchestrator (user-override, direto)
**Ratificação LACOUNCIL:** aprovada (proposta 87113c0f-46be-4ada-b81c-e6d2890ae23f, 4/4 SIM, maioria, 2026-06-09)

---

## Contexto

O projeto `giovanna-rupture-monitor` usa dados sintéticos (ShadowTraffic) por design — não existe fonte de dados real. Mas o padrão de "inventar dados para o artefato ficar completo" é uma tentação que vale para QUALQUER projeto, não só os que são propositalmente sintéticos.

O risco real: um subagente (`data-architect`, `dashboard-designer`, `automation-engineer`) não consegue acessar uma API ou tabela, e em vez de parar e reportar o gap, gera dados plausíveis que passam despercebidos. Isso é o que W. Edwards Chama de "defect injection" na etapa de inspeção (Fagan 1976) — é mais barato prevenir do que detectar downstream.

### Diagnóstico (5 Whys)

1. Por que dados sintéticos em artefatos de produção são um problema? → Porque passam despercebidos e distorcem decisões.
2. Por que passam despercebidos? → Porque não há marcação explícita no artefato.
3. Por que não há marcação? → Porque não existe regra que exija.
4. Por que não existe regra? → Porque o sistema assume que dados reais sempre estão disponíveis.
5. Por que assume isso? → Porque nenhum mecanismo formaliza o pedido de permissão ao usuário quando dados reais faltam.

### Fishbone

- **Processo:** Subagentes não têm protocolo para reportar gap de dados. O orchestrator não tem como saber que dados são sintéticos.
- **Ferramenta:** Nenhuma MCP tool valida se dados são reais ou gerados.
- **Pessoa:** A tentação de "só gerar um CSV fake" é alta porque o custo de parar e perguntar é alto.
- **Material:** Artefatos de produção (`artifacts/data/`, `artifacts/design/`, etc.) misturam-se com fixtures de teste sem distinção.

## Decisão

Criar Hard Rule #11 com três modos de permissão:

### Modo 1: Per-ask (padrão, estrito)

Subagente que não consegue recuperar dados reais **PARA e reporta ao orchestrator**. Orchestrator pergunta ao usuário. Default se silêncio = **NÃO**.

Protocolo por pergunta:
1. Subagente reporta gap: `gap: missing <dado>` + `reason` + `proposed_synthetic` + `scope` + `recommendation`
2. Orchestrator lê `data_policy` do `project.yaml` (se existir)
3. Se `allow_synthetic: true` e scope cobre → autoriza direto (modo project-scoped)
4. Senão → pergunta ao usuário literalmente
5. Decide: `y` (prossegue), `n` (para), `scope:<path>` (parcial), `use_alt_source:<X>` (fonte alternativa)
6. Loga a decisão na sessão

### Modo 2: Project-scoped (opt-in, menos estrito)

`project.yaml` declara:
```yaml
data_policy:
  allow_synthetic: true
  scope: ["data/*", "artifacts/data/*"]
  decided_at: "2026-06-09T00:00:00Z"
  decided_by: user_override
  reason: "..."
```

Dentro do escopo declarado, subagentes podem usar dados sintéticos SEM per-ask. Fora do escopo, volta ao modo per-ask.

### Modo 3: Exceções (sempre permitido)

- Test fixtures em diretórios `tests/`
- Wireframes explicitamente rotulados como `mock, not for production`
- Exemplos em documentação (`docs/`, `knowledge/`)

### Metadata obrigatória

Todo artefato com dados sintéticos em path de produção DEVE ter frontmatter:
```yaml
synthetic: true
granted_by: <user|project_yaml>
granted_at: <iso8601>
reason: <why_real_data_missing>
```

Ausência de marcação em artefato com dados = **P0 violation** (sign-off auto-fail).

## Alternativas consideradas

1. **Permitir sempre (sem pergunta):** rejeitado — a tentação de gerar dados fake é o anti-pattern que esta regra fecha (Fagan 1976).
2. **Proibir sempre (zero synthetic):** rejeitado — projetos como giovanna-rupture-monitor SÃO propositalmente sintéticos.
3. **Marcar no review (post-hoc):** rejeitado — o delivery-reviewer valida existência de metadata, mas não deve ser a primeira linha de defesa.

## Consequências

- **Positiva:** Nenhum artefato de produção tem dados não-marcados. Custo: 1 pergunta ao usuário por gap.
- **Positiva:** Padrão auditável — `delivery-reviewer` valida P0-15 em todo sign-off.
- **Risco:** Fricção extra em projetos que são propositalmente sintéticos. Mitigação: modo project-scoped elimina per-ask repetitivo.
- **Risco:** Usuário não responde (silêncio = NÃO). Mitigação: aceitar que "não fazer" é mais seguro que "fazer sem saber".

## Mudanças feitas

1. **AGENTS.md** — Hard Rule #11 com protocolo completo.
2. **knowledge/data-fabrication-policy.md** — nova entrada (12 seções, 3 exemplos worked).
3. **knowledge/padroes-entrega.md** — P0-15 adicionado.
4. **.opencode/agent/data-architect.md** — protocolo stop-and-report.
5. **.opencode/agent/dashboard-designer.md** — wireframe vs production modes.
6. **.opencode/agent/automation-engineer.md** — test fixture vs production modes.
7. **projects/giovanna-rupture-monitor/project.yaml** — `data_policy` retrofitado (projeto entregue com dados sintéticos por design).
