# ADR-004: Charter-based subagent autonomy + tool readiness at boot

**Status:** accepted
**Date:** 2026-06-04
**Decisor:** LACOUNCIL (supermaioria, 4/4 SIM, 100%)
**Proposal:** `518b82d5-1f04-4342-9b3f-6897e3e14623`

---

## Contexto

O orchestrator do LAOS despachava subagentes com prompts de 1.500-2.500
palavras que re-statuavam o charter a cada invocação. Concomitantemente,
`knowledge/stack-decisions.md` obrigava verificação de venv "antes de cada
comando Python". Em uma sessão recente, o subagente `dashboard-designer`
encontrou um `400` em `ladesign.create_artifact` mid-task e improvisou
workaround com `write_file` — exatamente o anti-pattern que um sistema
pronto-para-uso deveria evitar.

O usuário levantou o princípio: "um agente sabe o que faz e não precisa
de permissão por tarefa, ou não deveria estar fazendo. Se o problema é a
ferramenta (venv, MCP), precisamos pensar quem deve prepará-la."

## Decisão

Refatorar a relação orchestrator↔subagente em 4 camadas explícitas:

1. **Charter** (persistente) — `.opencode/agent/<name>.md` codifica
   identidade, MCPs primários/opcionais, paths, env vars, regras
   inegociáveis, anti-padrões, **artefatos obrigatórios** (mapeados aos
   P0 de `padroes-entrega.md`).
2. **Tool readiness** (boot-time) — `scripts/subagent_boot_check.py`
   valida 5 dimensões: venv, daemon, MCP primário, paths, env. Roda
   **uma vez** antes de cada dispatch.
3. **Task brief** (curto) — prompt do `task` é 5-15 linhas, só com o
   que varia. Não re-statui o charter.
4. **Authorization** (rara) — só para cross-charter ou LACOUNCIL.

**Mid-task tool failure:** subagente recebe `4xx/5xx` → re-chama
`*.health()` → se falhar, **escala ao orchestrator** com mensagem
acionável. **Nunca** improvisa workaround com outra tool.

## As 9 emendas dos 4 votantes

| # | De | Emenda |
|---|---|---|
| E1 | data-architect | Re-chamar `*.health()` no primeiro 4xx/5xx mid-session |
| E2 | data-architect | Boot valida output paths do projeto + env vars |
| E3 | data-architect | Manter boot check sob orchestrator até capability-architect STABLE |
| E4 | data-architect | MCPs primários obrigatórios no boot; opcionais lazy |
| E5 | dashboard-designer | Mid-task failure escala; não improvisar workaround |
| E6 | dashboard-designer | Boot check cobre LADESIGN daemon (Node), não só venv |
| E7 | delivery-reviewer | Cada instruction file tem seção "Artefatos obrigatórios" |
| E8 | delivery-reviewer | 3+ gaps consecutivos no mesmo artefato = charter incompleto |
| E9 | dashboard-designer | Primeira dispatch pode ter scaffolding; segunda em diante brief curto |

## Alternativas consideradas

1. **Manter prompts verbosos** — rejeitado, dilui foco do subagente.
2. **Auto-cura de MCP quebrado mid-task** — rejeitado, vira system admin dentro do subagente.
3. **Remover verificação de tooling completamente** — rejeitado, venv ausente descoberto no meio do trabalho.

## Consequências

### Positivas

- Briefs 70% menores; subagentes processam menos ruído.
- Erros de tooling aparecem no boot, não mid-task.
- Padrão reverso (DR-E8) conecta validação downstream à evolução upstream.
- Charter vira código versionado, evolui via LACOUNCIL.

### Custos

- 5 instruction files atualizados (esforço de escrita único).
- 1 script novo (subagent_boot_check.py).
- 1 ADR + 1 meta-projeto.
- 1 update em knowledge/stack-decisions.md.

### Transitório

Até `capability-architect` atingir STABLE (2026-07-04), o orchestrator
mantém `scripts/subagent_boot_check.py` (DA-E3). Após STABLE, handoff
formal.

## Implementação

10 deliverables (ver `projects/_meta/charter-autonomy/project.yaml`):
1. `projects/_meta/charter-autonomy/project.yaml` (contrato)
2. `projects/_meta/adr/ADR-004-charter-autonomy.md` (este ADR)
3-7. 5 instruction files atualizados
8. `scripts/subagent_boot_check.py`
9. `knowledge/stack-decisions.md` atualizado
10. `lacouncil.record_project()` chamado

## Referências

- Proposta LACOUNCIL: `518b82d5-1f04-4342-9b3f-6897e3e14623`
- Capability-architect (transitório): `2f42afe6-71d5-4ef8-a88a-1339d72ec501`
- LAECON (precedente de amendments): `cbe2d8ef-f65c-4d0e-8960-ea99527ab39f`
- Padrões de entrega: `knowledge/padroes-entrega.md`
- Stack decisions: `knowledge/stack-decisions.md`
- Capability-architect ADR-003 (precedente de meta-projeto): `projects/_meta/adr/ADR-003-capability-architect-creation.md`
