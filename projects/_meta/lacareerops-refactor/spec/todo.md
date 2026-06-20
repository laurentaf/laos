# TODO — lacareerops Refactor Meta-Project

> Status legend: ⏳ pending · 🔄 in-progress · ✅ done · 🚫 blocked · ❌ rejected

## Stage 0 — Discover + scaffold (Missão 0 / SDD)

- [x] ✅ Read project.yaml + contract.md (this meta-project's own).
- [x] ✅ Toolchain inventory: capabilities (lacouncil, github); no new
      runtime needed.
- [x] ✅ Confirm WDL verdict state = READY (`verdict.yaml`,
      `lacareerops-refactor-001`, verified_by = workflow-decomposer).
- [x] ✅ Confirm LACOUNCIL proposal `ba9a9bd7` status = `aprovada`.
- [x] ✅ Confirm upstream `santifer/career-ops` reachable + HEAD captured.
- [x] ✅ Snapshot existing `E:/projects/career-ops/config/` to
      `config/SNAPSHOT_2026-06-19/`.
- [x] ✅ Create meta-project skeleton (this directory + project.yaml).

## Stage 1 — Pre-authorize (binding conditions R1-R5)

- [x] ✅ Capability-architect prompt re-read.
- [x] ✅ R1 — proposal aprovada gate cleared (`ba9a9bd7`).
- [x] ✅ R2 — no project artifacts in this dispatch scope.
- [x] ✅ R3 — no Conselho voting in this dispatch.
- [x] ✅ R4 — not self-proposing; orchestrator owns proposals.
- [x] ✅ R5 — no other subagent prompt file modified.

## Stage 2 — Hub implementation (REMOTE WRITES)

- [x] ✅ Hub repo `laurentaf/lacareerops-hub` exists (PRIVATE).
- [x] ✅ `68d229c` initial commit (repo skeleton).
- [x] ✅ `9fc6f03` submodule + SUBMODULE_SHA.txt scaffold.
- [x] ✅ `9357af3` mcp/server.py v1.1.0 + career_ops_sync + LICENSE +
      docs/adr/ADR-013-lacareerops-submodule.md.
- [x] ✅ `c92d61c` README ADR numbering fix.

## Stage 3 — LAOS structural files (LOCAL WRITES)

- [x] ✅ `registry/capabilities.yaml` — `lacareerops.repo` → hub URL.
- [x] ✅ `knowledge/handoff-lacareerops.md` — "Submodule architecture (v1.1.0)"
      section.
- [x] ✅ `projects/_meta/capability-evolution/lacareerops.md` — loop 1 entry.
- [x] ✅ `projects/_meta/adr/ADR-013-lacareerops-submodule.md` — LAOS-side canonical.
- [x] ✅ `projects/_meta/lacareerops-refactor/project.yaml`.
- [x] ✅ `projects/_meta/lacareerops-refactor/contract.md`.
- [x] ✅ `projects/_meta/lacareerops-refactor/spec/constitution.md`.
- [x] ✅ `projects/_meta/lacareerops-refactor/spec/todo.md` (this file).

## Stage 4 — preflight + boot check

- [x] ✅ Hard Rule #8 (WDL preflight gate) cleared.
- [x] ✅ Hard Rule #9 (no external venv) cleared.
- [ ] ⏳ `uv run python scripts/preflight_check.py projects/lacareerops-refactor`
      — orchestrator will run before delivery-reviewer dispatch.
- [ ] ⏳ `uv run python scripts/subagent_boot_check.py delivery-reviewer
      --project-name lacareerops-refactor` — orchestrator will run pre-dispatch.

## Stage 5 — Domain-specialist review (G3)

- [ ] ⏳ automation-engineer KB + contracts review.
      (Owner: orchestrator / delivery-reviewer; not capability-architect scope.)

## Stage 6 — Delivery-reviewer G4 BASIC sign-off

- [ ] ⏳ delivery-reviewer validates:
  - `health_check: smoke_test_pending_first_session` (no real CV test).
  - `career_ops_sync(dry_run=True)` reports `{status: ok, smoke_passed: ...}`.
  - `list_supported_operations` returns 8 ids including `career_ops_sync`.
  - Wrapper crisis path (no upstream, no node): graceful failure, not 500.
  - Registry entry valid; KB non-empty; ADR-013 present; meta-project files
    non-empty.

## Stage 7 — Push (Regime A)

- [x] ✅ Hub already pushed (this dispatch).
- [ ] ⏳ LAOS repo push after delivery-reviewer sign-off.
  - Not in capability-architect scope; orchestrator owns the Regra A push.
  - File scope: only `projects/_meta/lacareerops-refactor/`,
    `projects/_meta/adr/ADR-013-lacareerops-submodule.md`,
    `projects/_meta/capability-evolution/lacareerops.md`,
    `knowledge/handoff-lacareerops.md`,
    `registry/capabilities.yaml`.

## Stage 8 — Project memory

- [ ] ⏳ `lacouncil.record_project(lacareerops_refactor)` for pattern detection.
      Caller: orchestrator after push.

## Stage 9 — Upstream tracking (`career_ops_sync` workflow)

- [ ] ⏳ **Manual advance (MVP, today).** `career_ops_sync(dry_run=False)`
      in MCPtakes pin from `SUBMODULE_SHA.txt` and offers advancing to
      upstream HEAD. Operator runs manually when santifer/career-ops
      updates. 4-check smoke battery (`package_json_parses`,
      `health_ok`, `list_ops_complete`, `node_on_path`) executes; on
      failure, **automatic rollback** to previous SHA + commit discarded.

- [ ] ⏳ **Scheduled advance (post-STABLE milestone, target M+30).** Wire
      `lan8n` cron workflow (default weekly) that calls
      `lacareerops.career_ops_sync(dry_run=True)` for drift detection,
      alerts operator if upstream SHA differs, then awaits operator
      confirmation before `dry_run=False`. Owner: `automation-engineer`
      + `lan8n.health()` integration. Tracking in
      `projects/_meta/capability-evolution/lacareerops.md` STABLE
      evolution section.

- [ ] ⏳ **Autonomous pin advance (M+60, opcional).** Once 30 days of
      stable operation pass with no operator interventions, propose
      LACOUNCIL to make `career_ops_sync` fully autonomous: auto-pull +
      smoke + commit on green, rollback on red, log to LACOUNCIL. This is
      the full vision of "stay updated without operator".

## Stage 10 — 30-day STABLE path legacy

- [ ] ⏳ M1 STABLE deadline: 2026-07-13. Track progress in
      `capability-evolution/lacareerops.md`.
