# ADR-003: Criação do subagente `capability-architect`

**Status:** accepted
**Date:** 2026-06-04
**Decisor:** LACOUNCIL (supermaioria, 4/4 SIM, 100%)
**Proposal:** `2f42afe6-71d5-4ef8-a88a-1339d72ec501`

---

## Contexto

LACOUNCIL é o mecanismo de governança estrutural do LAOS. Quando o Conselho aprova uma proposta, alguém tem que implementar a mudança. Até hoje, esse trabalho caía sobre o **orchestrator** (o próprio proponente da proposta) + o capability repo afetado. Esse arranjo tem quatro problemas:

1. **Conflito de interesse:** O orchestrator propõe, convence o Conselho, e implementa. As três funções estão misturadas.
2. **Qualidade irregular:** Cada capability nova inventa suas próprias "binding conditions" (LAECON teve 17 ad-hoc). Sem template, a próxima vai inventar outras 17 diferentes.
3. **Feedback loop lento:** Os subagentes de projeto (`data-architect`, `dashboard-designer`, `automation-engineer`) são desenhados para usar `latade.*` / `ladesign.*` / `lan8n.*` MCPs — não para mexer em registry, `opencode.jsonc`, `knowledge/`, ou criar novos capability repos.
4. **Cobertura de validação ausente:** `delivery-reviewer` valida projetos de domínio contra `knowledge/padroes-entrega.md`, mas não tem template/checklist para validar **meta-projetos** (novas capabilities). LAECON passou sem esse gate formal.

### Precedente concreto

- **LAECON** (`cbe2d8ef`, 2026-06-04): 17 condições vinculantes ad-hoc. Serviu, mas não é reutilizável.
- **LAENGINE** (BASIC em evolução): mesma trajetória implícita, sem template.
- O **2º** capability nova vai repetir o problema. O **3º** vai explodir.

### Diagnóstico de routing

- Need `improvement` (criação de capability nova) → `lacouncil` (investiga, propõe, vota) ✓
- Need `implementation` (criar capability repo + registry + KB) → **NÃO HÁ SUBAGENTE** com esse escopo. Hoje é orchestrator + capability repo ad-hoc.

Atende os 3 critérios cumulativos para um novo subagente (paralelo aos critérios de `e9cd6dd8` para nova capability):
- Aparece em ≥ 1 padrão recorrente (vai repetir).
- Tem escopo próprio, distinto dos subagentes de projeto.
- Tem ações concretas (escrever agent file, registry, opencode.jsonc, KB, ADR).

---

## Decisão

Criar o subagente **`capability-architect`** (6º subagente da topologia do LAOS), com escopo estrito e separação de funções em relação ao orchestrator, Conselho, e subagentes de projeto.

### Posicionamento

- **Implementa, não propõe.** Investigação + proposta continuam do orchestrator + LACOUNCIL.
- **Implementa, não delibera.** Não vota no Conselho.
- **Implementa, não decora.** Não escreve SQL, dashboards, workflows n8n, ou modelos ML. Domain specialists continuam donos desses domínios.
- **Implementa meta, não projeto.** O escopo é registry, opencode.jsonc, knowledge, workflows, capability repos, projects/_meta/.

### Topologia resultante

| # | Subagente | Domínio | MCP primário |
|---|-----------|---------|--------------|
| 1 | orchestrator (primary) | composição | nenhum (MCPs via leitura) |
| 2 | data-architect | data | `latade.*` |
| 3 | dashboard-designer | design | `ladesign.*` |
| 4 | automation-engineer | automação | `lan8n.*` |
| 5 | delivery-reviewer | gate | nenhum (read-only) |
| **6** | **capability-architect** | **estrutural (meta)** | **`lacouncil.*`** |

### Separação de funções (princípio fundador)

```
                  ┌────────────────────────────┐
                  │      orchestrator          │
                  │  propões + convence o      │
                  │  Conselho + dispatch       │
                  └─────────────┬──────────────┘
                                │ proposta aprovada
                                ▼
   ┌────────────────────────────────────────────────┐
   │              LACOUNCIL Conselho                │
   │  4 subagentes votam (data, dashboard,           │
   │  automation, delivery)                         │
   └────────────────────┬───────────────────────────┘
                        │ aprovada
                        ▼
   ┌────────────────────────────────────────────────┐
   │         capability-architect (NOVO)            │
   │  implementa a mudança estrutural               │
   │  (registry, opencode.jsonc, KB, capability     │
   │  repo, ADR, tracking)                          │
   └────────────────────┬───────────────────────────┘
                        │ scaffold pronto
                        ▼
   ┌────────────────────────────────────────────────┐
   │           delivery-reviewer                    │
   │  BASIC sign-off (G4) + STABLE sign-off (G8)    │
   └────────────────────────────────────────────────┘
```

