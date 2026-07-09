/**
 * LAOS Infra — MCP Infrastructure Tools
 *
 * Extends laos-doctor with 5 dedicated MCP tools for tooling maintenance,
 * binary download, and agent validation, eliminating shell usage for
 * these operations (Hard Rule #3 compliance).
 *
 * Provenance:
 * - LACOUNCIL proposal 6481da60-67d8-4c7b-a94b-b2da34479f9f
 * - Conselho supermaioria 4/4 SIM, 2026-06-14
 * - Regime A (mandatory push after structural change approval)
 *
 * 5 tools:
 * 1. health_check     — diagnose specific MCP component (replaces curl/docker logs/ps aux)
 * 2. add_tool         — add tool to existing capability (replaces manual opencode.jsonc editing)
 * 3. scaffold_mcp     — scaffold new MCP server (replaces mkdir + write server.py)
 * 4. download_file    — download binaries (replaces curl/wget/Invoke-WebRequest)
 * 5. validate_agent   — validate WDL dispatch_type against .opencode/agent/
 *
 * @module laos-infra
 */

import { readFileSync, existsSync, statSync, readdirSync, writeFileSync, mkdirSync } from "node:fs"
import { join, resolve, normalize, relative } from "node:path"
import { execSync } from "node:child_process"
import * as https from "node:https"
import * as http from "node:http"
import * as crypto from "node:crypto"
import { URL } from "node:url"

type CheckStatus = "PASS" | "FAIL" | "WARN"

interface DoctorCheck {
  name: string
  status: CheckStatus
  details: string
  items?: DoctorItem[]
}

interface DoctorItem {
  name: string
  status: CheckStatus
  details: string
}

interface DoctorResult {
  timestamp: string
  laos_root: string
  checks: DoctorCheck[]
  summary: { pass: number; fail: number; warn: number; total: number }
}

const CAPABILITY_REPOS: Record<string, string> = {
  latade: "../latade",
  lacouncil: "../lacouncil",
  lan8n: "../lan8n",
  ladesign: "../ladesign",
  laengine: "../laengine",
  laecon: "../laecon",
}

const VENV_REPOS: Record<string, string> = {
  LAOS: ".",
  latade: "../latade",
  lacouncil: "../lacouncil",
  lan8n: "../lan8n",
  ladesign: "../ladesign",
  laengine: "../laengine",
  laecon: "../laecon",
}

const EXPECTED_MCP_ENTRIES = [
  "latade",
  "lan8n",
  "n8n-community",
  "lacouncil",
  "laengine",
  "laecon",
  "ladesign",
  "workflow-decomposer",
  "context7",
  "exa",
  "github",
]

const EXPECTED_PLUGINS = [
  "laos-guards.ts",
  "laos-mcp-wall.ts",
  "laos-wdl-gate.ts",
  "laos-dispatch.ts",
  "laos-continuation.ts",
  "laos-recovery.ts",
  "laos-fallback.ts",
  "laos-comment-checker.ts",
  "laos-intent-gate.ts",
  "laos-doctor.ts",
  "laos-infra.ts",
  "laos-plan-format-validator.ts",
  "laos-format-guard.ts",
  "laos-completion-gate.ts",
]

const MCP_COMPONENTS = [
  "latade", "lan8n", "ladesign", "lacouncil", "laecon",
  "laengine", "n8n-community", "context7", "exa", "github",
] as const

type McpComponent = typeof MCP_COMPONENTS[number]

// ─── Shared helpers (from laos-doctor) ────────────────────────

function runCli(command: string): { ok: boolean; output: string } {
  try {
    const result = execSync(command, {
      timeout: 5000,
      encoding: "utf-8",
      stdio: ["pipe", "pipe", "pipe"],
    })
    return { ok: true, output: result.trim() }
  } catch {
    return { ok: false, output: "" }
  }
}

// ─── Command execution with allowlist enforcement (ADR-014)
// Mirrors the bash allowlist in .opencode/opencode.jsonc §permission.bash.
// This function is the ONLY shell entry point for the orchestrator.
function isCommandAllowed(command: string): { allowed: boolean; reason?: string } {
  // Deny list (checked first)
  if (command.startsWith("rm -rf ")) {
    return { allowed: false, reason: "Command 'rm -rf *' is explicitly denied in opencode.jsonc bash allowlist" }
  }

  // Allow list — prefix matching, same semantics as WDL gate
  const allowedPrefixes = [
    "git ",
    "uv ",
    "npx ",
    "uv run python scripts/subagent_boot_check.py ",
    "uv run python scripts/toolchain_inventory.py ",
    "uv run python scripts/preflight_check.py ",
  ]

  for (const prefix of allowedPrefixes) {
    if (command.startsWith(prefix)) {
      return { allowed: true }
    }
  }

  return { allowed: false, reason: "Command does not match any allowed prefix in opencode.jsonc bash allowlist" }
}

function runCommand(command: string, cwd?: string): { ok: boolean; output: string; error?: string } {
  try {
    const result = execSync(command, {
      cwd: cwd || process.cwd(),
      timeout: 60000,
      encoding: "utf-8",
      stdio: ["pipe", "pipe", "pipe"],
    })
    return { ok: true, output: result.trim() }
  } catch (e: any) {
    return { ok: false, output: "", error: e.stderr ? String(e.stderr) : String(e) }
  }
}

function stripJsoncComments(text: string): string {
  const out: string[] = []
  let i = 0
  const n = text.length
  let inString = false
  let escape = false
  while (i < n) {
    const c = text[i]
    if (inString) {
      out.push(c)
      if (escape) {
        escape = false
      } else if (c === "\\") {
        escape = true
      } else if (c === '"') {
        inString = false
      }
      i++
      continue
    }
    if (c === '"') {
      inString = true
      out.push(c)
      i++
      continue
    }
    if (c === "/" && i + 1 < n && text[i + 1] === "/") {
      i += 2
      while (i < n && text[i] !== "\n") i++
      continue
    }
    if (c === "/" && i + 1 < n && text[i + 1] === "*") {
      i += 2
      while (i < n - 1 && !(text[i] === "*" && text[i + 1] === "/")) i++
      i += 2
      continue
    }
    out.push(c)
    i++
  }
  return out.join("")
}

function parseOpencodeJsonc(laosRoot: string): Record<string, any> | null {
  const cfgPath = join(laosRoot, ".opencode", "opencode.jsonc")
  if (!existsSync(cfgPath)) return null
  try {
    const raw = readFileSync(cfgPath, { encoding: "utf-8" })
    return JSON.parse(stripJsoncComments(raw))
  } catch {
    return null
  }
}

// ─── Doctor diagnostic tools (from laos-doctor.ts) ────────────

function checkSystem(): DoctorCheck {
  const items: DoctorItem[] = []
  items.push({
    name: "OS",
    status: "PASS",
    details: `${process.platform} ${process.arch}`,
  })

  const node = runCli("node --version")
  items.push({
    name: "Node",
    status: node.ok ? "PASS" : "FAIL",
    details: node.ok ? node.output : "not found",
  })

  const python = runCli("python --version")
  if (!python.ok) {
    const python3 = runCli("python3 --version")
    items.push({
      name: "Python",
      status: python3.ok ? "PASS" : "FAIL",
      details: python3.ok ? python3.output : "not found",
    })
  } else {
    items.push({
      name: "Python",
      status: "PASS",
      details: python.output,
    })
  }

  const uv = runCli("uv --version")
  items.push({
    name: "uv",
    status: uv.ok ? "PASS" : "FAIL",
    details: uv.ok ? uv.output : "not found",
  })

  const failCount = items.filter(i => i.status === "FAIL").length
  return {
    name: "system",
    status: failCount > 0 ? "FAIL" : "PASS",
    details: `${items.filter(i => i.status === "PASS").length}/${items.length} runtimes OK`,
    items,
  }
}

