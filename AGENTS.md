# LAOS - Laurent Agent Operating System

LAOS is an **orchestration layer**. It contains no domain implementation.
All domain knowledge lives in capability repositories exposed via MCP.

## Hard rules

1. **Never put implementation code in LAOS.** SQL, dashboards, n8n
   workflows belong in the     capability repo (LATADE, LADESIGN, LAN8N),
   exposed through its MCP server. If you find yourself writing them
   here, stop.
2. **Projects live in their own GitHub repository.** A project is
   a `project.yaml` contract mirrored here in `projects/<name>/`
   (brief, needs, deliverables, child repo URL), plus a sibling
   repository `laurentaf/<project-name>` (or under an org) where
   all artifacts, code, snapshots and ADRs are produced. **LAOS
   never stores domain artifacts.** If you find yourself writing
   SQL, dashboard markup, n8n JSON, or any other implementation
   inside `LAOS/projects/<name>/`, it belongs in the child repo.
3. **Capabilities are reached only through MCP.** Never `cd ../latade`
   and execute a script. Call the MCP tool. If the tool is missing,
   add it to the capability repo's server, not to LAOS.
4. **Routing is deterministic.** `registry/needs-to-capabilities.yaml`
   maps abstract needs to concrete MCP capabilities. The orchestrator
   follows the map; it does not invent capability selection on its own.

## Repository layout

```
LAOS/
├── .opencode/              opencode config, agents, commands, skills
├── registry/               capability catalog + needs->capability routing
├── workflows/              declarative templates that compose capabilities
├── knowledge/              ONLY transversal knowledge (glossary, delivery patterns)
├── projects/               contract index: one project.yaml per project
│                           (artifacts live in each project's child repo)
├── capabilities-stubs/     starter MCP servers until real ones ship
├── scripts/                CLI helpers (bootstrap, list, sync)
├── pyproject.toml          local Python venv deps (mcp[cli], pyyaml)
├── setup.ps1               first-run setup
└── AGENTS.md               this file
```

## Capability repositories (the three pillars)

Each repo is a **capability**, not a project. LAOS composes these three
pillars — it never owns domain implementation.

| Repo | Domain | Capability name | MCP server | Role |
| ---- | ------ | --------------- | ---------- | ---- |
| `../latade` | Data | **LATADE** | `latade` | SQL, modeling, BI, DQ, docs |
| `../lan8n` | Automation | **LAN8N** | `lan8n` | Workflows, integrations, APIs, alerts |
| `../ladesign` | Design | **LADESIGN** | `ladesign` | Dashboards, decks, wireframes, design systems, video |

> **Naming note:** The folder names (`../lan8n`, `../ladesign`) pre-date
> the capability naming convention. The capability names — LATADE, LAN8N,
> LADESIGN — are the canonical identifiers; the folder paths are legacy
> shortcuts.

Platform MCPs (cross-cutting, used by any subagent):

- `context7` - fetch current library/API docs instead of hallucinating.
- `exa` - web search and page extraction. Remote OAuth.
- `github` - repos, issues, PRs, code search. Reads GITHUB_TOKEN from OS env.

## Agent topology

- **orchestrator** (primary, default). Owns the session. Reads
  project.yaml, resolves needs via the registry, dispatches subagents.
- **data-architect** (subagent). Talks only to `latade.*` MCP tools.
- **dashboard-designer** (subagent). Talks only to `ladesign.*` MCP
  tools and the LADESIGN skill library.
- **automation-engineer** (subagent). Talks only to `lan8n.*` and
  optionally `n8n-community.*` MCP tools.
- **delivery-reviewer** (subagent). Read-only. Validates artifacts
  against `knowledge/padroes-entrega.md`.

## Workflow

```
projects/<name>/project.yaml  (contract, lives in LAOS)
   ↓
orchestrator reads needs
   ↓
needs → capabilities (registry)
   ↓
workflow template (if matched) OR ad-hoc dispatch
   ↓
subagents push artifacts to the project's child GitHub repo
   ↓
delivery-reviewer clones the child repo, validates, signs off
```

## Child project repositories (per project)

Every project is born as its own GitHub repository. LAOS does not
modify itself to host project artifacts; the project repo evolves
on its own timeline.

| Lives in LAOS (this repo)        | Lives in the child project repo            |
| -------------------------------- | ------------------------------------------ |
| `projects/<name>/project.yaml`   | All artifacts: data models, dashboards,    |
| (contract: brief, needs,         | LAN8N flows, design tokens, snapshots, ADRs, |
| deliverables, child repo URL)    | the project's own README                   |
| Knowledge entries produced by    | Issue tracker, releases, branches          |
| the project (promoted after the  |                                          |
| fact into `knowledge/`)          |                                          |
| Registry updates triggered by    |                                          |
| the project (new capabilities    |                                          |
| added to `registry/`)            |                                          |

The orchestrator knows the child repo URL through the `repo:`
field in `project.yaml`. Subagents interact with the child repo
via the `github` MCP (or by `git push` through `bash` when the
capability MCP doesn't yet cover a specific write). The
`delivery-reviewer` clones the child repo, validates every
deliverable against `knowledge/padroes-entrega.md`, and writes
the sign-off back into the child repo's `review/` folder.

## When evolving LAOS

- New capability → add entry in `registry/capabilities.yaml` and a
  routing rule in `needs-to-capabilities.yaml`. Add MCP config in
  `.opencode/opencode.jsonc`.
- New project archetype → add a workflow template in `workflows/`.
- New cross-cutting convention → add to `knowledge/`. NEVER duplicate
  from a capability repo's own knowledge.
- New child project → the `github` MCP creates its repo. The contract
  `projects/<name>/project.yaml` here stays the source of truth for
  the orchestrator; everything else lives in the child repo.

## Commands

- `/new-project` - scaffold a project from a workflow template.
- `/list-capabilities` - print the active capability registry.
