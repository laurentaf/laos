# ADR-011: WDL — Workflow Discipline Layer v1 (workflow-decomposer subagent)

**Status:** accepted
**Date:** 2026-06-06
**Decisor:** LACOUNCIL (supermaioria, 4/4 SIM, 100%)
**Proposal:** `a4fe9faa-4d50-4668-845a-ef64f1d41c36`
**Implementer:** capability-architect
**Operating contract:** `workflows/wdl-contract.yaml` (pinned `wdl_version: 1`)

---

## Contexto

O LAOS orchestrator recebe pedidos de projeto (ex.: "make posts for
my LinkedIn") e historicamente pula direto para o trabalho: edits
inline, dispatching de especialistas sem analisar o plano, ou skipping
de decomposição. A causa-raiz é tripla:

1. **Não existe gate que force o orchestrator a despachar um planner
   primeiro.** O subagente planner (`workflow-decomposer`) é zero.
2. **`AGENTS.md` §"Your loop"** descreve o workflow em 5 steps mas
   não tem surface de enforcement entre needs resolution e
   specialist dispatch. O orchestrator segue o caminho de menor
   atrito.
3. **Project count está crescendo.** Usuários trazem projetos
   multi-capability (LinkedIn content = brainstorm + writing +
   design + automation; product spec = data + design + automation;
   deck = design + automation + investigation). O trabalho de PM
   do orchestrator é real mas não tem ferramenta.

A 4ª e 5ª raízes: especialista de delivery já sentiu o impacto
(reviewer de 63 linhas self-attested virou antídoto explícito
neste ADR), e `lacouncil.detect_patterns` está semeado mas
sem caller. WDL v1 entrega ambos.

### Diagnóstico (5 Whys + Fishbone)

- **5 Whys:** Orchestrator pula decomposição → não há gate
  → hard rule em AGENTS.md é narrativo, não estrutural → nenhum
  subagente forçado → orchestrator opera no escuro → capacidade
  do projeto desperdiçada.
- **Fishbone (Processo):** workflow do orchestrator termina em
  dispatch; falta uma "PM layer" que produza um plano verificável.
  Tools (LACOUNCIL) existem; faltam callers determinísticos.
- **Fishbone (Pessoas):** orchestrator prompt tem 5 steps
  informativos; user prompt não tem regra de precedência. Resultado:
  o caminho mais curto (skip planner) é o caminho mais natural.
- **Fishbone (Tecnologia):** se o contracto do plano não tem
  `verified_by`, o self-attested route é viável. Se os campos
  `gaps_acknowledged` / `capability_gaps` não estão no schema,
  a visibilidade do gap é perdida.

## Decisão

Adotar a primeira versão do **WDL — Workflow Discipline Layer**,
composto por quatro artefatos:

### 1. Subagente `workflow-decomposer`

Subagent read-only com MCP wall `lacouncil.*` only. Emite três
arquivos assinados por plan: `analysis.md`, `plan.json`,
`verdict.yaml`. Verdict tri-state: `READY | DEFER | ESCALATE`.
Stateless entre planos. Não propõe, não vota, não muta registry.
Charter file: `.opencode/agent/workflow-decomposer.md`.

### 2. Contrato operacional pinned `wdl_version: 1`

`workflows/wdl-contract.yaml` declara triggers, exemption scope
(allowlist enumerada de 9 `lacouncil.*` tools),
verdict schema (READY/DEFER/ESCALATE + sub-conditions),
granularity rubric (3-Q: Clear input / Validatable success /
Single type of reasoning), decomposition signals (4: conjunction /
plural-criteria / multi-owns / temporal), escalation handoff
schema, anti-pattern clause (temporal is weakest; multi_owns
cross-capability calibration), e 14 implementation_conditions
embedded como P0-blocking clauses.

### 3. Signing infrastructure

`memoria/lacouncil.duckdb.wdl_signatures` table (idempotente
via `scripts/migrate_lacouncil_wdl_signatures.py`). Schema:
`plan_id, sha256, contract_version, planner_id, signed_at,
verified_by` + 2 indexes (`idx_wdl_signatures_plan_id`,
`idx_wdl_signatures_planner_id`).

### 4. Enforcement scripts

`scripts/preflight_check.py` ganha sub-check `wdl-gate` com 4
sub-criteria (a)-(d):

- (a) **existence**: `verdict.yaml` existe e parsea.
- (b) **signing**: `verified_by` não-vazio, != `planner_id`,
  não em `{workflow-decomposer}` (self-attested forbidden).
- (c) **exemption scope**: se `exemption.applied: true`, então
  `triggering_call.tool` ∈ `lacouncil.*` allowlist de 9 tools.
- (d) **anti-backdating**: `user_confirmed_at >= dispatch_at`;
  same-minute + sem `manifest_entry` é tratado como suspect
  (DR-1).

`scripts/subagent_boot_check.py` ganha entry `workflow-decomposer`
com 7-dim schema: `venv: [laos, lacouncil]`, `daemon: []`,
`mcp_primary: [lacouncil]`, `output_subclasses: ["wdl"]`,
`external_directory_required_paths: ["../lacouncil/**"]`.

## 14 Implementation Conditions (Conselho Phase 4)

| ID | Resumo | Onde está |
|----|--------|-----------|
| WDL-IC-1 | `simple_task_exemption` emite verdict.yaml com `exemption: {applied, reason, signals_evaluated}` | contract §exemptions + agent G-VERDICT-1 |
| WDL-IC-2 | `verified_by: <agente_id>` mandatory on every verdict | agent G-VERDICT-2 + contract §signing + preflight (b) |
| WDL-IC-3 | `gaps_acknowledged` TTL `max_delivery_cycles: 2` | agent G-VERDICT-3 + contract §verdicts.states[readiness_subtypes] |
| WDL-IC-4 | `capability_gaps: [{description, affects, owner_notified, severity}]` | agent G-VERDICT-4 + contract §escalation.handoff_schema |
| WDL-IC-5 | Charter P0 é proposta LACOUNCIL separada | AGENTS.md Hard Rule #8 + ADR-012 |
| WDL-IC-6 | Temporal signal labeled as weakest; anti-pattern clause | contract §granularity.anti_pattern_clause + §decomposition.signals[temporal] |
| WDL-IC-7 | Define "session" no P0 rule (per-resolved-DEFER cycle) | contract §versioning.session_id + AGENTS.md §"Your loop" |
| WDL-IC-8 | Bypass anti-backdating; preflight tests manifest ordering | preflight §check_wdl_gate (d) |
| WDL-IC-9 | Preflight wdl-gate 4 sub-criteria | preflight §check_wdl_gate (a)-(d) |
| WDL-IC-10 | Sign-off checklist quotes exit_code from preflight | delivery-reviewer.md §"WDL preflight gate" |
| WDL-IC-11 | Exemption scope enumerable: lacouncil.* tool allowlist | contract §triggers.exempt.scope.tool_allowlist |
| WDL-IC-12 | Dispatch payload includes verdict.yaml path | AGENTS.md §"Your loop" (dispatch_payload_includes) |
| WDL-IC-13 | Capability-gap SLA within same plan-id cycle | contract §escalation.handoff_schema[capability_gap].sla |
| WDL-IC-14 | Charter calibration for automation's multi_owns | agent G-VERDICT-10 + contract §decomposition.signals[multi_owns] |

## Alternativas Consideradas

1. **Plano self-attested, sem `verified_by`**: rejeitado.
   Cria incentivo perverso de bypass. Reviewer de 63 linhas já
   demonstrou que self-attested é vetor de erro silencioso.
2. **Plano armazenado no project.yaml, sem artifact tree**:
   rejeitado. Mistura artefato de domínio com spec estrutural;
   quebra separation of duties.
3. **Subagente dentro de capability-architect (não top-level)**:
   rejeitado. É assessor de PM, não construtor de capability.
   Top-level em `.opencode/agent/` é o lugar correto.
4. **Schema stateful (e.g., workflow state machine)**:
   rejeitado para v1. Statelessness é mais simples e testável.
   Pode virar v2 se houver demanda concreta.
5. **Llm-in-the-loop no decomposer (3-Q com LLM judge)**:
   rejeitado. A 3-Q rubric é puramente estrutural; LLMs no
   decomposer virariam teatro. Signal é sintático.

## Consequências

- **Positiva:** Dispatch de specialist vira condicional a um
  verdict READY assinado. Falta de plano = sinal público, não
  silêncio.
- **Positiva:** Capability gaps ficam visíveis no verdict
  (G-VERDICT-4), criando loop orgânico com
  `lacouncil.detect_patterns`.
- **Positiva:** reviewer's sign-off começa a citar o
  `exit_code` do preflight wdl-gate, tornando a cadeia
  auditável.
- **Risco:** Orchestrator burla o gate por inércia. Mitigação:
  Charter P0 hard rule (ADR-012) impõe trust-score penalty
  + manifest overlay + user confirmation.
- **Risco:** WDL v1.0 sem signal de uso real (cold start).
  Mitigação: regime BASIC de 30 dias; o Conselho pode revogar
  se a evidência mostrar que a fricção supera o ganho.

## Mudanças feitas

1. `.opencode/agent/workflow-decomposer.md` — agent charter.
2. `workflows/wdl-contract.yaml` — operating contract.
3. `scripts/migrate_lacouncil_wdl_signatures.py` + tabela
   `wdl_signatures` em `memoria/lacouncil.duckdb`.
4. `.opencode/opencode.jsonc` — entry `workflow-decomposer`
   (reusa lacouncil stdio).
5. `scripts/preflight_check.py` — sub-check `wdl-gate`.
6. `scripts/subagent_boot_check.py` — entry
   `workflow-decomposer`.
7. `projects/_meta/capability-architect/binding-conditions.md`
   — G10 adicionado.
8. `projects/_meta/adr/ADR-011-wdl-workflow-decomposer.md` —
   este ADR.

## Cross-references

- Proposta LACOUNCIL: `a4fe9faa-4d50-4668-845a-ef64f1d41c36`
- Sibling proposal (Charter P0): `7fd94c1a-d21d-49cc-a0e6-07c07c716e73` → ADR-012
- LACOUNCIL Regime A: `391a8179-5a16-4b69-a3a3-d4ca1b20c2c3`
- Padrões de entrega: `knowledge/padroes-entrega.md` P0
- SDD principles: `knowledge/sdd-principles.md` §2
- Source of truth operacional: `workflows/wdl-contract.yaml`
  (pinned `wdl_version: 1`)
- Precedente meta-projeto: `projects/_meta/capability-architect/`
- Capability-evolution tracking: `projects/_meta/capability-evolution/workflow-decomposer.md`
  (criado no regime BASIC → STABLE promotion)

## Advisory do Conselho

O delivery-reviewer destacou que `simple_task_exemption` deve
emitir verdict mesmo assim (com `exemption: {applied: true, ...}`),
não skip-the-verdict. Caso contrário, o preflight sub-criterion
(a) falha e a exemption é invisível. Esta ADR incorpora o
advisory: toda exemption é recorded-as-verdict, não bypass-the-verdict.
