# Constitution — WDL v1 rollout (meta-projeto)

**Version:** 1.0 | **Status:** Vigente
**Project:** wdl-rollout (proposals a4fe9faa + 7fd94c1a, supermaioria 4/4 SIM, 2026-06-06)

---

## Princípios

1. **Decomposição precede dispatch.** Nenhum especialista
   (data-architect, dashboard-designer, automation-engineer,
   capability-architect) é despachado sem um `verdict.yaml`
   verificado (`state: READY`) emitido pelo `workflow-decomposer`.
   Esta é a P0 hard rule do WDL v1. Sem decomposição prévia,
   o orchestrator opera no escuro.

2. **Verdict é observável, não self-attested.** Todo `verdict.yaml`
   carrega `verified_by: <agente_id>` e a assinatura
   `sha256-canonical-json` do conteúdo. Self-attested verdicts
   falham o G4 sign-off (DR condition 1) — mesmo anti-pattern do
   predecessor reviewer de 63 linhas.

3. **Capability gaps são sinais públicos, não segredos de
   capability-architect.** Quando o decomposer detecta uma
   capability ausente, o verdict inclui
   `capability_gaps: [{ description, affects, owner_notified,
   severity }]`. O owner afetado é fonte de sinal E construtor
   eventual. Simetria com o loop `lacouncil.detect_patterns`.

4. **Regime A (LACOUNCIL 391a8179) para push estrutural.** Após
   delivery-reviewer emitir G4 sign-off, o orchestrator commita
   e pusha ao GitHub dentro da mesma sessão. A cadeia de
   autoridade está completa (Conselho aprovou → reviewer
   validou). Gate adicional é desnecessário.

5. **Separação de funções estrita (R3).** O workflow-decomposer
   NÃO propõe (não chama `lacouncil.create_proposal`), NÃO vota
   (não chama `lacouncil.register_vote`), NÃO modifica registry,
   AGENTS.md, knowledge, workflows, ou `project.yaml`. Emite
   sinais; o orchestrator os roteia.

## Scope

### Dentro do escopo deste meta-projeto

- Criar o subagente `workflow-decomposer` (read-only analyzer) +
  seu charter file `.opencode/agent/workflow-decomposer.md`.
- Criar o contrato operacional `workflows/wdl-contract.yaml`
  (pinned `wdl_version: 1`).
- Adicionar a tabela `wdl_signatures` no LACOUNCIL DuckDB
  (migration script idempotente).
- Adicionar entry `workflow-decomposer` em `.opencode/opencode.jsonc`
  (reusa o MCP server lacouncil; wall enforced pelo charter).
- Adicionar sub-check `wdl-gate` em `scripts/preflight_check.py`
  com 4 sub-criteria (DR-2).
- Adicionar entry `workflow-decomposer` em
  `scripts/subagent_boot_check.py` (7-dim schema).
- Adicionar G10 (WDL) e G11 (Charter P0) em
  `projects/_meta/capability-architect/binding-conditions.md`
  (14 → 16 conditions).
- Atualizar `AGENTS.md`: Hard Rule #8, topology, §"Your loop"
  WDL preflight gate subsection, §"Tools you do NOT use" clarifier.
- Adicionar WDL section em `.opencode/agent/delivery-reviewer.md`
  que quotes `exit_code` from preflight wdl-gate.
- Publicar ADR-011 (WDL) e ADR-012 (Charter P0).
- Bootstrap meta-projeto `projects/_meta/wdl-rollout/` com
  full Missão 0 SDD scaffold (8 fixos + 1 condicional pulado).

### Fora do escopo (separate work)

- Implementar SG-2 (proposal 70decf5e, Path-actor gate para
  structural files) — proposta separada, sessão separada.
- Modificar a Constitution do LAOS (não há uma — esta é meta).
- Criar uma capability repo nova para workflow-decomposer
  (não há: é subagent do LAOS, não domain capability).
- Implementar tools concretas no workflow-decomposer (o subagent
  é read-only; usa lacouncil.* já existentes; sem tool novo).

## Non-goals

1. **Não substituir o orchestrator.** O workflow-decomposer é um
   assessor read-only do orchestrator. O orchestrator continua
   dono do dispatch, da decisão de bypass, e da governança da
   sessão.

2. **Não adicionar ML à decomposição.** A 3-Q rubric é
   puramente estrutural (bounded input / validatable success /
   single type of reasoning). LLMs no decomposer virariam
   teatro: o signal para decompor é puramente sintático
   (keywords, structure).

3. **Não unificar o contrato do workflow-decomposer com o
   contrato do orchestrator.** São artefatos separados com
   lifecycles separados. Mudanças no contrato WDL exigem nova
   proposta LACOUNCIL supermaioria; mudanças no orchestrator
   charter idem.

4. **Não tornar o WDL v2 implícito.** `wdl_version: 1` é pinned.
   Breaking changes no verdict shape, gate sub-criteria, ou
   exemption allowlist exigem nova proposta LACOUNCIL.
   `wdl-contract.yaml` é imutável dentro do regime v1.

5. **Não auto-validar o G4 sign-off.** O capability-architect
   implementa; o delivery-reviewer valida. Esta separação é
   por design (separation of duties, capability-architect
   R3 + R4 + R5).
