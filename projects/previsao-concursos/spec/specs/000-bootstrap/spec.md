# SPEC-000: Bootstrap previsao-concursos (Missão 0)

**Status:** ACEITO
**Version:** 1.0
**Date:** 2026-06-05
**Owner:** Laurent
**Origem:** proposta LACOUNCIL `f9b636fc-5ca9-4860-94ca-3a6b43c6862c`
(unanimidade 4/4, 2026-06-05). Spec renomeada de `001-example` para
`000-bootstrap` para sinalizar que é a spec de bootstrap do projeto,
não uma feature.

---

## Contexto

O projeto `previsao-concursos` (POC) precisa de um **SDD scaffold**
mínimo antes do primeiro dispatch de subagente. A Missão 0 é
proposta LACOUNCIL `f9b636fc` e estabelece que:

1. Toda projeto LAOS tem `spec/constitution.md` (princípios),
   `spec/todo.md` (tracker desde Stage 0), `spec/adr/` (registro
   de decisões), `spec/harness/` (catálogo de validações),
   `spec/specs/000-bootstrap/spec.md` (esta spec), `contract.md`
   (espelho do `project.yaml` em prosa), `README.md` (≥ 400 chars).
2. Para projetos com `needs: dashboard` ou `design`, exige-se
   adicionalmente `spec/design-direction.md` (≥ 300 chars).
3. Gate mecânico: `subagent_boot_check.py` 6ª dimensão (sub-check
   `skeleton`) valida tamanho mínimo e headers canônicos de cada
   arquivo (matriz per-file em `knowledge/sdd-principles.md` §2).

A spec-000 captura **a decisão de adotar o scaffold** e define o
contrato mínimo do projeto LAOS para o workflow `dashboard-completo`.

## Decisões

### D-Scaffold-001: adotar a matriz per-file de `knowledge/sdd-principles.md` §2

Cada arquivo do scaffold atende um mínimo de chars e 1+ headers
canônicos (regex case-insensitive, multi-line). Mínimo:

| Arquivo | Min chars | Headers |
|---|--:|---|
| `spec/constitution.md` | 400 | `^##\s+Princ`, `^##\s+Scope`, `^##\s+Non.?goals` |
| `spec/todo.md` | 100 | `-\s+\[\s*\]` (≥ 1 task aberta) |
| `spec/adr/_template.md` | 0 (stub) | n/a |
| `spec/adr/README.md` | 80 | `^#\s+ADR`, `(vazio\|empty\|\bindex\b)` |
| `spec/harness/_template.md` | 0 (stub) | n/a |
| `spec/specs/000-bootstrap/spec.md` | 400 | `^##\s+Contexto`, `^##\s+Decis`, `^##\s+Crit` |
| `contract.md` | 250 | `^##\s+Brief`, `^##\s+Needs?`, `^##\s+Deliverables?`, `^##\s+Capabilities?`, `^##\s+Repo` |
| `README.md` | 400 | `^##\s+O\s+que`, `^##\s+Como`, `^##\s+Onde` |
| `spec/design-direction.md` (condicional) | 300 | n/a |

**Por que:** consistência transversal entre projetos LAOS; auditoria
mecânica de regressões; alinhamento com LACOUNCIL `f9b636fc`.

### D-Scaffold-002: Constitution adaptada, não literal

`spec/constitution.md` parte do template LATADE (9 artigos), mas
**adiciona** um Art. 0 (Missão 0 obrigatória) e as 3 seções canônicas
(Principles / Scope / Non-goals) para satisfazer o gate. Princípios
macro (LLM proibido, split temporal, probabilidades empíricas) ficam
em `## Principles`, escopo em `## Scope`, anti-escopo em `## Non-goals`.

**Por que:** gate exige os 3 headers; projeto ganha princípio macro
legível sem reabrir os 9 artigos do LATADE.

### D-Scaffold-003: 2 ADRs reais escritas neste bootstrap

`spec/adr/001-medallion-data-model.md` captura D-006..D-010
(data-model stage). `spec/adr/002-discovery-foundations.md` captura
D-001..D-005 (discovery stage). A `spec/adr/README.md` é o índice
vazio no início e vai ganhando entradas à medida que ADRs são
escritas.

**Por que:** gate `first-real-adr` é **gated** — só ativa quando há
≥ 1 ADR real em `spec/adr/`. Como o projeto já tem decisões tomadas
em Stages 1 e 2, escrevemos 2 ADRs no bootstrap para satisfazer o
gate e cristalizar o histórico.

### D-Scaffold-004: templates LATADE como ponto de partida, não contrato

O `subagent_boot_check.py` aceita `_template.md` e `_template.md` do
HARNESS como `stub_by_design` (gate passa sem checar chars/headers).
Para os demais, o conteúdo é **editável** mas o **registry original**
(`registry/spec-templates/`) é imutável (ver `registry/spec-templates/README.md` §"Política de imutabilidade").

**Por que:** separar autoridade (capability-architect mexe em
`registry/`; subagentes de projeto só mexem em `projects/<name>/`).

## Critérios de Aceitação

- [x] Os 9 arquivos do scaffold existem em `projects/previsao-concursos/`
      (8 fixos + 1 condicional `spec/design-direction.md`).
- [x] Cada arquivo satisfaz o `min_chars` do gate.
- [x] Cada arquivo satisfaz os `headers` regex do gate.
- [x] Templates `_template.md` (ADR e HARNESS) presentes como stub.
- [x] Pelo menos 2 ADRs reais em `spec/adr/`.
- [x] `subagent_boot_check.py` retorna exit code 0 no sub-check
      `skeleton` quando invocado para qualquer subagente do projeto.
- [x] `preflight_check.py` retorna exit code 0 quando invocado
      para `projects/previsao-concursos`.

## Referências

- `knowledge/sdd-principles.md` — princípio fundacional POC ≠ zero-shot,
  matriz per-file §2, política de imutabilidade §6.
- `knowledge/padroes-entrega.md` — checklist P0 §"Estrutura do projeto".
- `registry/spec-templates/README.md` — proveniência e política de drift.
- `projects/_meta/adr/ADR-005-modeling-routing-laecon.md` — decisão
  relacionada a `modeling` need (LACOUNCIL `bf91c407`).
- `projects/_meta/adr/ADR-006-mcp-boot-smoke-test.md` — decisão
  relacionada ao boot check 6ª dimensão (LACOUNCIL `f82d6261`).
