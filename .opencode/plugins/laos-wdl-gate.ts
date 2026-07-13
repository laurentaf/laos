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

import { readFileSync, existsSync, readdirSync, writeFileSync } from "node:fs"
import { join, resolve } from "node:path"

// ─── Shell usage tracking file (shared with laos-infra.ts) ──
const SHELL_USAGE_PATH = join(resolve("."), ".opencode", "plugins", ".shell-usage.json")

function trackShellCommand(command: string): void {
  try {
    // Normalize: truncate long args, but keep the command type
    const key = command.substring(0, 80)
    let data: { commands: Record<string, number>; total: number; last_promoted: string | null } = { commands: {}, total: 0, last_promoted: null }
    if (existsSync(SHELL_USAGE_PATH)) {
      try { data = JSON.parse(readFileSync(SHELL_USAGE_PATH, { encoding: "utf-8" })) } catch { /* reset on corrupt */ }
    }
    data.commands[key] = (data.commands[key] || 0) + 1
    data.total++
    writeFileSync(SHELL_USAGE_PATH, JSON.stringify(data, null, 2), { encoding: "utf-8" })
  } catch { /* tracking best-effort */ }
}

// ─── laos.infra tools allowlist ─────────────────────────────
const INFRA_TOOLS = [
  "laos-doctor",
  "health_check",
  "add_tool",
  "scaffold_mcp",
  "download_file",
  "validate_agent",
  "git_local",
  "uv_tool",
  "shell_usage_report",
  "explore_filesystem",
]

// ─── Known agent registry (sourced from .opencode/agent/) ────
// WARNING: This hardcoded map must stay in sync with .opencode/agent/*.md
// The runtime fallback in validateDispatchAgent() reads the directory.
// NEVER add agents here that don't have a charter file in .opencode/agent/.
const AGENT_TYPES: Record<string, "primary" | "subagent" | "evaluator"> = {
  orchestrator: "primary",
  "data-architect": "subagent",
  "dashboard-designer": "subagent",
  "automation-engineer": "subagent",
  "delivery-reviewer": "subagent",
  "capability-architect": "subagent",
  "workflow-decomposer": "subagent",
  "chief-data-scientist": "evaluator",
  "chief-designer": "evaluator",
  "chief-engineer": "evaluator",
  explore: "subagent",
  "debug-agent": "subagent",
}

function validateDispatchAgent(agentType: string): { valid: boolean; agent_type?: string; suggested_alternative?: string } {
  const normalized = agentType.toLowerCase().trim()

  // Check hardcoded registry first
  if (normalized in AGENT_TYPES) {
    return { valid: true, agent_type: AGENT_TYPES[normalized] }
  }

  // Check .opencode/agent/ directory (runtime)
  const agentsDir = join(resolve("."), ".opencode", "agent")
  if (existsSync(agentsDir)) {
    try {
      const agentFiles = readdirSync(agentsDir)
      const agentNames = agentFiles
        .filter(e => e.endsWith(".md") || e.endsWith(".ts"))
        .map(e => e.replace(/\.(md|ts)$/, "").toLowerCase())
      if (agentNames.includes(normalized)) {
        return { valid: true, agent_type: "subagent" }
      }
    } catch { /* ignore */ }
  }

  // Fuzzy suggestion
  const allNames = Object.keys(AGENT_TYPES)
  const suggestion = allNames.find(k => k.includes(normalized) || normalized.includes(k))
  return { valid: false, suggested_alternative: suggestion }
}

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

