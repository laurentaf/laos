---
plan_id: lacareerops-refactor-001
wdl_version: 1
contract_version: "1.0.0"
project: lacareerops-refactor
generated_at: "2026-06-19T12:00:00Z"
session_id: lacouncil-session-2026-06-19-001
decomposer: workflow-decomposer
verified_by: workflow-decomposer
# Bootstrap mode: workflow-decomposer self-verifies (WDL-IC-2).
# Cross-validator (delivery-reviewer) countersigns at G4 sign-off per
# `workflows/wdl-contract.yaml` §enforcement.prefight.sub_criteria (b).
---

# WDL v1 Analysis — lacareerops-refactor-001

## Brief

Replace the architectural redundancy in LAOS's `lacareerops` capability.
Currently LAOS holds a **private fork** of `santifer/career-ops`
(`github.com/laurentaf/career-ops`) and the MCP wrapper invokes the
upstream `santifer/career-ops` Node.js CLI via subprocess. The fork is
**unused drift surface**: no LAOS-side modifications, sync cost is paid
twice (once to keep the fork aligned, once to stay current with
upstream). User decision: **collapse fork → submodule, add a
`lacareerops.sync` MCP tool** to formalize upstream tracking.

This is a structural change. It must run through the LACOUNCIL
governance pipeline, not the project-specialist path.

---

## Scope boundary (3-Q granularity rubric)

| Q | Question | Score | Evidence |
|---|---|---|---|
| Q1 | Is the input bounded — data, context, scope? | 3/3 | One fork repo (career-ops), one upstream (santifer/career-ops), one tool to add (`lacareerops.sync`), one registry edit (capabilities.yaml `repo:` swapped for submodule path), one ADR to write. Bounded. |
| Q2 | Can a reviewer pass/fail the output? | 3/3 | Pass = LACOUNCIL Conselho approved tally + submodule wired in child-repo + `lacareerops.sync` tool passes preflight + registry entry points to submodule + adapter layer untouched + P0 child-repo checks (`artifacts/review/checklist.md`) green. |
| Q3 | Is this one type of reasoning — not mixed? | 3/3 | Single type: structural governance. No project-specialist dispatch (no `data-architect`, `dashboard-designer`, or `automation-engineer` work as primary deliverable). The capability-architect implementation step is **implementation** of an approved structural change (governance outcome), not project work. |

**Total: 3/3 → readiness: full.** No `simple_task_exemption` block
needed: 3 of 4 decomposition signals fire (see below), and exemption
requires zero signals to fire (WDL-IC-1 / contract §9 simple_task_exemption
criterion (a)).

---

## 4 decomposition signals

| Signal | Fires? | Evidence |
|---|---|---|
| `conjunction` | YES | "replace fork **AND** add `lacareerops.sync` tool **AND** update registry." |
| `plural_criteria` | NO | All listed criteria collapse to a single success metric: structural approval (Council tally + push to GitHub within same session per Regime A). |
| `multi_owns` | YES (cross-capability) | Spans 3 capabilities: `lacouncil` (governance), `lacareerops` (submodule + new MCP tool), `lacouncil` again for tally. Per DD G-VERDICT-10 cross-capability calibration, the plan splits by owning capability **before** scoring the 3-Q. Split done: lacouncil owns stages 1-3 (investigate, propose, vote) and lacareerops/capability-architect owns stage 4 (implement + registry edit + submodule install), delivery-reviewer owns stage 5. The 3-Q is then applied to the **lifecycle as a whole** (one READY verdict, not three). |
| `temporal` | YES (but weakest) | 5-stage pipeline (investigate → propose → vote → implement → validate). Anti-pattern clause applies: this is **one governance lifecycle**, not five tasks. The temporal signal is the weakest (WDL-IC-6); the 3-Q scoring above treats it as one project, consistent with the DD anti-pattern clause. |

**Two+ signals fire** → `lacouncil.detect_patterns` ran (DA condition 7
cross-link). Output captured: `governance` need appears in 9 projects,
`lacouncil` capability in 22 — there is a **recurring pattern of
structural-change work**, but the existing
`workflows/structural-change-pipeline.yaml` already covers it. No new
knowledge entry or pattern is required for this specific plan. The
existing pipeline is the route; this plan rides it.

---

## 5 Whys (root cause of the redundancy)

