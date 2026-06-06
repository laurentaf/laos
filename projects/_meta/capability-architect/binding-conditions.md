# Binding Conditions — capability-architect

**Status:** ACTIVE
**Date:** 2026-06-04 (initial) / 2026-06-06 (G10 + G11 added)
**Source proposals:**
- `2f42afe6-71d5-4ef8-a88a-1339d72ec501` (LACOUNCIL, supermaioria, 4/4 SIM, 100%) — capability-architect creation
- `a4fe9faa-4d50-4668-845a-ef64f1d41c36` (LACOUNCIL, supermaioria, 4/4 SIM, 2026-06-06) — WDL v1
- `7fd94c1a-d21d-49cc-a0e6-07c07c716e73` (LACOUNCIL, supermaioria, 4/4 SIM, 2026-06-06) — Charter P0

**Consolidated from:** Original 7 binding conditions + 4 council amendments (data-architect, dashboard-designer, automation-engineer, delivery-reviewer) + 2 WDL amendments (a4fe9faa + 7fd94c1a)

These conditions are non-negotiable. They govern what `capability-architect` may do, what it must produce, and what is forbidden. They block promotion from BASIC to STABLE in G7 if unmet.

**Total: 16 conditions (5 restrições R1–R5 + 11 quality gates G1–G11).**

---

## Section A — Restrições estruturais (invioláveis)

These define what `capability-architect` **may NOT** do. Violating any of them is a structural violation, not a quality miss.

| ID | Rule | Source amendment |
|----|------|------------------|
| **R1** | **Gate pós-aprovação obrigatória.** O agente só pode executar após `lacouncil.get_proposal()` retornar `status == "aprovada"` para a `proposal_id` correspondente. Implementação sem proposta aprovada = violação. Ler `proposal_id` do prompt do orchestrator e validar antes de qualquer escrita. | Proposta original |
| **R2** | **Não escreve artefatos de projeto.** Não escreve SQL (LATADE), dashboards/design (LADESIGN), workflows N8N (LAN8N), modelos ML (LAECON/LAENGINE). Esses domínios continuam sendo dos subagentes de projeto. | Proposta original |
| **R3** | **Não vota no Conselho.** O capability-architect implementa; o Conselho delibera. Separação de funções estrita. Se uma nova proposta estrutural surgir durante a implementação (ex: a capability nova precisa de mais uma capability auxiliar), voltar ao orchestrator, NÃO auto-propor. | Conselho — separação de funções |
| **R4** | **Não propõe mudanças estruturais.** Investigação e proposta continuam sendo do orchestrator + LACOUNCIL. capability-architect consome propostas aprovadas; não origina. | Proposta original |
| **R5** | **Não altera o prompt de outro agente sem aprovação.** Se durante a implementação for necessário mudar `data-architect.md`/`dashboard-designer.md`/etc., parar e reportar ao orchestrator. Mudanças em outros agentes exigem nova proposta LACOUNCIL. | Inferido da R3+R4 — previne drift silencioso |

---

## Section B — Quality gates (obrigatórios por capability nova)

These define what `capability-architect` **must produce** for every new capability it scaffolds. G1–G11 abaixo se aplicam a **cada** capability nova implementada, não a este meta-projeto. G1–G9 são o conjunto histórico (criação do capability-architect); G10–G11 são os gates de implementação do WDL v1 (propostas a4fe9faa + 7fd94c1a, 2026-06-06).

