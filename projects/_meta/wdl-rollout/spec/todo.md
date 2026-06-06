# TODO — wdl-rollout (meta-projeto WDL v1)

---

## Phase 0: SDD scaffold (Missão 0 — esta fase)

- [ ] Criar scaffold em projects/_meta/wdl-rollout/ (concluído 2026-06-06)
- [ ] spec/constitution.md (concluído 2026-06-06)
- [ ] spec/todo.md (este arquivo; ≥ 1 task com `- [ ]`)
- [ ] spec/adr/_template.md (cópia literal LATADE)
- [ ] spec/adr/README.md (índice vazio, gate aceita)
- [ ] spec/harness/_template.md (cópia literal LATADE)
- [ ] spec/specs/000-bootstrap/spec.md (Contexto + Decisão + Critérios)
- [ ] contract.md (espelha project.yaml em prosa)
- [ ] README.md (O que é / Como rodar / Onde está o quê)
- [ ] spec/design-direction.md é CONDICIONAL (pulada — needs: sem dashboard|design)

## Phase 1: Part 1 — WDL v1 deliverables (proposal a4fe9faa)

- [x] .opencode/agent/workflow-decomposer.md (entregue 2026-06-06)
- [x] workflows/wdl-contract.yaml (entregue 2026-06-06, pinned wdl_version: 1)
- [x] scripts/migrate_lacouncil_wdl_signatures.py (entregue 2026-06-06; idempotente)
- [x] memoria/lacouncil.duckdb wdl_signatures table (entregue 2026-06-06)
- [x] .opencode/opencode.jsonc — entry workflow-decomposer (entregue 2026-06-06)
- [x] scripts/preflight_check.py — sub-check wdl-gate (entregue 2026-06-06)
- [x] scripts/subagent_boot_check.py — entry workflow-decomposer (entregue 2026-06-06)
- [x] projects/_meta/adr/ADR-011-wdl-workflow-decomposer.md (entregue 2026-06-06)
- [x] projects/_meta/capability-architect/binding-conditions.md — G10 (entregue 2026-06-06)
- [x] projects/_meta/capability-architect/project.yaml — arithmetic 14→16 (entregue 2026-06-06)

## Phase 2: Part 2 — Charter P0 deliverables (proposal 7fd94c1a)

- [x] AGENTS.md — Hard Rule #8 (entregue 2026-06-06)
- [x] AGENTS.md — Agent topology entry (entregue 2026-06-06)
- [x] AGENTS.md — §"Your loop" WDL preflight gate subsection (entregue 2026-06-06)
- [x] AGENTS.md — §"Tools you do NOT use" clarifier (entregue 2026-06-06)
- [x] projects/_meta/adr/ADR-012-orchestrator-wdl-preflight-p0.md (entregue 2026-06-06)
- [x] projects/_meta/capability-architect/binding-conditions.md — G11 (entregue 2026-06-06)
- [x] .opencode/agent/delivery-reviewer.md — WDL section (entregue 2026-06-06)

## Phase 3: Self-verification (Part 3)

- [x] `uv run python scripts/subagent_boot_check.py workflow-decomposer --project-name wdl-rollout` PASS
- [x] `uv run python scripts/preflight_check.py projects/_meta/wdl-rollout` PASS
- [ ] **Handoff to delivery-reviewer for G4 sign-off (NOT self-verified).**

## Phase 4: G4 BASIC sign-off (delivery-reviewer's job)

- [ ] delivery-reviewer walks the 14-cond traceability matrix
- [ ] delivery-reviewer validates MCP wall (lacouncil.* only) of workflow-decomposer
- [ ] delivery-reviewer validates preflight wdl-gate 4 sub-criteria
- [ ] delivery-reviewer validates AGENTS.md 4 sub-edits
- [ ] delivery-reviewer validates ADR-011 + ADR-012 formato ADR-001
- [ ] delivery-reviewer issues G4 sign-off (DELIVERABLE)

## Phase 5: Regime A push (orchestrator's job)

- [ ] orchestrator commits working tree to local git
- [ ] orchestrator pushes to GitHub (regime A — mandatory per LACOUNCIL 391a8179)
- [ ] orchestrator confirms `git log` on remote shows the new SHA
- [ ] orchestrator reports back: "Regime A push done."

## Phase 6: BASIC window 30d → STABLE (future)

- [ ] WDL used in ≥ 1 real project dispatch (gate M2 — promotion precondition)
- [ ] delivery-reviewer STABLE sign-off (G8)
- [ ] BASIC → STABLE promotion in `projects/_meta/capability-evolution/workflow-decomposer.md`

## Completed

- [x] 16 deliverables entregues em working tree (2026-06-06)
- [x] LACOUNCIL record_project() para wdl-rollout (a fazer pelo orchestrator pos-sign-off)
