# codegraph-kb-adoption

Replicar KBs valiosos do CodeGraph (`colbymchenry/codegraph`) dentro das
capacidades existentes da LAOS — sem criar um novo capability repo.

**Não é um projeto de domínio.** É um projeto de melhoria estrutural
(Regime A) que enriquece knowledge/, scripts/ e charters de subagentes
com padrões testados do CodeGraph.

## Status

- Missão 0: ✅ SDD scaffold completo
- Stages 1–6: em progresso

## Origem

Análise de `colbymchenry/codegraph` feita em 2026-06-12. KBs-fonte:
- `CLAUDE.md` — retrieval performance + dynamic-dispatch coverage doctrine
- `docs/design/agent-codegraph-adoption.md` — P1/P2 resolution patterns
- `docs/SEARCH_QUALITY_LOOP.md` — 7-test battery
- `docs/benchmarks/call-sequence-analysis.md` — A/B eval methodology

## Quick ref

| Stage | Deliverable | Alvo |
|---|---|---|
| 1 | Eval methodology | `knowledge/eval-methodology.md` |
| 2 | Tool output sufficiency P0 | `knowledge/padroes-entrega.md` |
| 3 | Sufficiency + success-shaped errors | `knowledge/subagent-result-contract.md` |
| 4 | WDL adaptive scaling | `scripts/preflight_check.py` |
| 5 | MCP SSoT | `.opencode/agent/*.md` |
| 6 | G4 sign-off | `artifacts/review/checklist.md` |