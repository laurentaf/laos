# SPEC-000: Bootstrap — capability-architect meta-project

**Status:** ACEITO
**Version:** 1.0
**Authors:** Laurent (orchestrator)
**Owner:** Laurent

---

## Contexto

Meta-project for the capability-architect subagent. Created via LACOUNCIL proposal 2f42afe6-71d5-4ef8-a88a-1339d72ec501 (approved 4/4 SIM, supermajority, 2026-06-04). The capability-architect fills a gap: no dedicated agent existed for implementing structural changes approved by the Conselho. Previously the orchestrator did this inline, violating separation of duties.

## Decisão inicial

Add a 6th subagent (capability-architect) to the LAOS topology with:
- Scope restricted to LACOUNCIL-approved structural changes only
- 5 structural restrictions (R1–R5): no project work, no voting, no proposing, gate-checked, no cross-agent prompt edits
- 9 quality gates (G1–G9): observability, KB, domain review, BASIC sign-off, registry sync, evolution tracking, ADR, STABLE timeline, git sync
- BASIC status with 30-day mandatory evolution to STABLE by 2026-07-04

## Critérios de pronto

- [ ] M0 scaffold complete (BASIC sign-off passed — DONE 2026-06-04)
- [ ] M1 STABLE promotion by 2026-07-04 (>= 1 real use + community feedback + delivery-reviewer sign-off)
- [ ] All 14 binding conditions (R1–R5 + G1–G9) verified as enforceable
- [ ] Git sync regime (G9, LACOUNCIL 391a8179) enforced for all structural changes

## Sources

| Source | Description |
|--------|-------------|
| binding-conditions.md | R1–R5 + G1–G9 gates (canonical list) |
| ADR-003 | Rationale for capability-architect creation |

## Destination

N/A (meta-project, no data pipeline)

## Refresh Strategy

Mode: manual (on each structural change dispatch)
