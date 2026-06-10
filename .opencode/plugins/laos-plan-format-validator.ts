/**
 * LAOS Plan Format Validator — Schema-validates WDL verdict.yaml and plan.json
 *
 * Provenance:
 * - OmO plan-format-validator (provenance feature #13)
 * - WDL contract: workflows/wdl-contract.yaml (verdict schema §2, plan schema §4)
 * - LACOUNCIL a4fe9faa: WDL v1 proposal (supermaioria 4/4, 2026-06-06)
 * - LACOUNCIL 7fd94c1a: Charter P0 for workflow-decomposer
 *
 * Schemas enforced:
 *
 * verdict.yaml (after YAML parsing):
 *   Required: state (READY|DEFER|ESCALATE), plan_id (string),
 *             verified_by (string, known agent ID), timestamp (ISO 8601),
 *             wdl_version (integer)
 *   Optional: reason (string — REQUIRED if state is DEFER or ESCALATE),
 *             signals_evaluated (array of strings), notes (string)
 *
 * plan.json:
 *   Required: plan_id (string), project (string), needs (array),
 *             stages (array of { name, capabilities, subagent }),
 *             created_at (ISO 8601)
 *   Each stage: name (string), capabilities (array of strings),
 *               subagent (string)
 *
 * Advisory: this plugin appends warnings to tool output on validation failure
 * but does NOT block the write. The WDL gate plugin (laos-wdl-gate.ts)
 * handles blocking at dispatch time. This separation ensures format errors
 * are caught early (at write time) while the authoritative gate remains
 * at the pre-dispatch hook.
 */

import type { Plugin } from "@opencode-ai/plugin"

const VALID_VERDICT_STATES = ["READY", "DEFER", "ESCALATE"] as const

const KNOWN_AGENT_IDS = [
  "workflow-decomposer",
  "delivery-reviewer",
  "data-architect",
  "dashboard-designer",
  "automation-engineer",
  "capability-architect",
  "chief-data-scientist",
  "chief-designer",
  "chief-engineer",
  "orchestrator",
] as const

const ISO_8601_RE = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?$/

const VERDICT_PATH_RE = /artifacts\/wdl\/[^/]+\/verdict\.yaml$/
const PLAN_PATH_RE = /artifacts\/wdl\/[^/]+\/plan\.json$/

function normalizePath(p: string): string {
  return p.replace(/\\/g, "/")
}

interface ValidationResult {
  valid: boolean
  errors: string[]
}

function validateVerdict(content: string): ValidationResult {
  const errors: string[] = []

  let doc: Record<string, any>
  try {
    doc = parseYaml(content)
  } catch (e: any) {
    return { valid: false, errors: [`YAML parse error: ${e.message}`] }
  }

  if (!doc || typeof doc !== "object" || Array.isArray(doc)) {
    return { valid: false, errors: ["verdict.yaml must be a YAML mapping"] }
  }

  // ─── Required fields ───────────────────────────────────────
  if (!("state" in doc)) {
    errors.push("missing required field: state")
  } else if (!VALID_VERDICT_STATES.includes(doc.state)) {
    errors.push(
      `invalid state "${doc.state}" — must be one of: ${VALID_VERDICT_STATES.join(", ")}`
    )
  }

  if (!("plan_id" in doc)) {
    errors.push("missing required field: plan_id")
  } else if (typeof doc.plan_id !== "string" || doc.plan_id.trim() === "") {
    errors.push("plan_id must be a non-empty string")
  }

  if (!("verified_by" in doc)) {
    errors.push("missing required field: verified_by")
  } else if (typeof doc.verified_by !== "string" || doc.verified_by.trim() === "") {
    errors.push("verified_by must be a non-empty string")
  } else if (!(KNOWN_AGENT_IDS as readonly string[]).includes(doc.verified_by)) {
    errors.push(
      `verified_by "${doc.verified_by}" is not a known agent ID — ` +
      `expected one of: ${KNOWN_AGENT_IDS.join(", ")}`
    )
  }

  if (!("timestamp" in doc)) {
    errors.push("missing required field: timestamp")
  } else if (typeof doc.timestamp !== "string" || !ISO_8601_RE.test(doc.timestamp)) {
    errors.push(`timestamp "${doc.timestamp}" is not a valid ISO 8601 string`)
  }

  if (!("wdl_version" in doc)) {
    errors.push("missing required field: wdl_version")
  } else if (typeof doc.wdl_version !== "number" || !Number.isInteger(doc.wdl_version)) {
    errors.push("wdl_version must be an integer")
  }

  // ─── Conditional: reason required for DEFER / ESCALATE ─────
  if (
    (doc.state === "DEFER" || doc.state === "ESCALATE") &&
    (!("reason" in doc) || typeof doc.reason !== "string" || doc.reason.trim() === "")
  ) {
    errors.push(
      `reason is required when state is ${doc.state} (WDL contract §2 — ` +
      `block_reason / escalation_payload)`
    )
  }

  // ─── Optional field type checks ────────────────────────────
  if ("signals_evaluated" in doc) {
    if (!Array.isArray(doc.signals_evaluated)) {
      errors.push("signals_evaluated must be an array")
    } else if (!doc.signals_evaluated.every((s: any) => typeof s === "string")) {
      errors.push("signals_evaluated must be an array of strings")
    }
  }

  if ("notes" in doc && typeof doc.notes !== "string") {
    errors.push("notes must be a string")
  }

  return { valid: errors.length === 0, errors }
}

