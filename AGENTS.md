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

## Repository layout

```
LAOS/
├── .opencode/           opencode config, agents, commands, skills
├── lacouncil/           structural improvement support (SDD, propostas)
├── registry/            capability catalog + needs->capability routing
├── workflows/           declarative templates that compose capabilities
├── knowledge/           ONLY transversal knowledge (glossary, delivery patterns)
├── projects/            contract index: one project.yaml per project
│   ├── <name>/          domain projects
│   └── _meta/           meta-projects (LAOS improving itself)
├── capabilities-stubs/  starter MCP servers until real ones ship
├── scripts/             CLI helpers (bootstrap, list, sync)
├── pyproject.toml       local Python venv deps (mcp[cli], pyyaml)
├── setup.ps1            first-run setup
├── lacouncil.yaml       structural improvement config (LACOUNCIL MCP)
└── AGENTS.md            this file
```

## Capability repositories

Each repo is a **capability**, not a project. LAOS composes these capabilities — it never owns domain implementation.

| Repo | Domain | Capability name | MCP server | Role |
| ---- | ------ | --------------- | ---------- | ---- |
| `../latade` | Data | **LATADE** | `latade` | SQL, modeling, BI, DQ, docs |
| `../lan8n` | Automation | **LAN8N** | `lan8n` | Workflows, integrations, APIs, alerts |
| `../ladesign` | Design | **LADESIGN** | `ladesign` | Dashboards, decks, wireframes, design systems, video |
| `../lacouncil` | Improvement | **LACOUNCIL** | `lacouncil` | Investigation, proposals, voting, patterns |
| `../laengine` | Game Dev | **LAENGINE** | `laengine` | Sports simulation, match engine, squad management |

> **Naming note:** The folder names (`../lan8n`, `../ladesign`) pre-date
> the capability naming convention. The capability names — LATADE, LAN8N,
> LADESIGN — are the canonical identifiers; the folder paths are legacy
> shortcuts.

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
subagents push artifacts to the project's child GitHub repo
    ↓
delivery-reviewer validates against acceptance criteria + padroes-entrega.md
    ↓
if PASS → orchestrator commits + pushes for external evaluation
if FAIL → subagent fixes → back to delivery-reviewer
```

> **Hard rule:** Never push for external evaluation without delivery-reviewer approval. This is the first P0 check in `knowledge/padroes-entrega.md`.

### Your loop

The orchestrator's session loop, numbered for surface of enforcement:

1. **Read** `projects/<name>/project.yaml` and any brief context.
2. **Resolve** needs via `registry/needs-to-capabilities.yaml`.
3. **Plan template** — if a workflow template matches, plan via template; else ad-hoc.
4. **Dispatch** specialist (data-architect, dashboard-designer, automation-engineer, capability-architect, or any future subagent).
5. **Validate** via `delivery-reviewer`.
6. **Push** per Git sync regime (Regime A or Regime B; never both).

#### Step 2a — WDL preflight gate (between step 2 and step 3)

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

## Git sync regime (LACOUNCIL 391a8179)

Two distinct regimes govern when LAOS changes reach GitHub:

### Regime A — Structural changes (mandatory push)

Changes approved by the Conselho and validated by delivery-reviewer
(G4 BASIC or G8 STABLE sign-off) **must** be committed and pushed to
GitHub within the same session. This covers changes made by the
capability-architect **or** by the orchestrator directly (e.g., editing
`AGENTS.md`, `knowledge/`, `registry/`) when implementing a LACOUNCIL
proposal. The authority chain is complete: Conselho approved →
reviewer validated → no additional gate needed.

### Regime B — Domain project artifacts (gated push)

Domain artifacts (data models, dashboards, n8n workflows, design
deliverables) follow the existing rule: push only after
delivery-reviewer approval **and** user confirmation. This is P0 in
`knowledge/padroes-entrega.md`.

### How to distinguish

If the change was motivated by a LACOUNCIL proposal → Regime A.
If the change is project deliverable output → Regime B.
When in doubt, ask the user.

## Commands

- `/new-project` - scaffold a project from a workflow template.
- `/list-capabilities` - print the active capability registry.
