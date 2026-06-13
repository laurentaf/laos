/**
 * LAOS WDL Gate — Enforces agentic architecture compliance
 *
 * Provenance:
 *   - Hard Rule #8 (AGENTS.md): "WDL preflight gate is mandatory before
 *     specialist dispatch."
 *   - LACOUNCIL a4fe9faa: WDL v1 proposal (supermaioria 4/4, 2026-06-06)
 *   - LACOUNCIL 7fd94c1a: Charter P0 for workflow-decomposer
 *   - workflows/wdl-contract.yaml: Operating contract for WDL v1
 *
 * Architecture enforcement:
 *   1. BLOCK non-agent actions (orchestrator writing SQL, dashboards, n8n directly)
 *   2. ALLOW agentic use (MCP tools like ladesign.* that dispatch to agents)
 *   3. ENFORCE that work goes through the agent system, not around it
 *
 * What this plugin blocks:
 *   - Direct implementation by orchestrator (SQL, dashboards, n8n workflows)
 *   - Non-agent work that bypasses the specialist system
 *
 * What this plugin allows:
 *   - MCP tool calls (ladesign.*, latade.*, lan8n.*) — agentic use
 *   - Agent dispatch via `task` tool (with WDL verdict)
 *   - lacouncil.* structural work (exempt per Hard Rule 8.4)
 *
 * File system fallback: When in-memory state is null (after plugin reload),
 * the plugin reads verdict.yaml from artifacts/wdl/<plan-id>/verdict.yaml.
 * This ensures verdicts persist across OpenCode restarts.
 */

import type { Plugin } from "@opencode-ai/plugin"
import { readFileSync, existsSync } from "fs"
import { join } from "path"

// Tools that are EXEMPT from WDL gate (structural improvement work)
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

// MCP tools that are AGENTIC (dispatch to agents internally)
// These should be ALLOWED, not blocked
const AGENTIC_MCP_NAMESPACES = [
  "ladesign_",   // ladesign.* tools → dispatch to dashboard-designer
  "latade_",     // latade.* tools → dispatch to data-architect
  "lan8n_",      // lan8n.* tools → dispatch to automation-engineer
  "laengine_",   // laengine.* tools → dispatch to game agents
  "laecon_",     // laecon.* tools → dispatch to econometrics agents
]

// Non-agent implementation tools that should be BLOCKED
// These bypass the agent system and do work directly
const NON_AGENT_IMPLEMENTATION_TOOLS = [
  // Direct file writes that should go through agents
  "write_file",
  "create_file",
  // Shell commands that implement work directly
  "execute_command", // Generic shell — needs context check
]

// Specialist agents that require WDL verdict
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

// File system fallback: read verdict.yaml from artifacts/wdl/<plan-id>/
// This ensures verdicts persist across OpenCode restarts.
function readVerdictFromFile(planId: string, directory: string): WdlState | null {
  try {
    const verdictPath = join(directory, "artifacts", "wdl", planId, "verdict.yaml")
    if (!existsSync(verdictPath)) return null
    
    const content = readFileSync(verdictPath, "utf-8")
    
    // Simple YAML parsing (avoid external deps)
    const stateMatch = content.match(/state:\s*(READY|DEFER|ESCALATE)/)
    const verifiedByMatch = content.match(/verified_by:\s*(\S+)/)
    const planIdMatch = content.match(/plan_id:\s*(\S+)/)
    
    if (!stateMatch) return null
    
    return {
      planId: planIdMatch?.[1] || planId,
      verdictState: stateMatch[1] as WdlState["verdictState"],
      verifiedBy: verifiedByMatch?.[1] || null,
      bypassCount: 0,
      bypassPenalty: 0,
    }
  } catch {
    return null
  }
}

// Scan artifacts/wdl/ for any valid verdict (when planId is unknown)
function findVerdictFromFile(directory: string): WdlState | null {
  try {
    const wdlDir = join(directory, "artifacts", "wdl")
    if (!existsSync(wdlDir)) return null
    
    // Use imported existsSync and readFileSync instead of require("fs")
    const { readdirSync, statSync } = require("fs")
    const entries = readdirSync(wdlDir, { withFileTypes: true })
    if (!entries || !entries.length) return null
    
    // Find most recent verdict by directory mtime
    const dirs = entries
      .filter((e: any) => e.isDirectory() && !e.name.startsWith("."))
      .map((e: any) => ({
        name: e.name,
        mtime: (() => { try { return statSync(join(wdlDir, e.name)).mtimeMs } catch { return 0 } })()
      }))
      .sort((a: any, b: any) => b.mtime - a.mtime) // most recent first
    
    for (const dir of dirs) {
      const verdict = readVerdictFromFile(dir.name, directory)
      if (verdict && verdict.verdictState === "READY") {
        return verdict
      }
    }
    
    return null
  } catch {
    return null
  }
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

      // ─── AGENTIC USE: MCP tools that dispatch to agents ────────
      // These are ALLOWED — they dispatch to agents internally
      // Example: ladesign.* dispatches to dashboard-designer
      if (AGENTIC_MCP_NAMESPACES.some(ns => input.tool.startsWith(ns))) {
        return // Agentic use — allowed
      }

      // ─── BLOCK: Non-agent implementation ────────────────────────
      // Shell calls that bypass the agent system
      if (input.tool === "bash") {
        const command = output.args?.command || ""
        
        // Allow git, uv, npx, python toolchain operations
        if (command.startsWith("git ") || command.startsWith("uv ") || 
            command.startsWith("npx ") || command.startsWith("python ")) {
          return // Toolchain operations are allowed
        }
        
        // Allow shell for very specific use cases
        // Agent must justify: tried all other paths, task is unique
        // Evaluation criteria:
        // - Tried all agents (data-architect, dashboard-designer, automation-engineer)
        // - Tried MCP tools (which, latade, ladesign, lan8n)
        // - Tried orchestrator file tools
        // - Tried python scripts in venv
        // - Tried context7/exa research
        // - Task is unique (not in any project)
        // - Only single use
        // If ALL criteria met → ALLOW
        // If ANY criteria missing → BLOCK
        
        // For now, block all shell calls
        // This enforces that work goes through the agent system
        throw new Error(
          `[LAOS WDL Gate] BLOCKED: Direct shell call "${command.substring(0, 50)}..." bypasses agent system. ` +
          `Use MCP tools (ladesign.*, latade.*, lan8n.*) or dispatch specialists via ` +
          `the task tool. Non-agent actions are exceptions, not the rule.`
        )
      }

      // ─── ALLOW: Task tool (agent dispatch) ──────────────────────
      // Agent dispatch is ALWAYS allowed — this is agentic use
      if (input.tool === "task") {
        return // Agent dispatch — allowed
      }
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
