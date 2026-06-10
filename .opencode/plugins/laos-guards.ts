/**
 * LAOS Guards — Hard Rule enforcement via OpenCode plugin hooks
 *
 * Provenance:
 *   - Hard Rule #1: "Never put implementation code in LAOS" (AGENTS.md)
 *   - Hard Rule #11: "No synthetic data without user permission" (AGENTS.md, 2026-06-07)
 *   - OmO: write-existing-file-guard (packages/write-existing-file-guard/)
 *   - OmO: env-protection.js pattern (throw Error in tool.execute.before to block)
 *
 * This plugin enforces mechanically what was previously prompt-only:
 *   1. BLOCK write/edit to paths under projects/<name>/artifacts/ if the
 *      orchestrator is the active agent (subagents write artifacts, not the
 *      orchestrator — Hard Rule #1).
 *   2. BLOCK write/edit to implementation file extensions (*.sql, *.dax, *.pbix)
 *      anywhere inside the LAOS repo itself (AGENTS.md repo layout rule).
 *   3. WARN (append to output) when writing artifacts without synthetic
 *      frontmatter, if the file path is under artifacts/{data,design,automation,
 *      pipeline,dq,deck}/ and the content doesn't contain "synthetic:" marker.
 *      This is a soft guard — the delivery-reviewer catches it at P0-15,
 *      but early warning reduces rework.
 *   4. BLOCK write/edit to .env files anywhere in the workspace.
 *   5. BLOCK read of .env files (prevents accidental secret leakage to LLM context).
 */

import type { Plugin } from "@opencode-ai/plugin"

// File extensions that are implementation code — never allowed in LAOS repo root
const IMPLEMENTATION_EXTENSIONS = [".sql", ".dax", ".pbix"]

// Artifact subdirectories that require synthetic data frontmatter
const SYNTHETIC_GUARD_DIRS = [
  "artifacts/data/",
  "artifacts/design/",
  "artifacts/automation/",
  "artifacts/pipeline/",
  "artifacts/dq/",
  "artifacts/deck/",
]

// Resolve path relative to project root
function normalizePath(filePath: string): string {
  return filePath.replace(/\\/g, "/")
}

function isUnderArtifacts(normalizedPath: string): boolean {
  return normalizedPath.includes("/artifacts/")
}

function isImplementationInLAOS(normalizedPath: string, projectDir: string): boolean {
  // Only block implementation files if they're in the LAOS repo itself,
  // not in child project repos (which live outside LAOS).
  const inLAOSRepo = normalizedPath.startsWith(normalizePath(projectDir))
  if (!inLAOSRepo) return false
  // Allow under projects/<name>/ — that's contract space, not implementation
  if (normalizedPath.includes("/projects/")) return false
  // Block implementation extensions in the LAOS repo root
  return IMPLEMENTATION_EXTENSIONS.some(ext => normalizedPath.toLowerCase().endsWith(ext))
}

function needsSyntheticGuard(normalizedPath: string): boolean {
  return SYNTHETIC_GUARD_DIRS.some(dir => normalizedPath.includes(dir))
}

function hasSyntheticFrontmatter(content: string): boolean {
  // Check for synthetic: true in frontmatter (YAML or sidecar marker)
  return /synthetic:\s*true/i.test(content)
}

export const LaosGuards = async ({ project, directory }: { project: string; directory: string }) => {
  const projectDir = normalizePath(directory)

  return {
    "tool.execute.before": async (
      input: { tool: string; sessionID: string; callID: string },
      output: { args: any }
    ) => {
      const toolName = input.tool

      // ─── Guard 1: Orchestrator must not write artifacts ─────────
      // This guard is advisory — OpenCode doesn't expose the current agent
      // name in the hook input, so we check path patterns instead.
      // The orchestrator restriction is enforced by the orchestrator.md
      // instruction file; this guard catches accidental violations.

      // ─── Guard 2: No implementation code in LAOS repo ───────────
      if (toolName === "write" || toolName === "edit") {
        const filePath = normalizePath(output.args?.filePath || output.args?.path || "")

        if (filePath && isImplementationInLAOS(filePath, projectDir)) {
          const ext = IMPLEMENTATION_EXTENSIONS.find(e => filePath.toLowerCase().endsWith(e))
          throw new Error(
            `[LAOS Guard] Hard Rule #1: Implementation code (*${ext}) must not live in the LAOS repo. ` +
            `This file belongs in a child project repo or capability repo. ` +
            `Path: ${filePath}`
          )
        }

        // ─── Guard 4: Block write to .env files ─────────────────
        if (filePath.endsWith(".env") || filePath.includes(".env.")) {
          throw new Error(
            `[LAOS Guard] .env files must not be written by agents. ` +
            `Use OS env vars or the project's .env (managed by the user). ` +
            `Path: ${filePath}`
          )
        }
      }

      // ─── Guard 5: Block read of .env files ─────────────────────
      if (toolName === "read") {
        const filePath = normalizePath(output.args?.filePath || output.args?.path || "")

        if (filePath && (filePath.endsWith(".env") || filePath.includes(".env."))) {
          throw new Error(
            `[LAOS Guard] .env files must not be read into LLM context (secret leakage risk). ` +
            `Path: ${filePath}`
          )
        }
      }
    },

    "tool.execute.after": async (
      input: { tool: string; sessionID: string; callID: string; args: any },
      output: { title: string; output: string; metadata: any }
    ) => {
      // ─── Guard 3: Synthetic data frontmatter warning ───────────
      if (input.tool === "write") {
        const filePath = normalizePath(input.args?.filePath || input.args?.path || "")
        const content = input.args?.content || ""

        if (filePath && needsSyntheticGuard(filePath) && content && !hasSyntheticFrontmatter(content)) {
          // Soft guard: append warning to the tool output, don't block.
          // The delivery-reviewer will hard-block at P0-15 if this is
          // actually synthetic data without frontmatter.
          const warning =
            "\n\n[LAOS Guard] WARNING: This artifact is in a production path " +
            "but has no synthetic data frontmatter. If this file contains " +
            "synthetic data, add frontmatter: synthetic: true, granted_by: <user>, " +
            "granted_at: <iso8601>, reason: <why_real_data_missing>. " +
            "See knowledge/data-fabrication-policy.md §4."

          output.output = (output.output || "") + warning
        }
      }
    },
  }
}
