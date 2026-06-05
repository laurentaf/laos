# Capability Evolution — capability-architect

**Status:** M0 COMPLETE (G4 BASIC sign-off passed 2026-06-05; M1 deadline: 2026-07-04)
**Created:** 2026-06-04
**Proposal:** `2f42afe6-71d5-4ef8-a88a-1339d72ec501` (LACOUNCIL, supermaioria, aprovada 2026-06-04 — 4/4 SIM, 100%)
**Deadline BASIC→STABLE:** 2026-07-04 (+30 dias)
**Owner:** `.opencode/agent/capability-architect.md` (agent file) + `projects/_meta/capability-architect/` (meta-artifacts)

---

## Capability Info

| Field | Value |
|-------|-------|
| Name | capability-architect |
| Type | **meta-subagent** (NOT a domain capability — no MCP server, no capability repo) |
| Status atual | BASIC (M0 em progresso) |
| Status target | STABLE |
| Domínio | transversal (estrutural) |
| Tracking issue | este arquivo + LACOUNCIL proposal `2f42afe6-...` |
| Meta-projeto | `projects/_meta/capability-architect/project.yaml` |
| ADR | `projects/_meta/adr/ADR-003-capability-architect-creation.md` |
| Binding conditions | `projects/_meta/capability-architect/binding-conditions.md` (R1-R5 + G1-G8, 13 condições) |

---

## Why

LACOUNCIL aprovou recentemente capacidades novas (LAECON foi a 1ª que chegou a BASIC), mas a implementação caiu sobre o orchestrator + capability repo ad-hoc. Cada capability nova inventou suas próprias binding conditions (LAECON teve 17 ad-hoc). Isso não escala:

- **Conflito de interesse:** Orchestrator é quem propõe + convence o Conselho + implementa. Separação de funções violada.
- **Qualidade irregular:** Sem template, cada capability nova reinventa a roda.
- **Feedback loop lento:** Subagentes de projeto (data, dashboard, automation) não são desenhados para meta-projeto.
- **delivery-reviewer sem cobertura para meta-projetos:** Hoje só valida projetos de domínio.

A solução: um subagente dedicado, com escopo estrito, que implementa **somente** o que o Conselho já aprovou. 4 membros do Conselho votaram SIM com 4 emendas convergentes (todas integradas em `binding-conditions.md`).

---

## Escopo (consolidado pós-Conselho)

### Dentro do escopo

- **Implementação de mudanças estruturais APROVADAS pelo Conselho:**
  - Novas capabilities (criar `../<name>/` repo, MCP server, KB, Constitution skeleton, pyproject, README, .gitignore).
  - Novas entradas em `registry/capabilities.yaml` e `registry/needs-to-capabilities.yaml`.
  - Novas entradas em `.opencode/opencode.jsonc` para novos MCP servers.
  - Novos knowledge entries em `knowledge/`.
  - Novos workflow templates em `workflows/`.
  - Novos skill directories em `.opencode/skill/`.
  - Novos meta-projetos em `projects/_meta/`.
- **Geração dos meta-artifacts:** `project.yaml`, ADR, capability-evolution tracking.
- **Aplicação do scaffold template padronizado** (G1–G8 abaixo) — toda capability nova nasce BASIC, 30d para STABLE.
- **Handoff para `delivery-reviewer`** em dois gates: BASIC sign-off (light, G4) e STABLE sign-off (full, G8).

### Fora do escopo (separação de funções)

- **Não propõe mudanças estruturais.** Investigação + proposta continuam do orchestrator + LACOUNCIL.
- **Não faz trabalho de projeto.** Sem SQL, sem dashboards, sem workflows n8n, sem modelos ML. Esses domínios continuam sendo dos subagentes de projeto.
- **Não vota no Conselho.** Capability-architect implementa; o Conselho delibera.
- **Não altera o prompt de outro subagente.** Se a implementação precisar, reporta ao orchestrator (vira nova proposta LACOUNCIL).

---

## Condições vinculantes (13 itens consolidados)

Estas condições foram acordadas na votação LACOUNCIL. **Bloqueiam a promoção a STABLE em M1** se não forem atendidas.

### Section A — Restrições estruturais (5 vinculantes, R1–R5)

| ID | Condição | Origem |
|----|----------|--------|
| **R1** | **Gate pós-aprovação obrigatória.** `lacouncil.get_proposal()` deve retornar `status == "aprovada"` antes de qualquer escrita. | Proposta original |
| **R2** | **Não escreve artefatos de projeto.** Sem SQL, dashboards, workflows n8n, modelos ML. | Proposta original |
| **R3** | **Não vota no Conselho.** Separação de funções estrita. | Conselho (todas as 4 vozes) |
| **R4** | **Não propõe mudanças estruturais.** Originação é do orchestrator + LACOUNCIL. | Proposta original |
| **R5** | **Não altera prompt de outro agente** sem aprovação. | Inferido (R3+R4) |

### Section B — Quality gates por capability nova (8 vinculantes, G1–G8)