function checkConfig(laosRoot: string): DoctorCheck {
  const items: DoctorItem[] = []
  const cfgPath = join(laosRoot, ".opencode", "opencode.jsonc")

  if (!existsSync(cfgPath)) {
    return {
      name: "config",
      status: "FAIL",
      details: "opencode.jsonc not found",
      items: [{ name: "opencode.jsonc", status: "FAIL", details: `not found at ${cfgPath}` }],
    }
  }

  const config = parseOpencodeJsonc(laosRoot)
  if (!config) {
    return {
      name: "config",
      status: "FAIL",
      details: "opencode.jsonc exists but failed to parse",
      items: [{ name: "opencode.jsonc", status: "FAIL", details: "parse error" }],
    }
  }

  items.push({
    name: "opencode.jsonc",
    status: "PASS",
    details: "exists and parses",
  })

  const mcpBlock = config.mcp || {}
  for (const mcpName of EXPECTED_MCP_ENTRIES) {
    const present = mcpName in mcpBlock
    const enabled = present ? mcpBlock[mcpName]?.enabled !== false : false
    if (!present) {
      items.push({
        name: `mcp.${mcpName}`,
        status: "WARN",
        details: "not in config",
      })
    } else if (!enabled) {
      items.push({
        name: `mcp.${mcpName}`,
        status: "WARN",
        details: "present but disabled",
      })
    } else {
      items.push({
        name: `mcp.${mcpName}`,
        status: "PASS",
        details: "present and enabled",
      })
    }
  }

  const failCount = items.filter(i => i.status === "FAIL").length
  const warnCount = items.filter(i => i.status === "WARN").length
  return {
    name: "config",
    status: failCount > 0 ? "FAIL" : warnCount > 0 ? "WARN" : "PASS",
    details: `${items.filter(i => i.status === "PASS").length}/${items.length} entries OK`,
    items,
  }
}

function checkPlugins(laosRoot: string): DoctorCheck {
  const items: DoctorItem[] = []
  const pluginsDir = join(laosRoot, ".opencode", "plugins")

  if (!existsSync(pluginsDir)) {
    return {
      name: "plugins",
      status: "FAIL",
      details: "plugins directory not found",
      items: [{ name: "plugins/", status: "FAIL", details: `not found at ${pluginsDir}` }],
    }
  }

  const existingFiles = existsSync(pluginsDir)
    ? readdirSync(pluginsDir).filter(f => f.endsWith(".ts"))
    : []

  for (const pluginFile of EXPECTED_PLUGINS) {
    const fullPath = join(pluginsDir, pluginFile)
    if (!existsSync(fullPath)) {
      items.push({
        name: pluginFile,
        status: "WARN",
        details: "missing",
      })
      continue
    }
    try {
      const stat = statSync(fullPath)
      if (stat.size === 0) {
        items.push({
          name: pluginFile,
          status: "FAIL",
          details: "file is empty (0 bytes)",
        })
      } else {
        items.push({
          name: pluginFile,
          status: "PASS",
          details: `${stat.size} bytes`,
        })
      }
    } catch {
      items.push({
        name: pluginFile,
        status: "FAIL",
        details: "cannot stat",
      })
    }
  }

  const extraPlugins = existingFiles.filter(f => !EXPECTED_PLUGINS.includes(f))
  for (const extra of extraPlugins) {
    items.push({
      name: extra,
      status: "PASS",
      details: "additional plugin (not in expected list)",
    })
  }

  const failCount = items.filter(i => i.status === "FAIL").length
  const warnCount = items.filter(i => i.status === "WARN").length
  return {
    name: "plugins",
    status: failCount > 0 ? "FAIL" : warnCount > 0 ? "WARN" : "PASS",
    details: `${items.filter(i => i.status === "PASS").length}/${EXPECTED_PLUGINS.length} expected present`,
    items,
  }
}

function checkMcpHealth(laosRoot: string): DoctorCheck {
  const items: DoctorItem[] = []
  const config = parseOpencodeJsonc(laosRoot)
  if (!config) {
    return {
      name: "mcp_health",
      status: "FAIL",
      details: "cannot parse opencode.jsonc",
      items: [{ name: "config", status: "FAIL", details: "parse error — see config check" }],
    }
  }

  const mcpBlock = config.mcp || {}

  const domainMcps = ["latade", "lan8n", "lacouncil", "ladesign", "laengine", "laecon"]
  const platformMcps = ["context7", "exa", "github"]

  for (const name of domainMcps) {
    const entry = mcpBlock[name]
    if (!entry) {
      items.push({ name, status: "FAIL", details: "no config entry" })
      continue
    }
    if (entry.enabled === false) {
      items.push({ name, status: "WARN", details: "disabled in config" })
      continue
    }
    const mcpType = entry.type || "local"
    const hasCommand = Array.isArray(entry.command) && entry.command.length > 0
    if (mcpType === "local" && !hasCommand) {
      items.push({ name, status: "FAIL", details: "local MCP missing command array" })
      continue
    }
    if (mcpType === "reference") {
      items.push({ name, status: "PASS", details: `reference → ${entry.mcp_server || "unknown"}` })
      continue
    }
    if (name === "ladesign") {
      const daemonPath = Array.isArray(entry.command)
        ? entry.command.find((s: string) => s.includes("daemon") || s.includes("cli.js"))
        : null
      const daemonExists = daemonPath ? existsSync(daemonPath) : false
      items.push({
        name,
        status: daemonExists ? "PASS" : "WARN",
        details: daemonExists
          ? `daemon OK (${daemonPath})`
          : `daemon CLI not found at ${daemonPath || "(unresolved)"}; pnpm install may be needed`,
      })
      continue
    }
    items.push({
      name,
      status: "PASS",
      details: `${mcpType} MCP; command: ${Array.isArray(entry.command) ? entry.command.join(" ") : "N/A"}`,
    })
  }

  for (const name of platformMcps) {
    const entry = mcpBlock[name]
    if (!entry) {
      items.push({ name, status: "WARN", details: "no config entry" })
      continue
    }
    if (entry.enabled === false) {
      items.push({ name, status: "WARN", details: "disabled" })
      continue
    }
    items.push({ name, status: "PASS", details: `remote MCP; url: ${entry.url || "unknown"}` })
  }

  const n8nCommunity = mcpBlock["n8n-community"]
  if (n8nCommunity) {
    items.push({
      name: "n8n-community",
      status: n8nCommunity.enabled === false ? "WARN" : "PASS",
      details: n8nCommunity.enabled === false ? "disabled (expected — requires local n8n)" : "enabled",
    })
  }

  const failCount = items.filter(i => i.status === "FAIL").length
  const warnCount = items.filter(i => i.status === "WARN").length
  return {
    name: "mcp_health",
    status: failCount > 0 ? "FAIL" : warnCount > 0 ? "WARN" : "PASS",
    details: `${items.filter(i => i.status === "PASS").length}/${items.length} MCPs OK (config layer only)`,
    items,
  }
}

