# contract.md — previsao-concursos

**Version:** 1.0 | **Date:** 2026-06-05
**Origem:** espelho em prosa de `project.yaml` para satisfazer o
gate `subagent_boot_check.py` 6ª dimensão (sub-check `skeleton`).
Atualizar este arquivo quando `project.yaml` mudar.

---

## Brief

Plataforma web que prevê os assuntos mais prováveis por matéria
em concursos públicos brasileiros, usando histórico de provas da
banca avaliadora identificada a partir do edital. Entrega um
roteiro de estudo hierárquico (Matéria > Assunto > Sub-assunto) com
probabilidades empíricas por banca/cargo. POC 100% local, sem
cliente externo (`external_delivery: false`).

Público-alvo: candidatos a concursos (Auditor Fiscal federal /
estadual / municipal) que querem otimizar tempo de estudo sabendo
**onde a banca historicamente cobra mais**.

Sucesso = 4 KPIs quantitativos: Brier score < 0.25, Top-K@5 ≥ 0.6,
NDCG@10 ≥ 0.65, cobertura ≥ 80% dos sub-assuntos do edital.

## Needs

10 needs declaradas, todas resolvidas no
`registry/needs-to-capabilities.yaml`:

- `data` → latade
- `etl` → latade (+ lan8n)
- `modeling` → latade + laecon (LACOUNCIL `bf91c407`)
- `predictive-modeling` → laecon
- `data-quality` → latade
- `dashboard` → ladesign
- `design` → ladesign
- `automation` → lan8n
- `research` → exa
- `integration` → lan8n

4 custom stages (não cobertos pelo workflow base, executados
dentro de etapas do `dashboard-completo`):

- `scrap` — dentro de discovery + data-model (gap conhecido; skill
  local no LATADE até virar capability transversal).
- `chunking` — dentro de data-model.
- `classical-ml` — depois de data-model, antes de build.
- `study-plan` — dentro de build.

## Deliverables

Stages do workflow `dashboard-completo` + extensões POC:

- `artifacts/discovery/requirements.md` ✅
- `artifacts/data/model.md` ✅
- `artifacts/data/sql-stubs/001-medallion.md` ✅
- `artifacts/data/strategies/{scraping,chunking}.md` ✅
- `artifacts/dq/checks.md` ✅
- `artifacts/design/` (próximo)
- `artifacts/dashboard/`
- `artifacts/automation/`
- `artifacts/review/checklist.md`
- `artifacts/data/source-profile.md`
- `artifacts/data/train-validation-split.md`
- `artifacts/pipeline/` (scraper + chunker)
- `artifacts/ml/` (modelo + métricas)

Todos os artefatos acima são **commitados no child repo**
`laurentaf/previsao-concursos`, não em `LAOS/projects/<name>/`
(Hard Rule #1 LAOS).

## Capabilities

4 capacidades primárias:

- `latade` — DuckDB, SQL, modelagem dimensional, DQ, docs.
- `ladesign` — UI do candidato, design system, wireframes.
- `lan8n` — cache, refresh, ingestão automatizada, alertas.
- `exa` — descoberta de provas anteriores, dados da banca.

1 capacidade secundária (routing explícito via LACOUNCIL):

- `laecon` — modelo preditivo empírico (BASIC até 2026-07-04).
  Handoff documentado em `projects/_meta/adr/ADR-005`.

2 capacidades platform (transversal):

- `context7` — lookup de libs (pandas, scikit-learn, xgboost) durante
  build.
- `github` — operações no child repo (issues, PRs, releases).

2 gaps conhecidos:

- `scrap` (severidade alta) — não existe como capability; vira
  capability só se aparecer em 3+ projetos (regra da constitution).
- `classical-ml` (severidade resolvido) — responsabilidade de laecon.

## Repo

- **Child repo (artefatos):** https://github.com/laurentaf/previsao-concursos
- **LAOS mirror (apenas contrato + spec):** `E:\projects\LAOS\projects\previsao-concursos\`
- **Workflow:** `dashboard-completo` (5 stages base + review)
- **Custom stages:** 4 (scrap, chunking, classical-ml, study-plan)
- **Origem LACOUNCIL:** proposta `bf91c407-94b8-463f-a0e5-3d73bfaf6c68`
  (modeling → laecon, 4/4 SIM, 2026-06-05); proposta `f82d6261-7592-46e8-8ca3-b7368dfb72a4`
  (latade MCP boot smoke-test, 4/4 SIM, 2026-06-05).