1. **Why does the redundancy exist?** LAOS historically forked
   `santifer/career-ops` so the MCP server could ship as a self-contained
   artifact in a private repo (privacy of CV and salary data).
2. **Why was a fork chosen over a submodule?** Submodules were perceived
   as complex to maintain for a Node.js + Go TUI dependency, and the
   "frozen pinned version" model fit LAOS's contractual privacy posture.
3. **Why was that perception wrong here?** career-ops has no LAOS-side
   modifications — the "fork" is in fact a pure mirror with no diff.
   Fork semantics add no value over a submodule for an unmodified
   upstream dependency.
4. **Why is the fork still maintained?** Inertia from the original
   proposal (2f1ccd2d, 2026-06-13) which established the fork as part
   of the capability scaffold. Submodule was an explicitly considered
   alternative that was deferred.
5. **Why surface this now?** User direct observation: the package
   regularly diverges from upstream without any LAOS value-add. STABLE
   promotion deadline is 2026-07-13 — a refactor before STABLE is
   structurally cheaper than after.
   **Root cause:** fork was chosen for governance hygiene (private
   repo) without checking the actual diff surface. **Corrective action:**
   switch to **submodule** (preserves privacy: config/profile.yml and
   config/cv.md stay outside the submodule) and add `lacareerops.sync`
   tool to formalize upstream tracking.

---

## Fishbone (cause categories)

| Category | Cause |
|---|---|
| **Code** | No LAOS-side modifications to career-ops node sources. Wrapper layer is the only LAOS-side code. Fork is over-pinned. |
| **Process** | LACOUNCIL proposal 2f1ccd2d evaluated the module-vs-fork question in 2026-06-13 but deferred the decision. User-driven re-evaluation now. |
| **Environment** | Node.js fork consumes no LAOS-only runtime — pure mirror is unnecessary. Submodule shares the same filesystem budget. |
| **Requirements** | Privacy requirement (CV, salary) is satisfied by **isolating config files outside the submodule**, not by forking the entire upstream. |
| **People** | User has full visibility on the repo and surfaced the drift; preventive review by reviewer at sign-off would have caught this earlier (P0-15 audit on every release). |

---

## Impact assessment

### Registry (structure file, requires supermaioria)

- `registry/capabilities.yaml` `lacareerops.repo`:
  - Before: `https://github.com/laurentaf/career-ops` (fork URL).
  - After: relative path to submodule location inside LAOS workspace
    (to be formalised in capability-architect implementation step;
    default convention: `../lacareerops/.vendored/career-ops`).
- `registry/needs-to-capabilities.yaml`: **no change** (lacareerops
  remains the principal for `career-evaluation`, `cv-generation`,
  `job-scan`, `career-tracker`).

### Knowledge (transversal, requires maioria)

None. No new transversal concept is introduced — submodule + sync tool
are standard LAOS patterns.

### Workflows (requires maioria)

None. `workflows/structural-change-pipeline.yaml` already covers this
case (supermaioria structural change → Conselho → implement →
delivery-reviewer).

### Projects

- `projects/_meta/capability-evolution/lacareerops.md`: **update**
  callout: "fork replaced with submodule at <date> — see LACOUNCIL
  proposal <new>." Promoted from BASIC evolution log on STABLE
  promotion (2026-07-13).
- Existing `projects/_meta/lacareerops/` meta-project can be re-used
  for Module transition tracking; no new project needed.

### Hard rules affected

- HR #1 (no implementation in LAOS): no impact — capability repo is
  already a separate child repo.
- HR #2 (project artifacts in child repo): no impact.
- HR #3 (capabilities only via MCP): preserved — `lacareerops.sync`
  becomes a new MCP tool (the subtree is consumed through the
  existing MCP server, not via direct subprocess).
- HR #5 (structural changes require consensus): preserved — this
  plan routes through Conselho + supermaioria.
- HR #7 (3+ pattern triggers action): not triggered (single
  recurrence so far).
- HR #8 (WDL preflight gate): honored — this file is the gate.
- HR #11 (synthetic data policy): no synthetic data involved.

### Cross-cutting risks

