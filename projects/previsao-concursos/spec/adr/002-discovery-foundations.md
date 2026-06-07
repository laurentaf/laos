# ADR-002: Foundations (D-001..D-005)

**Status:** Accepted
**Date:** 2026-06-05
**Stage:** 1 (discovery)
**Origem:** `artifacts/discovery/requirements.md` (data-architect,
subagente). Defaults aplicados em 2026-06-05 (user disse "continue"
sem responder às 4 open questions do §8.1).

---

## Status

Accepted — capturado após `dispatch` de data-architect em 2026-06-05
e congelado em `artifacts/discovery/requirements.md` (16.7 KB).

## Context

Antes do `data-model` (Stage 2), o `discovery` (Stage 1) precisava
cristalizar 5 decisões macro sobre o escopo da POC:

1. Janela temporal e split treino/validação.
2. Granularidade de evento (um caderno vs concurso inteiro).
3. Estratégia de tagging de sub_assunto (LLM vs determinístico).
4. Fontes de dados (oficial vs scraping de terceiro).
5. Stack de modelagem preditiva (latade vs laecon).

Essas decisões não podem ser revertidas no Stage 2 sem re-trabalho
significativo do pipeline, então são capturadas **aqui** e
referenciadas pelos ADRs subsequentes.

## Decision

### D-001: split temporal 2022-2024 treino, 2025-2026 validação

**Decisão:** treino nunca vê dados de validação. Janela móvel anual.

**Por que:** anti-leak (regra `project.yaml:108`). Concursos da
FCC/FGV 2022-2024 são ~3 anos de histórico suficiente para o modelo
empirico; 2025-2026 vira out-of-sample test.

**Consequência:** o tamanho efetivo do dataset de treino é menor que
o total de concursos disponíveis; trade-off aceito por ser regra
de negócio (não negociável).

### D-002: cada caderno distinto vira `evento_id` próprio

**Decisão:** Manhã/Tarde e Tipos 1-4 do mesmo edital geram
múltiplos `evento_id`, não um único.

**Por que:** a banca pode distribuir pesos diferentes por caderno
(p.ex., Auditor Fiscal da RFB tem 2 cadernos distintos no mesmo
edital). Tratar como evento único mascara essa distribuição.

**Consequência:** a cardinalidade de `silver_eventos` é maior que
o número de concursos; impacto no HARNESS-002 (dedup) que precisa
incluir `caderno_tipo` na chave de deduplicação.

### D-003: tagging de sub_assunto via hierarquia do edital + sinônimos (LLM proibido)

**Decisão:** tagging é determinístico. Hierarquia do edital
(matemática) + dicionário de sinônimos (curado manualmente).

**Por que:** regra `project.yaml:107` — LLM em escala é inviável
(custo + latência + reprodutibilidade). Hierarquia + sinônimos é
tratamente bom para FCC/FGV (edital padronizado).

**Consequência:** o dicionário de sinônimos vira **artefato
versionado** (`artifacts/data/dict/sinonimos.csv`) e precisa de
curadoria periódica. Trade-off aceito: cobertura ~80% do qconcursos
em vez de ~95%, mas sem dependência de LLM em produção.

### D-004: NÃO usar qconcursos.com.br como fonte primária (apenas validação cruzada)

**Decisão:** fontes primárias são FCC oficial (`concursosfcc.com.br`)
e FGV oficial (`conhecimento.fgv.br`). qconcursos entra como
**validação cruzada opcional** (taggeamento de sub_assunto já
pronto para conferir cobertura).

**Por que:** qconcursos tem ToS provavelmente proibindo scraping
agressivo. Risco jurídico para a POC (mesmo local) é desnecessário
— FCC/FGV oficiais cobrem o necessário.

**Consequência:** perdemos ~30% da cobertura de tagging que
qconcursos daria. Aceito pelo §"Probabilidades são empíricas, não
causais" (constitution.md §Principles #1).

### D-005: ML preditivo via laecon (NÃO latade)

**Decisão:** capability `laecon` é responsável pelo modelo preditivo.
LATADE cobre apenas data prep / DQ / SQL / DuckDB.

**Por que:** laecon tem stack próprio (pandas, scikit-learn, xgboost,
shap, optuna) já instalada em `E:\projects\laecon\.venv` (BASIC
até 2026-07-04). Latade é SQL-first; ML é foreign territory.

**Consequência:** routing `modeling` no registry foi atualizado
via LACOUNCIL `bf91c407-94b8-463f-a0e5-3d73bfaf6c68` para
`primary: [latade, laecon]`. ADRs do LATADE (`projects/_meta/adr/ADR-005`)
documentam o handoff + fallback para `not_implemented_yet`.

## Alternatives

### A) Tudo via latade (rejeitado)

Forçar latade a implementar ML preditivo via SQL window functions.

**Prós:** menos capabilities.
**Contras:** viola Art. VIII (anti-abstraction); SQL não é a
ferramenta certa para xgboost/shap; expertise de modelagem está em
laecon, não em latade.

### B) ML via terceiro (Prophet, scikit-learn direto, etc) (rejeitado)

Pular as capabilities e usar libs direto.

**Prós:** speed.
**Contras:** viola Hard Rule #1 LAOS (capability não pode ser
implementada inline em `projects/<name>/`); sem reuso entre
projetos.

### C) ML via laecon (aceito)

Routing explícito `modeling → [latade, laecon]`.

**Prós:** separação clara; reuso; laecon tem a stack.
**Contras:** laecon é BASIC até 2026-07-04 — tools podem retornar
`not_implemented_yet`. Mitigado pelo fallback documentado em
`projects/_meta/adr/ADR-005`.

## Consequences

- (+) Routing determinístico (`registry/needs-to-capabilities.yaml`
  `modeling.primary: [latade, laecon]`).
- (+) 5 decisões cristalizadas; re-trabalho evitado em Stage 2/3.
- (+) Constitution §Principles (LLM proibido, split temporal,
  probabilidades empíricas) está alinhada com D-001..D-005.
- (-) laecon em BASIC significa risco de tools `not_implemented_yet`
  no Stage 4 (build). Mitigado por fallback documentado.
- (-) Dicionário de sinônimos precisa de curadoria contínua (D-003).
