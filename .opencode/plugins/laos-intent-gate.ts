/**
 * LAOS Intent Gate — auto-inject needs-specific context into specialist dispatches.
 *
 * Provenance:
 * - OmO `keyword-detector` (feature #11 in knowledge/omo-adoption-provenance.md)
 * - LAOS-specific: project.yaml already declares needs at session start,
 *   so this plugin can auto-inject without keyword detection.
 *
 * Mapping table (subagent_type → protocol snippet):
 * ┌───────────────────────┬──────────────────────────────────────────────────┐
 * │ subagent_type         │ Injected protocol (3-5 lines)                    │
 * ├───────────────────────┼──────────────────────────────────────────────────┤
 * │ data-architect        │ LATADE MCP, medallion, artifacts/{data,pipe,dq}  │
 * │ dashboard-designer    │ LADESIGN MCP + skills, DESIGN.md ref             │
 * │ automation-engineer   │ LAN8N + n8n-community MCP, trigger+SLA docs      │
 * │ delivery-reviewer     │ Read-only, padroes-entrega validation             │
 * │ capability-architect  │ LACOUNCIL + github MCP, binding-conditions       │
 * │ workflow-decomposer   │ LACOUNCIL ONLY (WDL-R1), verdict tri-state       │
 * │ chief-data-scientist  │ Read-only evaluator, 5-dimension scoring         │
 * │ chief-designer        │ Read-only evaluator, 5-dimension scoring         │
 * │ chief-engineer        │ Read-only evaluator, 5-dimension scoring         │
 * └───────────────────────┴──────────────────────────────────────────────────┘
 *
 * Idempotency: each protocol snippet carries a sentinel marker
 * `[intent-gate:<type>]`. The plugin skips injection when the sentinel
 * already appears in the prompt — prevents double-injection across
 * retries or re-dispatches.
 */

import * as fs from "fs"
import * as path from "path"

const PROTOCOL_SNIPPETS: Record<string, string> = {
  "data-architect": [
    "[intent-gate:data-architect]",
    "You are the data specialist. Use latade.* MCP tools only.",
    "Follow medallion pipeline (bronze→silver→gold).",
    "Write artifacts to artifacts/{data,pipeline,dq}/.",
    "Log ADRs to spec/adr/.",
  ].join("\n"),
  "dashboard-designer": [
    "[intent-gate:dashboard-designer]",
    "You are the design specialist. Use ladesign.* MCP tools + skill library.",
    "Reference DESIGN.md from artifacts/design/source.md.",
    "Write artifacts to artifacts/{design,deck}/.",
  ].join("\n"),
  "automation-engineer": [
    "[intent-gate:automation-engineer]",
    "You are the automation specialist. Use lan8n.* + n8n-community.* MCP tools.",
    "Document trigger + SLA for every workflow.",
    "Write artifacts to artifacts/automation/.",
  ].join("\n"),
  "delivery-reviewer": [
    "[intent-gate:delivery-reviewer]",
    "You are the read-only reviewer.",
    "Validate against knowledge/padroes-entrega.md.",
    "Write review to artifacts/review/checklist.md.",
    "Never mutate project artifacts.",
  ].join("\n"),
  "capability-architect": [
    "[intent-gate:capability-architect]",
    "You are the structural improvement implementer.",
    "Use lacouncil.* + github.* MCP tools.",
    "Follow binding-conditions.md (14 conditions).",
    "Never do project work.",
  ].join("\n"),
  "workflow-decomposer": [
    "[intent-gate:workflow-decomposer]",
    "You are the WDL PM layer. Use lacouncil.* ONLY (WDL-R1 wall).",
    "Emit analysis.md + plan.json + verdict.yaml.",
    "Verdict tri-state: READY | DEFER | ESCALATE.",
  ].join("\n"),
  "chief-data-scientist": [
    "[intent-gate:chief-data-scientist]",
    "You are the data/ML evaluator (read-only).",
    "Score candidates on: model fit 30%, residual diagnostics 20%,",
    "prediction accuracy 20%, interpretability 15%, robustness 15%.",
  ].join("\n"),
  "chief-designer": [
    "[intent-gate:chief-designer]",
    "You are the design/UX evaluator (read-only).",
    "Score candidates on: visual hierarchy 25%, accessibility 25%,",
    "DESIGN.md consistency 20%, anti-slop 15%, interaction quality 15%.",
  ].join("\n"),
  "chief-engineer": [
    "[intent-gate:chief-engineer]",
    "You are the engineering evaluator (read-only).",
    "Score candidates on: reliability 30%, SLA compliance 20%,",
    "test coverage 20%, performance 15%, operational readiness 15%.",
  ].join("\n"),
}

const SENTINEL_RE = /\[intent-gate:([a-z-]+)\]/

function readProjectNeeds(workspaceRoot: string): string[] {
  const candidates = [
    path.join(workspaceRoot, "project.yaml"),
    path.join(workspaceRoot, "projects", "project.yaml"),
  ]
  for (const candidate of candidates) {
    try {
      const raw = fs.readFileSync(candidate, "utf-8")
      const needsMatch = raw.match(/^needs:\s*\n((?:\s+- .+\n?)+)/m)
      if (needsMatch) {
        return needsMatch[1]
          .split("\n")
          .map((l: string) => l.trim())
          .filter((l: string) => l.startsWith("- "))
          .map((l: string) => l.replace(/^-\s*/, ""))
      }
    } catch {
      // file not found or unreadable — skip
    }
  }
  return []
}

export const IntentGate = async ({ directory }: { directory: string }) => {
  return {
    "tool.execute.before": async (
      _input: { tool: string; sessionID: string; callID: string },
      output: { args: Record<string, unknown> },
    ) => {
      if (_input.tool !== "task") return

      const subagentType = String(
        output.args?.subagentType ?? output.args?.subagent_type ?? output.args?.agent ?? "",
      )
      const snippet = PROTOCOL_SNIPPETS[subagentType]
      if (!snippet) return

      const prompt = String(output.args?.prompt ?? "")
      if (SENTINEL_RE.test(prompt)) return

      const needs = readProjectNeeds(directory)
      let needsBlock = ""
      if (needs.length > 0) {
        needsBlock = `\n\nProject needs: ${needs.join(", ")}.`
      }

      output.args.prompt = snippet + needsBlock + (prompt ? "\n\n" + prompt : "")
    },
  }
}
