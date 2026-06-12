# spec/todo.md — codegraph-kb-adoption

Tracking das stages e tasks deste meta-projeto.

## Mission 0 — SDD Scaffold ✅

- [x] project.yaml
- [x] contract.md
- [x] spec/constitution.md
- [x] spec/todo.md (este arquivo)
- [x] spec/adr/_template.md
- [x] spec/adr/README.md
- [x] spec/harness/_template.md

## Stage 1 — Eval Methodology (knowledge/eval-methodology.md)

- [ ] 1.1 Criar `knowledge/eval-methodology.md` com framework A/B
- [ ] 1.2 Documentar metric hierarchy (wall-clock > tool-calls > Read=0 > tokens)
- [ ] 1.3 Documentar model floor policy (Sonnet, never Opus/Fable for eval)
- [ ] 1.4 Criar `scripts/agent-eval/ab-new-vs-baseline.sh` (eval harness analog)
- [ ] 1.5 Criar `scripts/agent-eval/run-all.sh` (with-vs-without analog)
- [ ] 1.6 ADR-013: "Adotar framework de eval A/B"
- [ ] 1.7 Boot check passa

## Stage 2 — Tool Output Sufficiency (padroes-entrega.md)

- [ ] 2.1 Adicionar P0 clause em padroes-entrega.md: tool output sufficiency
- [ ] 2.2 Adicionar 7-test battery hook para nova capability MCP
- [ ] 2.3 ADR-014: "Sufficiency como critério P0 de output de tool"
- [ ] 2.4 Boot check passa

## Stage 3 — Subagent Result Contract Extended

- [ ] 3.1 Adicionar §4 "Suficiência não é steering" em subagent-result-contract.md
- [ ] 3.2 Adicionar §5 "Erros em formato de sucesso" (error teaching abandonment)
- [ ] 3.3 Validar que todos os 5 subagentes (data-architect, dashboard-designer,
        automation-engineer, capability-architect, delivery-reviewer) seguem o padrão
- [ ] 3.4 ADR-015: "Doutrina suficiência-sobre-steering"
- [ ] 3.5 Boot check passa

## Stage 4 — WDL Adaptive Scaling

- [ ] 4.1 Adicionar project-size tiers ao WDL preflight gate
        (<5 deliverables → simple, 5–15 → standard, >15 → deep)
- [ ] 4.2 Documentar invariant: larger tier nunca recebe threshold menor que
        smaller tier (analog to CodeGraph's getExploreOutputBudget)
- [ ] 4.3 Testar com projeto mínimo (< 5) e projeto médio (> 15)
- [ ] 4.4 Boot check passa

## Stage 5 — MCP Single Source of Truth

- [ ] 5.1 Adicionar princípio SSoT nos 5 subagent charters:
        "MCP initialize response é fonte única de verdade para guidance"
- [ ] 5.2 Remover guidance duplicada de lugares que não o initialize response
- [ ] 5.3 Verificar que cada capability repo (latade, lan8n, ladesign,
        lacouncil) entrega seu próprio guidance no MCP initialize
- [ ] 5.4 Boot check passa

## Stage 6 — delivery-reviewer G4 BASIC Sign-off

- [ ] 6.1 Rodar preflight_check.py
- [ ] 6.2 Dispatch delivery-reviewer
- [ ] 6.3 Resolver findings se houver
- [ ] 6.4 Obter G4 sign-off
- [ ] 6.5 Commit + push (Regime A)
- [ ] 6.6 30-day window: BASIC → STABLE (até 2026-07-12)