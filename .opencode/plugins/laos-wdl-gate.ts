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
 *   - Shell calls (except toolchain: git, uv, npx, python)
 *   - Direct implementation work bypassing agents
 *
 * What this plugin allows:
 *   - MCP tool calls (ladesign.*, latade.*, lan8n.*) — agentic use
 *   - Agent dispatch via `task` tool — always allowed
 *   - lacouncil.* structural work (exempt per Hard Rule 8.4)
 *   - File tools (read, glob, grep) for orchestrator
 *   - Research tools (context7, exa)
 *   - GitHub MCP operations
 *   - Toolchain operations (git, uv, npx, python)
 *
 * Shell policy:
 *   - Shell = blocked by default
 *   - Exceptions require justification (see knowledge/kitchen-hierarchy.md)
 *   - Toolchain ops (git, uv, npx, python) = always allowed
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

const AGENTIC_MCP_NAMESPACES = [
  "ladesign_",   // ladesign.* tools → dispatch to dashboard-designer
  "latade_",     // latade.* tools → dispatch to data-architect
  "lan8n_",      // lan8n.* tools → dispatch to automation-engineer
  "laengine_",   // laengine.* tools → dispatch to game agents
  "laecon_",     // laecon.* tools → dispatch to econometrics agents
]

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
      if (AGENTIC_MCP_NAMESPACES.some(ns => input.tool.startsWith(ns))) {
        return // Agentic use — allowed
      }

      // ─── BLOCK: Shell calls (non-agent) ──────────────────────────
      if (input.tool === "bash") {
        const command = output.args?.command || ""
        
        // Allow toolchain operations (infrastructure, not implementation)
        if (command.startsWith("git ") || command.startsWith("uv ") || 
            command.startsWith("npx ") || command.startsWith("python ")) {
          return // Toolchain operations — allowed
        }
        
        // Shell blocked by default
        // See knowledge/kitchen-hierarchy.md for justified shell policy
        throw new Error(
          `[LAOS WDL Gate] BLOCKED: Shell "${command.substring(0, 50)}..." bypasses agent system. ` +
          `Use MCP tools (ladesign.*, latade.*, lan8n.*) or dispatch specialists via ` +
          `the task tool. Non-agent actions are exceptions, not the rule.`
        )
      }

      // ─── ALLOW: Agent dispatch (always allowed) ──────────────────
      if (input.tool === "task") {
        return // Agent dispatch — always allowed
      }

      // ─── ALLOW: File tools (orchestrator infrastructure) ─────────
      if (["read", "glob", "grep", "list", "edit", "write", "write_file", "create_file"].includes(input.tool)) {
        return // File tools — allowed for orchestrator
      }

      // ─── ALLOW: Research tools ───────────────────────────────────
      if (["webfetch", "context7_query_docs", "context7_resolve_library_id", 
           "exa_web_search_exa", "exa_web_fetch_exa"].includes(input.tool)) {
        return // Research tools — allowed
      }

      // ─── ALLOW: GitHub MCP ───────────────────────────────────────
      if (input.tool.startsWith("github_")) {
        return // GitHub MCP — allowed
      }

      // ─── ALLOW: Read-only data tools ─────────────────────────────
      if (input.tool === "latade_inspect_table" || 
          input.tool === "latade_generate_schema_preview" ||
          input.tool === "latade_health") {
        return // Data inspection — allowed
      }

      // Default: allow all other tools
      // WDL gate is permissive for agentic actions, strict for non-agent actions
    },
  }
}