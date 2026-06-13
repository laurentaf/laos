/**
 * LAOS WDL Gate — Confidence path for agents
 *
 * Core principle: Agents do their tasks with confidence.
 * Orchestrator trusts specialists. User is rarely consulted.
 *
 * WDL gate philosophy:
 *   - Routine actions → just do (built confidence from repetition)
 *   - Cleanup actions → just do (obviously safe)
 *   - Obviously bad actions → block (idiot check)
 *   - Uncertain actions → could ask OR route to specialist
 *   - Never create decision paralysis
 *
 * Confidence levels:
 *   - 0-2 uses: check if obviously bad, otherwise allow
 *   - 3-5 uses: allow (routine behavior)
 *   - 5+ uses: allow without question (established pattern)
 *   - New type of task: route to specialist
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
  "ladesign_",
  "latade_",
  "lan8n_",
  "laengine_",
  "laecon_",
]

// Obviously bad actions — block without question
const BLOCKED_PATTERNS = [
  // Windows system folders
  /windows[\/\\]system/i,
  /c:\\windows/i,
  /program files/i,
  // Dangerous operations
  /rm\s+-rf\s+\//,  // rm -rf /
  /del\s+\/s\s+\//, // del /s / on windows
  // Production databases without backup
  /drop\s+database/i,
  /drop\s+table/i,
]

// Cleanup patterns — obviously safe, just do
const CLEANUP_PATTERNS = [
  // Temporary files
  /\.pyc$/,
  /__pycache__/,
  /\.tmp$/,
  /\.log$/,
  /node_modules\/\.cache/,
  /\.venv\/lib/,
  // Build artifacts
  /dist\//,
  /build\//,
  /\.egg-info\//,
]

// Routine patterns — just do, don't ask
const ROUTINE_PATTERNS = [
  // Git operations (routine for any developer)
  /^git\s+(add|commit|push|pull|status|log|diff)/i,
  // File operations in project
  /^git\s+/i,
  /^uv\s+(sync|run|pip)/i,
  /^npx\s+/i,
]

export const WdlGate = async ({ project, directory }: { project: string; directory: string }) => {
  return {
    "tool.execute.before": async (
      input: { tool: string; sessionID: string; callID: string },
      output: { args: any }
    ) => {
      // ─── ALWAYS ALLOW: Agent dispatch ───────────────────────────
      if (input.tool === "task") {
        return // Always allowed
      }

      // ─── ALWAYS ALLOW: Specialist and MCP tools ─────────────────
      if (AGENTIC_MCP_NAMESPACES.some(ns => input.tool.startsWith(ns))) {
        return // Agentic use — always allowed
      }

      // ─── ALWAYS ALLOW: Structural work ──────────────────────────
      if (WDL_EXEMPT_TOOLS.some(t => input.tool === t || input.tool.startsWith("lacouncil_"))) {
        return // Structural work — always allowed
      }

      // ─── ALWAYS ALLOW: File tools for orchestrator ─────────────
      if (["read", "glob", "grep", "list", "edit", "write", "write_file", "create_file"].includes(input.tool)) {
        return // File tools — always allowed
      }

      // ─── ALWAYS ALLOW: Research tools ───────────────────────────
      if (["webfetch", "context7_query_docs", "context7_resolve_library_id", 
           "exa_web_search_exa", "exa_web_fetch_exa"].includes(input.tool)) {
        return // Research tools — always allowed
      }

      // ─── ALWAYS ALLOW: GitHub MCP ───────────────────────────────
      if (input.tool.startsWith("github_")) {
        return // GitHub MCP — always allowed
      }

      // ─── ALWAYS ALLOW: Read-only data tools ─────────────────────
      if (input.tool === "latade_inspect_table" || 
          input.tool === "latade_generate_schema_preview" ||
          input.tool === "latade_health" ||
          input.tool === "latade_list_supported_operations") {
        return // Data inspection — always allowed
      }

      // ─── BLOCK: Obviously bad actions ───────────────────────────
      if (input.tool === "bash") {
        const command = output.args?.command || ""
        
// ─── BLOCK: Shell by default ──────────────────────────────
      if (input.tool === "bash") {
        const command = output.args?.command || ""
        
        // Allow git, uv, npx, python toolchain operations
        if (command.startsWith("git ") || command.startsWith("uv ") || 
            command.startsWith("npx ") || command.startsWith("python ")) {
          return // Toolchain operations are allowed
        }
        
        // Block shell — must route through specialist or MCP
        throw new Error(
          `[LAOS WDL Gate] BLOCKED: Direct shell call "${command.substring(0, 50)}..." bypasses agent system. ` +
          `Use MCP tools (ladesign.*, latade.*, lan8n.*) or dispatch specialists via ` +
          `the task tool. Non-agent actions are exceptions, not the rule.`
        )
      }

      // ─── Default: ALLOW ──────────────────────────────────────────
      return
    },
  }
}