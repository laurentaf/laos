# ADR — Architecture Decision Records

**Status inicial:** vazio (este arquivo é o índice).

Este é o **índice** de ADRs do projeto `previsao-concursos`. Foi
criado vazio na Missão 0 (proposta LACOUNCIL `f9b636fc`, 2026-06-05)
e vai sendo populado à medida que decisões são tomadas em cada
estágio do workflow `dashboard-completo`.

## Como adicionar uma ADR

1. Copie `spec/adr/_template.md` para `spec/adr/NNN-<slug>.md`
   (NNN = próximo número disponível, slug = kebab-case curto).
2. Preencha as seções: Status, Context, Decision, Alternatives,
   Consequences.
3. Adicione uma linha neste índice (em ordem cronológica).
4. Atualize `spec/todo.md` marcando a decisão correspondente.
5. Commit no child repo (não em LAOS).

## Índice

- `001-medallion-data-model.md` — D-006..D-010 (8 tabelas, FK chain).
- `002-discovery-foundations.md` — D-001..D-005 (split temporal, evento_id,
  tagging LLM-free, sem qconcursos scraping, ML via laecon).

## Status

Atualmente o índice contém **2 ADRs** (acima). O gate
`subagent_boot_check.py` 6ª dimensão (sub-check `first-real-adr`)
conta arquivos `.md` em `spec/adr/` excluindo `_template.md` e
`README.md`. Threshold: > 0 ADRs reais.
