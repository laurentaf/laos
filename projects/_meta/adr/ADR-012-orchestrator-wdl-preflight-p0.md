# ADR-012: Orchestrator Charter P0 — WDL preflight hard rule

**Status:** accepted
**Date:** 2026-06-06
**Decisor:** LACOUNCIL (supermaioria, 4/4 SIM, 100%)
**Proposal:** `7fd94c1a-d21d-49cc-a0e6-07c07c716e73`
**Implementer:** capability-architect
**Sibling ADR:** ADR-011 (WDL v1 — `a4fe9faa-4d50-4668-845a-ef64f1d41c36`)

---

## Contexto

ADR-011 introduz o subagente `workflow-decomposer` e o seu
contrato operacional. Mas um subagente novo, sem uma regra de
precedência explícita no AGENTS.md do orchestrator, é inerte:
o orchestrator pode ignorá-lo por inércia, sem custo
verificável. O 5 Whys do reviewer de 63 linhas demonstrou que
regras narrativas em AGENTS.md não são estruturalmente
enforcement-capable.

A proposta `7fd94c1a` complementa ADR-011: tornar **P0** a
precedência do workflow-decomposer dispatch sobre qualquer
specialist dispatch. Hard Rule #8 em `AGENTS.md`. Trust-score
penalty no orchestrator se o gate for burlado. Bypass requer
manifest overlay + user confirmation + cost.

### Diagnóstico (5 Whys + Fishbone)

- **5 Whys:** WDL v1 fica inerte → orchestrator não tem
  regra que force dispatch do planner → sem penalidade por
  skip → atrito de seguir o gate > atrito de skip → skip
  vence. Já vimos isso no capability-architect (M0-1..M0-9):
  regras narrativas não escalam.
- **Fishbone (Processo):** falta de penalty + falta de
  bypass-cost cria incentive misalignment. O atrito certo
  precisa estar no caminho errado.
- **Fishbone (Tecnologia):** trust-score é o signal nativo
  da LACOUNCIL. Trust-score penalty em bypass é o mecanismo
  que o Conselho já entende.

## Decisão

Adotar **Hard Rule #8** em `AGENTS.md`, com cinco sub-regras:

### 8.1 — WDL preflight gate is mandatory

The orchestrator MUST dispatch `workflow-decomposer` before
any specialist dispatch (`data-architect`, `dashboard-designer`,
`automation-engineer`, `capability-architect`, or any future
project subagent). The orchestrator MUST consume the verified
`verdict.yaml` (state: `READY`) before the specialist dispatch
payload is sent.

### 8.2 — Trust-score penalty on bypass

If the orchestrator dispatches a specialist without a verified
`verdict.yaml` of state `READY`, the orchestrator's trust score
is penalized:

- `-0.1` per individual bypass
- `-0.3` max penalty per plan-id
- `-0.5` max penalty per session (per-resolved-DEFER cycle,
  defined in `wdl-contract.yaml` §versioning.session_id)

The penalty is non-erasable within the session. Trust-score
recovery is via the standard LACOUNCIL `update_trust_score`
mechanism, gated on a successful G4 sign-off with all 14
WDL-IC conditions met.

### 8.3 — Bypass requires manifest overlay + user confirmation + cost

If a bypass is justified (e.g., trivial task, exemption), it
must be recorded with:

- **Manifest overlay**: `artifacts/wdl/<plan-id>/bypass-manifest.yaml`
  with `reason`, `alternative_dispatch_path`, `user_confirmed_at`,
  and `dispatch_at` (anti-backdating via preflight (d)).
- **User confirmation**: explicit verbal / written confirmation
  (recorded in the manifest).
- **Cost**: each bypass costs the orchestrator the trust-score
  penalty above. No bypass is free.

### 8.4 — Exemption scope is enumerable

Exemptions (where WDL gate is skipped entirely) apply only to
the orchestrator's own direct `lacouncil.*` invocations for
structural improvement work (LACOUNCIL proposals, structural
investigations, trust-score reads). Exemption scope is the
allowlist of 9 `lacouncil.*` tools declared in
`workflows/wdl-contract.yaml` §triggers.exempt.scope.tool_allowlist.
No narrative exemptions. Any tool outside the allowlist, or any
non-orchestrator-direct subagent, requires the WDL gate.

### 8.5 — Reviewer cites preflight exit_code

The `delivery-reviewer` MUST quote the `exit_code` from the
preflight `wdl-gate` in its G4 sign-off. The sign-off is NOT
DELIVERABLE if any P0 cite is open (missing_verdict,
expired_exemption, post_dated_bypass, self_attested_verdict,
missing_capability_gaps). The 5 cite categories are enumerated
in `.opencode/agent/delivery-reviewer.md` §"WDL preflight gate".

## Mudanças feitas

1. **`AGENTS.md` Hard Rules** — novo item #8 (5 sub-regras 8.1–8.5).
2. **`AGENTS.md` Agent topology** — entry `workflow-decomposer` adicionada
   (read-only PM layer; MCP wall `lacouncil.*` only).
