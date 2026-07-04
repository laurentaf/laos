/**
 * LAOS Doctor — Holistic System Diagnostic
 *
 * Provenance:
 * - OmO `src/cli/doctor/` (provenance feature #12 in knowledge/omo-adoption-provenance.md)
 * - LAOS `scripts/subagent_boot_check.py` (7-dimension boot check per subagent)
 * - Gap: no holistic diagnostic that covers MCP health, model availability,
 *   and plugin status in a single callable tool. The subagent_boot_check.py
 *   is per-subagent; this plugin gives the orchestrator a full-system view.
 *
 * 7 checks (matching OmO's 7 doctor checks):
 * 1. SYSTEM — OS, Node version, Python version, uv version
 * 2. CONFIG — opencode.jsonc exists and parses; all MCP entries present
 * 3. PLUGINS — all 7+ plugins in .opencode/plugins/ are present and non-empty
 * 4. MCP HEALTH — check MCP config entries for latade, lan8n, lacouncil,
 *    ladesign (daemon), laengine, laecon; report enabled/disabled status
 *    (actual health() calls happen via subagent_boot_check.py — this plugin
 *    validates the config layer, not the runtime layer)
 * 5. VENVS — check .venv exists in LAOS, latade, lacouncil, lan8n,
 *    ladesign, laecon, laengine
 * 6. MODELS — check which models are configured in opencode.jsonc
 * 7. WORKSPACE — check E:/projects/ exists, _commomdata exists,
 *    all capability repos exist
 *
 * This replaces the need to run subagent_boot_check.py separately for a
 * quick system overview. The boot check remains the authoritative gate
 * for per-subagent dispatch readiness (it includes runtime smoke-tests
 * and project-specific checks this plugin intentionally omits).
 *
 * Output: structured JSON with check name, status (PASS/FAIL/WARN), details.
 *
 * @module laos-doctor
 */

import { readFileSync, existsSync, statSync, readdirSync } from "node:fs"
import { join, resolve, normalize, sep } from "node:path"
import { execSync } from "node:child_process"

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

