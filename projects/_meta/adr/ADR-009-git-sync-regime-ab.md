# ADR-009: Git sync obrigatório após mudança estrutural aprovada (Regime A/B)

**Status:** accepted
**Date:** 2026-06-05
**Decisor:** LACOUNCIL (maioria, 4/4 SIM, 100%)
**Proposal:** `391a8179-5a16-4b69-a3a3-d4ca1b20c2c3`
**Implementer:** orchestrator (direct)

---

## Contexto

Mudanças estruturais aprovadas pelo Conselho (propostas f9b636fc, ecdc6305, f82d6261, etc.) foram implementadas pelo capability-architect e validadas pelo delivery-reviewer (G4 BASIC sign-off), mas ficaram apenas no repositório local sem commit+push para o GitHub. O repositório remoto ficou defasado até que o usuário perguntou explicitamente.

O AGENTS.md diz "Only commit, amend, push, or create PRs when explicitly requested" — correto para artefatos de projeto de domínio, mas incorreto para mudanças estruturais onde a aprovação já veio do Conselho e o reviewer já validou.

### Diagnóstico (5 Whys + Fishbone)

- **5 Whys:** Mudança não foi ao GitHub → ninguém executou push → regra AGENTS.md exige confirmação explícita → regra foi escrita para projetos de domínio, não para mudanças estruturais → não há distinção entre regimes.
- **Fishbone (Processo):** workflow do capability-architect termina em G4 sign-off, mas não tem passo "commit + push ao GitHub". O handoff do reviewer devolve ao orchestrator, que por default não pusha.

## Decisão

Adotar dois regimes de push:

### Regime A — Mudanças estruturais (mandatory push)

Changes approved by the Conselho and validated by delivery-reviewer (G4 BASIC or G8 STABLE sign-off) **must** be committed and pushed to GitHub within the same session. This applies regardless of which subagent executed the change (capability-architect, orchestrator direct, etc.).

A cadeia de autoridade está completa: Conselho aprovou → reviewer validou → gate adicional é desnecessário.

### Regime B — Artefatos de projeto de domínio (gated push)

Mantém a regra atual: push só após delivery-reviewer aprovar + usuário confirmar. Isso é P0 em `padroes-entrega.md`.

### Critério de distinção

- Se a mudança foi motivada por uma proposta LACOUNCIL → Regime A.
- Se a mudança é output de deliverable de projeto → Regime B.
- Na dúvida, perguntar ao usuário.

## Alternativas consideradas

1. **Sempre pedir confirmação do usuário** (status quo): rejeitado — a aprovação já veio do Conselho, pedir de novo é overhead e causa defasagem.
2. **Automatizar push via n8n webhook**: futuro possível, mas requer n8n cloud + triggers expostos. Por ora, push manual pelo orchestrator é suficiente.
3. **Push automático sem gate**: rejeitado — domain artifacts precisam do gate do reviewer + confirmação do usuário.

## Consequências

- **Positiva:** Remote repo sempre em sync após mudanças estruturais. Custo ~2 min por mudança.
- **Positiva:** Cria ponto determinístico (proposal approved + sign-off → commit+push) que pode virar webhook n8n no futuro.
- **Risco:** Push prematuro se reviewer errou? Mitigação: `git revert` é o caminho. O status quo (remote stale) é mais arriscado e mais difícil de detectar.
- **Risco:** Confusão entre regimes A e B? Mitigação: distinção é clara — "motivado por LACOUNCIL proposal" vs "project deliverable output".

## Mudanças feitas

1. **AGENTS.md** — nova seção "Git sync regime (LACOUNCIL 391a8179)" com Regime A e Regime B.
2. **knowledge/padroes-entrega.md** P0 — novo item: "Git sync pós-mudança estrutural (LACOUNCIL 391a8179)".
3. **projects/_meta/capability-architect/binding-conditions.md** — G9 adicionado.
4. **.opencode/agent/capability-architect.md** — G1–G8 → G1–G9, anti-patterns atualizado, G9 reminder no workflow.

## Advisory do Conselho

O delivery-reviewer sugeriu que Regime A seja amplo o suficiente para cobrir mudanças estruturais aplicadas diretamente pelo orchestrator (não só pelo capability-architect). Esta ADR incorpora esse advisory: Regime A vale para qualquer mudança estrutural aprovada pelo Conselho e validada pelo reviewer, independentemente do executor.
