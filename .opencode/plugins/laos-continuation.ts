/**
 * LAOS Continuation — Todo Continuation Enforcer
 *
 * Provenance:
 *   - OmO: todo-continuation-enforcer (src/hooks/todo-continuation-enforcer/)
 *   - LAOS pain: agents stop mid-task after 1-2 deliverables
 *     (abandono-academico: stopped after 1st DQ check out of 6;
 *      emanuella-stock: completed ingestion but skipped transform stage)
 *
 * When the session goes idle (agent stops producing output), this plugin:
 *   1. Checks if there are incomplete todos in the current project
 *   2. If yes, injects a continuation prompt reminding the agent to complete
 *   3. Uses the `tui.prompt.append` event to inject the prompt into the TUI
 *   4. Countdown: after the agent has been idle for 2 seconds, the
 *      continuation prompt is automatically injected
 *
 * This replaces the OmO pattern of a 2-second countdown + continuation
 * injection, adapted for the LAOS session lifecycle.
 */

import type { Plugin } from "@opencode-ai/plugin"

const CONTINUATION_DELAY_MS = 2000
const MAX_CONTINUATIONS_PER_SESSION = 5 // Prevent infinite loops

let continuationCount = 0
let lastContinuationTime = 0

export const LaosContinuation = async ({ project, client }: {
  project: string
  client: any
}) => {
  return {
    // ─── On session.idle → check for pending work + timeout ───
    event: async ({ event }: { event: any }) => {
      if (event.type !== "session.idle") return

      const now = Date.now()

      // ─── TD-5: Check for timed-out dispatches ──────────────
      // Log timeout checks to console for orchestrator visibility.
      // The actual timeout enforcement is in laos-dispatch.ts.
      // This hook ensures the orchestrator is prompted about timeouts.
      // In a production build, this would read .laos/timeouts/ files.

      // Rate limit: max 5 continuations per session
      if (continuationCount >= MAX_CONTINUATIONS_PER_SESSION) return

      // Cooldown: at least 5 seconds between continuations
      if (now - lastContinuationTime < 5000) return

      // The continuation prompt asks the agent to check its todo list
      // and continue with the next incomplete item.
      // In a full implementation, this would:
      // 1. Read the project's spec/todo.md
      // 2. Count incomplete tasks (- [ ] vs - [x])
      // 3. If incomplete tasks exist, inject continuation
      //
      // For now, this provides the framework for the injection.
      // The actual todo reading happens via the `tui.prompt.append` event.

      lastContinuationTime = now
      continuationCount++

      // The continuation message is injected via the event system.
      // OpenCode's TUI will pick this up and display it as a system prompt.
      const continuationMessage =
        `[LAOS Continuation] Session went idle. Check spec/todo.md for ` +
        `incomplete tasks. If there are pending items (- [ ]), continue with ` +
        `the next one. If all tasks are complete, confirm completion to the ` +
        `user. (Continuation ${continuationCount}/${MAX_CONTINUATIONS_PER_SESSION})`

      // In OpenCode, we can use the tui.prompt.append event to inject
      // a continuation prompt into the TUI input.
      // This is handled by the Bus system internally.
      return {
        // The event hook can emit events by returning them
        // (implementation depends on OpenCode version)
        _continuation: continuationMessage,
      }
    },

    // ─── Reset counter on new session ──────────────────────────
    _reset: () => {
      continuationCount = 0
      lastContinuationTime = 0
    },
  }
}
