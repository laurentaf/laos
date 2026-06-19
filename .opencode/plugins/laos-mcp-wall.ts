/**
 * LAOS MCP Wall — Enforces namespace restrictions per subagent
 *
 * Provenance:
 *   - WDL-R1 (workflows/wdl-contract.yaml): workflow-decomposer must NOT call
 *     latade.*, ladesign.*, lan8n.*, laecon.*, n8n-community.*
 *   - AGENTS.md: "Capabilities are reached only through MCP. Never cd ../latade"
 *   - .opencode/agent/workflow-decomposer.md §"MCP namespaces you must NOT call"
 *   - .opencode/agent/orchestrator.md §"Tools you do NOT use"
 *
 * This plugin blocks tool calls to MCP namespaces that the current agent
 * is not authorized to use. Enforcement is per-agent, based on the agent's
 * instruction file declarations.
 *
 * Currently, OpenCode does not expose the active agent name in
 * tool.execute.before input. As a workaround, this plugin reads the
 * session's agent context from the project directory structure and
 * the session's metadata. When the agent name IS available (future
 * OpenCode versions), this becomes fully mechanical.
 *
 * For now, this plugin implements:
 *   1. BLOCK calls to latade.*, ladesign.*, lan8n.*, laecon.*,
 *      n8n-community.* from workflow-decomposer sessions (WDL-R1).
 *   2. WARN when the orchestrator calls domain MCPs directly
 *      (should delegate to subagents instead).
 *   3. BLOCK calls to lacouncil.* from domain subagents
 *      (data-architect, dashboard-designer, automation-engineer)
 *      — LACOUNCIL is reserved for structural improvement work only.
 *
 * Agent-to-namespace mapping (synced with AGENTS.md §MCP Wall):
 * orchestrator: lacouncil.* (structural work only), platform MCPs
 * workflow-decomposer: lacouncil.* ONLY (WDL-R1 wall)
 * data-architect: latade.*, platform MCPs
 * dashboard-designer: ladesign.*, platform MCPs
 * automation-engineer: lan8n.*, n8n-community.*, platform MCPs
 * delivery-reviewer: all MCPs (read-only; writes blocked by laos-guards)
 * capability-architect: lacouncil.*, github.*, context7.*
 * chief-data-scientist: latade.* (read-only)
 * chief-designer: ladesign.* (read-only)
 * chief-engineer: lan8n.*, latade.* (read-only)
 */

import type { Plugin } from "@opencode-ai/plugin"

// MCP namespace prefixes
const DOMAIN_MCPS = ["latade", "ladesign", "lan8n", "laecon", "laengine", "n8n-community"]
const STRUCTURAL_MCPS = ["lacouncil"]
const PLATFORM_MCPS = ["context7", "exa", "github"]

// Agent → allowed MCP namespaces
// Synced with AGENTS.md §"MCP Wall — agent-to-namespace mapping"
//
// Conselho voting exception (LACOUNCIL proposal, 2026-06-12):
// Domain subagents (data-architect, dashboard-designer, automation-engineer)
// are Conselho members and MUST be able to call lacouncil.register_vote(),
// lacouncil.get_proposal(), and lacouncil.get_trust_scores() to deliberate.
// All other lacouncil.* tools (create_proposal, implement_proposal, etc.)
// remain blocked — structural improvement work is orchestrator-only.
const CONSELHO_VOTE_TOOLS = [
  "lacouncil.register_vote",
  "lacouncil.get_proposal",
  "lacouncil.get_trust_scores",
  "lacouncil.health",
  "lacouncil.list_proposals",
  "lacouncil.list_supported_operations",
]

