# Contract — codegraph-kb-adoption

Este contrato é a versão em prosa de `project.yaml`. É a "promessa do
projeto" legível sem YAML. Cite este arquivo quando precisar de uma
referência rápida ao escopo; cite `project.yaml` quando precisar de
campos estruturados.

---

## Brief

Replicar os KBs mais valiosos do CodeGraph (colbymchenry/codegraph) dentro
das capacidades existentes da LAOS, sem criar um novo capability repo.
O CodeGraph é um repositório de conhecimento sobre estrutura de código —
não um repo de programação. Seus KBs documentam padrões de how-to eval,
como fazer MCP tools que agents realmente usam, e scaling adaptativo.
Esses padrões não pertencem ao CodeGraph; são conhecimento transversal.

## Needs

- **investigation** — análise dos arquivos-fonte do CodeGraph
- **improvement** — incorporação dos padrões encontrados

## Capabilities

- **lacouncil** — investigate, create_proposal, detect_patterns
- **context7** — fetch dos KBs do CodeGraph (CLAUDE.md, docs/design/,
  docs/benchmarks/)

## Repo

Self-hosted. Meta-projeto sem child repo. LAOS se modifica diretamente:
knowledge/, scripts/, .opencode/agent/*.md, workflows/.

## Deliverables (resumo)

| # | Deliverable | Tipo | Alvo |
|---|---|---|---|
| 1 | Framework de eval A/B documentado | knowledge/ | `knowledge/eval-methodology.md` |
| 2 | P0 sufficiency de output de tool | extensão | `knowledge/padroes-entrega.md` §P0 |
| 3 | §4 Suficiência + §5 Erros em formato de sucesso | extensão | `knowledge/subagent-result-contract.md` |
| 4 | Scaling adaptativo na WDL preflight | extensão | `scripts/preflight_check.py` |
| 5 | MCP SSoT como princípio nos subagent charters | extensão | `.opencode/agent/*.md` |
| 6 | G4 sign-off + checklist | review | `artifacts/review/checklist.md` |

Total: 5 arquivos alterados/criados + 1 review output.

## Regime

A (LACOUNCIL 391a8179) — mudanças estruturais commit+push mandatory
dentro da sessão após G4 sign-off do delivery-reviewer.

## Status

- Missão 0: SDD scaffold criado (este arquivo).
- Stages 1–5: pendentes.
- G4 sign-off: pendente.

## Cross-references

- Source: `colbymchenry/codegraph` — CLAUDE.md, docs/design/,
  docs/benchmarks/ (analisado 2026-06-12)
- Proposta LACOUNCIL mais próxima: dbc88097 (subagent result contract)
- Template: `projects/_meta/wdl-rollout/` (mesmo padrão)

## Nota sobre o que NÃO foi adotado

- provenance tagging (cross-LATADE↔LAN8N trace) — adiado; não existe
  ainda a necessidade de tracing entre capabilities
- dynamic-dispatch coverage (bridging de linguagem) — fora do escopo;
  LAOS não faz parsing de código