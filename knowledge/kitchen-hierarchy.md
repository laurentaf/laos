# Kitchen Hierarchy Pattern

Agent routing pattern inspired by restaurant kitchen operations.
Transversal to all LAOS agents. Source: LACOUNCIL `612b1cf0`
(approved 4/4 SIM, maioria, 2026-06-13).

## Core principle

**Tasks are DONE, not blocked. Orchestrator routes, never asks.**

Like a restaurant kitchen, the orchestrator (chef) routes tasks to the
right agent (sous chef) without asking the customer (user).

## The 5-step routing logic (automatic)

```
1. Task arrives
   ↓
2. Orchestrator identifies specialist (data-architect, dashboard-designer, etc.)
   ↓
3. Dispatch to specialist — NEVER asks user
   ↓
4. Specialist does the work — never blocked
   ↓
5. Orchestrator routes next task — never asks user
```

**No general agents.** Every task goes to the right specialist.

## Agent hierarchy

| Role | Agent | When to Use |
|------|-------|-------------|
| Chef | orchestrator | Route, plan, dispatch specialists |
| Sous chef | data-architect | Data modeling, SQL, ETL |
| Sous chef | dashboard-designer | Design systems, decks, wireframes |
| Sous chef | automation-engineer | Integrations, workflows, alerts |
| Support | delivery-reviewer | Validate artifacts (read-only) |
| Support | workflow-decomposer | Plan and decompose tasks (read-only) |
| Support | capability-architect | Structural changes (registry, knowledge) |

## WDL gate — Tasks done, not blocked

### Core principle

**Tasks are DONE. Orchestrator routes. User is never asked.**

### What WDL NEVER does

- ❌ Ask user "which path?"
- ❌ Ask user "shell or agent?"
- ❌ Ask user "should I dispatch?"
- ❌ Block agent dispatch
- ❌ Block specialist work
- ❌ Create decision paralysis

### What WDL ALWAYS allows

- ✅ Agent dispatch (`task` tool) — always, never blocked
- ✅ Specialist work — never blocked
- ✅ MCP tools — never blocked
- ✅ File tools for orchestrator — never blocked
- ✅ Research tools — never blocked
- ✅ GitHub MCP — never blocked
- ✅ Toolchain (git, uv, npx, python) — never blocked

### What WDL blocks

- 🚫 Shell calls that bypass agents (except toolchain)
- 🚫 Direct implementation by orchestrator (should dispatch instead)

### Shell handling

Shell blocked → orchestrator routes to specialist → task done

Never: "Should I use shell?" → user says no → task blocked

Always: Shell blocked → orchestrator finds specialist → task done

### Toolchain exemptions (always allowed)

These are infrastructure, not implementation:
- `git *` — version control
- `uv *` — Python toolchain
- `npx *` — Node toolchain
- `python *` — Python execution

## Tool priority hierarchy

| Task Type | Primary Agent | Tool Priority |
|-----------|---------------|---------------|
| Data operations | data-architect | `latade.*` → file tools → BLOCK shell |
| Design operations | dashboard-designer | `ladesign.*` → file tools → BLOCK shell |
| Automation operations | automation-engineer | `lan8n.*` → file tools → BLOCK shell |
| Governance operations | orchestrator | `lacouncil.*` → file tools |
| File operations | orchestrator | file tools (never shell) |

## User interaction limits

**Orchestrator NEVER asks user for:**
- Which path to take
- Which agent to use
- Whether to dispatch
- Whether to use shell
- Any implementation decision

**Orchestrator ONLY informs user of:**
- Project status
- Deliverables complete
- Blockers requiring user decision (not implementation choices)

## Role boundaries

### Hard boundaries (cannot cross)

| Agent | Can Do | Cannot Do |
|-------|--------|-----------|
| data-architect | Data modeling, SQL, ETL | Ask user which path |
| dashboard-designer | Design, wireframes, decks | Use shell instead of dispatch |
| automation-engineer | Workflows, integrations, alerts | Implement directly |

### Soft boundaries (can flex for single task)

| Agent | Can Flex | But Not For |
|-------|----------|-------------|
| Any specialist | 1-2 simple cross-role tasks | Ask user for guidance |
| orchestrator | File operations | Implement instead of dispatch |

## Cross-references

- LACOUNCIL proposal: `612b1cf0-9d6e-4652-a301-b81d804949b9`
- Agent charters: `data-architect.md`, `dashboard-designer.md`, `automation-engineer.md`
- Orchestrator routing: `orchestrator.md` §"Routing table and refusal handling"
- OmO reliability patterns (source inspiration)