# LAOS - Laurent Agent Operating System

Personal agent orchestration layer. Composes domain capabilities
(LATADE, LADESIGN, LAN8N, LACOUNCIL, LAENGINE) into declarative projects.

## What this is (and isn't)

- **Is**: an orchestrator. Holds project specs, workflow templates, a
  capability registry, and opencode agent definitions.
- **Is not**: an implementation. No SQL, no dashboards, no LAN8N flows
  live here. Those live in their respective capability repos and are
  reached exclusively via MCP.

Read `AGENTS.md` for the architectural rules. Do not bypass them.

## Layout

```
E:\Projects\
├── LAOS\                   ← this repo (orchestrator)
├── latade\                 ← data capability  · LATADE
├── lan8n\                  ← automation capability · LAN8N
├── ladesign\               ← design capability · LADESIGN
├── lacouncil\              ← improvement capability · LACOUNCIL
└── laengine\               ← game dev capability · LAENGINE
```

LAOS expects siblings. If you keep capability repos elsewhere, edit the
relative paths in `.opencode/opencode.jsonc` and `registry/capabilities.yaml`.

## First-run setup

```powershell
# From E:\Projects\LAOS
pwsh .\setup.ps1
```

That script:
1. Runs `uv sync` to create a local `.venv` with `mcp[cli]` and `pyyaml`.
2. Copies `.env.example` to `.env` if missing.
3. Verifies the three sibling capability repos are present.

After setup, launch opencode from this folder:

```powershell
opencode
```

## MCP servers wired in

**Domain capabilities:**

| Server          | Capability  | Source                                                 | Default | Env |
| --------------- | ----------- | ------------------------------------------------------ | ------- | --- |
| `latade`        | **LATADE**  | `..\latade\.venv\Scripts\python ..\latade\mcp\server.py` | enabled | - |
| `lan8n`         | **LAN8N**   | `uv run python capabilities-stubs/lan8n-mcp/server.py` (*stub*) | enabled | - |
| `lacouncil`     | **LACOUNCIL**| `..\lacouncil\.venv\Scripts\python ..\lacouncil\mcp\server.py` | enabled | `LACOUNCIL_DB_PATH` |
| `laengine`      | **LAENGINE** | `uv run python ../laengine/src/laengine/mcp/server.py` | enabled | - |
| `n8n-community` | n8n raw API | npm `n8n-mcp` (local n8n on :5678)                    | disabled | `N8N_API_KEY` |
| `ladesign`      | **LADESIGN** | `od mcp serve` (requer `od` CLI) + skills em `../ladesign/skills/` | disabled | - |

**Platform capabilities:**

| Server     | Source                                       | Default | Env |
| ---------- | -------------------------------------------- | ------- | --- |
| `context7` | remote `https://mcp.context7.com/mcp`        | enabled | - (optional `CONTEXT7_API_KEY`) |
| `exa`      | remote `https://mcp.exa.ai/mcp` (OAuth)      | enabled | - (browser auth on first use) |
| `github`   | remote `https://api.githubcopilot.com/mcp/`  | enabled | `GITHUB_TOKEN` from **OS env** |

### Notes per server

- **LATADE**: server real em `../latade/mcp/server.py`. 7 ferramentas disponíveis:
  `execute_sql` (DuckDB), `load_csv_to_bronze`, `run_silver_dedup`,
  `run_gold_aggregation`, `validate_data_safety`, `generate_schema_preview`,
  `inspect_table`. Pipeline medallion (bronze → silver → gold).

- **LAN8N**: servidor **stub** (placeholder) em `capabilities-stubs/lan8n-mcp/server.py`.
  O server real ainda não foi implementado em `../lan8n/mcp/server.py`.
  O stub responde `health` e `list_supported_operations` com status "planned".

- **LACOUNCIL**: server real em `../lacouncil/mcp/server.py`. 10 ferramentas:
  `health`, `investigate` (5 Whys + Fishbone), `create_proposal`, `get_proposal`,
  `list_proposals`, `register_vote`, `tally_votes`, `implement_proposal`,
  `record_project`, `detect_patterns`. Backend DuckDB em `memoria/lacouncil.duckdb`.

- **LAENGINE**: server real em `../laengine/src/laengine/mcp/server.py`.
  7 ferramentas de simulação esportiva: `generate_seed`, `get_teams`,
  `get_team_players`, `generate_schedule`, `simulate_next_round`,
  `simulate_all_rounds`, `get_standings`. Motor Brasfoot.

- **LADESIGN**: o MCP server (`od mcp serve`) está **disabled** porque o CLI `od`
  não está instalado. Porém, as **skills visuais** em `../ladesign/skills/` são
  carregadas ativamente via `skills.paths` no `opencode.jsonc`. O
  `dashboard-designer` pode usar as skills mesmo sem o MCP server ativo.

- **n8n-community** (local n8n self-hosted): kept off until you have
  n8n running. Steps:
  1. `npx n8n` in a separate terminal.
  2. Open http://localhost:5678 and create the owner account.
  3. Settings > n8n API > enable and create an API key.
  4. Paste the key into `.env` as `N8N_API_KEY`.
  5. Set `"enabled": true` for the `n8n-community` MCP in `opencode.jsonc`.

- **exa**: OAuth-based remote MCP. No key. opencode will open a
  browser the first time the server is called. Manage your account
  at https://dashboard.exa.ai.

- **github**: reads `GITHUB_TOKEN` from your OS environment, not from
  `.env`. Set it once at the OS level so every project benefits.

## Project repositories (children)

A project has **two homes**:

1. **Contract** — `projects/<name>/project.yaml` here in LAOS. Holds
   the brief, `needs:`, `deliverables:` and the child repo URL.
2. **Child repository** — declared in `project.yaml` as `repo:`.
   Holds every artifact, snapshot, ADR and the project's own README.

The orchestrator creates the child repo at kickoff (via the
`github` MCP) and dispatches subagents that push to it. The
`delivery-reviewer` clones the child repo to validate, but the
checklist itself lives here in `knowledge/padroes-entrega.md`.

## Files you will touch most

- `registry/capabilities.yaml` - when a new capability comes online.
- `registry/needs-to-capabilities.yaml` - when routing a new abstract need.
- `workflows/*.yaml` - when defining a new project archetype.
- `projects/<name>/project.yaml` - the contract of every new project.
  (Artifacts go in the child repo, not here.)

## Files you should rarely touch

- `.opencode/agent/*.md` - subagent definitions. Stable.
- `.opencode/opencode.jsonc` - only when wiring a new MCP or permission rule.
- `knowledge/*.md` - only for genuinely transversal conventions.

## Files that should never exist here

- Any `.sql`, `.pbix`, `.dax`, `.dbt` file.
- Any LAN8N workflow JSON.
- Any dashboard markup, design system tokens, or component code.
- Any project artifact, snapshot, or ADR under `projects/<name>/`.

If you catch yourself adding one of those, the right home is
either a capability repo (for tooling-level artifacts) or the
project's child repository (for project-level artifacts). LAOS
holds the contract and the memory, nothing else.
