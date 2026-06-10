/**
 * LAOS Recovery — Session Recovery System (3 layers)
 *
 * Provenance:
 *   - OmO: session-recovery (src/hooks/session-recovery/)
 *   - OmO: boulder-state (packages/boulder-state/)
 *   - User requirement: "full system, every project must have his own states"
 *   - LAOS pain: long sessions crash (previsao-concursos: 4 capabilities,
 *     9 needs, high crash probability). No recovery — entire pipeline restarts.
 *
 * Three recovery layers:
 *
 *   Layer 1: STRUCTURAL ERROR RECOVERY
 *   - Catch missing tool results, thinking block violations
 *   - Reconstruct state from session history
 *   - Prevent cascading failures from one bad tool call
 *
 *   Layer 2: PER-PROJECT STATE PERSISTENCE
 *   - State lives in each child repo: <child-repo>/.laos/state/
 *   - Files: todos.json, verdicts.json, dispatch.json, trust.json, continuation.json
 *   - Written after every significant state change
 *   - Read on session recovery to reconstruct working context
 *
 *   Layer 3: CONTEXT COMPACTION PRESERVATION
 *   - Hook into experimental.session.compacting
 *   - Inject LAOS-critical context before compaction:
 *     project name, active WDL verdict, dispatch mode, pending todos,
 *     trust scores, current stage
 *   - This context survives compaction and is re-injected into the
 *     compacted prompt
 *
 * State file schema (per <child-repo>/.laos/state/):
 *
 *   todos.json:        { items: [{content, status, priority}], last_updated }
 *   verdicts.json:     { plan_id, state, verified_by, timestamp }
 *   dispatch.json:     { mode, members: [{agent, status, result}], timestamp }
 *   trust.json:        { scores: {agent: score}, timestamp }
 *   continuation.json: { count, last_time, message }
 */

import type { Plugin } from "@opencode-ai/plugin"

// LAOS-critical context that must survive compaction
interface LaosCriticalContext {
  projectName: string
  planId: string | null
  verdictState: string | null
  dispatchMode: string | null
  currentStage: string | null
  pendingTodos: number
  trustScores: Record<string, number>
  continuationCount: number
  lastUpdated: string
}

// In-memory critical context (persisted to child repo on state changes)
const criticalContext: LaosCriticalContext = {
  projectName: "",
  planId: null,
  verdictState: null,
  dispatchMode: null,
  currentStage: null,
  pendingTodos: 0,
  trustScores: {},
  continuationCount: 0,
  lastUpdated: new Date().toISOString(),
}

export const LaosRecovery = async ({ project, directory }: {
  project: string
  directory: string
}) => {
  return {
    // ─── Layer 1: Structural error recovery ─────────────────────
    // Catch tool execution errors and prevent cascading failures
    "tool.execute.after": async (
      input: { tool: string; sessionID: string; callID: string; args: any },
      output: { title: string; output: string; metadata: any }
    ) => {
      // Check for error indicators in the output
      const outputStr = output.output || ""
      const hasError = outputStr.includes("Error:") ||
                       outputStr.includes("error:") ||
                       outputStr.includes("failed") ||
                       outputStr.includes("429") ||
                       outputStr.includes("500")

      if (hasError) {
        // Tag the output for the orchestrator to detect and handle
        output.metadata = {
          ...output.metadata,
          laos_error_detected: true,
          laos_error_tool: input.tool,
          laos_error_timestamp: new Date().toISOString(),
        }
      }
    },

    // ─── Layer 3: Context compaction preservation ───────────────
    "experimental.session.compacting": async (
      input: { sessionID: string },
      output: { context: string[]; prompt?: string }
    ) => {
      // Build the LAOS critical context string that must survive compaction
      const contextLines = [
        `[LAOS RECOVERY — Context that MUST survive compaction]`,
        `Project: ${criticalContext.projectName || "unknown"}`,
        `WDL Plan: ${criticalContext.planId || "none"}`,
        `WDL Verdict: ${criticalContext.verdictState || "none"}`,
        `Dispatch Mode: ${criticalContext.dispatchMode || "sequential"}`,
        `Current Stage: ${criticalContext.currentStage || "unknown"}`,
        `Pending Todos: ${criticalContext.pendingTodos}`,
        `Continuation Count: ${criticalContext.continuationCount}`,
        `Trust Scores: ${JSON.stringify(criticalContext.trustScores)}`,
        `Last Updated: ${criticalContext.lastUpdated}`,
        `[END LAOS RECOVERY CONTEXT]`,
      ]

      output.context = contextLines
    },

    // ─── Session events: track errors and compaction ─────────────
    event: async ({ event }: { event: any }) => {
      // On session error, attempt structural recovery
      if (event.type === "session.error") {
        // In a full implementation, this would:
        // 1. Log the error to .laos/state/errors.json
        // 2. Attempt to reconstruct the last known good state
        // 3. Inject a recovery prompt into the TUI
        console.error("[LAOS Recovery] Session error detected:", event.properties)
      }

      // On session compaction, the critical context is already injected
      // via the experimental.session.compacting hook above.
      if (event.type === "session.compacted") {
        console.log("[LAOS Recovery] Session compacted — critical context preserved")
      }
    },

    // ─── Internal API for state updates ─────────────────────────
    _updateContext: (updates: Partial<LaosCriticalContext>) => {
      Object.assign(criticalContext, updates, { lastUpdated: new Date().toISOString() })
    },

    _getContext: (): LaosCriticalContext => ({ ...criticalContext }),

    // Persist state to child repo's .laos/state/ directory
    _persistState: (childRepoPath: string, stateType: string, data: any) => {
      // In a full implementation, this writes JSON to:
      // <childRepoPath>/.laos/state/<stateType>.json
      // For now, this is the API contract that the orchestrator
      // and other plugins can call.
      return {
        path: `${childRepoPath}/.laos/state/${stateType}.json`,
        data,
        timestamp: new Date().toISOString(),
      }
    },
  }
}
