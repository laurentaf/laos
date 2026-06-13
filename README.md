# LAOS — Laurent Agent Operating System

**Composable AI orchestration for data, design, and automation projects.**

LAOS is an orchestration layer that composes specialized capabilities
(LATADE for data, LADESIGN for design, LAN8N for automation, LACOUNCIL
for governance) into declarative client projects — without writing
implementation code in the orchestration layer.

## The 7-Capability Ecosystem

LAOS orchestrates 7 capabilities, each in its own repository:

```
├── latade          (https://github.com/laurentaf/latade)         # Data engineering · SQL, dbt, DuckDB, BI
├── lan8n           (https://github.com/laurentaf/lan8n)            # Automation · n8n workflows, integrations
├── ladesign        (https://github.com/laurentaf/ladesign)        # Design · dashboards, decks, wireframes
├── lacouncil       (https://github.com/laurentaf/lacouncil)        # Governance · proposals, voting, DuckDB memory
├── laecon          (https://github.com/laurentaf/laecon)          # Econometrics · regression, GLM, causal inference
├── laengine        (https://github.com/laurentaf/laengine)         # Game dev · match engine, sports simulation
└── lacareerops     (https://github.com/laurentaf/lacareerops)     # Career · job search, CV, portals
```

## How a Client Project Works

1. Brief → `projects/<name>/project.yaml` (the contract in LAOS)
2. Orchestrator resolves needs via `registry/needs-to-capabilities.yaml`
3. WDL preflight gate: workflow-decomposer validates the plan (READY/DEFER/ESCALATE)
4. Specialist subagents dispatched via MCP (data-architect, dashboard-designer, etc.)
5. delivery-reviewer validates against `knowledge/padroes-entrega.md`
6. Artifacts live in the child repo — LAOS holds the contract, nothing else

## Recent Projects

| Project | Domain | Capabilities Used | Child Repo |
|---------|--------|-------------------|------------|
| `abandono-academico-casa-grande` | Academic ML | LATADE + LADESIGN | github.com/laurentaf/abandono-academico-casa-grande |
| `hospital-viana-claims` | Healthcare ETL | LATADE | github.com/laurentaf/hospital-viana-claims |
| `giovanna-rupture-monitor` | Retail analytics | LATADE | github.com/laurentaf/giovanna-rupture-monitor |
| `emanuella-stock-ingestion` | Retail ingestion | LATADE | github.com/laurentaf/emanuella-stock-ingestion |

## What This Proves (for a Data Engineer role)

| Skill | Evidence |
|-------|----------|
| System design | Built a meta-system that orchestrates 7 independent capabilities |
| MCP (Model Context Protocol) | Wired 7 MCP servers, each with distinct tools |
| Declarative project contracts | `project.yaml` as the single source of truth per project |
| Governance / quality gates | LACOUNCIL proposals with voting, delivery-reviewer checklist |
| Multi-agent orchestration | Orchestrator dispatches specialist subagents, each with bounded scope |
| CI/CD for AI systems | GitHub Actions managing the LAOS meta-system itself |

## Quick Start

```powershell
pwsh .\setup.ps1   # Install deps, verify siblings, configure .env
opencode            # Launch LAOS orchestrator
```

## Key Files

| File | Purpose |
|------|---------|
| `AGENTS.md` | Hard rules: no implementation code in LAOS |
| `registry/needs-to-capabilities.yaml` | Routing from abstract needs → concrete capabilities |
| `knowledge/padroes-entrega.md` | Delivery checklist (P0 blockers for every project) |
| `workflows/` | Project archetype templates |
| `projects/<name>/project.yaml` | Contract for every client project |

## Architecture Rules (Non-negotiable)

- **No implementation in LAOS.** SQL, dashboards, n8n flows live in capability repos.
- **Reached only via MCP.** Capability repos are never `cd`'d into directly.
- **Projects have two homes.** Contract in LAOS; artifacts in child repo.
- **Structural changes require consensus.** LACOUNCIL proposals go through the Conselho.

See `AGENTS.md` for the full set of rules.

---

*LAOS — Composing specialized AI capabilities into declarative client projects.*