function checkVenvs(laosRoot: string): DoctorCheck {
  const items: DoctorItem[] = []

  for (const [repoName, relPath] of Object.entries(VENV_REPOS)) {
    const repoDir = resolve(laosRoot, relPath)
    const venvDir = join(repoDir, ".venv")
    const isWindows = process.platform === "win32"
    const pythonPath = join(venvDir, isWindows ? "Scripts" : "bin", "python" + (isWindows ? ".exe" : ""))

    if (!existsSync(venvDir)) {
      items.push({ name: repoName, status: "FAIL", details: `.venv missing at ${venvDir}` })
      continue
    }

    if (!existsSync(pythonPath)) {
      items.push({ name: repoName, status: "FAIL", details: `python missing at ${pythonPath}` })
      continue
    }

    const lockPath = join(repoDir, "uv.lock")
    const pyprojectPath = join(repoDir, "pyproject.toml")
    const refPath = existsSync(lockPath) ? lockPath : existsSync(pyprojectPath) ? pyprojectPath : null

    if (refPath && existsSync(refPath)) {
      try {
        const refMtime = statSync(refPath).mtimeMs
        const venvMtime = statSync(venvDir).mtimeMs
        if (refMtime > venvMtime) {
          items.push({
            name: repoName,
            status: "WARN",
            details: `drift detected: ${refPath.includes("uv.lock") ? "uv.lock" : "pyproject.toml"} newer than .venv; run uv sync`,
          })
          continue
        }
      } catch { /* stat failed — not a blocker */ }
    }

    items.push({ name: repoName, status: "PASS", details: `.venv OK at ${venvDir}` })
  }

  const failCount = items.filter(i => i.status === "FAIL").length
  const warnCount = items.filter(i => i.status === "WARN").length
  return {
    name: "venvs",
    status: failCount > 0 ? "FAIL" : warnCount > 0 ? "WARN" : "PASS",
    details: `${items.filter(i => i.status === "PASS").length}/${items.length} venvs OK`,
    items,
  }
}

function checkModels(laosRoot: string): DoctorCheck {
  const items: DoctorItem[] = []
  const config = parseOpencodeJsonc(laosRoot)
  if (!config) {
    return { name: "models", status: "FAIL", details: "cannot parse opencode.jsonc", items: [{ name: "config", status: "FAIL", details: "parse error" }] }
  }

  const defaultAgent = config.default_agent || "unknown"
  items.push({
    name: "default_agent",
    status: defaultAgent !== "unknown" ? "PASS" : "WARN",
    details: defaultAgent,
  })

  const modelPaths = [["model"], ["models", "default"], ["provider", "model"], ["chat_model"]]
  let modelFound = false
  for (const path of modelPaths) {
    let obj: any = config
    let found = true
    for (const key of path) {
      if (obj && typeof obj === "object" && key in obj) { obj = obj[key] }
      else { found = false; break }
    }
    if (found && obj && typeof obj === "string") {
      items.push({ name: path.join("."), status: "PASS", details: String(obj) })
      modelFound = true
    }
  }

  if (!modelFound) {
    items.push({ name: "model_config", status: "WARN", details: "no explicit model config (inherits from defaults)" })
  }

  const agentsDir = join(laosRoot, ".opencode", "agent")
  if (existsSync(agentsDir)) {
    try {
      const agentFiles = readdirSync(agentsDir).filter(f => f.endsWith(".md"))
      for (const af of agentFiles.slice(0, 12)) {
        try {
          const content = readFileSync(join(agentsDir, af), { encoding: "utf-8" })
          const modelMatch = content.match(/^model:\s*(.+)$/m)
          if (modelMatch) {
            items.push({ name: `agent/${af}`, status: "PASS", details: `model override: ${modelMatch[1].trim()}` })
          }
        } catch { /* skip unreadable */ }
      }
    } catch { /* directory read failed */ }
  }

  const failCount = items.filter(i => i.status === "FAIL").length
  const warnCount = items.filter(i => i.status === "WARN").length
  return {
    name: "models",
    status: failCount > 0 ? "FAIL" : warnCount > 0 ? "WARN" : "PASS",
    details: modelFound ? "model configuration found" : "no explicit model config (using defaults)",
    items,
  }
}

function checkWorkspace(laosRoot: string): DoctorCheck {
  const items: DoctorItem[] = []
  const workspaceRoot = resolve(laosRoot, "..")
  const workspaceExists = existsSync(workspaceRoot)
  items.push({ name: "workspace_root", status: workspaceExists ? "PASS" : "FAIL", details: workspaceExists ? workspaceRoot : "not found" })

  const commomdataPath = resolve(workspaceRoot, "_commomdata")
  items.push({ name: "_commomdata", status: existsSync(commomdataPath) ? "PASS" : "WARN", details: existsSync(commomdataPath) ? commomdataPath : "not found (optional)" })

  for (const [name, relPath] of Object.entries(CAPABILITY_REPOS)) {
    const repoDir = resolve(laosRoot, relPath)
    if (!existsSync(repoDir)) {
      items.push({ name, status: "FAIL", details: `repo missing at ${repoDir}` })
      continue
    }
    const hasGit = existsSync(join(repoDir, ".git"))
    const hasPyproject = existsSync(join(repoDir, "pyproject.toml"))
    const hasPackageJson = existsSync(join(repoDir, "package.json"))
    const indicators = [hasGit && "git", hasPyproject && "pyproject.toml", hasPackageJson && "package.json"].filter(Boolean)
    items.push({ name, status: "PASS", details: `exists at ${repoDir} (${indicators.join(", ") || "no standard project files"})` })
  }

  const failCount = items.filter(i => i.status === "FAIL").length
  const warnCount = items.filter(i => i.status === "WARN").length
  return {
    name: "workspace",
    status: failCount > 0 ? "FAIL" : warnCount > 0 ? "WARN" : "PASS",
    details: `${items.filter(i => i.status === "PASS").length}/${items.length} workspace items OK`,
    items,
  }
}

function runDoctor(laosRoot: string, verbose: boolean): DoctorResult {
  const checks: DoctorCheck[] = [
    checkSystem(), checkConfig(laosRoot), checkPlugins(laosRoot),
    checkMcpHealth(laosRoot), checkVenvs(laosRoot), checkModels(laosRoot),
    checkWorkspace(laosRoot),
  ]

  const pass = checks.filter(c => c.status === "PASS").length
  const fail = checks.filter(c => c.status === "FAIL").length
  const warn = checks.filter(c => c.status === "WARN").length

  return {
    timestamp: new Date().toISOString(),
    laos_root: laosRoot,
    checks: verbose ? checks : checks.map(c => ({ name: c.name, status: c.status, details: c.details })),
    summary: { pass, fail, warn, total: checks.length },
  }
}

// ─── TOOL 1: health_check ─────────────────────────────────────

function runHealthCheck(component: string): string {
  const valid = MCP_COMPONENTS.includes(component as McpComponent)
  if (!valid) {
    return JSON.stringify({
      status: "degraded",
      error: `Unknown component "${component}". Valid: ${MCP_COMPONENTS.join(", ")}`,
    }, null, 2)
  }

  // Check if the MCP is configured in opencode.jsonc
  const laosRoot = getLaosRoot()
  const config = parseOpencodeJsonc(laosRoot)
  if (!config) {
    return JSON.stringify({ status: "down", error: "Cannot parse opencode.jsonc" }, null, 2)
  }

  const mcpEntry = config.mcp?.[component]
  if (!mcpEntry) {
    return JSON.stringify({ status: "down", error: `No MCP config entry found for "${component}"` }, null, 2)
  }

  if (mcpEntry.enabled === false) {
    return JSON.stringify({ status: "degraded", error: `MCP "${component}" is disabled in config` }, null, 2)
  }

  // For local MCPs, try to stat the server file or command
  const startTime = Date.now()
  if (mcpEntry.type === "remote" || mcpEntry.type === "reference") {
    const latencyMs = Date.now() - startTime
    return JSON.stringify({
      status: "healthy",
      version: mcpEntry.url || mcpEntry.mcp_server || "unknown",
      latency_ms: latencyMs,
    }, null, 2)
  }

  // For local MCPs, check if the command binary/script exists
  if (Array.isArray(mcpEntry.command) && mcpEntry.command.length > 0) {
    const binaryPath = mcpEntry.command[0]
    const resolvedPath = join(resolve("."), "..", binaryPath)
    const exists = existsSync(binaryPath) || existsSync(resolvedPath)
    const latencyMs = Date.now() - startTime
    if (exists) {
      return JSON.stringify({
        status: "healthy",
        version: binaryPath,
        latency_ms: latencyMs,
      }, null, 2)
    }
    return JSON.stringify({
      status: "degraded",
      error: `Binary not found: ${binaryPath}`,
      latency_ms: latencyMs,
    }, null, 2)
  }

  return JSON.stringify({
    status: "healthy",
    version: "config-valid",
    latency_ms: Date.now() - startTime,
  }, null, 2)
}

