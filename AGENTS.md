# LAOS — Laurent Agent Operating System

LAOS is an **orchestration layer** with an independent structural improvement team (the **LACOUNCIL**). It contains no domain implementation. All domain knowledge lives in capability repositories exposed via MCP.

## Hard rules

1. **Never put implementation code in LAOS.** SQL, dashboards, n8n workflows belong in the capability repo (LATADE, LADESIGN, LAN8N), exposed through its MCP server. If you find yourself writing them here, stop.
2. **Projects live in their own GitHub repository.** A project is a `project.yaml` contract mirrored here in `projects/<name>/` (brief, needs, deliverables, child repo URL), plus a sibling repository `laurentaf/<project-name>` (or under an org) where all artifacts, code, snapshots and ADRs are produced. **LAOS never stores domain artifacts.** If you find yourself writing SQL, dashboard markup, n8n JSON, or any other implementation inside `LAOS/projects/<name>/`, it belongs in the child repo.
3. **Capabilities are reached only through MCP.** Never `cd ../latade` and execute a script. Call the MCP tool. If the tool is missing, add it to the capability repo's server, not to LAOS.
4. **Routing is deterministic.** `registry/needs-to-capabilities.yaml` maps abstract needs to concrete MCP capabilities. The orchestrator follows the map; it does not invent capability selection on its own.
5. **Structural changes require consensus.** Modifications to registry, workflows, knowledge, fundamentos, or subagent config go through the Conselho (via LACOUNCIL MCP). Unanimity for fundamentos, supermajority for registry, majority for knowledge.
6. **Every structural change is logged.** LACOUNCIL records all proposals, votes, and diffs in its DuckDB (`memoria/lacouncil.duckdb`).
7. **Patterns repeated 3+ times trigger action.** If the same issue appears in 3+ projects, LAOS calls LACOUNCIL to investigate and propose a fix — promote to knowledge/ or update registry.
8. **WDL preflight gate is mandatory before specialist dispatch.**
   The orchestrator MUST dispatch `workflow-decomposer` and obtain
   a verified `verdict.yaml` (state: `READY`) before dispatching
   any project subagent (data-architect, dashboard-designer,
   automation-engineer, capability-architect, or any future
   specialist). Source: LACOUNCIL `a4fe9faa-4d50-4668-845a-ef64f1d41c36`
   (WDL v1) + `7fd94c1a-d21d-49cc-a0e6-07c07c716e73` (Charter P0),
   both supermaioria 4/4 SIM, 2026-06-06. Sub-rules:
   - **8.1 (mandatory).** Specialist dispatch is conditional on
     `verdict.yaml` with `state: READY`. Without it, no dispatch.
   - **8.2 (penalty).** Bypass = trust-score penalty on the
     orchestrator: `-0.1` per individual bypass, `-0.3` max per
     plan-id, `-0.5` max per session (per-resolved-DEFER cycle,
     defined in `workflows/wdl-contract.yaml` §versioning.session_id).
     Penalty is non-erasable within the session.
   - **8.3 (cost).** Bypass requires manifest overlay
     (`artifacts/wdl/<plan-id>/bypass-manifest.yaml`) +
     user confirmation + cost (the trust-score penalty above).
     No bypass is free.
   - **8.4 (exemption scope).** Exemptions apply only to the
     orchestrator's own direct `lacouncil.*` invocations for
     structural improvement work (LACOUNCIL proposals, structural
     investigations, trust-score reads). Exemption scope is the
     allowlist of 9 `lacouncil.*` tools declared in
     `workflows/wdl-contract.yaml` §triggers.exempt.scope.tool_allowlist.
     No narrative exemptions. Any tool outside the allowlist, or
     any non-orchestrator-direct subagent, requires the WDL gate.
    - **8.5 (reviewer cites exit_code).** The `delivery-reviewer`
      MUST quote the `exit_code` from the preflight `wdl-gate` in
      its G4 sign-off. The 5 cite categories are enumerated in
      `.opencode/agent/delivery-reviewer.md` §"WDL preflight gate".
