# 👑 LAOS — Laurent Agent Operating System

> *The laurel was exclusive. The intelligence doesn't have to be.*

**LAOS dissolves the crown.** For 3,000 years, the laurel cinged one head — the emperor's. Intelligence was centralized, privileged, gated. LAOS distributes sovereignty to every operator: the laós.

Not a framework. Not a platform. An **operating system for composable AI** — 7 specialized capabilities, 1 orchestrator, zero implementation in the orchestration layer.

---

## The Inversion

| Old World | LAOS |
|-----------|------|
| Data team owns the pipeline | Every operator runs their own data |
| AI lab hoards the models | Capabilities are composed, not siloed |
| Tickets and dashboards for the rest | MCP-native tool access for every agent |
| Emperor decides | Conselho deliberates (proposals, voting, trust) |

---

## Ecosystem Architecture

```
                          ┌─────────────────┐
                          │     LAOS         │
                          │   Orchestrator   │
                          │  (this repo)     │
                          └────────┬────────┘
                                   │
            ┌──────────────────────┼──────────────────────┐
            │                      │                      │
      ┌─────┴─────┐         ┌─────┴─────┐         ┌─────┴─────┐
      │   LATADE   │         │  LADESIGN  │         │   LAN8N    │
      │  🗄️ Data   │         │  🎨 Design  │         │  ⚙️ Auto    │
      │ SQL·dbt·   │         │ dashboards·│         │ n8n flows· │
      │ DuckDB·BI  │         │ decks·UI   │         │ APIs       │
      └────────────┘         └────────────┘         └────────────┘
      ┌────────────┐         ┌────────────┐         ┌────────────┐
      │  LACOUNCIL  │         │   LAECON    │         │  LAENGINE   │
      │  🏛️ Gov     │         │  📊 Econo   │         │  🎮 Game    │
      │ proposals· │         │ regression·│         │ simulation·│
      │ voting·    │         │ causal·ML   │         │ match eng  │
      │ DuckDB mem │         │ interpret  │         │ squad mgmt │
      └────────────┘         └────────────┘         └────────────┘
      ┌────────────┐
      │LACAREEROPS │
      │  💼 Career  │
      │ job search·│
      │ CV·portals │
      └────────────┘
```

**7 capabilities. 7 MCP servers. 0 implementation in the orchestrator.**

Each capability is its own repository, its own MCP server, its own lifecycle. LAOS composes them — it never owns them.

---

## How a Client Project Works

```
Brief → project.yaml (contract) 
         → orchestrator resolves needs via registry
         → WDL preflight gate (workflow-decomposer validates plan)
         → specialist subagents dispatched via MCP
         → delivery-reviewer validates against P0 checklist
         → Artifacts live in child repo. LAOS holds the contract.
```

**Every project is born as its own repository.** LAOS holds the contract (`project.yaml`), the routing table, and the delivery checklist — nothing else.

### Delivered projects

| Project | Domain | Impact | Repo |
|---------|--------|--------|------|
| **abandono-academico** | ML (dropout prediction) | 87.5% accuracy, 93.7% recall, 32k students | public |
| **hospital-viana-claims** | Healthcare ETL | 6 DQ checks, IFRS17-ready, daily GH Actions | public |
| **giovanna-rupture-monitor** | Retail analytics | 4,150 regions analyzed, 33% stock-out detection | public |
| **emanuella-stock-ingestion** | Retail ETL | dbt-ready, 3-stage, SLA < 5 min | public |
| **previsao-concursos** | NLP/education | 1,236 questions, 27 contests, Laplace smoothing | public |
| **brasfoot-poc → laengine** | Game dev | 10-team simulation, round-robin, MCP tools | public |
| **laos-brand** | Brand system | Manifesto, keynote, landing page, DESIGN.md | public |

---

## What This Proves

| Skill | Evidence |
|-------|----------|
| **System architecture** | Designed a meta-system orchestrating 7 independent capabilities across 4 domains |
| **MCP (Model Context Protocol)** | Wired 7 MCP servers — data, design, automation, governance, econometrics, game, career |
| **Declarative contract design** | `project.yaml` as single source of truth → deterministic need-to-capability routing |
| **Governance engineering** | LACOUNCIL: proposals, Conselho voting (unanimity/supermajority/majority), trust scores, DuckDB memory |
| **Multi-agent orchestration** | 9 subagent types (data-architect, dashboard-designer, automation-engineer, etc.), WDL preflight gate |
| **Quality assurance automation** | 12 OpenCode plugins enforce hard rules mechanically (not by prompt). delivery-reviewer validates every project |
| **SDD (Spec-Driven Development)** | Every project produces 8+ SDD artifacts before any implementation code |
| **CI/CD for AI systems** | GitHub Actions, preflight checks, boot validation per dispatch |

---

## Key Files

| File | Purpose |
|------|---------|
| `AGENTS.md` | Hard rules + agent topology + 12-plugin architecture |
| `registry/needs-to-capabilities.yaml` | Deterministic routing: 20+ needs → capabilities |
| `registry/capabilities.yaml` | Full capability catalog (7 domain + platform MCPs) |
| `knowledge/padroes-entrega.md` | P0-P2 delivery checklist (13+ checks) |
| `knowledge/sdd-principles.md` | Spec-Driven Development: 9-file scaffold matrix |
| `workflows/` | Project archetype templates (etl, dashboard, presentation) |
| `projects/<name>/project.yaml` | Contract for every client project |
| `scripts/subagent_boot_check.py` | 6-dimension validation before every specialist dispatch |

---

## Quick Start

```powershell
uv sync                    # Install deps
uv run python scripts/preflight_check.py .   # Health check
opencode .                 # Launch LAOS orchestrator
```

---

## Architecture Rules (Non-negotiable)

- **No implementation in LAOS.** SQL, dashboards, n8n flows live in capability repos.
- **Reached only via MCP.** Capability repos are never `cd`'d into directly.
- **Structural changes require consensus.** LACOUNCIL proposals → Conselho voting (4 subagents) → implementation.
- **Every project has two homes.** Contract in LAOS; artifacts in child repo.
- **WDL preflight is mandatory.** No specialist dispatch without a READY verdict from workflow-decomposer.
- **Patterns repeated 3+ times trigger LACOUNCIL investigation.**

---

## The LAOS Difference

**LAOS is not a framework you import. It's a system you inhabit.**

- Frameworks give you functions. LAOS gives you **governance**.
- Platforms give you lock-in. LAOS gives you **MCP-native composability**.
- AI agents give you answers. LAOS gives you **a system that checks its own work**.

> *"Data architecture isn't about the tools — it's about whether the C-suite trusts what it sees on the dashboard."*

---

## About the Architect

**Laurent** — Data Architect & ML Engineer

Built LAOS because he couldn't find a system that composably orchestrates data, design, automation, and governance without becoming the implementation itself.

- [GitHub](https://github.com/laurentaf) · [LinkedIn](https://linkedin.com/in/lauferreira)
- Campinas/SP · Remote-first · Open to: Data Architect, AI Data Engineer, Analytics Engineering