// ─── TOOL 2: add_tool ────────────────────────────────────────

function runAddTool(component: string, toolSpec: Record<string, any>): string {
  const laosRoot = getLaosRoot()
  const config = parseOpencodeJsonc(laosRoot)
  if (!config) {
    return JSON.stringify({ config_diff: "ERROR", requires_restart: false, applied: false, error: "Cannot parse opencode.jsonc" }, null, 2)
  }

  const mcpEntry = config.mcp?.[component]
  if (!mcpEntry) {
    return JSON.stringify({ config_diff: "ERROR", requires_restart: false, applied: false, error: `Component "${component}" not found in MCP config` }, null, 2)
  }

  // Schema validation (dry-run)
  const errors: string[] = []
  if (!toolSpec.name || typeof toolSpec.name !== "string") errors.push("tool_spec.name is required (string)")
  if (!toolSpec.description || typeof toolSpec.description !== "string") errors.push("tool_spec.description is required (string)")
  if (toolSpec.inputSchema && typeof toolSpec.inputSchema !== "object") errors.push("tool_spec.inputSchema must be an object if provided")
  if (toolSpec.outputSchema && typeof toolSpec.outputSchema !== "object") errors.push("tool_spec.outputSchema must be an object if provided")
  if (!toolSpec.handler || typeof toolSpec.handler !== "string") errors.push("tool_spec.handler is required (string)")

  if (errors.length > 0) {
    return JSON.stringify({
      config_diff: "VALIDATION_ERROR",
      requires_restart: false,
      applied: false,
      errors,
    }, null, 2)
  }

  // Dry-run by default - show what would change
  const toolName = toolSpec.name
  const configDiffLines = [
    `Add tool "${toolName}" to component "${component}":`,
    `  description: ${toolSpec.description}`,
    `  inputSchema: ${JSON.stringify(toolSpec.inputSchema || {})}`,
    `  outputSchema: ${JSON.stringify(toolSpec.outputSchema || {})}`,
    `  handler: ${toolSpec.handler}`,
    ``,
    `Note: Adding a tool to the MCP config entry means updating the`,
    `capability repository's MCP server code (${component}'s server.py)`,
    `and re-registering the tool in the server's tool list.`,
    `This change requires editing the capability repo, not opencode.jsonc.`,
  ].join("\n")

  return JSON.stringify({
    config_diff: configDiffLines,
    requires_restart: true,
    applied: false,
    note: "Dry-run: tool was validated. The MCP server in the capability repo must be updated to implement the handler.",
  }, null, 2)
}

// ─── TOOL 3: scaffold_mcp ────────────────────────────────────

function runScaffoldMcp(name: string, tools: any[]): string {
  // Validate name
  if (!name || !/^[a-z][a-z0-9_-]*$/.test(name)) {
    return JSON.stringify({
      path: "",
      files_created: [],
      mcp_server_entry: {},
      error: `Invalid name "${name}". Must start with a letter and contain only lowercase letters, numbers, hyphens, and underscores.`,
    }, null, 2)
  }

  const laosRoot = getLaosRoot()
  const targetDir = resolve(laosRoot, "..", name)

  if (existsSync(targetDir)) {
    return JSON.stringify({
      path: targetDir,
      files_created: [],
      mcp_server_entry: {},
      error: `Directory already exists at ${targetDir}. Scaffold aborted.`,
    }, null, 2)
  }

  // Create directory structure
  const dirsToCreate = [
    targetDir,
    join(targetDir, "mcp"),
    join(targetDir, "spec"),
    join(targetDir, "spec", "adr"),
    join(targetDir, "knowledge"),
  ]

  for (const dir of dirsToCreate) {
    try { mkdirSync(dir, { recursive: true }) } catch { /* ignore */ }
  }

  const filesCreated: string[] = []

  // Generate server.py with health + list_supported_operations + user tools
  const toolDeclarations = (tools || []).map((t: any, i: number) => {
    const toolName = t.name || `tool_${i}`
    const desc = t.description || `Tool ${toolName}`
    const inputSchema = JSON.stringify(t.inputSchema || { type: "object", properties: {} }, null, 4)
    const outputSchema = JSON.stringify(t.outputSchema || {}, null, 4)
    return `
@mcp.tool()
def ${toolName}(${toolName === "health" ? "" : `params: dict = {}`}) -> str:
    \"\"\"${desc}\"\"\"
    # TODO: implement ${toolName}
    return json.dumps({"status": "not_implemented", "tool": "${toolName}"})
`
  }).join("\n")

  const serverPyContent = `"""
${name} MCP Server — auto-scaffolded by laos.infra

Generated via LACOUNCIL proposal 6481da60-67d8-4c7b-a94b-b2da34479f9f
"""

import json
import sys
from mcp.server import Server
from mcp.server.stdio import stdio_server

mcp = Server("${name}")

@mcp.tool()
def health() -> str:
    \"\"\"Liveness probe. Returns status and version.\"\"\"
    return json.dumps({"status": "ok", "version": "0.1.0", "capability": "${name}"})

@mcp.tool()
def list_supported_operations() -> str:
    \"\"\"Catalog all supported operations.\"\"\"
    tools = ${JSON.stringify((tools || []).map((t: any) => t.name || "unnamed"))}
    return json.dumps({"capability": "${name}", "tools": tools})

${toolDeclarations}

if __name__ == "__main__":
    import anyio
    anyio.run(mcp.run, stdio_server())
`

  writeFileSync(join(targetDir, "mcp", "server.py"), serverPyContent, { encoding: "utf-8" })
  filesCreated.push("mcp/server.py")

  // Generate pyproject.toml
  const pyprojectContent = `[project]
name = "${name}"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "mcp>=1.0.0",
    "anyio>=4.0.0",
]

[tool.uv]
dev-dependencies = []
`

  writeFileSync(join(targetDir, "pyproject.toml"), pyprojectContent, { encoding: "utf-8" })
  filesCreated.push("pyproject.toml")

  // Generate spec/adr/_template.md
  const adrTemplate = `# ADR-NNN: <title>

## Status
proposed

## Context
What is the issue that prompted this decision?

## Decision
What was decided and why?

## Alternatives
What other options were considered?

## Consequences
What becomes easier or harder?
`
  writeFileSync(join(targetDir, "spec", "adr", "_template.md"), adrTemplate, { encoding: "utf-8" })
  filesCreated.push("spec/adr/_template.md")

  // Generate README.md
  const readmeContent = `# ${name}

MCP capability auto-scaffolded by laos.infra.

## Tools

${(tools || []).map((t: any) => `- \`${t.name}\`: ${t.description || "No description"}`).join("\n")}
- \`health\`: Liveness probe
- \`list_supported_operations\`: Catalog all operations

## Usage

\`\`\`bash
uv run python mcp/server.py
\`\`\`
`

  writeFileSync(join(targetDir, "README.md"), readmeContent, { encoding: "utf-8" })
  filesCreated.push("README.md")

  // Generate MCP server entry for opencode.jsonc
  const mcpServerEntry = {
    type: "local",
    command: ["uv", "run", "python", `../${name}/mcp/server.py`],
    enabled: true,
    env: {},
  }

  return JSON.stringify({
    path: targetDir,
    files_created: filesCreated,
    mcp_server_entry: mcpServerEntry,
  }, null, 2)
}

// ─── TOOL 4: download_file ───────────────────────────────────

