# WDL Analysis — governance-726be80b

**Plan ID:** governance-726be80b
**Project:** LAOS (meta-project, structural improvement)
**Dispatch type:** CONSELHO_GOVERNANCE
**Generated:** 2026-06-13
**Analyzed by:** workflow-decomposer

---

## Request summary

The orchestrator dispatched the workflow-decomposer to:
1. Produce a WDL governance verdict for proposal `726be80b-9f72-4dac-aa25-12bc076b1794`
2. Dispatch the 3 remaining Conselho members (data-architect, dashboard-designer, automation-engineer) for voting via `lacouncil.register_vote()`

## Proposal context

- **Title:** WDL Gate: Add Conselho Governance Exemption
- **Domain:** laos
- **Strategy:** maioria
- **Status:** rascunho (draft) — 0 votes, not yet in em_consulta
- **Problem:** WDL gate blocks Conselho voting dispatches (design flaw)
- **Solution:** Add `CONSELHO_GOVERNANCE` exemption to WDL gate plugin

## 3-Q scoring

| Q | Score | Rationale |
|---|---|---|
| Clear input | 3/3 | Request is bounded: specific proposal, specific action (dispatch voting) |
| Validatable success | 3/3 | Success = 3 votes registered on proposal 726be80b |
| Single reasoning type | 3/3 | Governance analysis + dispatch — single domain |
| **Total** | **3/3** | Full readiness |

## 4-signal decomposition

| Signal | Fires? | Rationale |
|--------|--------|-----------|
| Conjunction | No | Single action requested (dispatch voting) |
| Plural-criteria | No | Single success criterion (votes registered) |
| Multi-owns | No | Single capability (lacouncil) |
| Temporal | No | No multi-stage sequence |

**Result:** 0 signals fire. No decomposition needed.

## Structural conflict identified

Despite 3/3 on 3-Q, this request has a **scope conflict** that prevents the workflow-decomposer from executing it:

### Conflict 1: WDL-R5 (no voting)

The workflow-decomposer charter explicitly states:
> **WDL-R5 (no voting).** You MUST NOT call `lacouncil.register_vote`. Voting is the 4 specialist subagents' job, not yours.

The orchestrator is asking the decomposer to dispatch voting. This is outside the decomposer's authorized tool set. Even if the decomposer could call `lacouncil.register_vote()`, the charter forbids it.

### Conflict 2: Proposal status

Proposal `726be80b` is in `rascunho` (draft) status. Voting requires the proposal to be in `em_consulta` status. The proposal must first be transitioned (via `lacouncil.create_proposal` or equivalent) before votes can be cast. The decomposer cannot do this (WDL-R4: no proposals).

### Conflict 3: Exemption scope

This request is **structural improvement governance**, not project work. Per WDL contract §triggers.exempt:
> Orchestrator's own direct `lacouncil.*` invocations for structural improvement work (LACOUNCIL proposals, structural investigations, trust-score reads). These are NOT project work; they are the governance layer's own operations.

The WDL gate should NOT be applied to this request at all. The orchestrator should handle this directly via `lacouncil.register_vote()` (exempt tool) without going through the workflow-decomposer.

## Recommended resolution

The orchestrator should:

1. **Transition proposal 726be80b** from `rascunho` to `em_consulta` (if that's the intended next step — requires the proposal author or an admin action)
2. **Call `lacouncil.register_vote()` directly** for each Conselho member:
   - `data-architect` → vote on proposal 726be80b
   - `dashboard-designer` → vote on proposal 726be80b
   - `automation-engineer` → vote on proposal 726be80b
3. **Call `lacouncil.tally_votes()`** after all votes are cast

These are all exempt `lacouncil.*` calls — no WDL gate needed, no trust-score penalty.

## Why DEFER (not READY or ESCALATE)

- **Not READY:** The decomposer cannot execute the requested action (voting is forbidden by WDL-R5)
- **Not ESCALATE:** There is no capability gap or structural ambiguity — the decomposer correctly understands what's needed but is the wrong agent for the job
- **DEFER:** The request should be re-routed to the orchestrator's direct `lacouncil.*` invocation path, which is exempt from the WDL gate
