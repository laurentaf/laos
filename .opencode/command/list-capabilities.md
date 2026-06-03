---
description: Print the active capability registry with status, MCP server name, and ownership.
---

Read `registry/capabilities.yaml` and print a compact table:

```
ID              KIND      MCP             STATUS    OWNS
─────────────── ───────── ─────────────── ───────── ─────────────────────────
latade          domain    latade          stub      sql.*, data.*, bi.*
lan8n           domain    lan8n           stub      automation.*, integration.*
ladesign         domain    ladesign        external  design.*, presentation.*, video.*
context7        platform  context7        external  docs.*
exa             platform  exa             external  web.*
github          platform  github          external  github.*
...
```

Then, for any capability with `status: stub`, add a one-line note
about what needs to happen to promote it (typically: create the real
repo and point opencode.jsonc at its MCP server).

Then, read `.opencode/opencode.jsonc` and print which MCPs are
currently `enabled: false`. Note that an `enabled: false` MCP cannot
be used by subagents until toggled on.

Equivalent non-interactive command:
  uv run python scripts/list_capabilities.py

Do not write anything. This is read-only output for the user.
