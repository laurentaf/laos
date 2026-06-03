# ADR-001: Arquitetura Híbrida LAOS + Governança de Capabilities

**Status:** accepted
**Date:** 2026-06-03
**Decisor:** LACOUNCIL (maioria)

---

## Contexto

LAOS (sistema operacional) não tinha estrutura definida para projetos. Cada capability repo (LATADE, LADESIGN, LAN8N) tinha seu próprio SDD e Constitution, mas LAOS não exigia isso dos projetos que criava.

Necessidade de governança surgiu quando:
- Usuário pediu game-simulation → LAENGINE é BASIC ( Constitution incompleta)
- Usuário pediu currículo → não existe capability para isso
- Usuário pediu postagens sociais → fuera do scope

## Decisão

Implementar arquitetura híbrida por domínio + regime de governança de capabilities, conforme proposta `e9cd6dd8-b1e4-4e5f-8216-5cd69a095d4f`.

### 1. Arquitetura Híbrida

Cada domínio primário segue sua própria Constitution:

| Domínio | Constitution | SDD | Gate no Dispatch |
|---------|-------------|-----|-----------------|
| data/etl/modeling | LATADE (9 artigos) | BRAINSTORM→DEFINE→PLAN→TASKS | SDD completo |
| dashboard/design/presentation | LADESIGN tokens | brief + design.md | Design referenciado |
| automation/integration/alerts | LAN8N native | workflow spec mínimo | Trigger + SLA |
| game-simulation | LAENGINE (match rules) | engine spec | ⚠️  BASIC - gate reduzido |
| improvement/council | LACOUNCIL | LACOUNCIL investigate |auto |

### 2. Capability Status

| Status | Significado | Comportamento |
|--------|-------------|---------------|
| STABLE | Validada em produção | Dispatch normal, zero fricção |
| BASIC | Existe mas incompleta | Dispatch com aviso, 30 dias para evoluir |
| MISSING | Não existe | LACOUNCIL.investigate → voting |

### 3. Confidence Indices

LAOS nunca pergunta se confidence >= 0.90:

```
NEVER_ASK (confidence >= 0.90):
  - routing_known_need
  - dispatch_stable_cap  
  - gate_sdd_pass
  - delivery_review_pass
  - new_project_known_needs

ALWAYS_ASK (confidence < 0.90):
  - routing_unknown_need
  - dispatch_missing_cap
  - gate_sdd_fail
  - evolution_30d_no_progress

EXECUTE_AND_LOG (0.75 <= confidence < 0.90):
  - dispatch_basic_cap
  - new_capability_approved
```

### 4. Quem Executa

| Tarefa | Executor |
|--------|----------|
| investigate | lacouncil (MCP) |
| create_proposal | lacouncil (MCP) |
| new_project | orchestrator |
| brainstorm | brainstorm_agent |
| plan | planner_agent |
| dispatch | subagent (data-architect, etc.) |
| capability_evolution | capability_repo_owner ou skill_owner ou human_issue |
| delivery_review | delivery-reviewer |

### 5. Quem Valida

| Validação | Validador | Gate |
|-----------|-----------|------|
| SDD phases | planner_agent | Gates por fase |
| Dispatch em cap BASIC | orchestrator | aviso + log |
| 30 dias evolução | delivery-reviewer | BLOQUEIA se não evoluiu |
| Nova capability | delivery-reviewer | G1-G8 quality gates |
| Projeto entregue | delivery-reviewer | padroes-entrega.md |
| ADR gerado | delivery-reviewer | formato + conteúdo |

## Alternativas Consideradas

1. **LAOS agentic** — Rejeitado. LAOS é OS, não executa ações de domínio.
2. **Uma Constitution para todos** — Rejeitado. Impor LATADE sobre design/automation é overengineering.
3. **Starter kit opcional** — Rejeitado. Sem enforcement não há garantia de estrutura.
4. **Unanimidade sempre** — Rejeitado. Impossibilita decisões rápidas. Majority para padrões, unanimidade para fundamentos.

## Consequências

- Projetos data/etl/modeling agora exigem SDD completo
- Capabilities BASIC (laengine) têm 30 dias para evoluir
- Needs fora do registry passam por LACOUNCIL antes de recusar
- Out-of-scope é registrado, não simplesmente recusado
- Confidence indices eliminam pedidos de autorização desnecessários

## Implementação

Arquivos criados:
- `lacouncil.yaml` — Config completo com confidence, executors, governance
- `projects/_meta/capability-evolution/TEMPLATE.md`
- `projects/_meta/out-of-scope/TEMPLATE.md`
- `projects/_meta/adr/ADR-001-capability-governance.md`

## Status Capabilities

| Capability | Before | After |
|------------|--------|-------|
| latade | STABLE | STABLE (sem mudança) |
| ladesign | STABLE | STABLE (sem mudança) |
| lan8n | STABLE | STABLE (sem mudança) |
| lacouncil | STABLE | STABLE (sem mudança) |
| laengine | unknown | BASIC (evolução obrigatória) |
| context7/exa/github | EXTERNAL | EXTERNAL (sem mudança) |