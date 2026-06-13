/**
 * LAOS WDL Gate — Enforces agentic architecture
 *
 * Core principle: Tasks are DONE, not blocked. Orchestrator routes, never asks.
 *
 * What this plugin ALLOWS (always):
 *   - Agent dispatch via `task` tool — always, never blocked
 *   - Specialist work — never blocked
 *   - MCP tools — never blocked
 *   - File tools for orchestrator — never blocked
 *   - Research tools — never blocked
 *   - GitHub MCP — never blocked
 *   - Toolchain (git, uv, npx, python) — never blocked
 *
 * What this plugin BLOCKS:
 *   - Shell calls that bypass the agent system
 *   - Direct implementation by orchestrator (should dispatch instead)
 *
 * What this plugin NEVER does:
 *   - Ask user for guidance
 *   - Block agent dispatch
 *   - Block specialist work
 *   - Create decision paralysis
 *
 * The orchestrator routes tasks. The user is never consulted on HOW.
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
      // ─── ALWAYS ALLOW: Agent dispatch ───────────────────────────
      // Agent dispatch is the primary path. Never block.
      if (input.tool === "task") {
        return // Always allowed
      }

      // ─── ALWAYS ALLOW: Specialist and MCP tools ─────────────────
      // Specialists do their work. Orchestrator routes, never blocks.
      if (AGENTIC_MCP_NAMESPACES.some(ns => input.tool.startsWith(ns))) {
        return // Agentic use — always allowed
      }

      // ─── ALWAYS ALLOW: lacouncil.* structural work ───────────────
      if (WDL_EXEMPT_TOOLS.some(t => input.tool === t || input.tool.startsWith("lacouncil_"))) {
        return // Structural work — always allowed
      }

      // ─── ALWAYS ALLOW: File tools for orchestrator ──────────────
      // Orchestrator needs file tools to operate
      if (["read", "glob", "grep", "list", "edit", "write", "write_file", "create_file"].includes(input.tool)) {
        return // File tools — always allowed
      }

      // ─── ALWAYS ALLOW: Research tools ───────────────────────────
      if (["webfetch", "context7_query_docs", "context7_resolve_library_id", 
           "exa_web_search_exa", "exa_web_fetch_exa"].includes(input.tool)) {
        return // Research tools — always allowed
      }

      // ─── ALWAYS ALLOW: GitHub MCP ────────────────────────────────
      if (input.tool.startsWith("github_")) {
        return // GitHub MCP — always allowed
      }

      // ─── ALWAYS ALLOW: Read-only data tools ──────────────────────
      if (input.tool === "latade_inspect_table" || 
          input.tool === "latade_generate_schema_preview" ||
          input.tool === "latade_health" ||
          input.tool === "latade_list_supported_operations") {
        return // Data inspection — always allowed
      }

      // ─── BLOCK: Shell calls (non-agent work) ─────────────────────
      // Shell bypasses the agent system. Block it.
      if (input.tool === "bash") {
        const command = output.args?.command || ""
        
        // Allow toolchain (infrastructure, not implementation)
        if (command.startsWith("git ") || command.startsWith("uv ") || 
            command.startsWith("npx ") || command.startsWith("python ")) {
          return // Toolchain — always allowed
        }
        
        // Shell blocked — route through agent instead
        // NEVER ask user for guidance
        throw new Error(
          `[LAOS WDL Gate] Shell "${command.substring(0, 30)}..." blocked. ` +
          `Use MCP tools (ladesign.*, latade.*, lan8n.*) or dispatch specialists via ` +
          `the task tool. Orchestrator routes — user is never asked.`
        )
      }

      // ─── Default: ALLOW ──────────────────────────────────────────
      // WDL gate is permissive. Tasks are done, not blocked.
      return
    },
  }
}