| Gate | Description | Validation | Source amendment |
|------|-------------|------------|------------------|
| **G1** | **Observability contract no MCP server.** Todo MCP server scaffolded deve expor `health` (status + version) e `list_supported_operations` (catálogo tipado) desde o dia 1. Padrão LATADE/LAN8N. Sem isso, a capability nova é fail. | Smoke test dos dois tools via MCP client. | **automation-engineer** |
| **G2** | **KB inicial com Handoff Boundaries.** A KB inicial da nova capability deve incluir seção explícita "Handoff Boundaries" com: (a) lista de capabilities adjacentes, (b) exemplos concretos de needs que devem rotear para a nova vs. para as existentes, (c) sinais de que a nova está sendo subutilizada ou sobrecarregada. Sem essa seção, project agents podem criar dead zones ou canibalizar trabalho. | Reviewer confirma seção existe + tem ≥ 2 exemplos concretos. | **data-architect** |
| **G3** | **Domain-specialist review do KB + contracts.** Quando a nova capability cai num domínio que já tem subagente especialista (data-architect, dashboard-designer, automation-engineer, delivery-reviewer), esse especialista é revisor obrigatório do KB inicial e dos contratos de I/O **antes** da submissão ao delivery-reviewer. Capability-architect constrói a casa; o especialista decora o quarto. | Workflow explícito: KB draft → specialist review → delivery-reviewer. | **dashboard-designer** |
| **G4** | **BASIC sign-off antes de expor para routing.** Antes da capability nova aparecer em `registry/needs-to-capabilities.yaml` para roteamento real, deve passar por um "BASIC sign-off" mais leve que o STABLE sign-off: (a) MCP `health` + `list_supported_operations` smoke passa, (b) sem segredos, (c) registry entry em `capabilities.yaml` válido, (d) entry em `opencode.jsonc` presente, (e) KB seed não-vazio, (f) tests/smoke mínimo presente. Sem isso, project agents começam a rotear para uma capability não validada. | delivery-reviewer (light checklist) emite sign-off; capability-architect só então atualiza `needs-to-capabilities.yaml`. | **delivery-reviewer** |
| **G5** | **Registry + opencode.jsonc atualizados.** `registry/capabilities.yaml` ganha entry com `status: BASIC`, `kind: domain`, `repo`, `owns`. `.opencode/opencode.jsonc` ganha entry do MCP server. | Ambos os arquivos modificados antes do STABLE sign-off. | Proposta original |
| **G6** | **Capability-evolution tracking file.** `projects/_meta/capability-evolution/<name>.md` criado com a timeline BASIC→STABLE, gates G1-G8, condições vinculantes, e roadmap de milestones. Formato segue `capability-evolution/TEMPLATE.md` + precedente LAECON. | Arquivo existe e segue o template. | Proposta original |
| **G7** | **ADR documentando rationale.** `projects/_meta/adr/ADR-XXX-<name>-creation.md` com Contexto, Decisão, Alternativas, Consequências, Status, Date, Decisor. Formato segue ADR-001. | delivery-reviewer valida formato. | Proposta original |
| **G8** | **Status inicial BASIC, 30d para STABLE.** Toda capability nova nasce BASIC. A promoção a STABLE exige: (a) todas as condições vinculantes da proposta LACOUNCIL atendidas, (b) ≥ 1 projeto real usou a capability, (c) delivery-reviewer STABLE sign-off, (d) Constitution/KB não-placeholder, (e) `padroes-entrega.md` compliance. Prazo: 30 dias da primeira dispatch. | delivery-reviewer + LACOUNCIL tally. | Proposta original (paralelo ao regime LAECON) |
| **G9** | **Git sync obrigatório pós-sign-off.** Após delivery-reviewer emitir DELIVERABLE (G4 BASIC ou G8 STABLE), o orchestrator deve commitar e pushar as mudanças ao GitHub dentro da mesma sessão. A cadeia de autoridade está completa (Conselho aprovou + reviewer validou); gate adicional não é necessário. Regime A (LACOUNCIL 391a8179). | Commit+push executado; `git log` no remote confirma. | **LACOUNCIL 391a8179** (4/4 SIM, maioria, 2026-06-05) |
| **G10** | **WDL v1 implementation gate.** Capability-architect scaffolda a 1ª versão do Workflow Discipline Layer conforme proposta `a4fe9faa-4d50-4668-845a-ef64f1d41c36`. Componentes obrigatórios: (i) subagent `workflow-decomposer` com MCP wall `lacouncil.*` only; (ii) `workflows/wdl-contract.yaml` pinned `wdl_version: 1` com 8 WDL-IC (1–8) embedded como P0-blocking clauses; (iii) tabela `wdl_signatures` em `memoria/lacouncil.duckdb` via migration idempotente; (iv) entry `workflow-decomposer` em `.opencode/opencode.jsonc`; (v) sub-check `wdl-gate` em `scripts/preflight_check.py` com 4 sub-criteria (a)-(d); (vi) entry `workflow-decomposer` em `scripts/subagent_boot_check.py` (7-dim schema); (vii) ADR-011 publicado. Sign-off do delivery-reviewer **deve** citar o `exit_code` do preflight wdl-gate. | (i)-(vii) entregues; preflight exit 0; reviewer cita exit_code. | **LACOUNCIL a4fe9faa** (supermaioria 4/4 SIM, 2026-06-06) |
| **G11** | **Charter P0 implementation gate.** Capability-architect implementa a hard rule que torna dispatch do `workflow-decomposer` mandatório para o orchestrator, conforme proposta `7fd94c1a-d21d-49cc-a0e6-07c07c716e73`. Componentes obrigatórios: (i) Hard Rule #8 em `AGENTS.md` com 5 sub-regras (8.1 preflight mandatory / 8.2 trust-score penalty / 8.3 bypass cost / 8.4 exemption allowlist / 8.5 reviewer cites exit_code); (ii) topology entry do `workflow-decomposer`; (iii) subsection "WDL preflight gate" em `AGENTS.md` §"Your loop" entre step 2 e step 3 com `dispatch_payload_includes: [verdict.yaml, plan_id, verified_by]`; (iv) clarifier em `AGENTS.md` §"Tools you do NOT use" sobre `lacouncil.*` apenas para structural improvement (não project work); (v) WDL section em `.opencode/agent/delivery-reviewer.md` com 5 cite categories (missing_verdict, expired_exemption, post_dated_bypass, self_attested_verdict, missing_capability_gaps); (vi) ADR-012 publicado. | (i)-(vi) entregues; AGENTS.md diff válido; reviewer valida 5 cite categories. | **LACOUNCIL 7fd94c1a** (supermaioria 4/4 SIM, 2026-06-06) |

