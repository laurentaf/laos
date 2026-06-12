# Constitution — codegraph-kb-adoption

## Art. 1 — Nome e natureza

Este é um meta-projeto de adoção de KBs (knowledge bases) — não um
projeto de domínio. Seu objetivo é enrich the capabilities that already
exist in LAOS with proven patterns from an external source
(CodeGraph by colbymchenry).

## Art. 2 — Fonte

Os padrões vêm de `colbymchenry/codegraph`, analisado em 2026-06-12.
Arquivos-fonte:
- `CLAUDE.md` — doctrine de retrieval performance e dynamic-dispatch
- `docs/design/agent-codegraph-adoption.md` — P1 (Read displacement)
  e P2 (MCP startup) resolution
- `docs/SEARCH_QUALITY_LOOP.md` — 7-test battery para validação de
  language/tool coverage
- `docs/benchmarks/call-sequence-analysis.md` — A/B eval methodology
- `docs/benchmarks/codegraph-ab-matrix.md` — eval framework design

## Art. 3 — O que NÃO é

Este projeto não:
- Cria um novo capability repo
- Implementa parsing de código (CodeGraph's core domain)
- Adota dynamic-dispatch coverage (bridging de linguagem cruzada)
- Adota provenance tagging (sem trace cross-capability existente)

## Art. 4 — Princípios de adoção

**Princípio 1 — Relevância.** Um padrão do CodeGraph só entra em LAOS
se resolve um problema real que LAOS já tem ou terá em < 6 meses.

**Princípio 2 — Integração, não duplicação.** Cada padrão adotado
entra no lugar certo (knowledge/ para transversal, scripts/ para
ops, charters para subagent guidance), nunca como arquivo isolado.

**Princípio 3 — Regime A obrigatório.** Como todas as mudanças
são estruturais, todas entram via Regime A: approved → validated →
committed → pushed na mesma sessão.

## Art. 5 — Métricas de sucesso

O projeto é bem-sucedido se, ao final:
1. `knowledge/eval-methodology.md` existe com framework A/B documentado
2. `padroes-entrega.md` tem P0 clause para tool output sufficiency
3. `subagent-result-contract.md` tem §4 + §5 completos
4. WDL preflight tem scaling adaptativo por tamanho do projeto
5. 5 subagent charters declaram MCP SSoT como princípio
6. delivery-reviewer deu G4 BASIC sign-off
7. Todos os 6 itens acima commitados + pushados (Regime A)

## Art. 6 — Validação

Cada stage é validada pelo boot check do subagente responsável.
Stage 6 é validada pelo delivery-reviewer contra `knowledge/padroes-entrega.md`.
Não há auto-verificação — o capability-architect não valida o próprio trabalho.