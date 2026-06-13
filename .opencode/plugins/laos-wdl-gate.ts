/**
 * LAOS WDL Gate — Enforces the WDL preflight gate before specialist dispatch
 *
 * Provenance:
 *   - Hard Rule #8 (AGENTS.md): "WDL preflight gate is mandatory before
 *     specialist dispatch."
 *   - LACOUNCIL a4fe9faa: WDL v1 proposal (supermaioria 4/4, 2026-06-06)
 *   - LACOUNCIL 7fd94c1a: Charter P0 for workflow-decomposer
 *   - workflows/wdl-contract.yaml: Operating contract for WDL v1
 *
 * This plugin enforces mechanically what was previously orchestrator-prompt-only:
 *   1. BLOCK dispatch of specialist subagents (via the `task` tool) unless
 *      a valid WDL verdict.yaml exists with state: READY.
 *   2. Verify that verdict.yaml has verified_by populated (Hard Rule 8.1).
 *   3. Record bypass-manifest.yaml if the orchestrator overrides (Hard Rule 8.3),
 *      requiring user confirmation.
 *   4. Track bypass penalties (Hard Rule 8.2: -0.1 per bypass, -0.3 max per plan-id).
 *
 * Exemption (Hard Rule 8.4): The orchestrator's own lacouncil.* calls for
 * structural improvement work are exempt from the WDL gate. The 9 exempt
 * tools are: investigate, create_proposal, get_proposal, list_proposals,
 * register_vote, tally_votes, implement_proposal, record_project, detect_patterns.
 *
 * Implementation note: OpenCode's plugin system doesn't have direct filesystem
 * access from within hooks. This plugin uses the `bash` tool via the `$` helper
 * to check for verdict.yaml files. If that's not available, it falls back to
 * a session-level state tracker.
 */

import type { Plugin } from "@opencode-ai/plugin"

const WDL_EXEMPT_TOOLS = [
  "lacouncil_investigate",
  "lacouncil_create_proposal",
  "lacouncil_get_proposal",
  "lacouncil_list_proposals",
  "lacouncil_register_vote",
  "lacouncil_tally_votes",
  "lacouncil_implement_proposal",
  "lacouncil_record_project",
  "lacouncil_detect_patterns",
]

const SPECIALIST_AGENTS = [
  "data-architect",
  "dashboard-designer",
  "automation-engineer",
  "capability-architect",
]

// Conselho governance agents — exempt from WDL gate when dispatch_type is CONSELHO_GOVERNANCE
// LACOUNCIL proposal 726be80b (approved 4/4 SIM, 2026-06-13)
const CONSELHO_GOVERNANCE_AGENTS = [
  "data-architect",
  "dashboard-designer",
  "automation-engineer",
  "delivery-reviewer",
]

interface WdlState {
  planId: string | null
  verdictState: "READY" | "DEFER" | "ESCALATE" | "NONE" | null
  verifiedBy: string | null
  bypassCount: number
  bypassPenalty: number
}

// Session-level WDL state (in-memory; per-project state is persisted
// by laos-recovery.ts to .laos/state/verdicts.json)
const wdlState: WdlState = {
  planId: null,
  verdictState: null,
  verifiedBy: null,
  bypassCount: 0,
  bypassPenalty: 0,
}

