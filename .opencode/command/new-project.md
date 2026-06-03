---
description: Scaffold a new LAOS project under projects/<name>/ using an optional workflow template.
---

You are creating a new project. Follow this exact procedure:

1. **Get the project name** from the user's invocation, e.g.
   `/new-project dashboard-financeiro`. If absent, ask once.

2. **Get the workflow** from `--workflow <name>` if present. If absent,
   list available workflows under `workflows/*.yaml` and ask the user
   to pick one, or to skip workflow (ad-hoc project).

3. **Verify uniqueness.** Check that `projects/<name>/` does not exist.
   If it does, abort and tell the user.

4. **Create the project directory** and a starter `project.yaml`:

```yaml
name: <name>
description: <one-line description prompted from user>
workflow: <workflow-name or null>
external_delivery: false      # set true if the artifact ships outside

needs:
  # Pulled from the workflow's `needs:` block if a workflow was chosen.
  # Otherwise ask the user which needs apply.
  - <need-1>
  - <need-2>

deliverables:
  # Copied from the workflow's `deliverables:` block.
  - <path>

inputs:
  # Workflow-defined inputs with placeholder values for the user to fill.
```

5. **Create the artifacts subtree** matching the workflow stages:
   `projects/<name>/artifacts/discovery/`, `data/`, `design/`,
   `automation/`, `review/` (only the ones the workflow uses).

6. **Validate every `need:` against `registry/needs-to-capabilities.yaml`.**
   If any need has no routing rule, stop. Ask the user to add the rule
   to the registry before continuing.

7. **Print a summary** of what was created, including the next command
   the user should run (typically asking the orchestrator to execute
   the first stage of the workflow).

Alternative: the user can run `uv run python scripts/bootstrap_project.py
<name> --workflow <workflow>` for the same effect non-interactively.

Do NOT execute any workflow stage as part of this command. This command
only scaffolds.