// Read-only command patterns — allowed for debug-agent
// These are safe exploration commands that DO NOT mutate state.
const READONLY_COMMAND_PATTERNS = [
  // PowerShell exploration
  /^Get-ChildItem/i,
  /^Get-Content/i,
  /^Select-String/i,
  /^Test-Path/i,
  /^Get-Command/i,
  /^Get-Item\b/i,
  /^Get-ItemProperty/i,
  /^Get-Location/i,
  /^Get-Process/i,
  /^Get-Service/i,
  /^Get-Date/i,
  /^Write-Output/i,
  /^Write-Host/i,
  // Unix-style (cross-platform)
  /^ls\b/i,
  /^dir\b/i,
  /^cat\b/i,
  /^type\b/i,
  /^findstr/i,
  /^where\b/i,
  /^which\b/i,
  /^echo\b/i,
  /^pwd\b/i,
  /^date\b/i,
  /^whoami/i,
  /^hostname/i,
  // Read-only file info
  /^Get-ItemProperty/i,
  /^stat\b/i,
  // Python version queries (read-only)
  /^python\b/i,
  /^python\s+--version/i,
  // Pipelines ending in read-only (e.g., Get-ChildItem | Select-Object)
  /^\s*(Get-ChildItem|Get-Content|Select-String|ls|dir|cat|type)/i,
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

// ─── Active agent tracking (synced with laos-dispatch.ts) ──
// The laos-dispatch plugin calls _setAgent before dispatching specialists.
// This allows the WDL Gate to apply agent-specific rules.
let currentAgent = "orchestrator" // Default: most permissive

export const WdlGate = async ({ project, directory }: { project: string; directory: string }) => {
  return {
    // Allow the dispatch plugin to set the active agent
    _setAgent: (agentName: string) => {
      currentAgent = agentName
    },

    "tool.execute.before": async (
      input: { tool: string; sessionID: string; callID: string },
      output: { args: any }
    ) => {
      // ─── ALWAYS ALLOW: laos.infra tools ─────────────────────
      if (INFRA_TOOLS.includes(input.tool)) {
        return // laos.infra tools always allowed
      }

      // ─── AGENT DISPATCH: Validate dispatch_type ──────────────
      if (input.tool === "task") {
        const subagentType = output.args?.subagent_type || ""
        if (subagentType) {
          const validation = validateDispatchAgent(subagentType)
          if (!validation.valid) {
            const suggestion = validation.suggested_alternative
              ? ` Did you mean "${validation.suggested_alternative}"?`
              : ""
            throw new Error(
              `[LAOS WDL Gate] BLOCKED: Unknown dispatch_type "${subagentType}".${
                suggestion
              } Agent not found in .opencode/agent/. Use validate_agent to check available agents.`
            )
          }
        }
        return // Agent dispatch — allowed after validation
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

      // ─── DEBUG-AGENT: Allow read-only commands ─────────────────
      // The debug-agent subagent is a special case: it exists ONLY for
      // read-only filesystem exploration during diagnostics/debugging.
      // It is NEVER used in production delivery pipelines. The charter
      // at .opencode/agent/debug-agent.md explicitly restricts it to
      // artifacts/debug/ output and read-only commands.
      if (input.tool === "bash" && currentAgent === "debug-agent") {
        const command = output.args?.command || ""
        const isReadOnly = READONLY_COMMAND_PATTERNS.some(p => p.test(command))
        if (isReadOnly) {
          trackShellCommand(command)
          return // Debug-agent read-only command — allowed
        }
        throw new Error(
          `[LAOS WDL Gate] BLOCKED: debug-agent attempted write command "${command.substring(0, 50)}...". ` +
          `debug-agent is restricted to read-only commands (Get-ChildItem, Get-Content, etc.). ` +
          `See .opencode/agent/debug-agent.md for the allowed command list.`
        )
      }

      // ─── BLOCK / REWRITE: Obviously bad actions ─────────────────
      if (input.tool === "bash") {
        const command = output.args?.command || ""

        // REWRITE git, uv, npx, python commands through pythonw.exe wrapper
        // (CREATE_NO_WINDOW flag) to avoid flashing console windows on Windows.
        // This respects the opencode.jsonc permission.bash allowlist which
        // ONLY allows .venv/Scripts/pythonw.exe entries.
        if (command.startsWith("git ") || command.startsWith("uv ") ||
            command.startsWith("npx ") || command.startsWith("python ")) {
          // Track original command for 80/20 tool promotion
          trackShellCommand(command)
          // Rewrite: prepend the hidden wrapper (pythonw.exe + run-hidden.py)
          output.args.command = `.venv/Scripts/pythonw.exe scripts/run-hidden.py ${command}`
          return // Toolchain operations allowed via hidden wrapper
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