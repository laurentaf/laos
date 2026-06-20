# Constitution — lacareerops Refactor Meta-Project

> **Origin:** LACOUNCIL `a4fe9faa-4d50-4668-845a-ef64f1d41c36` (WDL v1)
> + `7fd94c1a-d21d-49cc-a0e6-07c07c716e73` (Charter P0) + SDD scaffold
> Missão 0 (LACOUNCIL `f9b636fc-5ca9-4860-94ca-3a6b43c6862c`).
> Constitution template: `projects/_meta/capability-architect/spec/constitution.md`
> (que é o exemplo canônico).

## Article 1 — Purpose

This meta-project exists to **track the structural refactor of lacareerops**
and to anchor LACOUNCIL proposal `ba9a9bd7-3686-4d6e-9f1b-3efc46f37a8c`.

It does NOT produce code artifacts. It coordinates structural changes in
LAOS-side files (registry, knowledge, capability-evolution, ADR, meta-project)
and verifies the hub-side git submodule + new MCP tool exist and are valid.

## Article 2 — Scope

In scope (out of scope: project implementation artifacts):

- Add new MCP tool `career_ops_sync` to the wrapper (already in hub commit `9357af3`).
- Replace the lacareerops entry's repo URL in LAOS registry.
- Mirror ADR-013 (submodule refactor) in this meta-project's `spec/adr/`.
- Update LAOS knowledge base with "Submodule architecture" section.
- Update capability-evolution file with loop 1 refactor entry.

Out of scope:

- Any change to `career-ops` upstream behavior.
- Any change to `projects/_meta/lacareerops/` (the original creation meta-project;
  succeeded by this refactor meta-project; preserved as historical anchor).
- Any change to another subagent's prompt files (R5).

## Article 3 — Authority and roles

- **Capability-architect** implements structural changes (write files in
  LAOS repo + push hub files via github.* MCP).
- **Delivery-reviewer** validates G4 BASIC sign-off (WDL preflight gate +
  schema + non-empty + smoke check).
- **Orchestrator** commits + pushes LAOS repo (Regime A) once G4 passes.
- **Automation-engineer** is the G3 domain-specialist reviewer for both KB
  and contracts (carreer-ops is automation-domain).

## Article 4 — Quality bars

### 4.1 — Wrapper tools (G1 observability contract)

Every capability MUST expose, from day one:

- `health()` returns `{status, service, version, ...}`.
- `list_supported_operations()` returns typed catalog of all exposed tools.

### 4.2 — KB seed (G2)

Every KB seed MUST have a "Handoff Boundaries" section with ≥ 2 concrete
examples of when other capabilities should route to (or away from) this
capability.

### 4.3 — Smoke test (operative for sync tool)

`career_ops_sync` MUST run a 4-check smoke battery before persisting the
new pin: package.json parses, health() ok, list_supported_operations()
returns all 8 tools, node on PATH. Auto-rollback on any failure.

### 4.4 — Privacy invariants (preserved from ADR-003)

`config/profile.yml`, `config/cv.md`, `config/SNAPSHOT_*` MUST remain
gitignored. Hub is PRIVATE on GitHub. `career_ops_sync` MUST NOT read
user config.

## Article 5 — Calibration principle (PR-1, 20/10 vs 50/1)

Apply Level-A rigor: practical, defensible, evidence-backed.
Submodule + sync tool is the **least** architecture that closes the
investigation findings; do NOT over-engineer (e.g., no git LFS, no
custom git hooks server, no CI pipeline for sync). Ratio check:
+10% quality for +20% time = ADOPT. +1% for +50% = REJECT.

## Article 6 — Registry + opencode sync (G5)

After capability creation, BOTH `registry/capabilities.yaml` AND
`.opencode/opencode.jsonc` MUST reflect the new state:

- Registry entry `lacareerops.repo` points to the hub.
- opencode.jsonc `mcp.lacareerops` points to the hub's `mcp/server.py`.

