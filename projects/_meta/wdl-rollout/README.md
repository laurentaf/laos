# wdl-rollout (meta-projeto WDL v1)

Meta-projeto que entrega a primeira versão do **WDL — Workflow
Discipline Layer** (proposta LACOUNCIL `a4fe9faa-4d50-4668-845a-ef64f1d41c36`,
supermaioria 4/4 SIM, 2026-06-06) em conjunto com a **Charter P0 hard
rule** (proposta LACOUNCIL `7fd94c1a-d21d-49cc-a0e6-07c07c716e73`,
supermaioria 4/4 SIM, 2026-06-06).

## O que é

WDL é uma camada de governança de PM entre o orchestrator e os
subagentes de domínio. O subagente `workflow-decomposer` analisa o
brief, executa a 3-Q rubric (Clear input / Validatable success /
Single type of reasoning) e a 4-signal decomposition
(conjunction / plural-criteria / multi-owns / temporal), e emite um
verdict assinado (READY | DEFER | ESCALATE) antes de qualquer
dispatch de especialista. A Charter P0 hard rule torna o dispatch
do workflow-decomposer obrigatório.

## Onde está o quê

| Componente | Path |
|------------|------|
| Subagent charter | `.opencode/agent/workflow-decomposer.md` |
| Contrato operacional | `workflows/wdl-contract.yaml` (pinned `wdl_version: 1`) |
| DuckDB table (signatures) | `memoria/lacouncil.duckdb.wdl_signatures` |
| Migration script | `scripts/migrate_lacouncil_wdl_signatures.py` |
| MCP config | `.opencode/opencode.jsonc` (entry `workflow-decomposer`) |
| Preflight gate | `scripts/preflight_check.py` (§`check_wdl_gate`) |
| Boot check entry | `scripts/subagent_boot_check.py` (SUBAGENT_CHARTERS) |
| Delivery-reviewer WDL section | `.opencode/agent/delivery-reviewer.md` |
| AGENTS.md deltas | `AGENTS.md` (Hard Rule #8, topology, Your loop, Tools) |
| Capability-architect G10/G11 | `projects/_meta/capability-architect/binding-conditions.md` |
| ADR WDL | `projects/_meta/adr/ADR-011-wdl-workflow-decomposer.md` |
| ADR Charter P0 | `projects/_meta/adr/ADR-012-orchestrator-wdl-preflight-p0.md` |
| Meta-projeto (este dir) | `projects/_meta/wdl-rollout/` |

## Como rodar

### 1. Validação (rodar antes do delivery-reviewer G4 sign-off)

```bash
# Boot check do subagente workflow-decomposer
uv run python scripts/subagent_boot_check.py workflow-decomposer --project-name wdl-rollout

# Preflight completo do meta-projeto (6/6 checks)
uv run python scripts/preflight_check.py projects/_meta/wdl-rollout
```

Exit `0` em ambos = MISSÃO 0 entregue. Exit `1` = corrigir findings
acionáveis antes de despachar o delivery-reviewer.

### 2. Migration do DuckDB (idempotente)

```bash
# Roda do venv do lacouncil (que tem duckdb)
..\lacouncil\.venv\Scripts\python scripts/migrate_lacouncil_wdl_signatures.py
# ou de qualquer venv com duckdb:
uv run python scripts/migrate_lacouncil_wdl_signatures.py
```

Re-rodar é seguro (`CREATE TABLE IF NOT EXISTS`).

### 3. Regime A push (após G4 sign-off do delivery-reviewer)

```bash
# Capability-architect NAO executa este passo.
# Orchestrator commita + pusha ao GitHub na mesma sessao (LACOUNCIL 391a8179).
git add -A
git commit -m "feat(wdl): WDL v1 rollout — workflow-decomposer subagent + Charter P0"
git push origin main
```

## 14 Conditions Traceability (matriz)

| Cond | Descrição resumida | Deliverable que satisfaz |
|------|--------------------|--------------------------|
| WDL-IC-1 | `simple_task_exemption` emite verdict.yaml com `exemption: {applied, reason, signals_evaluated}` | `workflows/wdl-contract.yaml` §exemptions.simple_task_exemption; `.opencode/agent/workflow-decomposer.md` G-VERDICT-1 |
| WDL-IC-2 | `verified_by: <agente_id>` mandatory on every verdict | `.opencode/agent/workflow-decomposer.md` G-VERDICT-2; `workflows/wdl-contract.yaml` §signing; `scripts/preflight_check.py` §check_wdl_gate (b) |
| WDL-IC-3 | `gaps_acknowledged` TTL `max_delivery_cycles: 2` | `.opencode/agent/workflow-decomposer.md` G-VERDICT-3; `workflows/wdl-contract.yaml` §verdicts.states[readiness_subtypes] |
| WDL-IC-4 | `capability_gaps: [{description, affects, owner_notified, severity}]` | `.opencode/agent/workflow-decomposer.md` G-VERDICT-4; `workflows/wdl-contract.yaml` §escalation.handoff_schema |
| WDL-IC-5 | Charter P0 = separate LACOUNCIL proposal | `AGENTS.md` Hard Rule #8; `projects/_meta/adr/ADR-012-orchestrator-wdl-preflight-p0.md` |
| WDL-IC-6 | Temporal signal labeled as weakest; anti-pattern clause | `workflows/wdl-contract.yaml` §granularity.anti_pattern_clause + §decomposition.signals[id=temporal].weakest |
| WDL-IC-7 | Define "session" in P0 rule | `workflows/wdl-contract.yaml` §versioning.session_id; `AGENTS.md` §"Your loop" subsection |
| WDL-IC-8 | Bypass anti-backdating; preflight tests manifest ordering | `scripts/preflight_check.py` §check_wdl_gate (d) |
| WDL-IC-9 | Preflight wdl-gate 4 sub-criteria | `scripts/preflight_check.py` §check_wdl_gate (a)-(d) |
| WDL-IC-10 | Sign-off checklist quotes exit_code from preflight | `.opencode/agent/delivery-reviewer.md` §"WDL preflight gate" |
| WDL-IC-11 | Exemption scope enumerable: lacouncil.* tool allowlist | `workflows/wdl-contract.yaml` §triggers.exempt.scope.tool_allowlist |
| WDL-IC-12 | Dispatch payload includes verdict.yaml path | `AGENTS.md` §"Your loop" (dispatch_payload_includes) |
| WDL-IC-13 | Capability-gap SLA within same plan-id cycle | `workflows/wdl-contract.yaml` §escalation.handoff_schema[subtype=capability_gap].sla |
| WDL-IC-14 | Charter calibration for automation's multi_owns | `.opencode/agent/workflow-decomposer.md` G-VERDICT-10; `workflows/wdl-contract.yaml` §decomposition.signals[id=multi_owns].cross_capability_calibration |

## Capabilities envolvidas

- `lacouncil.*` (read): `get_proposal`, `list_proposals`, `detect_patterns`, `get_trust_scores`, `record_project`
- `lacouncil.*` (denied no workflow-decomposer charter): `create_proposal`, `register_vote`, `tally_votes`
- Demais MCPs (`latade.*`, `ladesign.*`, `lan8n.*`, `laecon.*`, `laengine.*`, `n8n-community.*`, `context7.*`, `exa.*`, `github.*`): DENIED no workflow-decomposer charter (WDL-R1, MCP wall).

## Cross-references

- Proposta LACOUNCIL WDL v1: `a4fe9faa-4d50-4668-845a-ef64f1d41c36`
- Proposta LACOUNCIL Charter P0: `7fd94c1a-d21d-49cc-a0e6-07c07c716e73`
- LACOUNCIL Regime A: `391a8179-5a16-4b69-a3a3-d4ca1b20c2c3`
- Binding conditions capability-architect: `projects/_meta/capability-architect/binding-conditions.md` (G10, G11)
- Padrões de entrega: `knowledge/padroes-entrega.md`
- SDD principles: `knowledge/sdd-principles.md`
- Precedente meta-projeto: `projects/_meta/capability-architect/`

## Status

`M0_entregue_local` (working tree 2026-06-06). Próximo:
`delivery-reviewer G4 BASIC sign-off` (não auto-verificado). 30-day
window para STABLE: 2026-07-06.