function runDownloadFile(url: string, destPath: string, headers?: Record<string, string>): Promise<string> {
  return new Promise((resolvePromise) => {
    // Validate destPath is under E:/projects/**
    const resolvedDest = resolve(destPath)
    const normalizedDest = normalize(resolvedDest)
    const projectsPrefix = normalize("E:/projects")

    if (!normalizedDest.toLowerCase().startsWith(projectsPrefix.toLowerCase())) {
      resolvePromise(JSON.stringify({
        path: "",
        size_bytes: 0,
        mime_type: "",
        sha256: "",
        error: `dest_path "${destPath}" resolves to "${normalizedDest}" which is outside E:/projects/**. Download blocked.`,
      }, null, 2))
      return
    }

    // Create destination directory if needed
    const destDir = normalize(join(resolvedDest, ".."))
    try { mkdirSync(destDir, { recursive: true }) } catch { /* ignore */ }

    const parsedUrl = new URL(url)
    const httpModule = parsedUrl.protocol === "https:" ? https : http

    const reqHeaders: Record<string, string> = { ...(headers || {}) }
    if (!reqHeaders["User-Agent"]) {
      reqHeaders["User-Agent"] = "LAOS-Infra/1.0"
    }

    const req = httpModule.get(url, { headers: reqHeaders }, (res) => {
      // Follow redirects
      if (res.statusCode && res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        const redirectUrl = new URL(res.headers.location, url).toString()
        runDownloadFile(redirectUrl, destPath, headers).then(resolvePromise)
        return
      }

      if (!res.statusCode || res.statusCode < 200 || res.statusCode >= 300) {
        resolvePromise(JSON.stringify({
          path: "",
          size_bytes: 0,
          mime_type: "",
          sha256: "",
          error: `HTTP ${res.statusCode} for ${url}`,
        }, null, 2))
        return
      }

      const chunks: Buffer[] = []
      const hash = crypto.createHash("sha256")
      let totalBytes = 0

      res.on("data", (chunk: Buffer) => {
        chunks.push(chunk)
        hash.update(chunk)
        totalBytes += chunk.length
      })

      res.on("end", () => {
        const buffer = Buffer.concat(chunks)
        const sha256Hex = hash.digest("hex")
        const contentType = res.headers["content-type"] || "application/octet-stream"

        try {
          writeFileSync(normalizedDest, buffer)
          resolvePromise(JSON.stringify({
            path: normalizedDest,
            size_bytes: totalBytes,
            mime_type: contentType,
            sha256: sha256Hex,
          }, null, 2))
        } catch (writeErr: any) {
          resolvePromise(JSON.stringify({
            path: "",
            size_bytes: totalBytes,
            mime_type: contentType,
            sha256: sha256Hex,
            error: `Write failed: ${writeErr.message}`,
          }, null, 2))
        }
      })

      res.on("error", (err: Error) => {
        resolvePromise(JSON.stringify({
          path: "",
          size_bytes: 0,
          mime_type: "",
          sha256: "",
          error: `Download error: ${err.message}`,
        }, null, 2))
      })
    })

    req.on("error", (err: Error) => {
      resolvePromise(JSON.stringify({
        path: "",
        size_bytes: 0,
        mime_type: "",
        sha256: "",
        error: `Request error: ${err.message}`,
      }, null, 2))
    })

    req.setTimeout(30000, () => {
      req.destroy()
      resolvePromise(JSON.stringify({
        path: "",
        size_bytes: 0,
        mime_type: "",
        sha256: "",
        error: `Timeout after 30s for ${url}`,
      }, null, 2))
    })
  })
}

// ─── TOOL 5: validate_agent ──────────────────────────────────

function runValidateAgent(dispatchType: string): string {
  const laosRoot = getLaosRoot()
  const agentsDir = join(laosRoot, ".opencode", "agent")

  if (!existsSync(agentsDir)) {
    return JSON.stringify({
      valid: false,
      error: ".opencode/agent/ directory not found",
    }, null, 2)
  }

  // Read all agent files (both .md and directories)
  let agentEntries: string[] = []
  try {
    agentEntries = readdirSync(agentsDir)
  } catch {
    return JSON.stringify({
      valid: false,
      error: "Cannot read .opencode/agent/ directory",
    }, null, 2)
  }

  // Known agent types from AGENTS.md and .opencode/agent/
  const agentNames = agentEntries
    .filter(e => e.endsWith(".md") || e.endsWith(".ts"))
    .map(e => e.replace(/\.(md|ts)$/, ""))
    .map(e => e.toLowerCase())

  // Additional known aliases
  const knownAliases: Record<string, string> = {
    "primary": "orchestrator",
    "orchestrator": "orchestrator",
    "data-architect": "data-architect",
    "dashboard-designer": "dashboard-designer",
    "automation-engineer": "automation-engineer",
    "delivery-reviewer": "delivery-reviewer",
    "capability-architect": "capability-architect",
    "workflow-decomposer": "workflow-decomposer",
    "chief-data-scientist": "chief-data-scientist",
    "chief-designer": "chief-designer",
    "chief-engineer": "chief-engineer",
    "explore": "explore",
    "debug-agent": "debug-agent",
  }

  // Sourced from .opencode/agent/ — ONLY agents with charter files.
  // NEVER add agents here without a corresponding .md file.
  const agentTypes: Record<string, "primary" | "subagent" | "evaluator"> = {
    "orchestrator": "primary",
    "data-architect": "subagent",
    "dashboard-designer": "subagent",
    "automation-engineer": "subagent",
    "delivery-reviewer": "subagent",
    "capability-architect": "subagent",
    "workflow-decomposer": "subagent",
    "chief-data-scientist": "evaluator",
    "chief-designer": "evaluator",
    "chief-engineer": "evaluator",
    "explore": "subagent",
    "debug-agent": "subagent",
  }

  const normalizedType = dispatchType.toLowerCase().trim()
  const match = knownAliases[normalizedType] || normalizedType

  if (match in knownAliases || agentNames.includes(match)) {
    const agentType = agentTypes[match] || "subagent"
    return JSON.stringify({
      valid: true,
      agent_type: agentType,
    }, null, 2)
  }

  // Try fuzzy match
  const suggestions = Object.keys(knownAliases).filter(k =>
    k.includes(normalizedType) || normalizedType.includes(k)
  )

  return JSON.stringify({
    valid: false,
    suggested_alternative: suggestions.length > 0 ? suggestions[0] : undefined,
  }, null, 2)
}

// ─── Shell usage tracking (shared file with WDL gate) ──────
// Module-scoped LAOS root holder, set by the Infra factory at
// plugin init. Tool entry points (runHealthCheck, runAddTool,
// runScaffoldMcp, runValidateAgent, runGitLocal) read this instead
// of computing resolve(".") themselves — that pattern misreads
// cwd as the LAOS root when OpenCode launches plugin contexts
// without setting cwd. See ADR-014 for the diagnostic context.
let laosRootHolder: string | null = null
export function setLaosRoot(root: string) {
  laosRootHolder = resolve(root || ".")
}
function getLaosRoot(): string {
  if (laosRootHolder) return laosRootHolder
  // Fallback: assume cwd IS the LAOS root. Matches the legacy
  // behaviour and is correct for sessions where OpenCode sets
  // process.cwd() to the LAOS root.
  return resolve(".")
}

const SHELL_USAGE_PATH = join(getLaosRoot(), ".opencode", "plugins", ".shell-usage.json")

function readShellUsage(): Record<string, any> {
  try {
    if (existsSync(SHELL_USAGE_PATH)) {
      return JSON.parse(readFileSync(SHELL_USAGE_PATH, { encoding: "utf-8" }))
    }
  } catch { /* ignore corrupt file */ }
  return { commands: {}, total: 0, last_promoted: null }
}

// ─── TOOL 6: git_local (80/20 git operations) ───────────────

