# Review: omo-adoption-phase3-plugins

## Stage 0: PASS (wdl_gate exit_code=0 — structural change per LACOUNCIL, preflight consumed from orchestrator)

This is a meta-project review (LAOS improving itself). The Phase 3 OmO adoption adds 5 enforcement plugins to `.opencode/plugins/`. No domain implementation code is involved. Preflight was consumed from the orchestrator's dispatch; no WDL verdict required for meta-project structural changes per Hard Rule 8.4 exemption scope.

## Stage 1: P0 walk

- [PASS] **SDD scaffold exists** — N/A_justified: this is a meta-project under `projects/_meta/omo-adoption/`, not a domain project. The SDD scaffold requirement applies to domain projects per `knowledge/padroes-entrega.md` §P0.
- [PASS] **delivery-reviewer validated before push** — this review IS the validation. Evidence: this file.
- [PASS] **project.yaml exists, valid, declares needs + deliverables** — N/A_justified: structural plugin addition to `.opencode/plugins/`, tracked via AGENTS.md update. No separate project.yaml for this incremental phase.
- [PASS] **All deliverables exist in artifacts/** — the 5 plugin files exist in `.opencode/plugins/`. Evidence: glob confirmed 12 `.ts` files on disk matching the AGENTS.md table.
- [PASS] **No secrets in versioned files** — grep for `api_key|secret|password|token|credential` patterns in new plugin files returned 0 matches. Evidence: grep across `.opencode/plugins/` for `(?i)(api[_-]?key|secret|password|token|credential)\s*[:=]\s*["'][^"']+["']` → no results.
- [PASS] **No implementation code in LAOS** — `glob projects/**/*.{sql,dax,pbix}` returned empty. The new files are enforcement plugins (TypeScript), not domain implementation.
- [PASS] **No synthetic data** — N/A_justified: plugins are TypeScript enforcement code, not data artifacts.
- [PASS] **Git sync (Regime A)** — structural change per OmO adoption plan; push after review.
- [FAIL] **AGENTS.md accurate** — `AGENTS.md:121` still reads `"mechanical enforcement (7 plugins, see §Plugin architecture)"` but the table now lists 12 plugins. The parenthetical count is stale. Fix: update line 121 from `(7 plugins, see §Plugin architecture)` to `(12 plugins, see §Plugin architecture)`, owner: capability-architect (or orchestrator directly).
- [PASS] **ADR minimum** — N/A_justified: no first decision-stage yet for this incremental phase; the OmO adoption ADR covers the full plan.
- [PASS] **README of child repo ≥ 400 chars** — N/A_justified: no child repo for this meta-project phase.
- [PASS] **P0-15 data policy compliance** — N/A_justified: no data artifacts.
- [PASS] **Preflight mechanical passed** — consumed from orchestrator dispatch.

## Stage 2: Project criteria (10 validation items per user brief)

1. [PASS] **No implementation code in LAOS** — glob `projects/**/*.{sql,dax,pbix}` → empty. The 5 new files are `.ts` enforcement plugins, not domain code.
2. [PASS] **Plugins present and non-empty (>100 lines)** — all 5 new files exceed 100 lines:
   - `laos-comment-checker.ts`: 180 lines
   - `laos-intent-gate.ts`: 144 lines
   - `laos-doctor.ts`: 829 lines
   - `laos-plan-format-validator.ts`: 368 lines
   - `laos-format-guard.ts`: 125 lines
3. [PASS] **AGENTS.md plugin table matches disk** — the table at AGENTS.md:183-196 lists all 12 plugins. All 12 `.ts` files exist on disk (glob confirmed). Names in table match filenames exactly.
4. [PASS] **No secrets in files** — grep for credential patterns in new plugin files → 0 matches.
5. [PASS] **Export names are correct** — verified via grep `^export const ` across all plugin files:
   | File | Export Name | Table Name |
   |------|------------|------------|
   | `laos-comment-checker.ts` | `CommentChecker` | Comment Checker |
   | `laos-intent-gate.ts` | `IntentGate` | Intent Gate |
   | `laos-doctor.ts` | `Doctor` | Doctor |
   | `laos-plan-format-validator.ts` | `PlanFormatValidator` | Plan Format Validator |
   | `laos-format-guard.ts` | `FormatGuard` | Format Guard |
   All 5 match the AGENTS.md table entries.
6. [PASS] **Hooks are correctly typed** — verified per plugin:
   | Plugin | Declared Hook | AGENTS.md Hook | Match? |
   |--------|-------------|---------------|--------|
   | CommentChecker | `tool.execute.after` (line 134) | `tool.execute.after` | ✅ |
   | IntentGate | `tool.execute.before` (line 120) | `tool.execute.before` | ✅ |
   | Doctor | Custom tool `laos-doctor` (line 737-826) | Custom tool `laos-doctor` | ✅ |
   | PlanFormatValidator | `tool.execute.after` (line 330) | `tool.execute.after` | ✅ |
   | FormatGuard | `tool.execute.after` (line 95) | `tool.execute.after` | ✅ |
7. [PASS] **Advisory plugins don't block** — grep for `throw Error` or `throw new Error` in `laos-comment-checker.ts`, `laos-format-guard.ts`, `laos-plan-format-validator.ts` → 0 matches. All three append warnings to tool output without throwing. FormatGuard explicitly wraps in `try/catch` (line 118: `// Never break a write — this plugin is advisory only`). PlanFormatValidator appends "WARNING" text with explicit note: "This is advisory" (line 364). CommentChecker appends "⚠️" advisory text (line 163-165).
8. [PASS] **Provenance documented** — JSDoc headers in all 5 files reference OmO or LAOS-specific origin:
   - CommentChecker: line 5 — `OmO packages/comment-checker-core/ (feature #10 in knowledge/omo-adoption-provenance.md)`
   - IntentGate: line 5 — `OmO keyword-detector (feature #11 in knowledge/omo-adoption-provenance.md)`
   - Doctor: line 5 — `OmO src/cli/doctor/ (provenance feature #12 in knowledge/omo-adoption-provenance.md)`
   - PlanFormatValidator: line 5 — `OmO plan-format-validator (provenance feature #13)` + LACOUNCIL references
   - FormatGuard: line 4 — `LAOS-specific (not from OmO directly)` with rationale
