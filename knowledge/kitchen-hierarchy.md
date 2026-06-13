# Kitchen Hierarchy Pattern

Agent routing pattern inspired by restaurant kitchen operations.
Transversal to all LAOS agents. Source: LACOUNCIL `612b1cf0`
(approved 4/4 SIM, maioria, 2026-06-13).

## Core principle

Like a restaurant kitchen, LAOS agents have roles, capabilities,
and cost levels. The orchestrator (chef) routes tasks to the
right agent (sous chef, support, etc.) based on:

1. **Capability** — Can the agent do this?
2. **Tool availability** — Does the agent have the right tool?
3. **Cost** — Is this the cheapest agent who can do it?
4. **Volume** — Should the senior do it or delegate?

## The 5-step routing logic

```
1. Agent receives task
   ↓
2. Check capability: Can I do this?
   ├── YES → Find tool → Execute
   └── NO → Refuse + report to orchestrator
   ↓
3. Orchestrator investigates tool access
   ├── Complex tool → Route to agent with tool
   ├── Simple auth issue → Fix auth, re-dispatch
   └── Missing tool → Create it
   ↓
4. Cost-effective routing (multiple capable agents)
   ├── 1-2 tasks → Senior does it (faster)
   └── 3+ tasks → Delegate to junior (cheaper)
   ↓
5. Role boundaries
   ├── HARD: Can't cross (waiter can't peel potatoes)
   └── SOFT: Can flex for 1 task (sous chef peels 1 potato)
```

## Agent hierarchy

| Role | Agent | When to Use |
|------|-------|-------------|
| Chef | orchestrator | Route, plan, file ops, research via MCP |
| Sous chef | data-architect | Data modeling, SQL, ETL |
| Sous chef | dashboard-designer | Design systems, decks, wireframes |
| Sous chef | automation-engineer | Integrations, workflows, alerts |
| Support | delivery-reviewer | Validate artifacts (read-only) |
| Support | workflow-decomposer | Plan and decompose tasks (read-only) |
| Support | capability-architect | Structural changes (registry, knowledge) |

**No general agents.** Every task has a specialist home.

**If no specialist fits:**
1. Orchestrator handles directly (file ops, git, research via MCP)
2. Task is too vague → clarify with user
3. Task is infrastructure → orchestrator handles

**The principle:** General agents are a code smell. If you need one, you're routing wrong.

## Tool access investigation

When Agent A has tool but Agent B doesn't, orchestrator investigates:

| Cause | Action |
|-------|--------|
| Complex tool requiring training | Route to Agent A |
| Simple authorization issue | Fix auth, re-dispatch to Agent B |
| Missing tool entirely | Create via capability-architect |

**Example:** Sous chef has sponge, dishwasher doesn't.
- Sponge = special technique → sous chef does it
- Sponge = different soap bottle → give dishwasher the soap
- Sponge = doesn't exist → buy one (create tool)

## Task volume threshold

| Volume | Action | Reason |
|--------|--------|--------|
| 1-2 tasks | Senior does it directly | Faster than calling junior |
| 3+ tasks | Senior delegates to junior | Senior's time is more expensive |

**Example:** Sous chef peels 1 potato = fast. Sous chef peels 3 potatoes = call line cook.

## Role boundaries

### Hard boundaries (cannot cross)

| Agent | Can Do | Cannot Do |
|-------|--------|-----------|
| data-architect | Data modeling, SQL, ETL | Serve tables (design), Cook (automation) |
| dashboard-designer | Design, wireframes, decks | Peel potatoes (data), Cook (automation) |
| automation-engineer | Workflows, integrations, alerts | Serve tables (design), Prep data (data) |
| orchestrator | Route, plan, file ops | Do specialist work (unless bypass) |

### Soft boundaries (can flex for single task)

| Agent | Can Flex | But Not For |
|-------|----------|-------------|
| Any specialist | 1-2 simple cross-role tasks | Batch work outside their role |
| orchestrator | Simple file operations | Complex specialist work |

**Examples:**
- Waiter CAN'T peel potatoes (hard boundary — no capability)
- Line cook CAN'T serve tables (hard boundary — no role)
- Sous chef CAN peel 1 potato (soft boundary — fast)
- Sous chef SHOULD NOT peel 10 potatoes (delegate to line cook)

## Refusal protocol

When agent refuses, return compact receipt:
```json
{
  "status": "refused",
  "reason": "no tool for X",
  "suggested_agent": "Y"
}
```

Orchestrator reads refusal and routes accordingly.

## User interaction limits

**Orchestrator asks user ONLY for:**
- Planning decisions (what to build)
- Strategy decisions (how to approach)
- Approval decisions (go/no-go)
- Missing data clarification

**Orchestrator NEVER asks user for:**
- Shell commands
- Technical implementation details
- Tool availability checks
- File system operations

## Tool priority hierarchy

| Task Type | Primary Agent | Tool Priority |
|-----------|---------------|---------------|
| Data operations | data-architect | `latade.*` → file tools → shell |
| Design operations | dashboard-designer | `ladesign.*` → file tools → shell |
| Automation operations | automation-engineer | `lan8n.*` → file tools → shell |
| Governance operations | orchestrator | `lacouncil.*` → file tools |
| File operations | orchestrator | file tools → shell (last resort) |

## WDL gate shell policy

**Shell = blocked by default. Exceptions require justification.**

### The 5-step shell check

1. **"I want a shell"** → BLOCK (always)

2. **Justified shell** (evaluate truth):
   Agent must prove they tried ALL of:
   - [ ] All specialists (data-architect, dashboard-designer, automation-engineer)
   - [ ] MCP tools (which, latade, ladesign, lan8n, context7, exa)
   - [ ] Orchestrator file tools (read, write, edit, glob, grep)
   - [ ] Python scripts in venv
   - [ ] Context7/exa research
   - [ ] KB lookup (knowledge/)
   - [ ] Task is unique (not in any project: ladesign, latade, lan8n, laecon, laengine)
   - [ ] Only single use

   If ALL criteria met → ALLOW
   If ANY criteria missing → BLOCK

3. **Usage tracking**:
   - Register shell usage: command hash (30 chars) + count
   - First 3-4 uses for same task type → ALLOW (grace period)
   - 5th use for same 30 chars → BLOCK + ask user:
     - "Create a new project with this capacity?"
     - "Create an agent for this task?"

4. **User interaction (never ask which path)**:
   - User will always deny shell requests
   - Ask: "Does WDL allow this?"
   - If not → find another path

5. **Never ask user which path**:
   - Never say "do you want shell or agent?"
   - User says no to shell → WDL decides → orchestrator finds alternative

### What counts as "unique task"

- Not in any existing project (laeon, laeon-capability, etc.)
- Not in any capability repo (latade, ladesign, lan8n, laecon, laengine)
- Not in KB (knowledge/)
- Not in registry (capabilities.yaml, needs-to-capabilities.yaml)
- First time this type of task appears

### Toolchain exemptions (always allowed)

These are infrastructure, not implementation:
- `git *` — version control
- `uv *` — Python toolchain
- `npx *` — Node toolchain
- `python *` — Python execution

## Cross-references

- LACOUNCIL proposal: `612b1cf0-9d6e-4652-a301-b81d804949b9`
- Agent charters: `data-architect.md`, `dashboard-designer.md`, `automation-engineer.md`
- Orchestrator routing: `orchestrator.md` §"Routing table and refusal handling"
- OmO reliability patterns (source inspiration)
