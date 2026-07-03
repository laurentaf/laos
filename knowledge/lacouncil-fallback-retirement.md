# Lacouncil automation-engineer fallback retirement

> **Provenance:** LACOUNCIL proposal `b43ca63d-b24e-4e9f-93a8-cc88d39c2678`
> (CLI/UX hygiene), C-B4 (30-day retirement plan). Approved 2026-07-02,
> 4/4 SIM unanimous (data, design, delivery, automation-via-proxy).

## Context

The OpenCode `task` tool's hardcoded `subagent_type` list does not include
`automation-engineer` in this version, even though
`.opencode/agent/automation-engineer.md` exists. The WDL gate would
accept (it validates by directory), but the `task` tool rejects before
WDL runs.

## Current workaround

Dispatch via `chief-engineer` with `voter: "automation-engineer"` in the
`lacouncil.vote.register` payload. Documented in
`.opencode/agent/orchestrator.md` §3a.

## When to retire

If `validate_agent(dispatch_type="automation-engineer")` returns
`valid: true` for **>=30 consecutive days**, the orchestrator should:

1. Prompt the user to remove the workaround section from
   `.opencode/agent/orchestrator.md` §3a.
2. Delete any `artifacts/wdl/<plan-id>/fallback.yaml` files from
   in-flight WDL plans.
3. Dispatch `automation-engineer` directly going forward.
4. Optionally: open a new LACOUNCIL proposal to formally retire the
   workaround (Registry change, supermaioria).

## How to check the 30-day condition

Manual check (no automated timer in the current LAOS):

```bash
validate_agent dispatch_type="automation-engineer"
# If returns valid: true, log the date.
```

After 30 days of `valid: true` returns, retire.

## Tracking

The 30-day clock starts on **2026-07-02** (the day of approval).
Retirement review due **2026-08-01** (30d).

## Related

- Proposal: `b43ca63d-b24e-4e9f-93a8-cc88d39c2678`
- Implementation: `.opencode/agent/orchestrator.md` §3a
- Original bug: P2 advisory from `d3095fa3` G4 BASIC sign-off (2026-07-02)
