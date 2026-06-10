# Review Checklist: OmO Adoption Plan Implementation

| Field | Value |
|-------|-------|
| **project_name** | omo-adoption (structural improvement, Regime A) |
| **review_date** | 2026-06-09 |
| **verdict** | NOT DELIVERABLE |

---

## Stage 0: Preflight

- **Preflight JSON**: Not provided (meta-project, not a `projects/<name>/` domain project)
- **Manual checks**: PASS (no .sql/.dax/.pbix in LAOS; no secrets; .env in .gitignore)
- **WDL gate**: N/A_justified — structural improvement work, exempt per Hard Rule 8.4

## Stage 1: P0 Walk

| # | Rule | Result | Evidence |
|---|------|--------|----------|
| 1 | SDD scaffold exists | N/A | Meta-project, not `projects/<name>/` |
| 2 | spec/todo.md populated | N/A | Same |
| 3 | contract.md exists | N/A | Same |
| 4 | delivery-reviewer validated | PASS | This IS the review |
| 5 | project.yaml valid | N/A | No project.yaml for meta-projects |
| 6 | All deliverables in artifacts/ | N/A | No project deliverables |
| 7 | No secrets in versioned files | PASS | grep `(API_KEY\|SECRET\|PASSWORD\|TOKEN\|CREDENTIAL)\s*[:=]` → 0 matches in `.opencode/` |
| 8 | Git sync (Regime A) | PASS | Structural change approved via LACOUNCIL governance |
| 9 | Data artifact specs | N/A | No data artifacts |
| 10 | Empty DataFrame guards | N/A | No data pipelines |
| 11 | DESIGN.md reference | N/A | No visual artifacts |
| 12 | Automation trigger/SLA | N/A | No automations |
| 13 | ADR-minimum-1 | N/A | LACOUNCIL proposals serve as decision records |
| 14 | ADR path canonical | PASS | No ADRs in `artifacts/decisions/` |
| 15 | Synthetic data compliance | PASS | No synthetic data artifacts |
| 16 | README ≥ 400 chars | N/A | No child repo |
| 17 | No implementation code in LAOS | PASS | glob `*.sql/*.dax/*.pbix` → 0 results. 7 `.ts` plugins are structural enforcement, not domain code |
| 18 | Calibration (PR-1) | PASS | 7 plugins for 11 HRs + 3 OmO patterns — proportional |
| 19 | Preflight passed | PASS | Manual equivalent checks performed |
| 20 | Boot check 6th dimension | N/A | Not dispatching a domain subagent |

## Stage 2: Project-Specific Criteria

| # | Criterion | Result | Evidence |
|---|-----------|--------|----------|
| C1 | No implementation code (*.sql, *.dax, *.pbix) | PASS | glob returned 0 matches |
| C2 | No secrets committed | PASS | grep for secret patterns → 0; .env in .gitignore |
| C3 | All files are structural | PASS | 7 `.ts` plugins + 3 `.md` charters + 1 provenance doc + config/doc updates |
| C4 | AGENTS.md consistent with files | **FAIL** | 4 inconsistencies (see Stage 3) |
| C5 | Plugin registration valid | PASS | `opencode.jsonc:22-26` → `plugins.paths: [".opencode/plugins"]` |
| C6 | 3 evaluator charters properly scoped | **FAIL** | Scope gaps (see Stage 3) |
| C7 | MCP wall table matches plugin | **FAIL** | 3 enforcement gaps (see Stage 3) |

## Stage 3: Coverage

| Criterion | Status | Detail |
|-----------|--------|--------|
| C1 (no impl code) | EXPLICITLY_VERIFIED | glob `*.sql/*.dax/*.pbix` → 0 |
| C2 (no secrets) | EXPLICITLY_VERIFIED | grep → 0; .gitignore covers .env |
| C3 (structural only) | EXPLICITLY_VERIFIED | All files are config/charter/enforcement |
| C4 (AGENTS.md consistency) | **VIOLATED** | 4 issues below |
| C5 (plugin registration) | EXPLICITLY_VERIFIED | `opencode.jsonc:22-26` |
| C6 (evaluator scope) | **VIOLATED** | 2 issues below |
| C7 (MCP wall vs plugin) | **VIOLATED** | 3 issues below |

### Finding F1: WDL gate bug unfixed (BLOCKING)

- **Rule**: Task description says "Bug fix: laos-wdl-gate.ts line 116: subagent_type → subagentType"
- **File**: `.opencode/plugins/laos-wdl-gate.ts:84`
- **Evidence**: Line 84 reads `output.args?.subagent_type` (snake_case property access). All 5 references to the local var `subagentType` are fine (camelCase local), but the **property read** from `output.args` uses snake_case. If OpenCode's task tool uses camelCase args (JS convention), this property access returns `undefined` → specialist dispatch is never identified → WDL gate is **dead code** (all dispatches pass through unblocked).
- **Fix**: Change `output.args?.subagent_type` → `output.args?.subagentType` on line 84
- **Owner**: orchestrator (or capability-architect)

### Finding F2: Evaluator agents missing from MCP wall plugin (BLOCKING)

- **Rule**: AGENTS.md lines 238-240 define MCP walls for chief-data-scientist, chief-designer, chief-engineer
- **File**: `.opencode/plugins/laos-mcp-wall.ts:48-73`
- **Evidence**: `AGENT_MCP_WALLS` object has no entries for the 3 evaluators. When any evaluator is dispatched, `wall` is `undefined` → plugin falls through to permissive mode (line 109: `if (!wall) return`). MCP wall is unenforced for evaluators.
- **Fix**: Add entries to `AGENT_MCP_WALLS` for `chief-data-scientist`, `chief-designer`, `chief-engineer` matching AGENTS.md table
- **Owner**: orchestrator (or capability-architect)

