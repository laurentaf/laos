# LAOS — Agent Operating System

LAOS é um **runtime de orquestração de agentes + control plane de
entrega**. Executa projetos de ponta a ponta: pipeline com auto-resume,
custo real por fase, verificação mecânica de entregáveis, observabilidade
(Langfuse/LiteLLM), painel portfolio e console LLM-aware.

**Este é o LAOS canônico.** O antecessor (governança + Conselho +
LACOUNCIL + WDL) foi congelado como legado em `laurentaf/laos` (repo
antigo) — não faz parte deste produto.

## Princípios

1. **Executar, não descrever.** Um projeto é entregue quando o pipeline
   rodou, o verifier passou e o handoff diz pronto — não quando um
   documento especifica como fazer.
2. **Custo real é dado.** Toda fase reporta tokens/custo reais da chamada
   LLM. Sem "estimativa" — medição.
3. **Verificação mecânica.** `laos verify` prova (existe/carrega/testa/
   spec) — não é opinião de reviewer.
4. **Sem governança de time.** Não há Conselho, votação, nem trust scores.
   O orquestrador executa; o verifier prova; o handoff entrega.
5. **Agentes são recursos.** A LLM é chamada via LiteLLM (OpenCode Go);
   o runtime orquestra, o LLM executa estágios, o verifier confere.

## Fluxo de um projeto

```
projects/<name>/project.yaml (contrato: fases + specs)
    ↓
laos run <name>          → pipeline executa fases em ordem (auto-resume)
    ↓                       cada fase: LLM gera artefato → custo real
laos verify <name>       → prova que cada deliverable existe/carrega/testa
    ↓
laos handoff <name>      → relatório de 20 itens (pronto para cliente?)
```

## Superfícies

- **CLI**: `laos doctor | run | resume | verify | gaps | handoff |
  projects | status | cost | trace | backup | server`
- **Painel** http://127.0.0.1:7331 — board (5 colunas), dashboard
  executivo, detalhe do projeto, console, handoff
- **Observabilidade**: Langfuse :3000 (traces/custo) + LiteLLM :4000
  (gateway LLM)

## Como evoluir

1. Leia `knowledge/observability-guide.md` (mapa de logs + diagnóstico).
2. Rode `uv run python -m pytest tests/` (37 testes, deve estar 100% verde).
3. Valide com `laos doctor` + um run real de projeto.
4. Commit + `laos backup` (ou git push).

## Repos

- **Este** (`laurentaf/laos-v2`): o produto LAOS canônico.
- **Legado** (`laurentaf/laos`): o LAOS antigo (governança) — congelado,
  referência histórica.