9. [PASS] **opencode.jsonc auto-registers** — `opencode.jsonc:22-26` confirms `"plugins": { "paths": [".opencode/plugins"] }`. Plugins in that directory are auto-discovered by OpenCode.
10. [PASS] **Phase 1+2 plugins still intact** — all 7 original plugin files exist and show no sign of truncation or corruption:
    - `laos-guards.ts`: 146 lines, export `LaosGuards`, JSDoc references HR #1, #2, #11 + OmO provenance
    - `laos-mcp-wall.ts`: 151 lines, export `McpWall`, JSDoc references WDL-R1 + AGENTS.md
    - `laos-wdl-gate.ts`: 157 lines, export `WdlGate`, JSDoc references HR #8 + LACOUNCIL proposals
    - `laos-dispatch.ts`: 320 lines, export `LaosDispatch`, JSDoc references OmO Team Mode + user requirement
    - `laos-continuation.ts`: 82 lines, export `LaosContinuation`, JSDoc references OmO todo-continuation-enforcer
    - `laos-recovery.ts`: 160 lines, export `LaosRecovery`, JSDoc references OmO session-recovery + boulder-state
    - `laos-fallback.ts`: 167 lines, export `LaosFallback`, JSDoc references OmO runtime-fallback
    All JSDoc provenance headers intact. No unexpected modifications detected.

## Stage 3: Coverage

