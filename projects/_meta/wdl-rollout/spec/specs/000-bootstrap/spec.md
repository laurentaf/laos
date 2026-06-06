# SPEC-001: WDL v1 bootstrap (workflow-decomposer subagent + Charter P0 hard rule)

**Status:** ACEITO
**Version:** 1.0
**Owner:** orchestrator (Regime A push) + capability-architect (scaffold)
**Origem:** Propostas LACOUNCIL `a4fe9faa-4d50-4668-845a-ef64f1d41c36` (WDL v1) +
`7fd94c1a-d21d-49cc-a0e6-07c07c716e73` (Charter P0), ambas supermaioria 4/4 SIM,
2026-06-06.

---

## 1. Contexto

O LAOS orchestrator recebe pedidos de projeto (ex.: "make posts for my
LinkedIn") e pula direto para o trabalho: edits inline, dispatching
de especialistas sem analisar o plano, ou skipping de decomposição.
A causa-raiz tripla:

1. Não existe gate que force o orchestrator a despachar um planner
   primeiro.
2. Só existe restraint estrutural (SG-2, proposal 70decf5e) que
   bloqueia writes ruins a paths estruturais do LAOS — não shapa
   o flow de decisão do orchestrator.
3. `AGENTS.md` §"Your loop" descreve o workflow em 5 steps mas
   não tem surface de enforcement entre needs resolution e
   specialist dispatch.

A 4ª e 5ª raízes: o project count está crescendo; usuários trazem
projetos multi-capability (LinkedIn content = brainstorm + writing +
design + automation); o trabalho de PM do orchestrator é real mas
não tem ferramenta. WDL v1 (workflow-decomposer + 3-Q granularity
gate) é a solução, votada 4/4 supermaioria em 2026-06-06.

## 2. Decisão inicial

Adotar dois artefatos novos:

### (a) workflow-decomposer subagent

Subagent read-only com MCP wall `lacouncil.*` only. Emite 3 arquivos
assinados por plan: `analysis.md`, `plan.json`, `verdict.yaml`.
Verdict tri-state: `READY | DEFER | ESCALATE`. Stateless entre
planos. Não propõe, não vota, não muta registry.

### (b) Charter P0 hard rule

Hard Rule #8 em `AGENTS.md`: orchestrator MUST invoke
workflow-decomposer before specialist dispatch. Trust-score penalty
no orchestrator (`-0.1/skip`, `-0.3 max/plan`, `-0.5 max/session`)
se o gate for burlado. Bypass requer manifest overlay + user
confirmation + cost.

### (c) Operating contract + signing

`workflows/wdl-contract.yaml` pinned `wdl_version: 1`. 14 conditions
vinculantes (8 WDL + 6 Charter P0) embedded como P0-blocking clauses.
Signatures em `memoria/lacouncil.duckdb.wdl_signatures` (idempotente).

### (d) Preflight + boot-check

`scripts/preflight_check.py` ganha sub-check `wdl-gate` com 4
sub-criteria (a)-(d). `scripts/subagent_boot_check.py` ganha entry
`workflow-decomposer` com 7-dim schema.

## 3. Critérios de pronto (Definition of Done — M0)

| ID | Critério | Como verificar |
|----|----------|----------------|
| **G0-1** | 16 deliverables entregues em working tree | `git status` mostra 16 paths modificados/criados; nenhum com erro de sintaxe |
| **G0-2** | Boot check workflow-decomposer PASS | `uv run python scripts/subagent_boot_check.py workflow-decomposer --project-name wdl-rollout` exit 0 |
| **G0-3** | Preflight projects/_meta/wdl-rollout PASS | `uv run python scripts/preflight_check.py projects/_meta/wdl-rollout` exit 0; 6/6 checks rodam |
| **G0-4** | DuckDB migration idempotente | Re-rodar `scripts/migrate_lacouncil_wdl_signatures.py` produz "OK" idêntico |
| **G0-5** | Arithmetic capability-architect/project.yaml | preflight 14 → 16 sem off-by-N; `conditions_total == sum(condicoes_vinculantes.*)` |
| **G0-6** | Capability-architect does NOT self-verify G4 | Nenhuma chamada de delivery-reviewer pelo capability-architect; handoff explícito no return message |
| **G0-7** | Regime A push pos-sign-off | Após G4 sign-off, orchestrator commita + pusha na mesma sessão; `git log --oneline` no remote confirma |

## 4. Acceptance Criteria — para o G4 BASIC sign-off (delivery-reviewer)

O delivery-reviewer valida 16 deliverables contra o
`14-cond traceability matrix` no return message. Cada cond das 14
implementation conditions deve estar mapeada para um deliverable
que a satisfaz. Ausência de mapping → P0 cite.

| Item | Validador | Critério |
|------|-----------|----------|
| MCP wall (lacouncil.* only) | reviewer | Charter WDL-R1 enumera as denials; agent file frontmatter tem external_directory restrito |
| Verdict schema (READY/DEFER/ESCALATE) | reviewer | `workflows/wdl-contract.yaml` §verdicts.states enuncia os 3 estados; sample tree `artifacts/wdl/<plan-id>/` matches |
| Preflight wdl-gate 4 sub-criteria | reviewer | `scripts/preflight_check.py` §check_wdl_gate implementa (a)-(d); anti-backdating testável |
| AGENTS.md 4 sub-edits | reviewer | Hard Rule #8, topology entry, §"Your loop" subsection, §"Tools" clarifier — todos presentes |
| 14 implementation conditions traceability | reviewer | Cada cond mapeada para 1+ deliverable; lacuna = P0 cite |
| ADR-011 + ADR-012 formato | reviewer | Seguem ADR-001; Contexto, Decisão, Alternativas, Consequências, Status, Date, Decisor |
| arithmetic 14 → 16 | reviewer | `capability-architect/project.yaml` arithmetic passa; preflight 6/6 |
| DuckDB wdl_signatures table | reviewer | `DESCRIBE wdl_signatures` retorna as 6 colunas esperadas; migration idempotente |

## 5. Cross-references

- Proposta LACOUNCIL: `a4fe9faa-4d50-4668-845a-ef64f1d41c36` (WDL v1)
- Proposta LACOUNCIL: `7fd94c1a-d21d-49cc-a0e6-07c07c716e73` (Charter P0)
- LACOUNCIL Regime A: `391a8179-5a16-4b69-a3a3-d4ca1b20c2c3`
- Binding conditions capability-architect: `projects/_meta/capability-architect/binding-conditions.md`
  (G10 + G11 adicionadas neste rollout; total 16)
- Capability-evolution template: `projects/_meta/capability-evolution/TEMPLATE.md`
- Padrões de entrega: `knowledge/padroes-entrega.md` P0 (PR-1, preflight, boot check, ADR-mínimo-1)
- SDD principles: `knowledge/sdd-principles.md` §2 (matriz per-file)
- Precedente: capability-architect (M0-1..M0-9), laecon-capability
- Source of truth operacional: `workflows/wdl-contract.yaml` (pinned wdl_version: 1)

## 6. Refresh Strategy

Não há refresh runtime — WDL é estático (wdl_version: 1). Mudanças
no contrato exigem nova proposta LACOUNCIL supermaioria. v2 (se
introduzida) coexists com v1 por um release cycle antes de v1
ser deprecated.