9. **Venv path policy (user authorization, 2026-06-07).** When invoking
   a Python virtual environment, the orchestrator and subagents follow
   this rule:
   - **In-scope (no prompt):** venv lives under `E:/projects/**/.venv/`
     or `E:/projects/**/venv/` (e.g. `E:/projects/laos/.venv`,
     `E:/projects/latade/.venv`, `E:/projects/lacouncil/.venv`). Use
     it directly.
   - **Out-of-scope (must explain):** venv lives OUTSIDE
     `E:/projects/**` (e.g. `~/.venv/`, system Python, `/usr/local/venv/`,
     `C:\Python3X\`). Stop and explain to the user WHY before invoking
     it: which capability needs the external venv, where it is, and
     why we cannot colocate it under `E:/projects/`. This is a user
     authorization boundary, not a hard technical constraint — the user
     has chosen to keep the LAOS workspace self-contained. The
     explanation is a one-time requirement per external venv; once the
     user accepts, subsequent invocations proceed without re-asking.
10. **Permission grants for the LAOS workspace (user authorization,
    2026-06-07).** The following operations are pre-authorized in
    `opencode.jsonc` and every subagent frontmatter (per Hard Rule #9
    + user grant). No prompt required:
    - **File operations** under `E:/projects/**` (read, write, edit,
      create, delete). This covers all LAOS projects, capability repos
      (latade, lan8n, lacouncil, laecon, laengine, ladesign), and
      cross-project grounding data (`E:/projects/_commomdata/**`).
    - **Bash `git *`** — all git subcommands (status, diff, log, add,
      commit, push, pull, fetch, branch, checkout, merge, rebase,
      stash, tag, etc.) run without prompt. Destructive operations
      are not separately blocked, but `rm -rf *` is denied at the
      opencode layer (filesystem-level, not git-level) and Regime A
      push rules still apply.
    Implementation lives in:
    - `.opencode/opencode.jsonc` `permission` block (top-level)
    - `.opencode/agent/<subagent>.md` frontmatter (per-subagent override;
      required because per `knowledge/opencode-permissions.md` §2.1
      the subagent's frontmatter overrides the top-level wholesale)
11. **No synthetic data in production artifacts without explicit user
    permission (proposed LACOUNCIL, 2026-06-07).** When a subagent
    (`data-architect`, `dashboard-designer`, `automation-engineer`, or
    any future specialist) cannot retrieve the **real** data needed
    for a deliverable, it MUST stop and report the gap to the
    orchestrator. The orchestrator MUST ask the user before any
    synthetic data is generated. The default user response is **NO**.
    The agent's temptation to "just make it up" is the failure mode
    this rule closes (Fagan 1976 inspection-stage principle: defect
    injection is cheaper to prevent than to detect downstream).
    Permission modes (see `knowledge/data-fabrication-policy.md` for
    the full policy, metadata schema, and audit trail):
    - **Per-ask (default, strict).** Agent stops, orchestrator asks
      the user, user decides per occurrence. The synthetic data
      artifact MUST carry frontmatter
      `synthetic: true, granted_by: <user>, granted_at: <iso8601>,
       reason: <why_real_data_missing>`.
    - **Project-scoped (opt-in, less strict).** The `project.yaml`
      declares `data_policy: { allow_synthetic: true, scope: [<list
      of artifact paths or classes>] }`. Within the declared scope,
      the agent can use synthetic data without per-ask. The
      `granted_by` field reads `project_yaml` (not the user name)
      and `granted_at` is the project.yaml `criado_em` or the
      data_policy block's `decided_at` field.
    - **Acceptable without permission (always allowed).** Test
      fixtures in `tests/` directories; wireframe mockups explicitly
      labeled `mock, not for production`; documentation examples
      in `docs/` or knowledge entries. Production deliverables
      (`artifacts/data/`, `artifacts/design/`, `artifacts/automation/`,
      `artifacts/deck/`, `artifacts/pipeline/`, `artifacts/dq/`) are
      never acceptable without the explicit permission flow above.
    Any synthetic-data artifact in a production path without
    frontmatter marking is a **P0 violation** (delivery-reviewer
    auto-fails the sign-off; see `knowledge/padroes-entrega.md`).

## Repository layout

```
LAOS/
├── .opencode/ opencode config, agents, commands, skills
│   ├── agent/ subagent charters (orchestrator + 9 specialists)
│ ├── plugins/ mechanical enforcement (12 plugins, see §Plugin architecture)
│   ├── skill/ LAOS-specific skills
│   └── opencode.jsonc main config (MCP, permissions, plugins)
├── lacouncil/ structural improvement support (SDD, propostas)
├── registry/ capability catalog + needs->capability routing
├── workflows/ declarative templates that compose capabilities
├── knowledge/ ONLY transversal knowledge (glossary, delivery patterns)
├── projects/ contract index: one project.yaml per project
│   ├── <name>/ domain projects
│   └── _meta/ meta-projects (LAOS improving itself)
├── capabilities-stubs/ starter MCP servers until real ones ship
├── scripts/ CLI helpers (bootstrap, list, sync, boot checks)
├── pyproject.toml local Python venv deps (mcp[cli], pyyaml)
├── setup.ps1 first-run setup
├── lacouncil.yaml structural improvement config (LACOUNCIL MCP)
└── AGENTS.md this file
```

## Capability repositories

Each repo is a **capability**, not a project. LAOS composes these capabilities — it never owns domain implementation.

| Repo | Domain | Capability name | MCP server | Role |
| ---- | ------ | --------------- | ---------- | ---- |
| `../latade` | Data | **LATADE** | `latade` | SQL, modeling, BI, DQ, docs |
| `../lan8n` | Automation | **LAN8N** | `lan8n` | Workflows, integrations, APIs, alerts |
| `../ladesign` | Design | **LADESIGN** | `ladesign` | Dashboards, decks, wireframes, design systems, video |
| `../laecon` | Economics | **LAECON** | `laecon` | Econometrics, interpretable ML, causal inference |
| `../lacouncil` | Improvement | **LACOUNCIL** | `lacouncil` | Investigation, proposals, voting, patterns |
| `../laengine` | Game Dev | **LAENGINE** | `laengine` | Sports simulation, match engine, squad management |

> **Naming note:** Capability names — LATADE, LAN8N, LADESIGN, LAECON,
> LAENGINE — are the canonical identifiers. The repo folder names
> match the capability names (e.g. `../lan8n` for LAN8N).

Platform MCPs (cross-cutting, used by any subagent):
- `context7` - fetch current library/API docs instead of hallucinating.
- `exa` - web search and page extraction. Remote OAuth.
- `github` - repos, issues, PRs, code search. Reads GITHUB_TOKEN from OS env.

## Agent topology

- **orchestrator** (primary, default). Owns the session. Reads project.yaml, resolves needs via the registry, dispatches subagents. When acting as structural improver, also manages improvements via LACOUNCIL, consults the Conselho, and maintains DuckDB memory through LACOUNCIL MCP. The orchestrator may also manage meta-projects in projects/_meta/.
  **Tools the orchestrator uses directly:** `lacouncil.*` is reserved for structural improvement work only (LACOUNCIL proposals, structural investigations, trust-score reads, project memory). For project work (specialist dispatch, plan analysis, capability gap diagnosis), the orchestrator dispatches `workflow-decomposer` — it does NOT call `lacouncil.*` directly for project planning, decomposition, or verification. This split is the WDL exemption scope (Hard Rule 8.4).
- **data-architect** (subagent). Talks only to `latade.*` MCP tools.
- **dashboard-designer** (subagent). Talks only to `ladesign.*` MCP tools and the LADESIGN skill library.
- **automation-engineer** (subagent). Talks only to `lan8n.*` and optionally `n8n-community.*` MCP tools.
- **delivery-reviewer** (subagent). Read-only. Validates artifacts against `knowledge/padroes-entrega.md`.
- **capability-architect** (subagent, BASIC → STABLE 2026-07-04). Implements LACOUNCIL-approved structural changes only — new capability repos, registry entries, opencode.jsonc entries, knowledge entries, workflows, and meta-projects. Does NOT do project work, propose changes, or vote in the Conselho. Separation of duties: orchestrator proposes + Conselho delibera + capability-architect implements + delivery-reviewer validates. See `projects/_meta/capability-architect/binding-conditions.md` for the 16 binding conditions (R1–R5 + G1–G11; G10 + G11 added in the WDL v1 rollout, 2026-06-06). Created via `ADR-003` and LACOUNCIL proposal `2f42afe6-71d5-4ef8-a88a-1339d72ec501`.
- **workflow-decomposer** (subagent, BASIC → STABLE 2026-07-06). WDL v1 read-only PM layer that sits between the orchestrator and any specialist dispatch. Calls **only** `lacouncil.*` MCP tools (wall: WDL-R1). Emits three signed files per plan-id: `artifacts/wdl/<plan-id>/{analysis.md, plan.json, verdict.yaml}`. Verdict tri-state: `READY | DEFER | ESCALATE`. Stateless across plans. Cannot vote in the Conselho, cannot propose, cannot modify registry/AGENTS.md/knowledge/workflows. Self-attested verdicts fail G4 sign-off. Operating contract: `workflows/wdl-contract.yaml` (pinned `wdl_version: 1`). Charter: `.opencode/agent/workflow-decomposer.md`. Created via LACOUNCIL `a4fe9faa-4d50-4668-845a-ef64f1d41c36` + `7fd94c1a-d21d-49cc-a0e6-07c07c716e73` (both supermaioria 4/4 SIM, 2026-06-06).
- **debug-agent** (subagent, diagnostic). Read-only interactive debugger for the LAOS workspace. Dispatched only by the orchestrator for diagnostics, exploration, and debugging. Calls a subset of safe read-only bash commands (Get-ChildItem, Get-Content, Select-String, ls, cat, etc.) enforced by the WDL Gate. May also call any MCP for read-only diagnostics. **Never used in production delivery pipelines.** Output limited to `artifacts/debug/`. All debug artifacts carry frontmatter `debug: true` for P0-15 exemption (delivery-reviewer skips debug artifacts). Charter: `.opencode/agent/debug-agent.md`. Created via LACOUNCIL proposal `7fcc6cd5-37d2-40c0-a6ac-6a8ab59b3708` (supermaioria 4/4 SIM, 2026-06-19). Complementary to the `explore_filesystem` infra tool.
- **chief-data-scientist** (evaluator, empirical consensus). Evaluates candidate data/ML solutions on model fit (R², AIC), residual diagnostics, prediction accuracy, interpretability (SHAP), and robustness. Only activated in empirical consensus mode. Does NOT produce solutions — only evaluates. Charter: `.opencode/agent/chief-data-scientist.md`. Provenance: OmO adoption plan, 2026-06-09.
- **chief-designer** (evaluator, empirical consensus). Evaluates candidate design solutions on visual hierarchy, accessibility (WCAG 2.1 AA), DESIGN.md consistency, anti-slop signals, and interaction quality. Only activated in empirical consensus mode. Does NOT produce solutions — only evaluates. Charter: `.opencode/agent/chief-designer.md`. Provenance: OmO adoption plan, 2026-06-09.
- **chief-engineer** (evaluator, empirical consensus). Evaluates candidate engineering/automation solutions on reliability, SLA compliance, test coverage, performance, and operational readiness. Only activated in empirical consensus mode. Does NOT produce solutions — only evaluates. Charter: `.opencode/agent/chief-engineer.md`. Provenance: OmO adoption plan, 2026-06-09.

## Plugin architecture

OpenCode's native plugin system (`.opencode/plugins/*.ts`) is LAOS's mechanical enforcement layer. Plugins convert hard rules from **prompt-only** (LLM can ignore them) to **mechanical** (OpenCode blocks violations by throwing `Error` in `tool.execute.before`).

**Provenance:** OmO adoption plan (2026-06-09). Core insight: OmO optimizes agent-to-tool reliability; LAOS ports those reliability primitives into its governance framework. See `knowledge/omo-adoption-provenance.md` for the 15-feature source mapping.

### Active plugins (12)

| Plugin | File | Hard Rule(s) | Hook | What it blocks/detects |
|--------|------|-------------|------|---------------|
| **Guards** | `laos-guards.ts` | HR #1, #2, #11 | `tool.execute.before` | Implementation code writes in LAOS (*.sql, *.dax, *.pbix), `.env` read/write, synthetic data without frontmatter, orchestrator writing to artifact paths |
| **MCP Wall** | `laos-mcp-wall.ts` | HR #3 | `tool.execute.before` | Subagent calls MCP tools outside its namespace (e.g., data-architect calling `ladesign.*`) |
| **WDL Gate** | `laos-wdl-gate.ts` | HR #8 | `tool.execute.before` | Specialist `task` dispatch without READY verdict, enforces bypass penalties (-0.1/-0.3/-0.5) |
| **Dispatch** | `laos-dispatch.ts` | — (new feature) | Custom tool `laos-dispatch` | Provides sequential/parallel/consensus dispatch modes (see §Agentic Framework Modes) |
| **Continuation** | `laos-continuation.ts` | — (OmO pattern) | `session.idle` | 2s countdown → auto-inject next todo item; max 5 continuations per session, 5s cooldown |
| **Recovery** | `laos-recovery.ts` | — (OmO pattern) | `tool.execute.after` + `experimental.session.compacting` | 3 layers: structural error recovery, per-project state persistence (`.laos/state/`), context compaction preservation |
| **Fallback** | `laos-fallback.ts` | — (OmO pattern) | `tool.execute.after` + `chat.params` | Detects 429/500/502/503/timeout errors, switches to fallback model, configurable chain (max 3 attempts, 30s cooldown) |
| **Comment Checker** | `laos-comment-checker.ts` | — (advisory) | `tool.execute.after` | Detects AI slop patterns in net-new comments (advisory WARN, does not block) |
| **Intent Gate** | `laos-intent-gate.ts` | — (new feature) | `tool.execute.before` | Auto-injects needs-specific protocol snippets into specialist `task` dispatches; sentinel markers prevent double-injection |
| **Doctor** | `laos-doctor.ts` | — (diagnostic) | Custom tool `laos-doctor` | Holistic system diagnostic: 7 checks (system, config, plugins, MCP health, venvs, models, workspace) |
| **Plan Format Validator** | `laos-plan-format-validator.ts` | — (advisory) | `tool.execute.after` | Schema-validates WDL verdict.yaml and plan.json on write; warns on missing/invalid fields |
| **Format Guard** | `laos-format-guard.ts` | — (advisory) | `tool.execute.after` | Warns on trailing whitespace, missing final newline, mixed indentation, CRLF in .py/.sh/.yaml |

### Plugin API reference

```typescript
// Plugin format (OpenCode native):
export const PluginName = async ({ project, client, $, directory, worktree }) => {
  return {
    "tool.execute.before": async (input, output) => {
      // input: { tool, sessionID, callID }
      // output: { args } — mutable, changes flow to the tool
      // throw Error → BLOCKS the tool call
    },
    "tool.execute.after": async (input, output) => {
      // output.result is mutable — can transform tool results
      // return value replaces the output
    },
    "session.idle": async () => {
      // fires when the agent stops producing output
      // can inject continuation messages
    },
    "experimental.session.compacting": async (context) => {
      // fires before context compaction
      // return critical context that must survive compaction
    },
    tool: {
      myCustomTool: tool({
        description: "...",
        args: { /* schema */ },
        async execute(args, context) { /* ... */ },
      }),
    },
  }
}
```

### MCP Wall — agent-to-namespace mapping

| Agent | Allowed MCP namespaces | Blocked | Tool-level exceptions |
|-------|----------------------|---------|----------------------|
| orchestrator | all | (none — trust-based) | — |
| data-architect | `latade.*` | `lacouncil.*`, `ladesign.*`, `lan8n.*`, `laecon.*`, `laengine.*`, `n8n-community.*` | `lacouncil.register_vote`, `get_proposal`, `get_trust_scores`, `health`, `list_proposals`, `list_supported_operations` |
| dashboard-designer | `ladesign.*` | `lacouncil.*`, `latade.*`, `lan8n.*`, `laecon.*`, `laengine.*`, `n8n-community.*` | `lacouncil.register_vote`, `get_proposal`, `get_trust_scores`, `health`, `list_proposals`, `list_supported_operations` |
| automation-engineer | `lan8n.*`, `n8n-community.*` | `lacouncil.*`, `latade.*`, `ladesign.*`, `laecon.*`, `laengine.*` | `lacouncil.register_vote`, `get_proposal`, `get_trust_scores`, `health`, `list_proposals`, `list_supported_operations` |
| delivery-reviewer | all (read-only) | write operations (enforced by laos-guards) | — |
| capability-architect | `lacouncil.*`, `github.*` | `latade.*`, `ladesign.*`, `lan8n.*`, `laecon.*`, `laengine.*`, `n8n-community.*` | — |
| workflow-decomposer | `lacouncil.*` + platform MCPs | all domain MCPs (WDL-R1 wall) | — |
| chief-data-scientist | `latade.*` (read-only) | `ladesign.*`, `lan8n.*`, `laecon.*`, `laengine.*`, `lacouncil.*`, `n8n-community.*` | — |
| chief-designer | `ladesign.*` (read-only) | `latade.*`, `lan8n.*`, `laecon.*`, `laengine.*`, `lacouncil.*`, `n8n-community.*` | — |
| chief-engineer | `lan8n.*`, `latade.*` (read-only) | `ladesign.*`, `laecon.*`, `laengine.*`, `lacouncil.*`, `n8n-community.*` | — |
| debug-agent | all MCPs (read-only) + read-only bash | write operations (enforced by WDL Gate + laos-guards) | — |

> **Conselho voting exception (2026-06-12):** Domain subagents (`data-architect`, `dashboard-designer`, `automation-engineer`) are Conselho members and need `lacouncil.register_vote()` to deliberate. The MCP Wall blocks `lacouncil.*` at namespace level but whitelists these 6 specific tools via `allowedTools` in `laos-mcp-wall.ts`. All other `lacouncil.*` tools (`create_proposal`, `implement_proposal`, `investigate`, `record_project`, `detect_patterns`, `update_trust_score`, `tally_votes`) remain blocked — structural work is orchestrator-only.

**Known limitation:** OpenCode doesn't expose the active agent name in hook inputs. The MCP wall plugin uses an internal `_setAgent` API called by `laos-dispatch.ts` when dispatching specialists. If `_setAgent` hasn't been called, the wall falls back to permissive mode (logs warning, doesn't block).

## Agentic Framework Modes

Provenance: OmO Team Mode (`src/features/team-mode/`) + user requirement ("was a requisite for LAOS"). Three dispatch modes, selected via `laos-dispatch` tool or orchestrator decision.

### 1. Sequential (default, current LAOS behavior)

One specialist at a time. Each stage completes before the next begins. Use when: stages have hard dependencies (data model → dashboard → automation). This is the existing LAOS workflow — no change in behavior.

### 2. Parallel (new — OmO-style)

Multiple independent specialists run simultaneously using git worktrees. Architecture: lead (orchestrator) + 1-8 members (specialist subagents), each in their own worktree, coordinated via mailbox files.

**Protocol:**
1. Create worktrees: `git worktree add .worktrees/<name> -b <name>`
2. Each member works in their worktree independently
3. Members write status to mailbox: `.laos/mailbox/<worktree-name>`
4. Lead checks mailboxes on `session.idle` events
5. When all members signal "done", lead merges worktrees
6. Mailbox message format: `{ from, to, type: "status"|"artifact"|"blocker"|"done", payload, timestamp }`

**Use when:** deliverables are independent (data model + design can run in parallel). Example: `previsao-concursos` (9 needs, 4 capabilities — prime parallel candidate).

### 3. Consensus (new — two sub-modes)

#### 3a. Governance (LACOUNCIL voting)

The EXISTING LACOUNCIL governance flow, formalized as a first-class dispatch mode. Each Conselho member votes via `lacouncil.register_vote()`, tally determines outcome. Use for: structural decisions, registry changes, new capabilities.

#### 3b. Empirical (evaluator picks best)

N agents produce solutions independently, then a domain-specific evaluator picks the best. Use for: model selection, design comparison, engineering trade-offs.

**Protocol:**
1. Dispatch all candidates IN PARALLEL (they're independent)
2. Each candidate produces their solution independently
3. All solutions are collected and presented to the evaluator
4. Evaluator selects the best solution based on quantitative criteria
5. Winning solution is adopted; others are archived with rationale

**Evaluators:**

| Evaluator | Domain | Evaluation Criteria |
|-----------|--------|-------------------|
| `chief-data-scientist` | Data/ML | Model fit (R², AIC), residual diagnostics, prediction accuracy, interpretability (SHAP), robustness |
| `chief-designer` | Design/UX | Visual hierarchy, accessibility (WCAG 2.1 AA), DESIGN.md consistency, anti-slop signals, interaction quality |
| `chief-engineer` | Engineering/Automation | Reliability, SLA compliance, test coverage, performance, operational readiness |

Each evaluator scores candidates on 5 dimensions (0-10) with weighted totals. Evaluation is advisory — the orchestrator makes the final call but must justify any deviation.

## Workflow

```
projects/<name>/project.yaml (contract, lives in LAOS)
    ↓