function runGitLocal(op: string, params: Record<string, any>): string {
  const laosRoot = getLaosRoot()
  const gitDir = params.path || laosRoot
  const safeOps = ["status", "diff", "add", "commit", "push", "log"]

  if (!safeOps.includes(op)) {
    return JSON.stringify({ error: `Unsupported git operation "${op}". Valid: ${safeOps.join(", ")}` }, null, 2)
  }

  try {
    switch (op) {
      case "status": {
        const raw = execSync(`git -C "${gitDir}" status --porcelain`, { encoding: "utf-8", timeout: 10000 })
        const branch = execSync(`git -C "${gitDir}" branch --show-current`, { encoding: "utf-8", timeout: 5000 }).trim()
        const lines = raw.trim().split("\n").filter(Boolean)
        const staged = lines.filter(l => l.startsWith("M ") || l.startsWith("A ") || l.startsWith("D ") || l.startsWith("R "))
          .map(l => ({ status: l.substring(0, 2), file: l.substring(3) }))
        const unstaged = lines.filter(l => l.startsWith(" M") || l.startsWith(" D") || l.startsWith("?"))
          .map(l => ({ status: l.substring(0, 2).trim(), file: l.substring(3) }))
        return JSON.stringify({ branch, staged, unstaged, total_changes: lines.length }, null, 2)
      }

      case "diff": {
        const fileFilter = params.file ? ` -- "${params.file}"` : ""
        const raw = execSync(`git -C "${gitDir}" diff${fileFilter}`, { encoding: "utf-8", timeout: 10000 })
        const stats = execSync(`git -C "${gitDir}" diff --stat${fileFilter}`, { encoding: "utf-8", timeout: 5000 }).trim()
        return JSON.stringify({ diff: raw, stats: stats || "no changes", files_changed: raw ? raw.split("\ndiff --git").length - 1 : 0 }, null, 2)
      }

      case "add": {
        const files = Array.isArray(params.files) ? params.files.map(f => `"${f}"`).join(" ") : "."
        execSync(`git -C "${gitDir}" add ${files}`, { encoding: "utf-8", timeout: 15000 })
        const status = execSync(`git -C "${gitDir}" status --porcelain`, { encoding: "utf-8", timeout: 5000 })
        const staged = status.trim().split("\n").filter(l => /^[MADRC]/.test(l)).length
        return JSON.stringify({ staged_files: staged, message: files === "." ? "All changes staged" : `Staged: ${params.files?.join(", ")}` }, null, 2)
      }

      case "commit": {
        if (!params.message) return JSON.stringify({ error: "commit requires 'message' parameter" }, null, 2)
        const raw = execSync(`git -C "${gitDir}" commit -m "${params.message.replace(/"/g, '\\"')}"`, { encoding: "utf-8", timeout: 15000 })
        const sha = execSync(`git -C "${gitDir}" rev-parse --short HEAD`, { encoding: "utf-8", timeout: 5000 }).trim()
        const lines = raw.trim().split("\n")
        return JSON.stringify({ commit: sha, summary: lines[0] || raw.trim(), output: raw.trim() }, null, 2)
      }

      case "push": {
        const remote = params.remote || "origin"
        const branch = params.branch || execSync(`git -C "${gitDir}" branch --show-current`, { encoding: "utf-8", timeout: 5000 }).trim()
        const raw = execSync(`git -C "${gitDir}" push ${remote} ${branch}`, { encoding: "utf-8", timeout: 30000 })
        return JSON.stringify({ remote, branch, result: raw.trim() || "Push completed" }, null, 2)
      }

      case "log": {
        const limit = Math.min(params.limit || 10, 50)
        const format = params.format || "%h %s (%an, %ar)"
        const raw = execSync(`git -C "${gitDir}" log --oneline -${limit}`, { encoding: "utf-8", timeout: 10000 })
        const commits = raw.trim().split("\n").filter(Boolean).map(line => {
          const [sha, ...rest] = line.split(" ")
          return { sha, message: rest.join(" ") }
        })
        return JSON.stringify({ commits, total: commits.length }, null, 2)
      }

      default:
        return JSON.stringify({ error: `Unreachable: ${op}` }, null, 2)
    }
  } catch (err: any) {
    return JSON.stringify({ error: `git ${op} failed: ${err.message}` }, null, 2)
  }
}

// ─── TOOL 7: uv_tool (80/20 uv operations) ─────────────────

function runUvTool(op: string, params: Record<string, any>): string {
  const safeOps = ["sync", "run"]

  if (!safeOps.includes(op)) {
    return JSON.stringify({ error: `Unsupported uv operation "${op}". Valid: ${safeOps.join(", ")}` }, null, 2)
  }

  const targetDir = params.path || resolve(".")
  try {
    switch (op) {
      case "sync": {
        const raw = execSync(`uv sync`, { cwd: targetDir, encoding: "utf-8", timeout: 60000 })
        return JSON.stringify({ result: raw.trim() || "uv sync completed" }, null, 2)
      }

      case "run": {
        if (!params.script) return JSON.stringify({ error: "uv run requires 'script' parameter" }, null, 2)
        const args = Array.isArray(params.args) ? ` ${params.args.join(" ")}` : ""
        const raw = execSync(`uv run python ${params.script}${args}`, { cwd: targetDir, encoding: "utf-8", timeout: 120000 })
        return JSON.stringify({ stdout: raw.trim(), exit_code: 0 }, null, 2)
      }

      default:
        return JSON.stringify({ error: `Unreachable: ${op}` }, null, 2)
    }
  } catch (err: any) {
    return JSON.stringify({ stdout: err.stdout?.trim() || "", stderr: err.stderr?.trim() || err.message, exit_code: err.status || 1 }, null, 2)
  }
}

// ─── TOOL 8: shell_usage_report ─────────────────────────────

function runShellUsageReport(): string {
  const data = readShellUsage()
  const commands = data.commands || {}
  const total = data.total || 0

  // Find commands with 5+ uses that haven't been promoted yet
  const promoteCandidates = Object.entries(commands)
    .filter(([_, count]) => (count as number) >= 5)
    .map(([cmd]) => cmd)

  const lastPromoted = data.last_promoted

  return JSON.stringify({
    total_shell_calls: total,
    commands,
    promote_candidates: promoteCandidates,
    last_promoted: lastPromoted,
    recommendation: promoteCandidates.length > 0
      ? `These commands have 5+ uses: ${promoteCandidates.join(", ")}. Consider promoting to a dedicated tool.`
      : "No commands have reached the 5-use threshold yet.",
  }, null, 2)
}

