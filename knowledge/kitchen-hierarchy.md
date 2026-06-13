# Kitchen Hierarchy Pattern

Agent routing pattern inspired by restaurant kitchen operations.
Transversal to all LAOS agents. Source: LACOUNCIL `612b1cf0`
(approved 4/4 SIM, maioria, 2026-06-13).

## Core principle

**Agents do their tasks with confidence. Orchestrator trusts specialists.**

The WDL gate enforces a flawless path for agents:
- Routine actions → just do
- Cleanup actions → just do
- Obviously bad actions → block
- Uncertain actions → route to specialist
- **Never ask user**

## Confidence levels

| Action Type | Example | Behavior |
|-------------|---------|----------|
| **Routine** | git push (20th time) | Just do. Built confidence from repetition. |
| **Cleanup** | Delete .pyc files | Just do. Obviously safe. |
| **Obviously bad** | Delete Windows folder | Block. No specialist. User would never approve. |
| **Uncertain** | Postgres vs SQLite | Route to specialist. Never ask user. |
| **New task** | First time task | Route to specialist. |

## Agent hierarchy

| Role | Agent | When to Use |
|------|-------|-------------|
| Chef | orchestrator | Route, plan, trust specialists |
| Sous chef | data-architect | Data modeling, SQL, ETL |
| Sous chef | dashboard-designer | Design systems, decks, wireframes |
| Sous chef | automation-engineer | Integrations, workflows, alerts |
| Support | delivery-reviewer | Validate artifacts (read-only) |
| Support | workflow-decomposer | Plan and decompose tasks (read-only) |
| Support | capability-architect | Structural changes (registry, knowledge) |

## Routine patterns (just do)

These are allowed without question:
- `git add` — version control
- `git commit` — version control
- `git push` — version control (routine after 3-5 uses)
- `git pull` — version control
- `git status` — version control
- `git log` — version control
- `git diff` — version control
- `uv sync` — Python toolchain
- `uv run` — Python toolchain
- `npx` — Node toolchain
- `python` — Python execution

## Cleanup patterns (just do)

Obviously safe, just do:
- `*.pyc` — Python bytecode
- `__pycache__/` — Python cache
- `*.tmp` — Temporary files
- `*.log` — Log files
- `node_modules/.cache` — Node cache
- `.venv/lib` — Python venv libs
- `dist/` — Build artifacts
- `build/` — Build artifacts

## Obviously bad actions (block)

No specialist for these. User would never approve:
- Delete Windows system folders
- `rm -rf /` — Root deletion
- `del /s /` — Windows system deletion
- `DROP DATABASE` — Production database without backup
- `DROP TABLE` — Table deletion without backup

## WDL gate decision tree

```
Action requested
    ↓
Is it agent dispatch (task tool)? → YES → ALLOW
    ↓ NO
Is it MCP tool (ladesign, latade, lan8n)? → YES → ALLOW
    ↓ NO
Is it file tool (read, write, glob)? → YES → ALLOW
    ↓ NO
Is it research tool (context7, exa)? → YES → ALLOW
    ↓ NO
Is it GitHub MCP? → YES → ALLOW
    ↓ NO
Is it toolchain (git, uv, npx, python)? → YES → ALLOW
    ↓ NO
Is it bash?
    ↓
    Is it obviously bad (windows, rm -rf /, DROP)? → BLOCK
    ↓ NO
    Is it routine pattern (git push, uv run)? → ALLOW (just do)
    ↓ NO
    Is it cleanup pattern (*.pyc, __pycache__)? → ALLOW (just do)
    ↓ NO
    → Route to specialist (never ask user)
```

## User interaction

**Orchestrator NEVER asks user for:**
- Which path to take
- Which agent to use
- Whether to dispatch
- Whether to use shell
- Any implementation decision

**The only time user is informed:**
- Project status updates
- Deliverables complete
- Blockers (not implementation choices)

## Example flows

### Git push (routine)
```
git push → ALLOW (routine pattern) → DONE
User: never asked
```

### Delete temp files (cleanup)
```
rm *.pyc → ALLOW (cleanup pattern) → DONE
User: never asked
```

### Delete Windows folder (obviously bad)
```
rm -rf C:\Windows → BLOCK → "Obviously bad action"
User: never asked, task blocked
```

### Postgres vs SQLite (uncertain)
```
"Which database?" → route to data-architect → data-architect decides
User: never asked
```

## Tool priority

| Task Type | Primary Agent | Fallback |
|-----------|---------------|----------|
| Data operations | data-architect | — |
| Design operations | dashboard-designer | — |
| Automation operations | automation-engineer | — |
| Governance operations | orchestrator | lacouncil |
| File operations | orchestrator | — |

## Cross-references

- LACOUNCIL proposal: `612b1cf0-9d6e-4652-a301-b81d804949b9`
- Agent charters: `data-architect.md`, `dashboard-designer.md`, `automation-engineer.md`
- Orchestrator routing: `orchestrator.md` §"Routing table and refusal handling"