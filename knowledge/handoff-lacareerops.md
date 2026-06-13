# Handoff Boundaries — lacareerops

**Capability:** lacareerops | **Kind:** domain (automation/career)
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

## Knowledge base seed

- **KB index:** `knowledge/handoff-lacareerops.md` (este arquivo)
- **Constitution:** `projects/_meta/lacareerops/spec/constitution.md`
- **Domain specialist reviewer:** automation-engineer (G3 requirement)

## Notes for domain specialist review (G3)

automation-engineer é o domain specialist reviewer para lacareerops KB + contracts porque:
1. lacareerops é domínio automation (career job-search)
2. career-ops CLI é automation tool (Node.js, subprocess-based)
3. Handoff boundaries com lan8n são críticas para workflows de job-search automation

KB draft está em `knowledge/handoff-lacareerops.md` (este arquivo).
Delivery-reviewer vai enviar para automation-engineer review antes de G4 sign-off.

---

*Created per binding-conditions.md G2 (data-architect amendment).*
*Domain specialist review: automation-engineer (G3).*