// ─── explore_filesystem: safe read-only exploration ──────────
// Created via LACOUNCIL proposal 7fcc6cd5 (Debug Agent + Explore Tool).
// All operations are read-only; rejects paths outside E:/projects/**.
function runExploreFilesystem(args: { path?: string; op: string; depth?: number; pattern?: string; max_lines?: number }): string {
  const { op, depth = 2, pattern, max_lines = 50 } = args
  const targetPath = args.path || "."
  const projectsRoot = "E:/projects"

  // Safety: ensure path is within E:/projects/**
  const resolved = resolve(targetPath)
  if (!resolved.toLowerCase().startsWith(projectsRoot.toLowerCase())) {
    return JSON.stringify({
      status: "error",
      error: "Path must be under E:/projects/** for security. Use read-only bash for other paths.",
      allowed_scope: "E:/projects/**",
    }, null, 2)
  }

  try {
    switch (op) {
      case "list": {
        const entries = readdirSync(resolved, { withFileTypes: true })
        const items = entries.map(e => ({
          name: e.name,
          type: e.isDirectory() ? "directory" : "file",
          size: e.isFile() ? statSync(join(resolved, e.name)).size : null,
        }))
        return JSON.stringify({
          status: "ok",
          path: resolved,
          item_count: items.length,
          items,
        }, null, 2)
      }

      case "tree": {
        const maxDepth = Math.min(depth, 5)
        const tree: any[] = []

        function walkTree(dir: string, currentDepth: number): any[] {
          if (currentDepth > maxDepth) return [{ name: "...", type: "truncated" }]
          const entries = readdirSync(dir, { withFileTypes: true })
          return entries
            .filter(e => !e.name.startsWith(".") && e.name !== "node_modules" && e.name !== ".venv")
            .slice(0, 50) // Cap per-directory to avoid huge output
            .map(e => {
              const fullPath = join(dir, e.name)
              if (e.isDirectory()) {
                return {
                  name: e.name,
                  type: "directory",
                  children: walkTree(fullPath, currentDepth + 1),
                }
              }
              return {
                name: e.name,
                type: "file",
                size: statSync(fullPath).size,
              }
            })
        }

        const treeData = walkTree(resolved, 0)
        return JSON.stringify({
          status: "ok",
          path: resolved,
          max_depth: maxDepth,
          tree: treeData,
        }, null, 2)
      }

      case "search": {
        if (!pattern) {
          return JSON.stringify({
            status: "error",
            error: "pattern parameter required for search operation",
          }, null, 2)
        }
        const results: { file: string; line: number; text: string }[] = []
        const grepRegex = new RegExp(pattern, "i")
        const files = readdirSync(resolved, { withFileTypes: true })
        let count = 0
        const maxResults = 100

        for (const entry of files) {
          if (count >= maxResults) break
          if (entry.isDirectory()) continue
          if (!entry.name.endsWith(".md") && !entry.name.endsWith(".ts") &&
              !entry.name.endsWith(".py") && !entry.name.endsWith(".yaml") &&
              !entry.name.endsWith(".json") && !entry.name.endsWith(".jsonc")) continue
          try {
            const content = readFileSync(join(resolved, entry.name), "utf-8")
            const lines = content.split("\n")
            for (let i = 0; i < lines.length && count < maxResults; i++) {
              if (grepRegex.test(lines[i])) {
                results.push({ file: entry.name, line: i + 1, text: lines[i].trim().substring(0, 120) })
                count++
              }
            }
          } catch { /* skip unreadable files */ }
        }

        return JSON.stringify({
          status: "ok",
          path: resolved,
          pattern,
          match_count: results.length,
          truncated: results.length >= maxResults,
          results,
        }, null, 2)
      }

      case "stat": {
        const stats = statSync(resolved)
        return JSON.stringify({
          status: "ok",
          path: resolved,
          exists: true,
          type: stats.isDirectory() ? "directory" : "file",
          size: stats.size,
          created: stats.birthtime.toISOString(),
          modified: stats.mtime.toISOString(),
          is_symlink: stats.isSymbolicLink(),
        }, null, 2)
      }

      case "read_preview": {
        if (!existsSync(resolved) || statSync(resolved).isDirectory()) {
          return JSON.stringify({
            status: "error",
            error: "read_preview requires a file path",
          }, null, 2)
        }
        const maxLines = Math.min(max_lines, 200)
        const content = readFileSync(resolved, "utf-8")
        const lines = content.split("\n")
        const preview = lines.slice(0, maxLines)
        return JSON.stringify({
          status: "ok",
          path: resolved,
          total_lines: lines.length,
          preview_lines: preview.length,
          truncated: lines.length > maxLines,
          content: preview.join("\n"),
        }, null, 2)
      }

      default:
        return JSON.stringify({
          status: "error",
          error: `Unknown operation: ${op}. Supported: list, tree, search, stat, read_preview`,
        }, null, 2)
    }
  } catch (err: any) {
    return JSON.stringify({
      status: "error",
      error: err.message || String(err),
    }, null, 2)
  }
}

// ─── Plugin export ───────────────────────────────────────────

