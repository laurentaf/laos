# _example

Reference project used by LAOS for end-to-end testing. The
`/new-project` command and `bootstrap_project.py` both rely on this
shape to validate the wiring.

## How LAOS stores a project

A project has two homes:

1. **Contract** — this folder (`LAOS/projects/<name>/project.yaml`).
   Holds `name`, `description`, `workflow`, `needs:`, `deliverables:`
   and the child repo URL. The orchestrator reads this.
2. **Child repository** — declared in `repo:` (e.g. `laurentaf/_example`).
   Holds every artifact, snapshot, ADR and the project's own README.
   Subagents push to it; `delivery-reviewer` clones it to validate.

LAOS itself never stores domain artifacts. If you see SQL, dashboard
markup, n8n JSON, design tokens, etc. inside `LAOS/projects/<name>/`,
it belongs in the child repo instead.

## How to use

1. Copy this folder:
   `cp -r projects/_example projects/<your-name>`
2. Edit `project.yaml`:
   - Set `repo:` to the GitHub repo that will hold the artifacts
     (or let the orchestrator create it via the `github` MCP).
   - Replace `description` and add/remove items from `needs:` and
     `deliverables:` (paths are relative to the child repo root).
3. Ask the orchestrator to execute the workflow. It will:
   - Validate the `needs:` against `registry/needs-to-capabilities.yaml`.
   - Create the child repo if it doesn't exist.
   - Walk the stages in `workflows/dashboard-completo.yaml`,
     dispatching the right subagent per stage.
   - Each subagent pushes its artifacts to the child repo.
4. `delivery-reviewer` clones the child repo, validates against
   `knowledge/padroes-entrega.md`, and writes the sign-off into
   the child repo's `review/` folder.

## Delete me

This folder exists only as a reference. Once you have a real
project, feel free to `rm -rf projects/_example` (the `registry/`,
`workflows/` and `AGENTS.md` references are not file paths into
this folder).
