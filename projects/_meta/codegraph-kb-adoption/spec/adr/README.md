# ADR Index

Arquivos ADR deste projeto usam o formato `NNN-<slug>.md` onde:
- `NNN` é um número sequencial a partir de 013 (011 e 012 usados no WDL rollout)
- `slug` é kebab-case descritivo

## ADRs

| # | Título | Status | Stage |
|---|---|---|---|
| ADR-013 | Adotar framework de eval A/B | proposed | Stage 1 |
| ADR-014 | Sufficiency como critério P0 de output de tool | proposed | Stage 2 |
| ADR-015 | Doutrina suficiência-sobre-steering | proposed | Stage 3 |

## Como adicionar um ADR

1. Criar arquivo `spec/adr/NNN-<slug>.md` usando `_template.md`
2. Preencher contexto, decisão, alternativas, consequências
3. Citar provenance (arquivo do CodeGraph de origem)
4. Atualizar esta tabela

## Path canônico

Apenas `spec/adr/NNN-<slug>.md` — **nunca** `artifacts/decisions/`.
Isso é enforced pelo `laos-guards.ts` plugin (Hard Rule em padroes-entrega.md).