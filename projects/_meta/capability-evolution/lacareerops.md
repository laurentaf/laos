# Capability Evolution — lacareerops

**Status:** IN_PROGRESS
**Created:** 2026-06-13
**Proposal:** 2f1ccd2d-7d0a-44fc-8382-24c3e16ebd0c (LACOUNCIL, supermaioria, aprovada 2026-06-13 — 3 SIM + 1 ABSTENCAO)
**Deadline:** 2026-07-13 (+30 dias da primeira dispatch)
**Owner:** github.com/laurentaf/lacareerops (repo privado) + projects/_meta/lacareerops/ (meta-projeto)

---

## Capability Info

| Field | Value |
|-------|-------|
| Name | lacareerops |
| Status atual | BASIC (scaffold entregue 2026-06-13) |
| Status target | STABLE |
| Domínio | automation (career job-search optimization) |
| Capability repo | github.com/laurentaf/lacareerops (PRIVADO) |
| Local path | N/A (repo externo privado) |
| Tracking issue | this file + lacouncil proposal `2f1ccd2d-...` |
| Meta-projeto | projects/_meta/lacareerops/project.yaml |
| ADR | projects/_meta/adr/ADR-003-lacareerops-creation.md |

---

## why

LAOS não tinha capability para gestão de carreira/busca de emprego. O ecossistema precisava de forma estruturada de:
- Avaliar ofertas de emprego (salary, remote, equity, benefits vs. market)
- Gerar CVs ATS-optimized em PDF
- Escanear portais de emprego (LinkedIn, Indeed, Glassdoor)
- Processar múltiplas URLs em batch
- Rastrear pipeline de candidaturas

A motivação veio do career-ops (santifer/career-ops, 740+ offers evaluated, 100+ CVs gerados) que já provou valor em produção com integração OpenCode nativa.

Decisão de PRIVACIDADE: repo é **PRIVADO** porque dados de carreira são sensíveis (CV, salary history, career trajectory, target companies). Cada usuário configura seus próprios `config/profile.yml` + `cv.md`.

---

## Escopo (BASIC)

### Dentro do escopo
- **Avaliação de ofertas:** salary, remote, equity, benefits vs. market benchmarks
- **Geração de CV PDF:** ATS-optimized via Playwright, a partir de markdown estruturado
- **Escaneamento de portais:** Companies (LinkedIn, Indeed, Glassdoor, G2, etc.)
- **Processamento em batch:** múltiplas URLs de uma vez
- **Tracker list:** pipeline atual de candidaturas com status

### Fuera do escopo (BASIC)
- Submissão automática de candidaturas — pós-STABLE se houver demanda
- Integração com ATS externos (Workday, Greenhouse) — extensão futura
- Armazenamento centralizado de dados do usuário — repo é local por design

---

## MCP Tools — Escopo Inicial (BASIC, 5 tools)

| # | Tool | Descrição | Status |
|---|------|-----------|--------|
| 1 | `health` | Liveness probe | ✅ implementado |
| 2 | `list_supported_operations` | Catálogo de operações | ✅ implementado |
| 3 | `career_ops_evaluate` | Avalia job description contra profile + market data | ✅ implementado |
| 4 | `career_ops_generate_pdf` | Gera CV PDF ATS-optimized | ✅ implementado |
| 5 | `career_ops_scan_portals` | Escaneia portais por companies | ✅ implementado |
| 6 | `career_ops_batch_process` | Processa múltiplas URLs | ✅ implementado |
| 7 | `career_ops_tracker_list` | Lista pipeline atual | ✅ implementado |

### Tools futuras (STABLE+)
- `career_ops_submit` — submissão automática (se automação validar)
- `career_ops_interview_tracker` — scheduling e follow-ups
- `career_ops_offer_negotiation` — salary negotiation playbook

---

## Quality Gates (G1-G8)

| Gate | Descrição | Status (2026-06-13) |
|------|-----------|---------|
| G1 | MCP server funcional (health + list_supported_operations + 5 tools operacionais) | ✅ entregue |
| G2 | Entry em capabilities.yaml (status=BASIC) | ✅ entregue |
| G3 | Routing em needs-to-capabilities.yaml | ✅ entregue |
| G4 | BASIC sign-off via delivery-reviewer | ⏳ pendente |
| G5 | KB com Handoff Boundaries (≥2 exemplos) | ✅ entregue (knowledge/handoff-lacareerops.md) |
| G6 | Capability-evolution tracking file | ✅ entregue |
| G7 | STABLE sign-off via delivery-reviewer | ⏳ pendente (deadline 2026-07-13) |
| G8 | ADR documentando rationale | ✅ entregue |

---

## Evolution Plan

| Milestone | Descrição | Deadline | Status |
|-----------|-----------|----------|--------|
| **M0** | Meta-projeto + LACOUNCIL proposal + scaffold BASIC | 2026-06-13 | ✅ entregue |
| G1 | MCP server funcional (7 tools) | 2026-06-13 | ✅ |
| G2 | Registry entry lacareerops BASIC | 2026-06-13 | ✅ |
| G3 | Routing needs-to-capabilities.yaml | 2026-06-13 | ✅ |
| G5 | KB com Handoff Boundaries | 2026-06-13 | ✅ |
| G6 | Capability-evolution tracking | 2026-06-13 | ✅ |
| G8 | ADR publicado | 2026-06-13 | ✅ |
| G4 | delivery-reviewer BASIC sign-off | 2026-06-20 | ⏳ |
| G7 | delivery-reviewer STABLE sign-off | 2026-07-13 | ⏳ |
| **M1 (STABLE)** | Status promovido para STABLE | 2026-07-13 | ⏳ |
| **M2** | Auto-submission + interview tracker | 2026-08-13 | ⏳ |

---

## Handoff Boundaries

Capability adjacentes:
- **lan8n** — automação de workflows; lacareerops é consumido por lan8n para workflows de job-search automation (ex: weekly job alert → evaluate → generate CV → tracker update)
- **latade** — dados; lacareerops pode outputs para gold tables se o usuário quiser analytics de carreira
- **ladesign** — dashboards; tracker de candidaturas pode ser visualizado como dashboard ladesign

---

## Condições do Conselho (3 votadas, da abstenção do data-architect)

O data-architect ABSTVEU-se (incerteza sobre pipeline compatibility com LATADE). A decision do Conselho:
- A compatibilidade com LATADE é **NÃO um requisito** para BASIC — lacareerops usa career-ops CLI (Node.js), não DuckDB
- lacareerops outputs são PDFs e JSON structs; consumo por latade/ladesign é opcional e pós-STABLE
- A ausência de LATADE dependency é uma decisão de design, não uma limitação

### Condições de security (delivery-reviewer, P0)
- **SC-1:** Repo PRIVADO — dados sensíveis (CV, salary, career history)
- **SC-2:** Sem credenciais no código — cada usuário configura profile.yml localmente
- **SC-3:** .gitignore cobre .env, *.log, __pycache__, .venv

---

## Notes

- Repo privado por design (dados de carreira são sensíveis)
- career-ops CLI (Node.js) é o engine; MCP wrapper é apenas interface LAOS
- Cada usuário tem seus próprios cv.md e profile.yml — sem shared data
- Automation-engineer é domain-specialist reviewer (G3) para KB + contracts