function checkSystem(): DoctorCheck {
  const items: DoctorItem[] = []
  const osInfo = `${process.platform} ${process.arch}`

  items.push({
    name: "OS",
    status: "PASS",
    details: osInfo,
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
      items.push({
        name,
        status: "FAIL",
        details: "no config entry",
      })
      continue
    }
    if (entry.enabled === false) {
      items.push({
        name,
        status: "WARN",
        details: "disabled in config",
      })
      continue
    }
    const mcpType = entry.type || "local"
    const hasCommand = Array.isArray(entry.command) && entry.command.length > 0
    if (mcpType === "local" && !hasCommand) {
      items.push({
        name,
        status: "FAIL",
        details: `local MCP missing command array`,
      })
      continue
    }
    if (mcpType === "reference") {
      const refServer = entry.mcp_server
      items.push({
        name,
        status: "PASS",
        details: `reference → ${refServer || "unknown"} (shares process)`,
      })
      continue
    }
    if (name === "ladesign") {
      const daemonPath = Array.isArray(entry.command) ? entry.command.find(
        (s: string) => s.includes("daemon") || s.includes("cli.js")
      ) : null
      const daemonExists = daemonPath ? existsSync(daemonPath) : false
      if (daemonExists) {
        items.push({
          name,
          status: "PASS",
          details: `daemon OK (${daemonPath}); config valid`,
        })
      } else {
        items.push({
          name,
          status: "WARN",
          details: `daemon CLI not found at ${daemonPath || "(unresolved)"}; pnpm install may be needed`,
        })
      }
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
      items.push({
        name,
        status: "WARN",
        details: "no config entry",
      })
      continue
    }
    if (entry.enabled === false) {
      items.push({
        name,
        status: "WARN",
        details: "disabled",
      })
      continue
    }
    const url = entry.url || "unknown"
    items.push({
      name,
      status: "PASS",
      details: `remote MCP; url: ${url}`,
    })
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
    details: `${items.filter(i => i.status === "PASS").length}/${items.length} MCPs OK (config layer only; runtime health via subagent_boot_check.py)`,
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
      items.push({
        name: repoName,
        status: "FAIL",
        details: `.venv missing at ${venvDir}`,
      })
      continue
    }

    if (!existsSync(pythonPath)) {
      items.push({
        name: repoName,
        status: "FAIL",
        details: `python missing at ${pythonPath}`,
      })
      continue
    }

    // Drift detection: compare venv mtime against lockfile (matches subagent_boot_check.py logic)
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
      } catch {
        // stat failed — not a blocker
      }
    }

    items.push({
      name: repoName,
      status: "PASS",
      details: `.venv OK at ${venvDir}`,
    })
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
    return {
      name: "models",
      status: "FAIL",
      details: "cannot parse opencode.jsonc",
      items: [{ name: "config", status: "FAIL", details: "parse error" }],
    }
  }

  const defaultAgent = config.default_agent || "unknown"
  items.push({
    name: "default_agent",
    status: defaultAgent !== "unknown" ? "PASS" : "WARN",
    details: defaultAgent,
  })

  // Check for model configuration in various possible locations
  const modelPaths = [
    ["model"],
    ["models", "default"],
    ["provider", "model"],
    ["chat_model"],
  ]

  let modelFound = false
  for (const path of modelPaths) {
    let obj: any = config
    let found = true
    for (const key of path) {
      if (obj && typeof obj === "object" && key in obj) {
        obj = obj[key]
      } else {
        found = false
        break
      }
    }
    if (found && obj && typeof obj === "string") {
      items.push({
        name: path.join("."),
        status: "PASS",
        details: String(obj),
      })
      modelFound = true
    }
  }

  if (!modelFound) {
    items.push({
      name: "model_config",
      status: "WARN",
      details: "no explicit model config in opencode.jsonc (inherits from OpenCode defaults)",
    })
  }

  // Check agent files for model overrides
  const agentsDir = join(laosRoot, ".opencode", "agent")
  if (existsSync(agentsDir)) {
    try {
      const agentFiles = readdirSync(agentsDir).filter(f => f.endsWith(".md"))
      for (const af of agentFiles.slice(0, 12)) {
        try {
          const content = readFileSync(join(agentsDir, af), { encoding: "utf-8" })
          const modelMatch = content.match(/^model:\s*(.+)$/m)
          if (modelMatch) {
            items.push({
              name: `agent/${af}`,
              status: "PASS",
              details: `model override: ${modelMatch[1].trim()}`,
            })
          }
        } catch {
          // skip unreadable files
        }
      }
    } catch {
      // directory read failed — not critical
    }
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

  // Check E:/projects/ root
  const workspaceRoot = resolve(laosRoot, "..")
  const workspaceExists = existsSync(workspaceRoot)
  items.push({
    name: "workspace_root",
    status: workspaceExists ? "PASS" : "FAIL",
    details: workspaceExists ? workspaceRoot : "not found",
  })

  // Check _commomdata
  const commomdataPath = resolve(workspaceRoot, "_commomdata")
  const commomdataExists = existsSync(commomdataPath)
  items.push({
    name: "_commomdata",
    status: commomdataExists ? "PASS" : "WARN",
    details: commomdataExists ? commomdataPath : "not found (optional grounding data dir)",
  })

  // Check capability repos
  for (const [name, relPath] of Object.entries(CAPABILITY_REPOS)) {
    const repoDir = resolve(laosRoot, relPath)
    if (!existsSync(repoDir)) {
      items.push({
        name: name,
        status: "FAIL",
        details: `repo missing at ${repoDir}`,
      })
      continue
    }
    // Check for basic repo indicators
    const hasGit = existsSync(join(repoDir, ".git"))
    const hasPyproject = existsSync(join(repoDir, "pyproject.toml"))
    const hasPackageJson = existsSync(join(repoDir, "package.json"))
    const indicators = [
      hasGit && "git",
      hasPyproject && "pyproject.toml",
      hasPackageJson && "package.json",
    ].filter(Boolean)

    items.push({
      name: name,
      status: "PASS",
      details: `exists at ${repoDir} (${indicators.join(", ") || "no standard project files"})`,
    })
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
    checkSystem(),
    checkConfig(laosRoot),
    checkPlugins(laosRoot),
    checkMcpHealth(laosRoot),
    checkVenvs(laosRoot),
    checkModels(laosRoot),
    checkWorkspace(laosRoot),
  ]

  const pass = checks.filter(c => c.status === "PASS").length
  const fail = checks.filter(c => c.status === "FAIL").length
  const warn = checks.filter(c => c.status === "WARN").length

  let result: DoctorResult = {
    timestamp: new Date().toISOString(),
    laos_root: laosRoot,
    checks,
    summary: { pass, fail, warn, total: checks.length },
  }

  if (!verbose) {
    result = {
      ...result,
      checks: checks.map(c => ({
        name: c.name,
        status: c.status,
        details: c.details,
        items: undefined,
      })),
    }
  }

  return result
}