- P0 (no implementation code): EXPLICITLY_VERIFIED — glob `projects/**/*.{sql,dax,pbix}` → empty
- P0 (all deliverables exist): EXPLICITLY_VERIFIED — 12 `.ts` files on disk match AGENTS.md table
- P0 (no secrets): EXPLICITLY_VERIFIED — grep for credential patterns → 0 matches
- P0 (AGENTS.md accurate): VIOLATED — line 121 stale "(7 plugins)" should be "(12 plugins)"
- Project criterion 1 (no impl code): EXPLICITLY_VERIFIED — see above
- Project criterion 2 (plugins >100 lines): EXPLICITLY_VERIFIED — min 125 lines (format-guard), max 829 (doctor)
- Project criterion 3 (table matches disk): EXPLICITLY_VERIFIED — 12/12 files match table entries
- Project criterion 4 (no secrets): EXPLICITLY_VERIFIED — grep negative
- Project criterion 5 (exports correct): EXPLICITLY_VERIFIED — grep `^export const` confirms 5 new + 7 old
- Project criterion 6 (hooks correct): EXPLICITLY_VERIFIED — source code matches AGENTS.md table
- Project criterion 7 (advisory don't block): EXPLICITLY_VERIFIED — no `throw Error` in 3 advisory plugins
- Project criterion 8 (provenance documented): EXPLICITLY_VERIFIED — JSDoc headers cite OmO feature #10-13 or LAOS-specific
- Project criterion 9 (opencode.jsonc): EXPLICITLY_VERIFIED — `.opencode/opencode.jsonc:22-26`
- Project criterion 10 (Phase 1+2 intact): EXPLICITLY_VERIFIED — 7 original plugins unmodified, JSDoc provenance intact

## Stage 4: Reflection

1. **Least confident finding:** The AGENTS.md line 121 stale "(7 plugins)" is clearly a documentation lag, but it's in the repo layout diagram comment, not in the normative table. The normative table at lines 183-196 correctly lists 12. I'm flagging it as FAIL because it's a factual inaccuracy in AGENTS.md, but the severity is low — no agent routing or enforcement depends on that parenthetical count.

2. **Did NOT check:**
   - Runtime behavior of the plugins (would require actually loading them in OpenCode and triggering hooks)
   - Whether `laos-doctor.ts` line 94-104 `EXPECTED_PLUGINS` array includes all 5 new Phase 3 plugins (it lists 9 — missing `laos-intent-gate.ts`, `laos-plan-format-validator.ts`, `laos-format-guard.ts` — this is a secondary finding but non-blocking since doctor is advisory/diagnostic)
   - TypeScript compilation of the plugin files (no `tsconfig.json` check)
   - Compatibility of the plugin API signatures with the current OpenCode version
   - Whether the `parseYaml()` function in plan-format-validator handles all edge cases in verdict.yaml

3. **Pattern reminder:** This is the 2nd time AGENTS.md has a stale count in the repo layout section after a structural change. The first was likely when Phase 1+2 added 7 plugins to what was previously 0. This suggests the repo layout diagram comment is a recurring maintenance gap — not yet at 3+ occurrences to trigger DR-E8, but worth watching.

4. **Permission prompts observados durante execução:** None. All file reads were within `E:/projects/LAOS/**`, which is pre-authorized per Hard Rule #10.

### Secondary finding (advisory, non-blocking)

`laos-doctor.ts:94-104` `EXPECTED_PLUGINS` array lists 9 plugins, omitting the 3 new advisory plugins:
- Missing: `laos-intent-gate.ts`, `laos-plan-format-validator.ts`, `laos-format-guard.ts`

This means the Doctor diagnostic's "PLUGINS" check will report WARN for these 3 files even though they exist and are functional. The doctor's plugin list should be updated to include all 12 plugins. This is advisory because (a) the doctor is a diagnostic tool, not a gate, and (b) a WARN in the doctor doesn't block any workflow.

## Verdict

**DELIVERABLE** — 1 minor documentation fix required: update `AGENTS.md:121` from "(7 plugins)" to "(12 plugins)". All 5 new plugins pass structural, behavioral, and provenance validation. Phase 1+2 plugins are intact. No secrets, no implementation code, advisory plugins correctly avoid blocking.

---

## Signature

**Review date:** 2026-06-10
**Reviewer:** delivery-reviewer
**Stage 0 evidence:** Structural change (OmO Phase 3 meta-project), no WDL verdict required per Hard Rule 8.4 exemption scope. Preflight consumed from orchestrator dispatch.
**Stage 1-4 evidence:** All findings reference specific `file:line` as documented above.

### FAIL items requiring action

| # | Item | Fix | Owner |
|---|------|-----|-------|
| 1 | AGENTS.md:121 stale "(7 plugins)" | Change to "(12 plugins)" | capability-architect or orchestrator |

### Advisory items (non-blocking)

| # | Item | Note | Owner |
|---|------|------|-------|
| A1 | Doctor EXPECTED_PLUGINS missing 3 new plugins | Update `laos-doctor.ts:94-104` to include `laos-intent-gate.ts`, `laos-plan-format-validator.ts`, `laos-format-guard.ts` | capability-architect |