### Finding F3: `laengine.*` missing from MCP wall plugin (BLOCKING)

- **Rule**: AGENTS.md lines 232-234 list `laengine.*` in Blocked for data-architect, dashboard-designer, automation-engineer
- **File**: `.opencode/plugins/laos-mcp-wall.ts:43`
- **Evidence**: `DOMAIN_MCPS` array is `["latade", "ladesign", "lan8n", "laecon", "n8n-community"]` — `"laengine"` is absent. No agent's blocked list includes laengine. The AGENTS.md MCP wall for `laengine.*` is entirely unenforced.
- **Fix**: Add `"laengine"` to `DOMAIN_MCPS` array and add `"laengine"` to blocked lists for data-architect, dashboard-designer, automation-engineer, delivery-reviewer, capability-architect (matching AGENTS.md table)
- **Owner**: orchestrator (or capability-architect)

### Finding F4: delivery-reviewer MCP access overly restricted in plugin (BLOCKING)

- **Rule**: AGENTS.md line 235: delivery-reviewer = "(read-only, all)" with "write operations" blocked
- **File**: `.opencode/plugins/laos-mcp-wall.ts:65-68`
- **Evidence**: Plugin blocks ALL MCP namespaces for delivery-reviewer (line 67: `blocked: ["latade", "ladesign", "lan8n", "laecon", "n8n-community", "lacouncil"]`). This prevents the reviewer from calling `latade.execute_sql` for data inspection, `latade.inspect_table` for schema checks, etc. AGENTS.md says reviewer has read-only access to all MCPs — only writes are blocked.
- **Fix**: Change delivery-reviewer wall to `allowed: ["latade", "ladesign", "lan8n", "lacouncil", "laecon", "laengine", "context7", "exa", "github"]` (read-only all MCPs). The write-blocking should be enforced separately (the reviewer's charter already says read-only).
- **Owner**: orchestrator (or capability-architect)

### Finding F5: Evaluator charters — laecon.* omission (ADVISORY)

- **Rule**: MCP wall consistency
- **File**: `.opencode/agent/chief-data-scientist.md:122`, `.opencode/agent/chief-designer.md:119`
- **Evidence**: Both evaluator charters and AGENTS.md table omit `laecon.*` from Blocked. This is internally consistent (charter matches AGENTS.md), but arguably the evaluators shouldn't call laecon either. Low risk since evaluators are constrained by their charters.
- **Fix**: Consider adding `laecon.*` to "Tools you do NOT use" in both charters + AGENTS.md table for completeness
- **Owner**: orchestrator (advisory, not blocking)

## Stage 4: Reflection

1. **Least confident finding**: F1 (subagent_type vs subagentType). I cannot verify OpenCode's task tool arg naming convention without running the code. If task uses snake_case args, line 84 is correct and the "bug fix" description was wrong. But the task description itself says this IS a bug that should have been fixed, and it wasn't — so I must flag it. If the fix was intentionally not applied, the task description should be corrected.

2. **Did NOT check**: (1) Whether plugins compile under OpenCode's TypeScript system, (2) Whether `@opencode-ai/plugin` type imports resolve, (3) Runtime behavior of inter-plugin `_setAgent`/`_setVerdict` APIs, (4) Whether `plugins.paths` is the correct config key for the installed OpenCode version, (5) Security of `.env` file contents (blocked by our own Guard 5).

3. **Pattern reminder**: This is the 2nd occurrence of **documentation-implementation drift** in AGENTS.md (1st was the Git sync regime duplication, reportedly fixed in this change). The MCP wall table is a manually-maintained duplicate of `laos-mcp-wall.ts` — a 2-source-of-truth problem. Recommend: make the plugin the canonical source, have AGENTS.md reference it rather than duplicate it. If this pattern appears a 3rd time, escalate via `lacouncil.detect_patterns`.

4. **Permission prompts observed**: None. All paths under `E:/projects/**` (pre-authorized per HR #10).

## Required Actions (if FAIL)

| # | Finding | Fix | Owner |
|---|---------|-----|-------|
| F1 | WDL gate `subagent_type` bug unfixed | Change `output.args?.subagent_type` → `output.args?.subagentType` on line 84 of `laos-wdl-gate.ts` | orchestrator |
| F2 | Evaluator agents missing from MCP wall plugin | Add `chief-data-scientist`, `chief-designer`, `chief-engineer` entries to `AGENT_MCP_WALLS` in `laos-mcp-wall.ts` | orchestrator |
| F3 | `laengine.*` missing from MCP wall plugin | Add `"laengine"` to `DOMAIN_MCPS` + blocked lists in `laos-mcp-wall.ts` | orchestrator |
| F4 | delivery-reviewer overly restricted in plugin | Change reviewer wall to `allowed: [all MCPs]` (read-only), enforce write-blocking separately | orchestrator |

## Signature

- **Stage 0 evidence**: Manual preflight equivalent performed (no .sql/.dax/.pbix, no secrets, .env gitignored). WDL gate N/A (structural improvement, exempt per HR 8.4).
- **Stage 1-4 evidence**: This document — 20 P0 items walked, 7 project criteria evaluated, 4 blocking findings + 1 advisory identified.
- **Reviewer**: delivery-reviewer subagent
- **Date**: 2026-06-09
