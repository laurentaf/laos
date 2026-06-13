# Kitchen Hierarchy Pattern

Agent routing pattern inspired by restaurant kitchen operations.
Transversal to all LAOS agents. Source: LACOUNCIL `612b1cf0`
(approved 4/4 SIM, maioria, 2026-06-13).

## Core principle

Like a restaurant kitchen, LAOS agents have roles, capabilities,
and cost levels. The orchestrator (chef) routes tasks to the
right agent (line cook, sous chef, etc.) based on:

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

| Role | Agent | Cost Level | Can Do | Cannot Do |
|------|-------|------------|--------|-----------|
| Chef | orchestrator | — | Route, plan, file ops | Specialist work |
| Sous chef | data-architect | HIGH | Complex data modeling | Design, automation |
| Sous chef | dashboard-designer | HIGH | Complex design systems | Data, automation |
| Sous chef | automation-engineer | HIGH | Complex integrations | Data, design |
| Line cook | any specialist (simple mode) | MEDIUM | Simple tasks in their domain | Cross-domain work |
| Support | orchestrator | LOW | File ops, git, reads/writes | Specialist work |

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
| File operations | any specialist | file tools → shell (last resort) |

## WDL gate architecture enforcement

The WDL gate enforces that work goes through the agent system:

**BLOCKED (non-agent actions):**
- `bash` (shell) — always blocked, forces agent use

**ALLOWED (agentic use):**
- `task` tool (agent dispatch) — always allowed
- MCP tools (`ladesign.*`, `latade.*`, `lan8n.*`) — dispatch to agents internally
- `lacouncil.*` structural work (exempt per Hard Rule 8.4)
- Conselho governance dispatch

**The principle:** Agents = good (always allowed). Shell = bad (always blocked).
MCP tools = agentic use (always allowed).

## Cross-references

- LACOUNCIL proposal: `612b1cf0-9d6e-4652-a301-b81d804949b9`
- Agent charters: `data-architect.md`, `dashboard-designer.md`, `automation-engineer.md`
- Orchestrator routing: `orchestrator.md` §"Routing table and refusal handling"
- OmO reliability patterns (source inspiration)