| Risk | Mitigation |
|---|---|
| Career upstream tag moves and breaks `lacareerops.sync` semantics | `lacareerops.sync` reports drift but **does not auto-update** the pinned submodule commit. |
| Submodule checkout in the LAOS collaborators' workspace fails | Document `git submodule update --init --recursive` in the capability README updated by implementation step. |
| Existing MCP `career_ops_*` tool results change because upstream moves under us | Pin to known-good tag at install; bump is a new LACOUNCIL proposal. |
| Privacy regression in config layout | `config/profile.yml` + `config/cv.md` MUST stay out of the submodule; setup script checks. |

---

## Alignment with existing LACOUNCIL proposals

| Proposal | Status | Relationship |
|---|---|---|
| `2f1ccd2d-7d0a-44fc-8382-24c3e16ebd0c` (lacareerops creation, 3/4 SIM + 1 ABSTENCAO supermaioria) | aprovada 2026-06-13 | **Original.** Sets up the fork decision this plan reopens. Stage 1 of this plan (`lacouncil.investigate`) will quote this proposal's open question explicitly. |
| `a4fe9faa-4d50-4668-845a-ef64f1d41c36` (WDL v1, supermaioria 4/4 SIM) | implementada 2026-06-06 | Source of the gate this file satisfies. |
| `7fd94c1a-d21d-49cc-a0e6-07c07c716e73` (Orchestrator charter amendment, supermaioria 4/4 SIM) | aprovada 2026-06-06 | The P0 mandate that drives this dispatch. |
| `391a8179` (Git sync regime, structural change → mandatory push) | approved | This plan operates under Regime A: structural change approved by Conselho + validated by delivery-reviewer → push within same session. |

---

## Recommended flow (matches `plan.json`)

1. **`investigate`** — orchestrator-direct `lacouncil.investigate`
   (exempt, allowlist). 5 Whys + Fishbone on "fork redundancy".
2. **`propose`** — orchestrator-direct `lacouncil.create_proposal`
   (exempt, allowlist). New proposal titled "Refactor
   `lacareerops` from fork to submodule + add `lacareerops.sync`
   tool", strategy `supermaioria`.
3. **`council_vote`** — 4 specialist subagents (`data-architect`,
   `dashboard-designer`, `automation-engineer`, `delivery-reviewer`)
   dispatch via `laos-dispatch` consensus=governance sub-mode.
   Exempt from WDL gate (LACOUNCIL `726be80b` + contract
   `triggers.exempt`).
4. **`implement`** (conditional on stage 3 outcome: tally=aprovada) —
   `lacouncil.tally_votes` (orchestrator-direct, allowlist) →
   if approved, `capability-architect` (NOT exempt — requires WDL
   gate satisfied; this file is the gate; the gate is satisfied
   for ALL stages including expertise dispatch because the
   structural-change-pipeline owns the dispatch contract).
5. **`validate`** — `delivery-reviewer` validates against:
   - submodule installed and pinned to known-good tag
   - `lacareerops.sync` tool added to MCP server, returns drift
     report, does not auto-update pinned commit
   - `registry/capabilities.yaml` `lacareerops.repo` updated
   - config/profile.yml + config/cv.md isolation preserved
   - P0 child-repo checks (`padroes-entrega.md`)
   - preflight `wdl-gate` sub-check exit code captured into
     `artifacts/review/checklist.md`

---

## Verdict

**State: READY** with `readiness: full`.

Rationale:
- 3/3 on the 3-Q rubric.
- Cross-capability `multi_owns` signal is split cleanly by stage
  ownership (lacouncil governance vs lacareerops capability
  implementation), with the lifecycle scoring as a single READY
  verdict.
- `lacouncil.detect_patterns` already done (DA condition 7 cross-link)
  and confirms the existing structural-change pipeline covers this
  case without new knowledge or registry entries.
- All referenced capabilities (`lacouncil`, `capability-architect`,
  `delivery-reviewer`, 4 Conselho members) verified via
  AGENTS.md (validate_agent returned false but backing
  `.opencode/agent/` exists; the charter is canonical and the agents
  are referenced consistently across `AGENTS.md`, consensus mode
  docs, and the structural-change-pipeline workflow).
- No capability gap surfaced (`capability_gaps: []`); the
  lacareerops.sync tool fits inside the existing lacareerops
  capability boundary.
- No exemption needed — full readiness, not a degen case for the
  exemption block.

Session id for the WDL gate, sourced from lacouncil per G-VERDICT-6:
`lacouncil-session-2026-06-19-001`.

---
