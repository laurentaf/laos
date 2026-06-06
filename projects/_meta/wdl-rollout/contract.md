# Contract — wdl-rollout (meta-projeto WDL v1)

Este contrato é a versão em prosa de `projects/_meta/wdl-rollout/project.yaml`.
É a "promessa do projeto" legível sem YAML. Cite este arquivo quando
precisar de uma referência rápida ao escopo; cite `project.yaml` quando
precisar de campos estruturados.

---

## Brief

Entregar a primeira versão do WDL (Workflow Discipline Layer) — um
subagente read-only `workflow-decomposer` que emite um verdict assinado
antes de qualquer dispatch de especialista — e adicionar ao AGENTS.md
do orchestrator o Hard Rule #8 que torna o dispatch de
workflow-decomposer obrigatorio. Combinação das propostas LACOUNCIL
`a4fe9faa` (WDL v1) e `7fd94c1a` (Charter P0), ambas supermaioria
4/4 SIM, 2026-06-06. 14 condições vinculantes da fase 4 do Conselho
(8 WDL + 6 Charter P0) ficam embedded como P0-blocking clauses no
`wdl-contract.yaml` (pinned `wdl_version: 1`) e nos scripts que
operacionalizam o gate.

## Needs

- improvement
- governance
- investigation

## Capabilities

- **lacouncil** — primary; surface para `get_proposal`, `record_project`, `detect_patterns`.
- **context7** — library lookups durante scaffold (FastMCP, DuckDB).
- **github** — reservado para follow-ups (não usado neste rollout).

## Repo

Self-hosted. Meta-projeto sem child repo. O agent file vive em
`.opencode/agent/workflow-decomposer.md`; o contrato operacional em
`workflows/wdl-contract.yaml`; a tabela de signatures em
`memoria/lacouncil.duckdb.wdl_signatures`; os meta-artifacts em
`projects/_meta/wdl-rollout/`. A alteração estrutural do AGENTS.md
vive no próprio LAOS.

## Deliverables (resumo)

**Part 1 — WDL v1 (proposal a4fe9faa):** 10 deliverables cobrindo o
agent file, o contrato, a migration do DuckDB, o opencode.jsonc, os
scripts de preflight + boot-check, o ADR-011, e a adição de G10 ao
binding-conditions.md do capability-architect.

**Part 2 — Charter P0 (proposal 7fd94c1a):** 6 deliverables cobrindo
as 4 sub-edits de AGENTS.md (Hard Rule, topology, Your loop, Tools),
o ADR-012, a adição de G11 ao binding-conditions.md, e a WDL section
em `delivery-reviewer.md`.

**Part 3 — Self-verification:** 3 deliverables — boot check PASS,
preflight PASS, e handoff explícito ao delivery-reviewer para G4
sign-off (sem auto-verificação).

Total: 19 deliverables. (Brief list above is 16; the diff is that
some deliverables in Part 1 are bundled in capability-architect
binding-conditions.md or scripts. See project.yaml for the
authoritative list.)

## Regime

A (LACOUNCIL 391a8179) — mudanças estruturais commit+push within
session após delivery-reviewer G4 sign-off. capability-architect
implementa localmente; orchestrator commita + pusha ao GitHub na
mesma sessão. Capability-architect NÃO se auto-valida no G4.

## Status

- `M0_entregue_local` (working tree 2026-06-06).
- Próximo: delivery-reviewer G4 BASIC sign-off.
- 30-day window: BASIC → STABLE até 2026-07-06.
- 14 conditions vinculantes, 0 completed, 14 blocking_stable.

## Cross-references

- Proposals: `a4fe9faa-4d50-4668-845a-ef64f1d41c36`, `7fd94c1a-d21d-49cc-a0e6-07c07c716e73`
- ADRs: ADR-011 (WDL), ADR-012 (Charter P0)
- Binding conditions: `projects/_meta/capability-architect/binding-conditions.md` (G10, G11)
- WDL contract: `workflows/wdl-contract.yaml` (pinned wdl_version: 1)
- Precedente: `projects/_meta/capability-architect/project.yaml`
- Source of truth: `workflows/wdl-contract.yaml`