---

## Section C — Quality gates deste meta-projeto (capability-architect scaffolding)

These apply **once**, to the creation of `capability-architect` itself. After this meta-project is delivered, only Section A + B apply on a per-capability basis. **Canonical numbering: M0-1..M0-9** (matches `project.yaml` and `capability-evolution.md`).

| Gate | Description | Status (2026-06-04) |
|------|-------------|---------------------|
| **M0-1** | Agent file `.opencode/agent/capability-architect.md` criado, segue formato dos outros subagents (frontmatter + scope + namespaces + output rules + anti-patterns). | ✅ entregue |
| **M0-2** | Meta-project `projects/_meta/capability-architect/project.yaml` criado, segue formato LAECON meta-project. | ✅ entregue |
| **M0-3** | `binding-conditions.md` (este arquivo) com R1-R5 + G1-G8 + mapeamento das 4 emendas. | ✅ entregue |
| **M0-4** | Capability-evolution tracking `projects/_meta/capability-architect/capability-evolution.md` criado. | ✅ entregue |
| **M0-5** | ADR-003 publicado, formato ADR-001, referenciando este BC file. | ✅ entregue |
| **M0-6** | AGENTS.md topology section atualizado (5 → 6 agentes). | ✅ entregue |
| **M0-7** | Orchestrator agent file atualizado para mencionar capability-architect como dispatch target. | ✅ entregue |
| **M0-8** | LACOUNCIL.record_project() chamado (project_id `30c9521a-8a50-40f3-9b6f-eb9f01722af8`). | ✅ entregue |
| **M0-9** | delivery-reviewer validou M0-1..M0-8 contra este BC + `knowledge/padroes-entrega.md` (3 passes: inicial → 2 correções P0 → final DELIVERABLE). | ✅ entregue_2026-06-04 |
| **M0→M1** | Status do capability-architect promovido de BASIC a STABLE após 30 dias e ≥ 1 uso real. | ⏳ |

---

## Mapeamento: 4 emendas → BCs

| Emenda original | Onde foi consolidada |
|-----------------|----------------------|
| data-architect: "Handoff Boundaries" na KB | **G2** |
| dashboard-designer: "domain specialist review" | **G3** |
| automation-engineer: "health + list_supported_operations" | **G1** |
| delivery-reviewer: "BASIC sign-off gate" | **G4** |

Todas as 4 emendas foram integradas. Nenhuma foi rejeitada.

---

## Diferenças em relação à proposta original

1. **R5** (não altera prompt de outro agente) é nova, inferida da lógica R3+R4. Se a comunidade discordar, vira proposta de revogação.
2. **G2, G3, G4** são as emendas do Conselho consolidadas. A proposta original tinha uma única BC #4 (STABLE sign-off); agora há duas (G4 BASIC + STABLE na G8).
3. **G1** (observability contract) é da emenda do automation-engineer; não estava na proposta original.
4. Seção A (R1–R5) e Seção B (G1–G8) separaram "restrições estruturais" de "quality gates", porque têm naturezas diferentes: violar R1–R5 é má-fé; falhar G1–G8 é incompletude.

---

## Revogação / amendment

Qualquer mudança nestas condições exige nova proposta LACOUNCIL com estratégia **supermaioria** (regra de registry — paralelismo com a proposta original). Mudanças em R1–R5 podem exigir **unanimidade** (analogia com "fundamentos").
