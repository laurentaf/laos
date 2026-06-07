# ADR-001: Medallion data-model (D-006..D-010)

**Status:** Accepted
**Date:** 2026-06-05
**Stage:** 2 (data-model)
**Origem:** `artifacts/data/model.md` (data-architect, subagente).

---

## Status

Accepted — capturado após `dispatch` de data-architect em 2026-06-05
e congelado em `artifacts/data/model.md` (19.3 KB).

## Context

Após o discovery (Stage 1) cristalizar 5 decisões (D-001..D-005)
sobre o problema (probabilidade empírica por banca/cargo), o
Stage 2 (data-model) precisa definir a **arquitetura de dados**
para suportar:

1. Ingestão de editais (HTML/PDF) e provas anteriores (PDF gabarito).
2. Normalização por banca, área, disciplina, assunto, sub-assunto.
3. Agregação por (banca, cargo, ano) com split temporal 2022-2024 / 2025-2026.
4. View gold congelada (snapshot) para o `study-plan` consumir.

O design precisa ser:
- Compatível com DuckDB (LATADE), sem dependência de Postgres/BigQuery.
- Idempotente (re-rodar com mesmo input produz mesmo output — Art. IV).
- Testável com HARNESS levels 1/2/3 (Art. II).
- Sem leitura cross-layer (Art. VI — silver não lê bronze direto).

## Decision

Adotar **8 tabelas** distribuídas em 3 camadas (medallion), com FK
chain estrita e 5 regras de DQ mecânicas:

### Fonte (3 tabelas)

- `bronze_editais_raw` — landing de editais raspados (HTML/PDF binary
  blob + URL + banca + data_publicacao + _ingested_at).
- `bronze_provas_raw` — landing de provas e gabaritos (PDF binary +
  URL + banca + caderno_tipo + _ingested_at).
- `bronze_qconcursos_tags_raw` — tags da qconcursos quando usadas como
  validação cruzada (não como fonte primária — ver D-004 do
  discovery).

### Enriquecimento (2 tabelas silver)

- `silver_concursos` — uma linha por `(banca, sigla, cargo, ano)`,
  deduplicada por URL do edital. FK opcional para `bronze_editais_raw.id`.
- `silver_eventos` — uma linha por **caderno** distinto de cada concurso
  (Manhã/Tarde, Tipo 1-4). Cada `evento_id` único. FK obrigatória para
  `silver_concursos.id`. Contém: caderno_tipo, total_questoes, total_paginas.

### Consumo (3 tabelas gold)

- `gold_matriz_cobranca` — uma linha por `(banca, cargo, materia, assunto,
  sub_assunto, ano)`, com `n_questoes` e `n_eventos`. Agregação anual.
- `gold_topicos_chave` — pré-agregação das 100 (banca, cargo, topico)
  mais frequentes (cache de leitura para o `study-plan`).
- `gold_predicoes_view` — view materializada que une `gold_matriz_cobranca`
  + features temporais (lag 1 ano, lag 2 anos) e expõe a probabilidade
  empírica final `p(sub_assunto | banca, cargo, ano)`.

### Decisões detalhadas

- **D-006:** `silver_eventos` separa cadernos (Manhã/Tarde, Tipo 1-4)
  porque a banca pode distribuir pesos diferentes por caderno.
- **D-007:** `gold_matriz_cobranca` agrega por ANO (não por concurso
  individual) para evitar flutuação de amostras pequenas.
- **D-008:** `gold_predicoes_view` é VIEW (não tabela) — recalcula on
  the fly a partir de `gold_matriz_cobranca`, mas é **snapshot-frozen**
  por data no `study-plan` consumer.
- **D-009:** Schema é `bronze_*` / `silver_*` / `gold_*` para fazer
  invariante de layer explícita no nome (Art. VI, sem cross-layer).
- **D-010:** Tabelas têm coluna `_ingested_at` e `_snapshot_date` para
  reprodutibilidade (Art. IV — idempotência).

## Alternatives

### A) Single big-table (sem medallion)

Tudo em uma tabela fato larga, sem separação de camadas.

**Prós:** simplicidade inicial.
**Contras:** viola Art. VI (cross-layer reads inevitáveis), impede
teste isolado de cada transformação, dificulta o versionamento de
schemas.

**Rejeitado** — viola Constitution Art. I e VI.

### B) Star schema puro (1 fato + N dimensões)

Modelo dimensional Kimball clássico.

**Prós:** BI-friendly, ferramentas OLAP direto.
**Contras:** POC não tem BI tool; a granularidade "um concurso tem
múltiplos cadernos" é mal modelada em star schema; probabilidade
empírica não precisa de SCD tipo 2.

**Rejeitado** — overhead desnecessário para o POC; pode ser
revisitado em M2 se houver migração para BI.

### C) Medallion (escolhido)

3 camadas (bronze / silver / gold) com 8 tabelas no total.

**Prós:** alinha com Constitution LATADE (Art. I, VI); separa
responsabilidades (Art. VIII); HARNESS por camada; cache gold
reduz custo de recálculo.
**Contras:** 8 tabelas é mais que "single big-table".

**Aceito** — custo de 8 tabelas é trivial em DuckDB local; benefícios
são estruturais.

## Consequences

- (+) Cada camada tem HARNESS próprio (HARNESS-001 ingestion,
  HARNESS-002 silver, HARNESS-003 gold).
- (+) `study-plan` consome apenas `gold_predicoes_view` + snapshot
  date — não precisa conhecer o pipeline.
- (+) `data-architect` (subagente) pode implementar em
  `../latade/src/pipelines/previsao_concursos/` sem ambiguidade.
- (-) 3 conjuntos de schemas para manter (mas validados pelo
  preflight `padroes-entrega.md` §"P0 - Dados").
- (-) View materializada precisa de strategy de refresh (D-008);
  implementado no Stage 5 (automate) via n8n cron mensal.