orchestrator reads needs
    ↓
needs → capabilities (registry)
    ↓
workflow template (if matched) OR ad-hoc dispatch
    ↓
subagents write full results to detail files, return compact receipts
    ↓
delivery-reviewer validates against acceptance criteria + padroes-entrega.md
    ↓
if PASS → orchestrator commits + pushes for external evaluation
if FAIL → subagent fixes → back to delivery-reviewer
```

> **Compact result contract (LACOUNCIL dbc88097):** Subagents write
> full detailed results to `artifacts/<project>/reviews/<task-id>.md`
> and return ONLY a compact receipt to the orchestrator. Receipt schema:
> `{ status, summary (max 2 lines, actionable), details_path, task_id, error_class? }`.
> Orchestrator reads the receipt; drills into the detail file only when
> needed (error investigation, deeper verification, or user request).
> See `knowledge/subagent-result-contract.md` for full spec.

> **Hard rule:** Never push for external evaluation without delivery-reviewer approval. This is the first P0 check in `knowledge/padroes-entrega.md`.

### Your loop

The orchestrator's session loop, numbered for surface of enforcement:

1. **Read** `projects/<name>/project.yaml` and any brief context.
2. **Toolchain inventory** — run `.venv/Scripts/pythonw.exe scripts/toolchain_inventory.py`. Uses pythonw.exe (WINDOWS subsystem, sem console) para evitar flashing de janela. Se pythonw não estiver disponível, fallback `uv run python scripts/toolchain_inventory.py`. Output informs all subsequent planning (stack suggestions, dependency reuse). See `knowledge/stack-decisions.md` §"Toolchain inventory" and `knowledge/discover-before-build.md` §Fase 1.
3. **Resolve** needs via `registry/needs-to-capabilities.yaml`.
4. **Plan template** — if a workflow template matches, plan via template; else ad-hoc.
5. **Dispatch** specialist (data-architect, dashboard-designer, automation-engineer, capability-architect, or any future subagent).
6. **Validate** via `delivery-reviewer`.
7. **Push** per Git sync regime (Regime A or Regime B; never both).

#### Step 3a — WDL preflight gate (between step 3 and step 4)

WDL v1 (`a4fe9faa` + `7fd94c1a`) inserts a read-only PM step between
needs resolution and workflow template selection. **Mandatory** for
project work; **exempt** for the orchestrator's own `lacouncil.*`
structural improvement calls (Hard Rule 8.4).

```yaml
# Dispatch payload to workflow-decomposer:
plan_id: <uuid>           # unique per plan; orchestrator generates
project: <name>           # the project being decomposed
needs: [...]              # resolved from step 2
brief_context: ...        # user prompt + project.yaml + relevant files
prior_verdicts: []        # any prior DEFER/ESCALATE verdicts
exemption:                # only if simple_task_exemption applies
  applied: bool
  reason: string
  signals_evaluated: [...]
