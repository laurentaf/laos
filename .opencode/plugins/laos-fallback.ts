/**
 * LAOS Fallback — Runtime Model Fallback on Provider Errors
 *
 * Provenance:
 *   - OmO: runtime-fallback (src/hooks/runtime-fallback/)
 *   - LAOS pain: long sessions with multiple specialist dispatches are
 *     vulnerable to provider errors (429 rate limit, 500 server error).
 *     No recovery — agent just stops.
 *
 * Configuration (per session):
 *   - max_fallback_attempts: 3 (default)
 *   - cooldown_seconds: 30 (default)
 *   - timeout_seconds: 120 (default)
 *   - fallback_models: ordered list of model IDs to try
 *
 * When a provider error is detected (429, 500, timeout), this plugin:
 *   1. Records the error
 *   2. Waits for the cooldown period
 *   3. Retries with the next model in the fallback chain
 *   4. If all models fail, reports the failure to the orchestrator
 *
 * Implementation note: Model switching happens at the provider level.
 * This plugin detects errors and can modify chat.params to switch models,
 * but the actual model selection is done by OpenCode's core routing.
 * The plugin's role is to detect errors and emit events that trigger
 * the fallback mechanism.
 */

import type { Plugin } from "@opencode-ai/plugin"

interface FallbackConfig {
  maxAttempts: number
  cooldownSeconds: number
  timeoutSeconds: number
  fallbackModels: string[]
}

interface FallbackState {
  attemptCount: number
  currentModel: string | null
  lastError: string | null
  lastErrorTime: number
  cooldownUntil: number
}

const DEFAULT_CONFIG: FallbackConfig = {
  maxAttempts: 3,
  cooldownSeconds: 30,
  timeoutSeconds: 120,
  fallbackModels: [], // Populated from opencode.jsonc or project config
}

const fallbackState: FallbackState = {
  attemptCount: 0,
  currentModel: null,
  lastError: null,
  lastErrorTime: 0,
  cooldownUntil: 0,
}

// Provider error patterns
const PROVIDER_ERROR_PATTERNS = [
  /429/i,                    // Rate limit
  /500/i,                    // Server error
  /502/i,                    // Bad gateway
  /503/i,                    // Service unavailable
  /timeout/i,                // Request timeout
  /rate.?limit/i,            // Rate limit (verbose)
  /overloaded/i,             // Provider overloaded
  /capacity/i,               // Capacity exceeded
  /too many requests/i,      // Too many requests
]

function isProviderError(output: string): boolean {
  return PROVIDER_ERROR_PATTERNS.some(pattern => pattern.test(output))
}

export const LaosFallback = async ({ project, client }: {
  project: string
  client: any
}) => {
  return {
    // ─── Detect provider errors in tool output ──────────────────
    "tool.execute.after": async (
      input: { tool: string; sessionID: string; callID: string; args: any },
      output: { title: string; output: string; metadata: any }
    ) => {
      if (!isProviderError(output.output)) return

      // Record the error
      fallbackState.attemptCount++
      fallbackState.lastError = output.output.substring(0, 200)
      fallbackState.lastErrorTime = Date.now()
      fallbackState.cooldownUntil = Date.now() + (DEFAULT_CONFIG.cooldownSeconds * 1000)

      // Tag the output for the orchestrator
      output.metadata = {
        ...output.metadata,
        laos_provider_error: true,
        laos_fallback_attempt: fallbackState.attemptCount,
        laos_fallback_max: DEFAULT_CONFIG.maxAttempts,
        laos_cooldown_until: new Date(fallbackState.cooldownUntil).toISOString(),
      }

      if (fallbackState.attemptCount < DEFAULT_CONFIG.maxAttempts) {
        // Not yet exhausted — signal that retry is possible
        output.output +=
          `\n\n[LAOS Fallback] Provider error detected (attempt ${fallbackState.attemptCount}/${DEFAULT_CONFIG.maxAttempts}). ` +
          `Cooldown: ${DEFAULT_CONFIG.cooldownSeconds}s. ` +
          `The orchestrator should wait and retry, or switch to a fallback model.`
      } else {
        // All attempts exhausted — report failure
        output.output +=
          `\n\n[LAOS Fallback] All ${DEFAULT_CONFIG.maxAttempts} attempts exhausted. ` +
          `Last error: ${fallbackState.lastError}. ` +
          `The orchestrator should abort the current task and report to the user.`
      }
    },

    // ─── Modify chat params on error (switch model) ─────────────
    "chat.params": async (
      input: { sessionID: string; agent: string; model: any; provider: any; message: any },
      output: { temperature: number; topP: number; topK: number; options: Record<string, any> }
    ) => {
      // If we're in cooldown from a provider error, and we have fallback models,
      // signal a model switch via the options.
      if (fallbackState.cooldownUntil > Date.now() && DEFAULT_CONFIG.fallbackModels.length > 0) {
        const nextModelIdx = Math.min(fallbackState.attemptCount - 1, DEFAULT_CONFIG.fallbackModels.length - 1)
        const nextModel = DEFAULT_CONFIG.fallbackModels[nextModelIdx]
        if (nextModel) {
          output.options = {
            ...output.options,
            _laos_fallback_model: nextModel,
            _laos_fallback_reason: "provider_error",
          }
        }
      }
    },

    // ─── Session error event ────────────────────────────────────
    event: async ({ event }: { event: any }) => {
      if (event.type === "session.error") {
        const errorStr = String(event.properties?.error || "")
        if (isProviderError(errorStr)) {
          fallbackState.attemptCount++
          fallbackState.lastError = errorStr.substring(0, 200)
          fallbackState.lastErrorTime = Date.now()
          fallbackState.cooldownUntil = Date.now() + (DEFAULT_CONFIG.cooldownSeconds * 1000)
        }
      }
    },

    // ─── Internal API ───────────────────────────────────────────
    _setConfig: (config: Partial<FallbackConfig>) => {
      Object.assign(DEFAULT_CONFIG, config)
    },

    _getState: () => ({ ...fallbackState }),

    _reset: () => {
      fallbackState.attemptCount = 0
      fallbackState.lastError = null
      fallbackState.lastErrorTime = 0
      fallbackState.cooldownUntil = 0
    },
  }
}