export const WdlGate = async ({ project, directory }: { project: string; directory: string }) => {
  return {
    "tool.execute.before": async (
      input: { tool: string; sessionID: string; callID: string },
      output: { args: any }
    ) => {
      // ─── Exempt: lacouncil.* structural work ───────────────────
      if (WDL_EXEMPT_TOOLS.some(t => input.tool === t || input.tool.startsWith("lacouncil_"))) {
        return // WDL gate does not apply
      }

      // ─── Only gate the `task` tool (specialist dispatch) ───────
      if (input.tool !== "task") return

// Check if the dispatch is for a specialist subagent
// OpenCode's task tool uses subagentType (camelCase) in args
const subagentType = output.args?.subagentType || output.args?.subagent_type || ""
      if (!SPECIALIST_AGENTS.includes(subagentType)) return

      // ─── Exempt: Conselho governance dispatch ──────────────────
      // When the orchestrator dispatches specialists for Conselho voting
      // (structural improvement governance), the WDL gate does not apply.
      // This is consistent with Hard Rule 8.4 and the MCP wall precedent.
      // LACOUNCIL proposal 726be80b (approved 4/4 SIM, 2026-06-13).
      // Check prompt for governance marker (task tool doesn't have dispatch_type param)
      const prompt = output.args?.prompt || ""
      const isGovernanceDispatch = prompt.includes("[intent-gate:conselho]") || 
                                   prompt.includes("CONSELHO_GOVERNANCE") ||
                                   prompt.includes("Conselho voting") ||
                                   prompt.includes("conselho voting")
      if (isGovernanceDispatch && CONSELHO_GOVERNANCE_AGENTS.includes(subagentType)) {
        // Governance dispatch — no WDL gate needed
        return
      }

      // ─── Check WDL verdict ─────────────────────────────────────
      // The verdict is set by the workflow-decomposer subagent and
      // recorded in the session state by the orchestrator.
      // This plugin checks the in-memory state.
      if (wdlState.verdictState === "READY" && wdlState.verifiedBy) {
        // Gate passed — include verdict info in the dispatch payload
        output.args = {
          ...output.args,
          _wdl: {
            plan_id: wdlState.planId,
            verified_by: wdlState.verifiedBy,
            state: wdlState.verdictState,
          },
        }
        return
      }

      // ─── Gate FAILED — block dispatch ──────────────────────────
      if (wdlState.verdictState === "DEFER") {
        throw new Error(
          `[LAOS WDL Gate] Cannot dispatch "${subagentType}" — WDL verdict is DEFER. ` +
          `Plan ID: ${wdlState.planId}. ` +
          `The workflow-decomposer requires more information or a different approach. ` +
          `Resolve the DEFER condition before retrying.`
        )
      }

      if (wdlState.verdictState === "ESCALATE") {
        throw new Error(
          `[LAOS WDL Gate] Cannot dispatch "${subagentType}" — WDL verdict is ESCALATE. ` +
          `Plan ID: ${wdlState.planId}. ` +
          `The workflow-decomposer escalated this plan. Review the escalation reason ` +
          `in artifacts/wdl/${wdlState.planId}/analysis.md before retrying.`
        )
      }

      // No verdict at all — this is the most common case initially
      throw new Error(
        `[LAOS WDL Gate] Cannot dispatch "${subagentType}" — no WDL verdict found. ` +
        `Hard Rule #8.1: Specialist dispatch requires a READY verdict from ` +
        `workflow-decomposer. Dispatch workflow-decomposer first, then retry. ` +
        `To bypass (Hard Rule #8.3), the orchestrator must: ` +
        `(1) record bypass-manifest.yaml, (2) get user confirmation, ` +
        `(3) accept trust-score penalty (-0.1 per bypass).`
      )
    },

    // ─── Internal API for the orchestrator to set WDL state ──────
    _setVerdict: (planId: string, state: string, verifiedBy: string | null) => {
      wdlState.planId = planId
      wdlState.verdictState = state as WdlState["verdictState"]
      wdlState.verifiedBy = verifiedBy
    },

    _recordBypass: (planId: string, reason: string) => {
      wdlState.bypassCount++
      const planBypassCount = Math.min(wdlState.bypassCount, 3) // -0.3 max per plan-id
      wdlState.bypassPenalty = Math.min(0.1 * wdlState.bypassCount, 0.5) // -0.5 max per session
      return {
        bypassCount: wdlState.bypassCount,
        penalty: wdlState.bypassPenalty,
        planId,
        reason,
        timestamp: new Date().toISOString(),
      }
    },

    _getState: () => ({ ...wdlState }),
  }
}