### Restrições estruturais (Section A de `binding-conditions.md`)

- **R1:** Gate pós-aprovação. `lacouncil.get_proposal() == "aprovada"` antes de qualquer escrita.
- **R2:** Não escreve artefatos de projeto.
- **R3:** Não vota no Conselho.
- **R4:** Não propõe mudanças.
- **R5:** Não altera prompt de outro agente.

### Quality gates por capability nova (Section B de `binding-conditions.md`)

- **G1:** Observability contract (`health` + `list_supported_operations`).
- **G2:** Handoff Boundaries na KB inicial.
- **G3:** Domain-specialist review do KB + contracts.
- **G4:** BASIC sign-off antes de expor para routing.
- **G5:** Registry + opencode.jsonc atualizados.
- **G6:** Capability-evolution tracking file.
- **G7:** ADR documentando rationale.
- **G8:** Status BASIC, 30d para STABLE.

### Localização

- Agent file: `.opencode/agent/capability-architect.md` (paralelo a `data-architect.md`).
- Meta-artifacts: `projects/_meta/capability-architect/` (paralelo a `projects/_meta/laecon-capability/`).
- Sem capability repo. Sem MCP server. Sem entrada em `registry/capabilities.yaml` (registry é para domain capabilities).
- Entrada em `AGENTS.md` topology section.

### Status e evolução

- **Status inicial:** BASIC.
- **Deadline BASIC→STABLE:** 2026-07-04 (+30 dias).
- **Tracking:** `projects/_meta/capability-architect/capability-evolution.md`.
- **Binding conditions:** `projects/_meta/capability-architect/binding-conditions.md`.
- **Meta-projeto:** `projects/_meta/capability-architect/project.yaml` (este arquivo).

---

## As 4 emendas do Conselho (consolidadas)

| De | Emenda | BC resultante |
|----|--------|---------------|
| `data-architect` | "KB inicial deve ter seção Handoff Boundaries com exemplos concretos" | **G2** |
| `dashboard-designer` | "Domain-specialist deve revisar KB + contracts antes de delivery-reviewer" | **G3** |
| `automation-engineer` | "Todo MCP server deve expor `health` + `list_supported_operations` desde o dia 1" | **G1** |
| `delivery-reviewer` | "BASIC sign-off (light) antes de expor para routing, STABLE sign-off (full) para promoção" | **G4 + G8** |

**4 emendas, 4 ângulos, 1 sinal:** os 4 membros do Conselho viram o mesmo gap de "sem template + sem gate intermediário" de perspectivas diferentes. Todas integradas em `binding-conditions.md`; nenhuma rejeitada.

---

## Alternativas Consideradas

1. **Manter o orchestrator como implementador.** Rejeitado. Conflito de interesse direto (proponente + implementador) e nenhuma das 4 vozes do Conselho apoiou.

2. **Estender a topologia com um agente generalista "do everything" (e.g., "laos-builder").** Rejeitado. O Conselho já demonstrou preferência por especialistas (data, dashboard, automation, delivery foram adicionados lateralmente, não houve generalista). Generalista iria canibalizar trabalho dos especialistas de projeto.

3. **Reusar um subagente existente (e.g., `data-architect` aprende meta-trabalhos).** Rejeitado. Sobrecarrega o subagente, mistura escopo de projeto com escopo meta-estrutural, e não resolve o conflito de interesse do orchestrator.

4. **Criar um capability repo separado (e.g., `../laos-architect/`) com MCP server próprio.** Considerado. Rejeitado pela desproporção: capability-architect não tem tools de domínio (não faz SQL/design/automation), só consome `lacouncil.*` para ler propostas. Um capability repo + MCP server seria overhead sem ganho. **Mantido como fallback** se a comunidade discordar (vira R-revogação + ADR-004).

5. **Esperar pela 3ª capability nova e ver se o problema realmente se repete.** Rejeitado. LAECON já demonstrou o problema (17 condições ad-hoc), e o 2º caso está batendo na porta. Esperar custa mais que corrigir.

6. **Confiar no LACOUNCIL `implement_proposal()` para fazer tudo.** Considerado. Hoje, `implement_proposal()` retorna "implementation details including meta-project template or diff" — ou seja, ele **gera o template**, mas a execução real do scaffold ainda é manual. capability-architect é quem executa o template gerado. Separação limpa: LACOUNCIL é o "what", capability-architect é o "how".

---

## Consequências

### Positivas