```

The workflow-decomposer returns a signed verdict (tri-state) at
`artifacts/wdl/<plan-id>/verdict.yaml`. Specialist dispatch in step 4
**requires** a `state: READY` verdict with `verified_by: <agente_id>`
populated (Hard Rule 8.1; preflight `check_wdl_gate` (b)).

**`dispatch_payload_includes`** (Hard Rule 8.4 clarification): the
specialist dispatch payload must carry `[verdict.yaml, plan_id,
verified_by]` forward from the workflow-decomposer output. The
specialist subagent uses these to scope its own work and to log
which plan produced the dispatch.

**Bypass** (Hard Rule 8.3): if the orchestrator proceeds without a
READY verdict, it must (a) record `bypass-manifest.yaml` with
`reason`, `alternative_dispatch_path`, `user_confirmed_at`,
`dispatch_at`; (b) obtain user confirmation; (c) pay the trust-score
penalty (`-0.1/-0.3/-0.5` per 8.2).

#### Conselho Governance Exemption (LACOUNCIL 726be80b)

When the orchestrator dispatches specialists for Conselho voting (structural improvement governance), the WDL preflight gate does NOT apply. This exemption is consistent with Hard Rule 8.4 (exemption scope for lacouncil.* structural work).

**Conditions:**
- `dispatch_type: "CONSELHO_GOVERNANCE"` in the `task` tool args
- `subagentType` is a Conselho member (`data-architect`, `dashboard-designer`, `automation-engineer`, `delivery-reviewer`)

**Why no penalty:**
The trust-score penalty exists to discourage bypassing the WDL gate for **project work**. Conselho voting is **not project work** — it's the governance layer's own operations. Penalizing the orchestrator for legitimate governance dispatch defeats the purpose.

**Precedent:**
- Hard Rule 8.4 (exemption scope for lacouncil.* structural work)
- MCP Wall Conselho voting exception (laos-mcp-wall.ts lines 53-60)
- Existing bypass manifest `governance-bypass-3473c12b` (which documented this exact issue)

### LACOUNCIL (structural improvement) workflow

```
Project pattern detected (3+ occurrences) OR improvement identified
    ↓