| ID | Condição | Origem |
|----|----------|--------|
| **G1** | **Observability contract** — todo MCP server expõe `health` + `list_supported_operations` desde o dia 1. | **automation-engineer** (emenda) |
| **G2** | **Handoff Boundaries** na KB inicial — seção explícita + ≥ 2 exemplos de routing. | **data-architect** (emenda) |
| **G3** | **Domain-specialist review** do KB + contracts antes do delivery-reviewer. | **dashboard-designer** (emenda) |
| **G4** | **BASIC sign-off** antes de expor em `registry/needs-to-capabilities.yaml` para routing real. | **delivery-reviewer** (emenda) |
| **G5** | **Registry + opencode.jsonc atualizados** com `status: BASIC`. | Proposta original |
| **G6** | **Capability-evolution tracking file** segue o template. | Proposta original |
| **G7** | **ADR** documentando rationale, formato ADR-001. | Proposta original |
| **G8** | **Status BASIC, 30d para STABLE.** | Proposta original (paralelo à LAECON) |

**Total:** 5 + 8 = **13 condições vinculantes**. Detalhamento em `binding-conditions.md`.

---

## Quality Gates deste meta-projeto (M0–1..M0–9)

| Gate | Descrição | Status (2026-06-04) |
|------|-----------|---------------------|
| **M0-1** | Agent file `.opencode/agent/capability-architect.md` criado | ✅ entregue |
| **M0-2** | `projects/_meta/capability-architect/project.yaml` criado | ✅ entregue |
| **M0-3** | `binding-conditions.md` com R1-R5 + G1-G8 + mapeamento de 4 emendas | ✅ entregue |
| **M0-4** | `capability-evolution.md` (este arquivo) | ✅ entregue |
| **M0-5** | ADR-003 publicado, formato ADR-001 | ✅ entregue |
| **M0-6** | `AGENTS.md` topology atualizada (5 → 6 agentes) | ✅ entregue |
| **M0-7** | `.opencode/agent/orchestrator.md` menciona capability-architect | ✅ entregue |
| **M0-8** | `lacouncil.record_project()` chamado (project_id `30c9521a-8a50-40f3-9b6f-eb9f01722af8`) | ✅ entregue |
| **M0-9** | `delivery-reviewer` validou M0-1..M0-8 contra `binding-conditions.md` + `padroes-entrega.md` (3 passes, final DELIVERABLE) | ✅ entregue_2026-06-04 |
| **M0-10** | G4 BASIC sign-off da proposta `f9b636fc` (SDD scaffold Missao 0) — delivery-reviewer DELIVERABLE, 15/17 verified, 0 VIOLATED | ✅ entregue_2026-06-05 |
| **M0-11** | ADR-008 publicado documentando a mudanca + template README.md para spec/adr/ (advisory do reviewer coberto) | ✅ entregue_2026-06-05 |

---

## Evolution Plan

| Milestone | Descrição | Deadline | Status |
|-----------|-----------|----------|--------|
| **M0** | Scaffold completo deste meta-projeto | 2026-06-04 | ✅ completo (2026-06-05) |
| **M1 (STABLE)** | Promoção a STABLE após 30d + delivery-reviewer STABLE sign-off + ≥ 1 uso real em capability scaffolding | 2026-07-04 | ⏳ |
| **M2** | Primeira capability real implementada por capability-architect (vai ser a próxima a ser aprovada) | ~2026-07-15 | ⏳ |
| **M3+** | Refinamento do scaffold template baseado em lições aprendidas de M2 | sob demanda | ⏳ |

---

## Projetos que disparam evolução

| Projeto | Data primeira dispatch | Status | Nota |
|---------|----------------------|--------|------|
| capability-architect (este) | 2026-06-04 | M0 completo | Scaffold do meta-agente + 13 condicoes vinculantes |
| SDD scaffold Missao 0 (f9b636fc) | 2026-06-05 | G4 DELIVERABLE | 23 arquivos tocados, ADR-008, template README.md |

---

## Fontes de grounding

| Fonte | Tipo | Uso |
|-------|------|-----|
| LAECON capability-evolution (precedente) | meta-projeto | Referência para o scaffold template (com adaptações) |
| ADR-001 (formato) | adr | Formato de ADR seguido por ADR-003 |
| ADR-002 (precedente) | adr | Contexto do regime de capabilities |

---

## Bloqueadores

- Nenhum no momento. M0 completo. Aguardando M1 (STABLE) em 2026-07-04.

---

## Notas

- **4 emendas convergiram de 4 ângulos diferentes** — sinal forte de que o gap era real e a solução cobre o problema. Nenhuma emenda foi rejeitada.
- **Separação de funções é o princípio fundador**: orchestrator propõe + Conselho delibera + capability-architect implementa + delivery-reviewer valida.
- **13 condições vinculantes** substituem as 17 ad-hoc da LAECON. A próxima capability nova vai herdar o template, não inventar novas condições.
- **R5 (não alterar prompt de outro agente)** é a única condição *inferida* (não veio das 4 emendas nem da proposta original). Se a comunidade discordar, vira proposta de revogação em M1 ou M2.
- **Basic window de 30 dias** é conservador mas necessário: capability-architect é o primeiro subagente meta-estrutural do LAOS, e o Conselho precisa de uma janela para observar se a separação de funções funciona na prática.
- **`delivery-reviewer` ganha cobertura para meta-projetos** (G4 + G8). Hoje só validava projetos de domínio.
