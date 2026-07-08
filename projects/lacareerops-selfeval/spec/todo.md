# TODO — lacareerops-selfeval

---

## Stage 0: SDD Scaffold (current)

- [x] Missão 0 — SDD scaffold created (constitution, todo, ADRs, harness, spec 000, contract, README, design-direction)
- [x] `project.yaml` declara needs, deliverables, capabilities_used
- [x] `user_input_data/` documentado como fonte de input (convenção local)

## Stage 1: WDL Preflight Gate

- [x] 1.1 Dispatch `workflow-decomposer` com plan_id `wdl-lacareerops-selfeval-2026-06-21`
- [x] 1.2 Receber `verdict.yaml` com `state: READY` (readiness: partial, quality_score: 2)
- [x] 1.3 Bypass-manifest filed for TD-1 false positive (dashboard-specific stage check)
- [x] **Output:** `artifacts/wdl/wdl-lacareerops-selfeval-2026-06-21/verdict.yaml`

## Stage 2: Parse & Inventory

- [x] 2.1 Extrair texto do docx via data-architect subagent (python-docx)
- [x] 2.2 Listar todos os 25 repos públicos + privados via github API
- [x] 2.3 4 public repo READMEs read in depth, remaining 11 catalogued by metadata
- [x] **Outputs:** `artifacts/cv/parsed-cv.md`, `artifacts/portfolio/repos-inventory.md`

## Stage 3: Market Skills/Tools Gaps

- [x] 3.1 Pesquisar 10+ JDs de AI Data Engineer + mercado DE 2026 via exa
- [x] 3.2 Extrair frequency de 19 skills/tools cruciais
- [x] 3.3 Produzir ranking 3-zonas: Covered / Partial / Absent
- [x] 3.4 Sprint plan 7 dias: RAG, LangGraph, MLOps, Docker, CI/CD
- [x] **Output:** `artifacts/market/tools-gaps.md`

## Stage 4: GitHub Portfolio Audit

- [x] 4.1 READMEs lidos: giovanna (8.5), abandono (8.0), emanuella (7.0), hospital-viana (6.5)
- [x] 4.2 Auditado 9 dimensões com pesos (D1-D9, max 90pts)
- [x] 4.3 Sumário: média 7.5/10, melhor=giovanna, pior=logistica-me
- [x] 4.4 Quick wins identificados: topics tags, screenshots, descriptions
- [x] **Output:** `artifacts/portfolio/github-audit.md`

## Stage 5: Curriculum Gaps Synthesis

- [x] 5.1 Cruzar 19 skills do tools-gaps com CV + portfolio
- [x] 5.2 Matriz 3 zonas com score CV, score portfolio, market demand
- [x] 5.3 Sprint plan 7 dias fechando 3 gaps críticos
- [x] **Output:** `artifacts/cv/curriculum-gaps.md`

## Stage 6: LinkedIn Strategy

- [x] 6.1 McDonald's 3-layer evaluation com 6 melhorias propostas
- [x] **Output:** `artifacts/strategy/strategy-evaluation.md`
- [x] 6.2 Backlog de 30 posts com calendário semanal 10 semanas
- [x] **Output:** `artifacts/strategy/30-posts-backlog.md`
- [ ] 6.3 Visuais para os 30 conceitos (lade-design)
  - **Output:** `artifacts/strategy/visuals-deck.html` via dashboard-designer
  - *Depende de WDL READY verdict (READY obtido) + dispatch dashboard-designer*

## Stage 7: Wage Bands Research

- [x] 7.1 Pesquisar salários BR PJ, BR CLT, US remote, EU remote
- [x] 7.2 4 brackets (júnior, pleno, sênior, lead) por modalidade
- [x] 7.3 Premium bracket with RAG/Agent/MLOps = +R$5k-10k/mês
- [x] 7.4 ROÌ do sprint 30d: R$36k-120k/year uplift
- [x] **Output:** `artifacts/market/wage-bands.md`

## Stage 8: ADR

- [x] 8.1 ADR `001-tools-gaps-methodology.md`
- [x] 8.2 ADR `002-linkedin-content-strategy.md`
- [x] 8.3 ADR `003-wage-bands-sources.md`

## Stage 9: delivery-reviewer sign-off

- [x] 9.1 Preflight pass: M1 tier, 0 findings, 6 checks
- [x] 9.2 Dispatch `delivery-reviewer` — 1st review: NOT DELIVERABLE (design/source.md P0)
- [x] 9.3 Auto-retry #1: P0 fix verified, sign-off DELIVERABLE
- [x] 9.4 `artifacts/review/checklist.md` written
- [x] **Output:** `artifacts/review/checklist.md` (sign-off complete)

## Notes

- **Nenhum dado sintético** (constituição Art. VI). Se algum stage
  precisar sample, parar e perguntar ao orchestrator (regra-mãe Hard #11).
- **user_input_data conv** é local a este projeto. Se reaparecer em 2+
  projetos, formalizar em `knowledge/data-conventions.md`.