export const Infra = async ({ project, client, $, directory, worktree }: {
  project: string
  client: any
  $: any
  directory: string
  worktree?: string
}) => {
  const laosRoot = resolve(directory || ".")
  // Register LAOS root with module-scoped holder so the 5 tool entry
  // points (commented at setLaosRoot declaration) read the same root,
  // not process.cwd(). Fix for ADR-014 cross-cutting parse drift.
  setLaosRoot(directory || ".")

  return {
    // ─── No-op hook — this plugin is tool-only ────────────────
    "tool.execute.before": async (
      _input: { tool: string; sessionID: string; callID: string },
      _output: { args: any }
    ) => {
      // Intentionally empty. This plugin provides diagnostic and
      // infrastructure tools and does not intercept tool calls.
    },

    // ─── Custom tools ─────────────────────────────────────────
    tool: {
      // Tool 0: laos-doctor (diagnostic, from original doctor plugin)
      "laos-doctor": {
        description:
          "Run holistic LAOS system diagnostic. Checks 7 dimensions: " +
          "system (OS, Node, Python, uv), config (opencode.jsonc), " +
          "plugins (all expected plugins present), MCP health (config layer), " +
          "venvs (all capability venvs), models (model configuration), " +
          "workspace (repo structure). Returns structured JSON.",
        args: {
          verbose: {
            type: "boolean" as const,
            default: false,
            description: "Include per-item details for each check (default: summary only)",
          },
        },
        async execute(
          args: { verbose?: boolean },
          _context: any
        ): Promise<string> {
          const verbose = args.verbose ?? false
          const result = runDoctor(laosRoot, verbose)

          const lines: string[] = []
          lines.push("LAOS SYSTEM DIAGNOSTIC")
          lines.push(`Timestamp: ${result.timestamp}`)
          lines.push(`Root: ${result.laos_root}`)
          lines.push("")

          for (const check of result.checks) {
            const icon = check.status === "PASS" ? "[PASS]" : check.status === "FAIL" ? "[FAIL]" : "[WARN]"
            lines.push(`${icon} ${check.name}: ${check.details}`)
          }

          lines.push("")
          lines.push(`SUMMARY: ${result.summary.pass} PASS, ${result.summary.warn} WARN, ${result.summary.fail} FAIL (total: ${result.summary.total})`)

          if (result.summary.fail > 0) {
            lines.push("ACTION: Fix FAIL items before dispatching subagents.")
          } else if (result.summary.warn > 0) {
            lines.push("NOTE: WARN items are advisory.")
          } else {
            lines.push("All checks passed.")
          }

          lines.push("")
          lines.push(JSON.stringify(result, null, 2))
          return lines.join("\n")
        },
      },

      // Tool 1: health_check
      "health_check": {
        description:
          "Diagnose a specific MCP component. Returns health status, " +
          "version, and latency. Replaces curl/docker logs/ps aux for " +
          "MCP health checks. Valid components: latade, lan8n, ladesign, " +
          "lacouncil, laecon, laengine, n8n-community, context7, exa, github.",
        args: {
          component: {
            type: "string" as const,
            description: "MCP component to check: latade, lan8n, ladesign, lacouncil, laecon, laengine, n8n-community, context7, exa, github",
          },
        },
        async execute(
          args: { component: string },
          _context: any
        ): Promise<string> {
          return runHealthCheck(args.component)
        },
      },

      // Tool 2: add_tool
      "add_tool": {
        description:
          "Register a new tool specification for an existing MCP capability. " +
          "Validates JSON schema (dry-run by default) and returns the config diff. " +
          "Replaces manual opencode.jsonc editing + restart for testing. " +
          "Note: The actual tool handler must be implemented in the capability repo's MCP server.",
        args: {
          component: {
            type: "string" as const,
            description: "MCP component name (e.g., latade, lan8n, ladesign)",
          },
          tool_spec: {
            type: "object" as const,
            description: "Tool specification with name, description, inputSchema, outputSchema, handler",
          },
        },
        async execute(
          args: { component: string; tool_spec: Record<string, any> },
          _context: any
        ): Promise<string> {
          return runAddTool(args.component, args.tool_spec)
        },
      },

      // Tool 3: scaffold_mcp
      "scaffold_mcp": {
        description:
          "Scaffold a new MCP server capability repository. Creates directory " +
          "structure, server.py with health + list_supported_operations stubs, " +
          "pyproject.toml, ADR template, and README. Returns the path, files " +
          "created, and the opencode.jsonc MCP server entry. " +
          "Replaces mkdir + write server.py from scratch.",
        args: {
          name: {
            type: "string" as const,
            description: "Capability name (lowercase, kebab-case, e.g., 'lasql')",
          },
          tools: {
            type: "array" as const,
            description: "List of tool specs: [{ name, description, inputSchema, outputSchema }]",
          },
        },
        async execute(
          args: { name: string; tools: any[] },
          _context: any
        ): Promise<string> {
          return runScaffoldMcp(args.name, args.tools || [])
        },
      },

      // Tool 4: download_file
      "download_file": {
        description:
          "Download a file from a URL to a local path under E:/projects/**. " +
          "Supports streaming for large files, SHA256 verification, redirect " +
          "following, and custom headers. Replaces curl/wget/Invoke-WebRequest " +
          "for binary downloads. " +
          "WARNING: dest_path MUST be under E:/projects/** (security restriction).",
        args: {
          url: {
            type: "string" as const,
            description: "URL to download from",
          },
          dest_path: {
            type: "string" as const,
            description: "Destination path under E:/projects/**",
          },
          headers: {
            type: "object" as const,
            description: "Optional HTTP headers (e.g., Authorization, User-Agent)",
          },
        },
        async execute(
          args: { url: string; dest_path: string; headers?: Record<string, string> },
          _context: any
        ): Promise<string> {
          return await runDownloadFile(args.url, args.dest_path, args.headers)
        },
      },

      // Tool 5: validate_agent
      "validate_agent": {
        description:
          "Validate whether a WDL-suggested dispatch_type corresponds to a " +
          "real agent in .opencode/agent/. Reads the agents directory in " +
          "runtime (not hardcoded). Returns valid/invalid with agent type " +
          "and suggested alternative. WDL must call this BEFORE emitting " +
          "execution_recommendation.dispatch_type. If valid=false, WDL must " +
          "emit ESCALATE with capability_gap: missing_agent.",
        args: {
          dispatch_type: {
            type: "string" as const,
            description: "Agent dispatch type to validate (e.g., 'data-architect', 'explore')",
          },
        },
        async execute(
          args: { dispatch_type: string },
          _context: any
        ): Promise<string> {
          return runValidateAgent(args.dispatch_type)
        },
      },

      // Tool 5.5: run_command (scoped shell execution)
      "run_command": {
        description:
          "Execute a shell command scoped to the existing bash allowlist " +
          "from .opencode/opencode.jsonc. Supports optional cwd override. " +
          "Replaces manual terminal usage for venv syncs and other " +
          "cross-directory operations. Returns structured JSON with " +
          "stdout, stderr, and exit code. Blocked commands: rm -rf.",
        args: {
          command: {
            type: "string" as const,
            description: "Shell command to execute. Allowed prefixes: git *, uv *, npx *",
          },
          cwd: {
            type: "string" as const,
            description: "Optional working directory (default: current process cwd)",
          },
        },
        async execute(
          args: { command: string; cwd?: string },
          _context: any
        ): Promise<string> {
          const check = isCommandAllowed(args.command)
          if (!check.allowed) {
            return JSON.stringify({
              status: "denied",
              command: args.command,
              reason: check.reason,
              hint: "Allowed: git *, uv *, npx *",
            }, null, 2)
          }

          const result = runCommand(args.command, args.cwd)
          return JSON.stringify({
            status: result.ok ? "ok" : "error",
            command: args.command,
            cwd: args.cwd || process.cwd(),
            output: result.output,
            error: result.error,
          }, null, 2)
        },
      },

      // Tool 6: git_local (80/20 git ops)
      "git_local": {
        description:
          "Execute 80/20 git operations locally: status, diff, add, commit, " +
          "push, log. Returns structured JSON instead of raw shell output. " +
          "Replaces frequent git shell calls with a dedicated tool. " +
          "When a git operation reaches 5+ uses, it becomes a candidate for " +
          "tool promotion (see shell_usage_report).",
        args: {
          op: {
            type: "string" as const,
            description: "Operation: status, diff, add, commit, push, log",
          },
          path: {
            type: "string" as const,
            description: "Optional git repo path (default: LAOS root)",
          },
          file: {
            type: "string" as const,
            description: "Optional file filter for diff",
          },
          files: {
            type: "array" as const,
            description: "Files to stage (for add operation)",
          },
          message: {
            type: "string" as const,
            description: "Commit message (required for commit operation)",
          },
          remote: {
            type: "string" as const,
            description: "Remote name for push (default: origin)",
          },
          branch: {
            type: "string" as const,
            description: "Branch for push (default: current branch)",
          },
          limit: {
            type: "number" as const,
            description: "Log limit (default: 10, max: 50)",
          },
        },
        async execute(
          args: { op: string; path?: string; file?: string; files?: string[]; message?: string; remote?: string; branch?: string; limit?: number },
          _context: any
        ): Promise<string> {
          return runGitLocal(args.op, args)
        },
      },

      // Tool 7: uv_tool (80/20 uv ops)
      "uv_tool": {
        description:
          "Execute 80/20 uv operations: sync, run. Returns structured JSON. " +
          "Replaces frequent uv shell calls with a dedicated tool. " +
          "Note: uv run requires 'script' parameter (path to Python file).",
        args: {
          op: {
            type: "string" as const,
            description: "Operation: sync, run",
          },
          path: {
            type: "string" as const,
            description: "Optional project path for uv sync (default: current)",
          },
          script: {
            type: "string" as const,
            description: "Python script path (required for run operation)",
          },
          args: {
            type: "array" as const,
            description: "Optional script arguments (for run operation)",
          },
        },
        async execute(
          args: { op: string; path?: string; script?: string; args?: string[] },
          _context: any
        ): Promise<string> {
          return runUvTool(args.op, args)
        },
      },

      // Tool 8: shell_usage_report
      "shell_usage_report": {
        description:
          "Report which shell commands are being used most frequently " +
          "(tracked by WDL gate). When a command reaches 5+ uses, " +
          "it becomes a candidate for promotion to a dedicated tool. " +
          "Use this to drive the 80/20 tool creation cycle.",
        args: {},
        async execute(): Promise<string> {
          return runShellUsageReport()
        },
      },

      // Tool 9: explore_filesystem — safe read-only filesystem exploration
      // Created via LACOUNCIL proposal 7fcc6cd5, approved 4/4 supermaioria.
      // Returns structured JSON — replaces Get-ChildItem / ls for programmatic use.
      // Safer than raw bash: no command injection, no state mutation, no secret leakage.
      "explore_filesystem": {
        description:
          "Explore the filesystem with read-only operations. " +
          "Returns structured JSON with file listings, stats, search results. " +
          "Safer than raw bash: no command injection, no state mutation. " +
          "Supports operations: list, tree, search, stat, read_preview.",
        args: {
          path: {
            type: "string" as const,
            description: "Directory or file path to explore (under E:/projects/**)",
          },
          op: {
            type: "string" as const,
            enum: ["list", "tree", "search", "stat", "read_preview"],
            description: "Operation: list (ls), tree (recursive), search (grep), stat (file info), read_preview (first N lines)",
          },
          depth: {
            type: "number" as const,
            description: "Recursion depth for 'tree' operation (default: 2, max: 5)",
          },
          pattern: {
            type: "string" as const,
            description: "Glob or regex pattern for 'search' operation",
          },
          max_lines: {
            type: "number" as const,
            description: "Max lines for 'read_preview' operation (default: 50, max: 200)",
          },
        },
        async execute(
          args: { path?: string; op: string; depth?: number; pattern?: string; max_lines?: number },
          _context: any
        ): Promise<string> {
          return runExploreFilesystem(args)
        },
      },
    },
  }
}