export const Doctor = async ({ project, client, $, directory, worktree }: {
  project: string
  client: any
  $: any
  directory: string
  worktree?: string
}) => {
  const laosRoot = resolve(directory || ".")

  return {
    // ─── No-op hook — this plugin is tool-only ──────────────────
    "tool.execute.before": async (
      _input: { tool: string; sessionID: string; callID: string },
      _output: { args: any }
    ) => {
      // Intentionally empty. This plugin provides a diagnostic tool
      // and does not intercept any tool calls.
    },

    // ─── Custom tool: laos-doctor ───────────────────────────────
    tool: {
      "laos-doctor": {
        description:
          "Run holistic LAOS system diagnostic. Checks 7 dimensions: " +
          "system (OS, Node, Python, uv), config (opencode.jsonc), " +
          "plugins (all expected plugins present), MCP health (config layer), " +
          "venvs (all capability venvs), models (model configuration), " +
          "workspace (repo structure). Returns structured JSON. " +
          "Use verbose=true for per-item breakdown. " +
          "Note: actual MCP health() calls happen via subagent_boot_check.py; " +
          "this plugin validates the config layer only.",
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
            const icon =
              check.status === "PASS" ? "[PASS]" :
              check.status === "FAIL" ? "[FAIL]" :
              "[WARN]"
            lines.push(`${icon} ${check.name}: ${check.details}`)

            if (verbose && check.items) {
              for (const item of check.items) {
                const iIcon =
                  item.status === "PASS" ? "  [PASS]" :
                  item.status === "FAIL" ? "  [FAIL]" :
                  "  [WARN]"
                lines.push(`${iIcon} ${item.name}: ${item.details}`)
              }
            }
          }

          lines.push("")
          lines.push(
            `SUMMARY: ${result.summary.pass} PASS, ` +
            `${result.summary.warn} WARN, ` +
            `${result.summary.fail} FAIL ` +
            `(total: ${result.summary.total})`
          )

          if (result.summary.fail > 0) {
            lines.push("ACTION: Fix FAIL items before dispatching subagents.")
          } else if (result.summary.warn > 0) {
            lines.push("NOTE: WARN items are advisory. Run `uv run python scripts/subagent_boot_check.py` for runtime-level validation.")
          } else {
            lines.push("All checks passed. Run `uv run python scripts/subagent_boot_check.py` for per-subagent runtime validation.")
          }

          lines.push("")
          lines.push(JSON.stringify(result, null, 2))

          return lines.join("\n")
        },
      },
    },
  }
}
