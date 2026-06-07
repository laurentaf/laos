# TODO — previsao-concursos

**Filtro:** o gate `subagent_boot_check.py` 6ª dimensão (sub-check
`skeleton`) exige pelo menos uma task aberta (`- [ ]`) neste arquivo.
Veja §"Completed" abaixo: Missão 0 foi concluída em 2026-06-05.

---

## Phase 0 — Missão 0 (SDD scaffold) [CONCLUÍDA 2026-06-05]

- [x] Criar `spec/constitution.md` com Principles/Scope/Non-goals.
- [x] Criar `spec/todo.md` (este arquivo).
- [x] Criar `spec/adr/_template.md` (stub-by-design, cópia do LATADE).
- [x] Criar `spec/adr/README.md` (índice vazio até a 1ª ADR real).
- [x] Criar `spec/harness/_template.md` (stub-by-design, cópia do LATADE).
- [x] Criar `spec/specs/000-bootstrap/spec.md` com Contexto/Decisões/Critérios.
- [x] Criar `contract.md` (espelho do `project.yaml` em prosa).
- [x] Criar `README.md` (≥ 400 chars, 3 seções O que é / Como rodar / Onde está o quê).
- [x] Criar `spec/design-direction.md` (condicional, ≥ 300 chars).
- [x] Submeter o projeto ao preflight + boot check 6ª dimensão (esperado: PASS).

---

## Phase 1 — Discovery [CONCLUÍDA 2026-06-05]

- [x] Identificar bancas-alvo (FCC, FGV) e cargo-alvo (Auditor Fiscal).
- [x] Mapear fontes prováveis de provas (FCC oficial, FGV oficial, qconcursos validação).
- [x] Definir KPIs (Brier < 0.25, Top-K@5 ≥ 0.6, NDCG@10 ≥ 0.65).
- [x] Decidir split temporal (2022-2024 treino, 2025-2026 validação).
- [x] Documentar 5 decisões D-001..D-005 em `artifacts/discovery/requirements.md`.
- [x] **ADR-002 (LAOS)**: routing `modeling` → `[latade, laecon]` (4/4 SIM, 100%).

---

## Phase 2 — Data-model [CONCLUÍDA 2026-06-05]

- [x] Definir 8 tabelas (3 fonte + 2 enriquecimento + 3 consumo).
- [x] Cadeia FK bronze → silver → gold documentada.
- [x] Decisões D-006..D-010 em `artifacts/data/model.md`.
- [x] Stub DDL em `artifacts/data/sql-stubs/001-medallion.md` (DuckDB-flavored).
- [x] Estratégia de scraping + chunking documentadas.
- [x] 5 regras de DQ em `artifacts/dq/checks.md` com severity/threshold/canal.
- [x] **ADR-006 (LAOS)**: fix do boot check 6ª dimensão (4/4 SIM, 100%).

---

## Phase 3 — Design (próximo)

- [ ] Despachar `dashboard-designer` com `ladesign` para
      `artifacts/design/` (wireframe + visual spec + componente breakdown).
- [ ] `artifacts/design/source.md` referenciando o `spec/design-direction.md`.
- [ ] Storyboard do roteiro hierárquico (Matéria > Assunto > Sub-assunto).
- [ ] Deck de 1 página com a visão geral da plataforma.

## Phase 4 — Build (clássico-ML + study-plan)

- [ ] Custom stage `classical-ml` (laecon): spec do modelo preditivo
      empírico + plano de treino. Output em `artifacts/ml/`.
- [ ] Custom stage `study-plan`: gerador do roteiro hierárquico com
      probabilidades empíricas. Output em `artifacts/dashboard/`.
- [ ] Pipeline ETL (latade): bronze → silver → gold, com guards para
      DataFrame vazio em todas as etapas.
- [ ] HARNESS por componente (HARNESS-001 ingestion, HARNESS-002
      tagging, HARNESS-003 ml, HARNESS-004 study-plan).

## Phase 5 — Automate

- [ ] Workflow n8n para refresh mensal do cache de editais.
- [ ] Alertas para DQ violations (canal: stdout + log file, sem webhook
      externo no POC).
- [ ] Trigger: cron mensal (1º dia útil, 03:00 BRT).

## Phase 6 — Review

- [ ] `delivery-reviewer` valida contra `knowledge/padroes-entrega.md`.
- [ ] Preflight mecânico passou (5 checks).
- [ ] `artifacts/review/checklist.md` produzido pelo reviewer.

## Completed (resumo histórico)

- [x] Projeto scaffold criado em `projects/previsao-concursos/`.
- [x] `project.yaml` válido com 10 needs + 4 custom_stages + 14 deliverables.
- [x] 2 ADRs reais escritas em `spec/adr/`.
- [x] LACOUNCIL: 2 propostas aprovadas e implementadas.