3. **`AGENTS.md` §"Your loop"** — nova subsection "WDL preflight gate"
   entre step 2 e step 3; dispatch_payload_includes declara
   `[verdict.yaml, plan_id, verified_by]`.
4. **`AGENTS.md` §"Tools you do NOT use"** — clarifier explícito:
   orchestrator não chama `lacouncil.*` para project work
   (apenas para structural improvement). Para project work,
   chama `workflow-decomposer`.
5. **`.opencode/agent/delivery-reviewer.md`** — WDL section
   com 5 cite categories.
6. **`projects/_meta/capability-architect/binding-conditions.md`**
   — G11 adicionado.
7. **`projects/_meta/adr/ADR-012-orchestrator-wdl-preflight-p0.md`**
   — este ADR.

## 6 Implementation Conditions (Charter P0)

| ID | Resumo | Onde está |
|----|--------|-----------|
| WDL-IC-9 | Preflight wdl-gate 4 sub-criteria | `scripts/preflight_check.py` §check_wdl_gate (a)-(d) |
| WDL-IC-10 | Sign-off checklist quotes exit_code from preflight | `delivery-reviewer.md` §"WDL preflight gate" |
| WDL-IC-11 | Exemption scope enumerable: lacouncil.* tool allowlist | `wdl-contract.yaml` §triggers.exempt.scope.tool_allowlist |
| WDL-IC-12 | Dispatch payload includes verdict.yaml path | `AGENTS.md` §"Your loop" (dispatch_payload_includes) |
| WDL-IC-13 | Capability-gap SLA within same plan-id cycle | `wdl-contract.yaml` §escalation.handoff_schema[capability_gap].sla |
| WDL-IC-14 | Charter calibration for automation's multi_owns | `workflow-decomposer.md` G-VERDICT-10 + `wdl-contract.yaml` §decomposition.signals[multi_owns] |

(Estas 6 conditions + as 8 do ADR-011 = 14 implementation
conditions totais do WDL v1 rollout, todas P0-blocking.)

## Alternativas Consideradas

1. **Sem trust-score penalty** (regras narrativas em
   AGENTS.md): rejeitado. Já vimos que narrativas não escalam
   (precedente: capability-architect M0-1..M0-9).
2. **Penalty per-bypass sem cap por session**: rejeitado.
   Risco de catch-up penalty acumular ao ponto de inviabilizar
   o orchestrator. `-0.5/session` é o cap razoável.
3. **Hard block (impossível bypassar)**: rejeitado. Há
   casos legítimos (orchestrator's own lacouncil.* work) onde
   o gate é overhead. Allowlist de 9 tools é o equilíbrio.
4. **Penalty só no orchestrator user-facing, não no trust-score**:
   rejeitado. Trust-score é o signal canônico do Conselho.
5. **Bypass sem manifest overlay**: rejeitado. Sem registro,
   a penalty é invisível e o signal se perde.

## Consequências

- **Positiva:** WDL v1 deixa de ser opcional por inércia.
  Cada specialist dispatch vira condicional a um verdict READY.
- **Positiva:** Trust-score penalty cria incentive alignment
  com o Conselho. Bypass custar >0 é o mecanismo estrutural
  que faltava.
- **Positiva:** Manifest overlay + user confirmation + cost
  = bypass explícito, registrado, auditável.
- **Risco:** Atrito excessivo em projetos simples. Mitigação:
  `simple_task_exemption` no WDL v1 permite zero-friction
  emission de verdict para tarefas simples, desde que
  `exemption: {applied: true, ...}` esteja presente.
- **Risco:** Reviewer overload se exit_code cita forem
  granulares demais. Mitigação: 5 cite categories
  enumeradas, todas binárias (open / closed). Granularidade
  é o necessário e suficiente.

## Cross-references

- Proposta LACOUNCIL: `7fd94c1a-d21d-49cc-a0e6-07c07c716e73`
- Sibling proposal (WDL v1): `a4fe9faa-4d50-4668-845a-ef64f1d41c36` → ADR-011
- LACOUNCIL Regime A: `391a8179-5a16-4b69-a3a3-d4ca1b20c2c3`
- Source of truth operacional: `workflows/wdl-contract.yaml` (pinned `wdl_version: 1`)
- WDL contract signers: `memoria/lacouncil.duckdb.wdl_signatures`
- Padrões de entrega: `knowledge/padroes-entrega.md` P0
- SDD principles: `knowledge/sdd-principles.md` §2
- Precedente: `projects/_meta/capability-architect/` (regime G1–G9 → G1–G11)

## Advisory do Conselho

O delivery-reviewer propôs que a trust-score penalty use os
thresholds do `lacouncil.calculate_confidence()` (KB ✅ + MCP ✅
HIGH = 0.95) como referência de "evidência forte o suficiente".
Esta ADR incorpora o advisory: a penalty é fixa (`-0.1/-0.3/-0.5`),
mas o orchestrator pode submeter evidência (latade.inspect_table,
exa.web_search, etc.) para reduzir a penalty, gated pelo
mecanismo `update_trust_score` do LACOUNCIL.