function validatePlan(content: string): ValidationResult {
  const errors: string[] = []

  let doc: Record<string, any>
  try {
    doc = JSON.parse(content)
  } catch (e: any) {
    return { valid: false, errors: [`JSON parse error: ${e.message}`] }
  }

  if (!doc || typeof doc !== "object" || Array.isArray(doc)) {
    return { valid: false, errors: ["plan.json must be a JSON object"] }
  }

  // ─── Required top-level fields ─────────────────────────────
  if (!("plan_id" in doc)) {
    errors.push("missing required field: plan_id")
  } else if (typeof doc.plan_id !== "string" || doc.plan_id.trim() === "") {
    errors.push("plan_id must be a non-empty string")
  }

  if (!("project" in doc)) {
    errors.push("missing required field: project")
  } else if (typeof doc.project !== "string" || doc.project.trim() === "") {
    errors.push("project must be a non-empty string")
  }

  if (!("needs" in doc)) {
    errors.push("missing required field: needs")
  } else if (!Array.isArray(doc.needs)) {
    errors.push("needs must be an array")
  }

  if (!("stages" in doc)) {
    errors.push("missing required field: stages")
  } else if (!Array.isArray(doc.stages)) {
    errors.push("stages must be an array")
  } else {
    // ─── Per-stage validation ───────────────────────────────
    doc.stages.forEach((stage: any, i: number) => {
      const prefix = `stages[${i}]`

      if (!stage || typeof stage !== "object" || Array.isArray(stage)) {
        errors.push(`${prefix} must be an object`)
        return
      }

      if (!("name" in stage)) {
        errors.push(`${prefix} missing required field: name`)
      } else if (typeof stage.name !== "string" || stage.name.trim() === "") {
        errors.push(`${prefix}.name must be a non-empty string`)
      }

      if (!("capabilities" in stage)) {
        errors.push(`${prefix} missing required field: capabilities`)
      } else if (!Array.isArray(stage.capabilities)) {
        errors.push(`${prefix}.capabilities must be an array`)
      } else if (!stage.capabilities.every((c: any) => typeof c === "string")) {
        errors.push(`${prefix}.capabilities must be an array of strings`)
      }

      if (!("subagent" in stage)) {
        errors.push(`${prefix} missing required field: subagent`)
      } else if (typeof stage.subagent !== "string" || stage.subagent.trim() === "") {
        errors.push(`${prefix}.subagent must be a non-empty string`)
      }
    })
  }

  if (!("created_at" in doc)) {
    errors.push("missing required field: created_at")
  } else if (typeof doc.created_at !== "string" || !ISO_8601_RE.test(doc.created_at)) {
    errors.push(`created_at "${doc.created_at}" is not a valid ISO 8601 string`)
  }

  return { valid: errors.length === 0, errors }
}

/**
 * Minimal YAML parser for flat-ish verdict.yaml files.
 * Handles: key: value, nested maps, lists of strings, comments, blank lines.
 * Not a full YAML spec parser — sufficient for the verdict schema which
 * is shallow (one level of nesting max, e.g. exemption: { applied, reason }).
 */