## Article 7 — Traceability

Every artifact here MUST be traceable to a LACOUNCIL proposal:

- `spec/adr/ADR-013-lacareerops-submodule.md` ← `ba9a9bd7`
- `capability-evolution/lacareerops.md` ← `ba9a9bd7` (loop 1 row added)
- `registry/capabilities.yaml` ← `ba9a9bd7` (URL change + sync tool added)
- `knowledge/handoff-lacareerops.md` ← `ba9a9bd7` (Submodule architecture section)
- `mcp/server.py` (hub) ← `ba9a9bd7` (career_ops_sync + auto-rollback)

## Article 8 — Pre-flight + boot check

Before dispatching `delivery-reviewer`:

- `uv run python scripts/preflight_check.py projects/lacareerops-refactor`
  returns exit 0.
- `uv run python scripts/subagent_boot_check.py delivery-reviewer
  --project-name lacareerops-refactor` returns exit 0.
- Hard Rule 8 (WDL preflight gate) cleared at dispatch time (`verdict.yaml`
  state = READY, `verified_by` populated).

## Article 9 — Definition of done

- [x] Hub commits on main: `68d229c`, `9fc6f03`, `9357af3`, `c92d61c`.
- [x] LAOS-side structural files updated (registry, KB, capability-evolution,
      ADR-013, this meta-project).
- [ ] Delivery-reviewer G4 BASIC sign-off.
- [ ] LAOS repo push (Regime A, gated by reviewer's sign-off).
- [ ] `lacouncil.record_project(lacareerops_refactor)` for pattern detection.

## Article 10 — Amendments

Amendments to this constitution must go through LACOUNCIL approval.
In-scope: architectural shape, quality bars, calibration principle.
Out-of-scope: minor wording, formatting.

---

## Provenance

- WDL v1: `a4fe9faa-4d50-4668-845a-ef64f1d41c36` (supermaioria 4/4 SIM, 2026-06-06).
- Charter P0 WDL: `7fd94c1a-d21d-49cc-a0e6-07c07c716e73` (supermaioria 4/4 SIM, 2026-06-06).
- SDD scaffold Missão 0: `f9b636fc-5ca9-4860-94ca-3a6b43c6862c` (unanimidade 4/4, 2026-06-05).
- Lacareerops refactor proposal: `ba9a9bd7-3686-4d6e-9f1b-3efc46f37a8c` (2026-06-19).
- Lacareerops creation proposal: `2f1ccd2d-7d0a-44fc-8382-24c3e16ebd0c` (2026-06-13).
- Lacareerops creation ADR: `ADR-003-lacareerops-creation.md`.
- Lacareerops refactor ADR (this): `ADR-013-lacareerops-submodule.md`.

## Hard-rule alignment

| Hard Rule | Status |
|-----------|--------|
| HR #1 (no implementation in LAOS) | ✅ — only structural files; no SQL/code in LAOS repo. |
| HR #2 (projects live in their own repo) | ✅ — only contract mirror here; artifacts live in hub. |
| HR #3 (capabilities reached only through MCP) | ✅ — wrapper is the MCP origin. |
| HR #4 (routing is deterministic) | ✅ — needs unchanged; `registry/needs-to-capabilities.yaml` not modified. |
| HR #5 (structural changes require consensus) | ✅ — supermaioria 4/4 SIM. |
| HR #6 (every change logged) | ✅ — `ba9a9bd7` record + duckdb log. |
| HR #7 (3+ pattern triggers action) | N/A — single refactor. |
| HR #8 (WDL preflight gate mandatory) | ✅ — verdict READY. |
| HR #9 (venv policy) | N/A — no Python venv change in this meta-project. |
| HR #10 (LAOS permission grants) | ✅ — file ops under E:/projects/**. |
| HR #11 (no synthetic data) | ✅ — no synthetic; user data only in local snapshot. |
