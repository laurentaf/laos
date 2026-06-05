# Binding Conditions — capability-architect

**Status:** ACTIVE
**Date:** 2026-06-04
**Source proposal:** `2f42afe6-71d5-4ef8-a88a-1339d72ec501` (LACOUNCIL, supermaioria, 4/4 SIM, 100%)
**Consolidated from:** Original 7 binding conditions + 4 council amendments (data-architect, dashboard-designer, automation-engineer, delivery-reviewer)

These conditions are non-negotiable. They govern what `capability-architect` may do, what it must produce, and what is forbidden. They block promotion from BASIC to STABLE in G7 if unmet.

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

These define what `capability-architect` **must produce** for every new capability it scaffolds. G1–G8 abaixo se aplicam a **cada** capability nova implementada, não a este meta-projeto.

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
