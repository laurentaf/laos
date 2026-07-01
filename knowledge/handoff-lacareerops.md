# Handoff Boundaries — lacareerops

> **⛔ DEPRECATED** per LACOUNCIL `e65617ec` (2026-07-01, 4/4 SIM).
> The lacareerops MCP wrapper never functioned locally — the hub repo was
> never cloned, the MCP server never ran, and all 8 promised tools were
> unreachable. Upstream `santifer/career-ops` is actively maintained and
> usable directly via `npx`. Routing entries removed from
> `needs-to-capabilities.yaml`. This file is preserved as historical record.

**Capability:** lacareerops | **Kind:** domain (automation/career) | **Status:** DEPRECATED
**Created:** 2026-06-13 | **G2 requirement (binding conditions)**

---

## Adjacent Capabilities

| Capability | Relationship | Shared boundary |
|-----------|-------------|-----------------|
| **lan8n** | Parent/conummer | lacareerops outputs são consumed por lan8n workflows; lan8n pode triggerar lacareerops em pipelines de job-search automation |
| **latade** | Potential consumer | Se usuário quiser analytics de carreira em DuckDB, outputs de lacareerops podem ser gold tables — extensão futura, não em BASIC |
| **ladesign** | Potential consumer | Tracker de candidaturas pode ser visualizado como dashboard ladesign — extensão futura, não em BASIC |
| **github** | External data source | job openings de portais públicos são scraped via career-ops; sem API credentials necessárias |

---

## Concrete routing examples (≥ 2 per G2)

### Example 1: Job evaluation workflow
**Trigger:** "avaliar esta oferta de emprego"
**Routing:** `automation` need → lacareerops (PRIMARY)
**Not:** `data` → latade (career-ops usa career-ops CLI, não DuckDB)
**Not:** `design` → ladesign (não é design work)

### Example 2: Weekly job alert pipeline
**Trigger:** "mandar alerta semanal de vagas novas"
**Routing:** `automation` need → lan8n (PRIMARY) → lacareerops (tool call via MCP)
**Why:** O workflow de agendamento é lan8n; a avaliação de vagas é lacareerops

### Example 3: CV for specific job application
**Trigger:** "gerar um CV ATS-optimized para esta vaga"
**Routing:** `automation` need → lacareerops (PRIMARY)
**Not:** `design` → ladesign (PDF generation ≠ design work)

### Example 4: Career analytics dashboard
**Trigger:** "dashboard mostrando minha taxa de sucesso por empresa"
**Routing:** `dashboard` need → ladesign (PRIMARY) → latade (data source)
**Note:** lacareerops só trackeia; não produz o dashboard. Handoff: lacareerops outputs → latade gold table → ladesign visualization.

---

## Subutilization signals

- Usuário avalia ofertas manualmente quando `career_ops_evaluate` existe
- CV gerado em Word quando `career_ops_generate_pdf` pode gerar ATS-optimized
- Usuário abre 20 abas de LinkedIn manualmente quando `career_ops_scan_portals` existe
- Usuário mantém tracker em planilha quando `career_ops_tracker_list` existe

## Overutilization signals

- Usuário tentando usar lacareerops para coisas que são `data` (armazenar histórico de avaliações) → redirecionar para latade
- Usuário esperando dashboards nativos do lacareerops → redirecionar para ladesign
- Usuário pedindo auto-submission de candidaturas em BASIC → remarcar para M2

---

## Submodule architecture (v1.1.0, 2026-06-19)

> **Loop 1 refactor approved:** LACOUNCIL `ba9a9bd7-3686-4d6e-9f1b-3efc46f37a8c`
> (supermaioria 4/4 SIM, 2026-06-19). Replaces the legacy `laurentaf/career-ops`
> fork mirror with a **git submodule** hosted at `laurentaf/lacareerops-hub`.

### Architecture shape

```
laurentaf/lacareerops-hub/    (PRIVATE GitHub repo)
+- mcp/server.py              (Python MCP wrapper; 8 tools incl. career_ops_sync)
+- config/                    (templates only; real data gitignored)
+- upstream/                  (git submodule -> santifer/career-ops)
+- .gitmodules                (submodule declaration)
+- SUBMODULE_SHA.txt          (last-known-good SHA; mutated only on smoke pass)
+- pyproject.toml
+- LICENSE                    (MIT)
+- docs/adr/ADR-013-lacareerops-submodule.md   (hub-side mirror of LAOS ADR)
```

### Sync flow

The new tool `career_ops_sync` automates submodule advancement:

```
orchestrator / subagent
        |
        v
  await career_ops_sync()           # advance to upstream HEAD (smoke-gated)
  await career_ops_sync(target_sha="<40-hex>")  # pin explicitly
  await career_ops_sync(dry_run=True)
        |
        v
  - resolves target SHA (HEAD or explicit)
  - runs 4-check smoke battery
        \
         +- if all pass -> advance submodule + persist SUBMODULE_SHA.txt
         +- if any fail -> auto-rollback to previous SHA, status: rolled_back
```

### What this changes for orchestrator / subagents

- **No call-site changes.** Existing tool calls (`career_ops_evaluate`,
  `career_ops_generate_pdf`, etc.) are preserved as-is.
- **One new tool available:** `career_ops_sync` for users that want to
  roll forward the pinned upstream SHA.
- **Routing unchanged.** `registry/needs-to-capabilities.yaml` does not
  need to change; the same needs (`career-evaluation`, `cv-generation`,
  `job-scan`, `career-tracker`) still resolve to `lacareerops` primary.
- **Privacy invariant preserved.** `config/profile.yml` + `config/cv.md`
  remain gitignored; sync tool never reads user config.

### Local-state sync pattern (orchestrator)

When the orchestrator updates `registry/capabilities.yaml` to point to a
new hub repo (this refactor itself), the user-side checkout must catch up:

```bash
cd $repo_dir_to_host_hub      # e.g., E:/projects/lacareerops-hub (or local fork)
git remote set-url origin https://github.com/laurentaf/lacareerops-hub.git
git pull --rebase origin main
git submodule update --init --recursive upstream/
uv sync
```

If the orchestrator needs to roll forward the pinned upstream, it calls
`lacouncil.get_trust_scores()` before invoking sync (to ensure no trust
spike from a recent fork) and only then advances the SHA.

---

## Knowledge base seed

- **KB index:** `knowledge/handoff-lacareerops.md` (este arquivo)
- **Constitution:** `projects/_meta/lacareerops/spec/constitution.md`
- **Domain specialist reviewer:** automation-engineer (G3 requirement)

## Notes for domain specialist review (G3)

automation-engineer é o domain specialist reviewer para lacareerops KB + contracts porque:
1. lacareerops é domínio automation (career job-search)
2. career-ops CLI é automation tool (Node.js, subprocess-based)
3. Handoff boundaries com lan8n são críticas para workflows de job-search automation
4. Após LACOUNCIL `ba9a9bd7` (2026-06-19): a carreira de sync em
   `career_ops_sync` é read-only mirror upstream — não há mutação de
   LAN8N workflows, então continua sendo domain-specialist review
   adequada (automation-engineer concorda conforme voto na proposta).

KB draft está em `knowledge/handoff-lacareerops.md` (este arquivo).
Delivery-reviewer vai enviar para automation-engineer review antes de G4 sign-off.

---

*Created per binding-conditions.md G2 (data-architect amendment).*
*Domain specialist review: automation-engineer (G3).*
*Loop-1 submodule architecture added 2026-06-19 (LACOUNCIL ba9a9bd7).*