- LAOS passa de 5 → 6 subagentes, com separation of duties estrita: orchestrator propõe, Conselho delibera, capability-architect implementa, delivery-reviewer valida.
- 13 condições vinculantes substituem as 17 ad-hoc da LAECON. Próxima capability nova herda o template, não reinventa.
- `delivery-reviewer` ganha cobertura para meta-projetos (G4 + G8).
- Conflict of interest do orchestrator removido: ele propõe e dispatcha, mas não implementa o que ajudou a aprovar.
- Domain specialists mantêm autoridade sobre seus domínios: capability-architect constrói a casa, eles decoram o quarto (G3).
- Observability contract padronizado (G1) evita fragmentação da MCP discovery surface conforme a topologia cresce.

### Custos e responsabilidades

- 13 condições vinculantes (5 R + 8 G) a serem respeitadas em toda capability nova implementada.
- Risco de over-bureaucratization: BASIC sign-off + STABLE sign-off + domain-specialist review = 3 gates por capability. Mitigação: os 3 gates são leves (smoke, formato, contrato) e o G4 evita o cenário pior (rotear para capability quebrada).
- Topologia cresce de 5 → 6 agentes. Custo de manutenção marginal: agent file + binding conditions + tracking + ADR. Aceitável.
- 30 dias de BASIC para o próprio capability-architect: janela para o Conselho observar se a separation of duties funciona.

### Riscos

| Risco | Mitigação |
|-------|-----------|
| Capability-architect implementa R1-R5 + G1-G8 só no papel, na prática viola | BASIC window de 30d + delivery-reviewer BASIC + STABLE sign-off detecta |
| Domain specialists sobrecarregados por G3 (revisão obrigatória) | Review é leve (KB draft + contracts, ~30 min) e é uma extensão natural do papel |
| capability-architect se torna "generalista por acúmulo" | R2 explícito (não escreve artefatos de projeto) + R5 (não altera prompt de outros) |
| Conselho aprova proposta e capability-architect não consegue implementar (proposta ambígua) | Stop-and-report explícito no agent file; orchestrator decide |
| 30 dias não bastam para o capability-architect acumular evidência de uso | Promoção a STABLE não é automática; Conselho pode prorrogar ou revogar via nova proposta |

---

## Implementação

### Já entregue (2026-06-04, M0 em progresso)

- `.opencode/agent/capability-architect.md` — agent file com frontmatter, scope, MCP namespaces, R1-R5 + G1-G8, anti-patterns.
- `projects/_meta/capability-architect/project.yaml` — meta-projeto.
- `projects/_meta/capability-architect/binding-conditions.md` — 13 condições vinculantes + mapeamento das 4 emendas.
- `projects/_meta/capability-architect/capability-evolution.md` — tracking BASIC.
- `projects/_meta/adr/ADR-003-capability-architect-creation.md` — este ADR.
- `AGENTS.md` — topology atualizada (5 → 6 agentes).
- `.opencode/agent/orchestrator.md` — capability-architect adicionado como dispatch target.
- `lacouncil.record_project()` chamado.

### Próximos passos

- **M0-9** (2026-06-04, hoje): `delivery-reviewer` valida M0-1..M0-8 contra `binding-conditions.md` + `knowledge/padroes-entrega.md`.
- **M1** (2026-07-04, +30d): Promoção a STABLE após delivery-reviewer STABLE sign-off + ≥ 1 uso real em capability scaffolding.
- **M2** (~2026-07-15): Primeira capability real implementada por capability-architect (vai ser a próxima a ser aprovada pelo Conselho).
- **M3+**: Refinamento do scaffold template baseado em lições aprendidas.

---

## Referências

- Proposta LACOUNCIL: `2f42afe6-71d5-4ef8-a88a-1339d72ec501`
- Governança de capabilities: `e9cd6dd8-b1e4-4e5f-8216-5cd69a095d4f` (regime G1-G8 + MISSING/BASIC/STABLE)
- LAECON precedente: `cbe2d8ef-f65c-4d0e-8960-ea99527ab39f` (17 condições ad-hoc — substituídas pelo template)
- ADR-001 (formato): `projects/_meta/adr/ADR-001-capability-governance.md`
- ADR-002 (precedente): `projects/_meta/adr/ADR-002-laecon-creation.md`
- Meta-projeto: `projects/_meta/capability-architect/project.yaml`
- Binding conditions: `projects/_meta/capability-architect/binding-conditions.md`
- Tracking BASIC: `projects/_meta/capability-architect/capability-evolution.md`
- Padrões de entrega: `knowledge/padroes-entrega.md`
- Agent topology: `AGENTS.md` (atualizado em 2026-06-04)