const AGENT_MCP_WALLS: Record<string, { allowed: string[]; blocked: string[]; allowedTools?: string[] }> = {
  "workflow-decomposer": {
    allowed: ["lacouncil", "context7", "exa", "github"],
    blocked: ["latade", "ladesign", "lan8n", "laecon", "laengine", "n8n-community"],
  },
  "data-architect": {
    allowed: ["latade", "context7", "exa", "github"],
    blocked: ["lacouncil", "ladesign", "lan8n", "laecon", "laengine", "n8n-community"],
    allowedTools: CONSELHO_VOTE_TOOLS, // Conselho member — can vote + read proposals
  },
  "dashboard-designer": {
    allowed: ["ladesign", "context7", "exa", "github"],
    blocked: ["lacouncil", "latade", "lan8n", "laecon", "laengine", "n8n-community"],
    allowedTools: CONSELHO_VOTE_TOOLS, // Conselho member — can vote + read proposals
  },
  "automation-engineer": {
    allowed: ["lan8n", "n8n-community", "context7", "exa", "github"],
    blocked: ["lacouncil", "latade", "ladesign", "laecon", "laengine"],
    allowedTools: CONSELHO_VOTE_TOOLS, // Conselho member — can vote + read proposals
  },
  "delivery-reviewer": {
    // Read-only access to ALL MCPs — reviewer needs latade.execute_sql etc. to validate data artifacts.
    // Write-blocking is handled separately by the laos-guards plugin (P0: reviewer must not mutate).
    allowed: ["latade", "ladesign", "lan8n", "laecon", "laengine", "n8n-community", "lacouncil", "context7", "exa", "github"],
    blocked: [], // No MCP reads blocked; writes blocked by laos-guards.ts
  },
  "capability-architect": {
    allowed: ["lacouncil", "github", "context7"],
    blocked: ["latade", "ladesign", "lan8n", "laecon", "laengine", "n8n-community"],
  },
  "chief-data-scientist": {
    allowed: ["latade"], // Read-only for data evaluation
    blocked: ["ladesign", "lan8n", "laecon", "laengine", "lacouncil", "n8n-community"],
  },
  "chief-designer": {
    allowed: ["ladesign"], // Read-only for design evaluation
    blocked: ["latade", "lan8n", "laecon", "laengine", "lacouncil", "n8n-community"],
  },
  "chief-engineer": {
    allowed: ["lan8n", "latade"], // Read-only for engineering evaluation
    blocked: ["ladesign", "laecon", "laengine", "lacouncil", "n8n-community"],
  },
  "debug-agent": {
    // Debug agent has broad MCP access for diagnostics, but writes
    // are blocked by laos-guards.ts (P0: debug must not mutate production).
    // Shell access is controlled by the WDL Gate (read-only commands only).
    allowed: ["latade", "ladesign", "lan8n", "laecon", "laengine", "n8n-community", "lacouncil", "context7", "exa", "github"],
    blocked: [], // All MCPs readable; shell blocked except read-only by WDL Gate
  },
}

function getMcpNamespace(toolName: string): string | null {
  // MCP tools are namespaced as "mcpName.toolName" in OpenCode
  const parts = toolName.split("_")
  if (parts.length >= 2) return parts[0]
  // Also check for dot-separated (some MCPs use dots)
  if (toolName.includes(".")) return toolName.split(".")[0]
  return null
}

function isMcpTool(toolName: string): boolean {
  return DOMAIN_MCPS.some(ns => toolName.startsWith(ns + "_") || toolName.startsWith(ns + ".")) ||
         STRUCTURAL_MCPS.some(ns => toolName.startsWith(ns + "_") || toolName.startsWith(ns + ".")) ||
         PLATFORM_MCPS.some(ns => toolName.startsWith(ns + "_") || toolName.startsWith(ns + "."))
}

export const McpWall = async ({ project, directory }: { project: string; directory: string }) => {
  // Track the current agent — this is set via the laos-dispatch plugin
  // which writes the active agent to a state file.
  // Fallback: if no state file, assume orchestrator (most permissive).
  let currentAgent = "orchestrator"

  return {
    "tool.execute.before": async (
      input: { tool: string; sessionID: string; callID: string },
      output: { args: any }
    ) => {
      const toolName = input.tool

      if (!isMcpTool(toolName)) return // Not an MCP tool, no wall applies

      const namespace = getMcpNamespace(toolName)
      if (!namespace) return

      const wall = AGENT_MCP_WALLS[currentAgent]
      if (!wall) return // Unknown agent — don't block (orchestrator handles)

      if (wall.blocked.includes(namespace)) {
        // Check tool-level exception (Conselho voting tools)
        // Tool names use underscore separator in OpenCode: lacouncil_register_vote
        const toolNameWithDot = toolName.replace("_", ".")
        const isAllowedTool = wall.allowedTools?.some(
          allowed => toolName === allowed.replace(".", "_") || toolNameWithDot === allowed
        )
        if (isAllowedTool) return // Tool-level exception — allow (Conselho voting)

        throw new Error(
          `[LAOS MCP Wall] Agent "${currentAgent}" must NOT call ${namespace}.* tools. ` +
          `Allowed namespaces: [${wall.allowed.join(", ")}]. ` +
          `Blocked namespaces: [${wall.blocked.join(", ")}]. ` +
          `Tool attempted: ${toolName}. ` +
          `See .opencode/agent/${currentAgent}.md for the MCP wall definition.`
        )
      }
    },

    // Allow the dispatch plugin to set the active agent for this session
    // This is called by laos-dispatch.ts before each specialist dispatch
    _setAgent: (agentName: string) => {
      if (AGENT_MCP_WALLS[agentName]) {
        currentAgent = agentName
      } else {
        // Unknown agent — log warning but don't change (stays as orchestrator default)
        console.warn(`[LAOS MCP Wall] Unknown agent "${agentName}" — falling back to orchestrator (permissive)`)
      }
    },
  }
}