LAOS calls LACOUNCIL.investigate() → 5 Whys + Fishbone
    ↓
LACOUNCIL.create_proposal() → proposal in DuckDB
    ↓
Conselho convoked (each subagent votes via LACOUNCIL.register_vote())
    ↓
LACOUNCIL.tally_votes() per conselho.yaml strategy
    ↓
If approved → LACOUNCIL.implement_proposal() → meta-project or diff
    ↓
LAOS applies change, delivery-reviewer validates
```

> **Pipeline completo:** Conselho → implementação → preflight → reviewer → 
> iteração → commit → push. Ver `workflows/structural-change-pipeline.yaml` 
> para o workflow declarativo com cláusula de iteração obrigatória e 
> referências em `registry/workflows.yaml`.

## Child project repositories (per project)

Every project is born as its own GitHub repository. LAOS does not modify itself to host project artifacts; the project repo evolves on its own timeline.

| Lives in LAOS (this repo) | Lives in the child project repo |
| -------------------------------- | ------------------------------------------ |
| `projects/<name>/project.yaml` | All artifacts: data models, dashboards, |
| (contract: brief, needs, | LAN8N flows, design tokens, snapshots, ADRs, |
| deliverables, child repo URL) | the project's own README |
| Knowledge entries produced by | Issue tracker, releases, branches |
| the project (promoted after the | |
| fact into `knowledge/`) | |
| Registry updates triggered by | |
| the project (new capabilities | |
| added to `registry/`) | |

The orchestrator knows the child repo URL through the `repo:` field in `project.yaml`. Subagents interact with the child repo via the `github` MCP (or by `git push` through `bash` when the capability MCP doesn't yet cover a specific write). The `delivery-reviewer` clones the child repo, validates every deliverable against `knowledge/padroes-entrega.md`, and writes the sign-off back into the child repo's `review/` folder.

## When evolving LAOS

- New capability → add entry in `registry/capabilities.yaml` and a routing rule in `needs-to-capabilities.yaml`. Add MCP config in `.opencode/opencode.jsonc`. (Requires Conselho supermajority.)
- New project archetype → add a workflow template in `workflows/`. (Requires Conselho majority.)
- New cross-cutting convention → add to `knowledge/`. NEVER duplicate from a capability repo's own knowledge. (Conselho majority.)
- New child project → the `github` MCP creates its repo. The contract `projects/<name>/project.yaml` here stays the source of truth for the orchestrator; everything else lives in the child repo.
- Structural improvement → the orchestrator (via LACOUNCIL) creates a proposal, convokes the Conselho, implements if approved, logs to DuckDB memory (via LACOUNCIL MCP tools).

## Git sync regime (LACOUNCIL 391a8179)

Two distinct regimes govern when LAOS changes reach GitHub:

### Regime A — Structural changes (mandatory push)

Changes approved by the Conselho and validated by delivery-reviewer (G4 BASIC or G8 STABLE sign-off) **must** be committed and pushed to GitHub within the same session. This covers changes made by the capability-architect **or** by the orchestrator directly (e.g., editing `AGENTS.md`, `knowledge/`, `registry/`) when implementing a LACOUNCIL proposal. The authority chain is complete: Conselho approved → reviewer validated → no additional gate needed.

### Regime B — Domain project artifacts (gated push)

Domain artifacts (data models, dashboards, n8n workflows, design deliverables) follow the existing rule: push only after delivery-reviewer approval **and** user confirmation. This is P0 in `knowledge/padroes-entrega.md`.

### How to distinguish

If the change was motivated by a LACOUNCIL proposal → Regime A.
If the change is project deliverable output → Regime B.
When in doubt, ask the user.

## Commands

- `/new-project` - scaffold a project from a workflow template.
- `/list-capabilities` - print the active capability registry.
