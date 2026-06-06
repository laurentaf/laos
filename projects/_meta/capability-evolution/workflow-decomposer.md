# Capability Evolution — workflow-decomposer

**Status:** IN_PROGRESS
**Created:** 2026-06-06
**Deadline:** 2026-07-06 (+30 dias da primeira dispatch)
**Owner:** `.opencode/agent/workflow-decomposer.md` (subagent do LAOS, não domain capability)

---

## Capability Info

| Field | Value |
|-------|-------|
| Name | workflow-decomposer |
| Status atual | BASIC (cold start) |
| Status target | STABLE |
| Tipo | meta_subagent (PM layer read-only) |
| Domínio | transversal (improvement, governance, investigation) |
| Charter | `.opencode/agent/workflow-decomposer.md` |
| Operating contract | `workflows/wdl-contract.yaml` (pinned `wdl_version: 1`) |
| Tracking issue | (none — wdl-rollout meta-project is the tracking vehicle) |

---

## Why

A orchestrator não tem ferramenta de PM entre needs resolution e
specialist dispatch. Sem isso, dispatch é inercial e capability gaps
ficam invisíveis. WDL v1 entrega a 1ª camada de governança: o
workflow-decomposer emite um verdict assinado (READY | DEFER |
ESCALATE) com `verified_by` populated, capability_gaps surfaced, e
exemption scope enumerable. 14 implementation conditions (8 WDL +
6 Charter P0) embute o regime de governança completo.

### Lacuna

- Subagent existe mas ainda não foi usado em 1+ projeto real.
- Confidence no MCP wall (lacouncil.* only) é hipotético até
  1+ dispatch real validar.
- Penalty schedule (-0.1/-0.3/-0.5) ainda não foi calibrado com
  evidência empírica.

---

## Evolution Plan

| Milestone | Descrição | Deadline | Status |
|-----------|-----------|----------|--------|
| WDL-M0 | Capability scaffold + 14 ICs implemented | 2026-06-06 | **done** (this rollout) |
| WDL-M1 | delivery-reviewer G4 BASIC sign-off | 2026-06-09 | pending |
| WDL-M2 | ≥ 1 real project dispatch with READY verdict | 2026-06-30 | pending |
| WDL-M3 | delivery-reviewer G8 STABLE sign-off | 2026-07-06 | pending |
| WDL-M4 | LACOUNCIL record: workflow-decomposer promoted BASIC→STABLE | 2026-07-07 | pending |

### WDL-M2 success criteria (gate to STABLE)

- ≥ 1 dispatch real do workflow-decomposer (não ad-hoc test).
- The verdict was `state: READY` with `verified_by != planner_id`.
- The orchestrator carried `[verdict.yaml, plan_id, verified_by]`
  forward into the specialist dispatch payload.
- The preflight `check_wdl_gate` exit_code was `0`.
- The delivery-reviewer STABLE sign-off (G8) cites the exit_code.

---

## Progress Log

| Data | Evento | Detalhe |
|------|--------|---------|
| 2026-06-06 | Created | Cold start via wdl-rollout meta-project. Proposal a4fe9faa (WDL v1) + 7fd94c1a (Charter P0), both supermaioria 4/4 SIM, 2026-06-06. |
| 2026-06-06 | WDL-M0 done | 16 deliverables entregues: agent file, contract, DuckDB migration, opencode.jsonc, preflight sub-check, boot check entry, AGENTS.md 4 sub-edits, ADR-011 + ADR-012, binding-conditions G10+G11, project.yaml arithmetic 14→16, SDD scaffold (8 files), tracking file. |

---

## Projects Dispatched (BASIC gate)

| Projeto | Data primeira dispatch | Status | Nota |
|---------|----------------------|--------|------|
| (none yet) | — | — | wdl-rollout é a M0; primeiro dispatch real acontece pós-G4 sign-off |

---

## Bloqueadores

- G4 sign-off do delivery-reviewer ainda não obtido (próximo passo).
- Regime A push ao GitHub depende de G4 (orchestrator executa, não
  capability-architect).

---

## Notas

- WDL v1 é pinned (`wdl_version: 1`). Mudanças no contrato
  operacional exigem nova proposta LACOUNCIL supermaioria.
- 14 implementation conditions são P0-blocking. Nenhuma pode ser
  removida sem revogação explícita do Conselho.
- Cross-references: ADR-011 (WDL), ADR-012 (Charter P0),
  `workflows/wdl-contract.yaml`, `binding-conditions.md` G10+G11.