function parseYaml(raw: string): Record<string, any> {
  const result: Record<string, any> = {}
  const lines = raw.split("\n")
  let currentKey: string | null = null
  let currentObj: Record<string, any> | null = null
  let currentListKey: string | null = null
  let currentList: string[] | null = null

  for (const line of lines) {
    const trimmed = line.trimEnd()

    if (trimmed === "" || trimmed.startsWith("#")) continue

    // List item ("- value")
    const listMatch = trimmed.match(/^(\s*)- (.+)$/)
    if (listMatch && currentListKey !== null) {
      if (currentList === null) {
        currentList = []
        result[currentListKey] = currentList
      }
      let val: string = listMatch[2].trim()
      // Strip quotes
      if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
        val = val.slice(1, -1)
      }
      currentList.push(val)
      continue
    }

    // Reset list tracking when we hit a non-list, non-indented line
    if (currentListKey !== null && !trimmed.startsWith(" ") && !trimmed.startsWith("-")) {
      currentListKey = null
      currentList = null
    }

    // Nested key (indented, e.g. "  applied: true")
    const nestedMatch = trimmed.match(/^(\s+)(\w[\w_-]*):\s*(.*)$/)
    if (nestedMatch && currentKey !== null) {
      if (currentObj === null) {
        currentObj = {}
        result[currentKey] = currentObj
      }
      const subKey = nestedMatch[2]
      const subVal = nestedMatch[3].trim()
      if (subVal === "" || subVal === "|" || subVal === ">") {
        // Sub-key starts a nested block — too deep for this parser,
        // store as empty string (verdict.yaml is one-level deep)
        currentObj[subKey] = ""
      } else {
        currentObj[subKey] = coerceYamlScalar(subVal)
      }
      continue
    }

    // Top-level key: value
    const kvMatch = trimmed.match(/^(\w[\w_-]*):\s*(.*)$/)
    if (kvMatch) {
      currentKey = kvMatch[1]
      currentObj = null
      const rawVal = kvMatch[2].trim()

      if (rawVal === "" || rawVal === "|" || rawVal === ">") {
        // Value is a block (multi-line) or empty — next lines may be
        // a nested map or a list. Peek ahead handled by list/nested matchers.
        // Set list tracking so subsequent "- x" lines collect here.
        currentListKey = currentKey
        currentList = null
        continue
      }

      result[currentKey] = coerceYamlScalar(rawVal)
      currentListKey = null
      currentList = null
      continue
    }
  }

  return result
}

function coerceYamlScalar(raw: string): any {
  if (raw === "true") return true
  if (raw === "false") return false
  if (raw === "null" || raw === "~") return null

  if ((raw.startsWith('"') && raw.endsWith('"')) || (raw.startsWith("'") && raw.endsWith("'"))) {
    return raw.slice(1, -1)
  }

  if (/^-?\d+$/.test(raw)) return parseInt(raw, 10)
  if (/^-?\d+\.\d+$/.test(raw)) return parseFloat(raw)

  return raw
}

export const PlanFormatValidator = async ({
  project,
  directory,
}: {
  project: string
  directory: string
}) => {
  return {
    "tool.execute.after": async (
      input: { tool: string; sessionID: string; callID: string; args: any },
      output: { title: string; output: string; metadata: any }
    ) => {
      if (input.tool !== "write") return

      const rawPath = normalizePath(input.args?.filePath || input.args?.path || "")
      if (!rawPath) return

      const content: string = input.args?.content ?? ""
      if (!content) return

      let result: ValidationResult | null = null
      let fileType: string | null = null

      if (VERDICT_PATH_RE.test(rawPath)) {
        result = validateVerdict(content)
        fileType = "verdict.yaml"
      } else if (PLAN_PATH_RE.test(rawPath)) {
        result = validatePlan(content)
        fileType = "plan.json"
      }

      if (!result || !fileType) return

      const tag = "[LAOS Plan Format Validator]"

      if (result.valid) {
        output.output = (output.output || "") + `\n\n${tag} OK — ${fileType} schema valid.`
      } else {
        const bulletList = result.errors.map(e => `  - ${e}`).join("\n")
        output.output =
          (output.output || "") +
          `\n\n${tag} WARNING — ${fileType} schema validation failed:\n${bulletList}\n` +
          `This is advisory. The WDL gate (laos-wdl-gate.ts) handles blocking at dispatch time.`
      }
    },
  }
}
