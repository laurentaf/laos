# ADR-005: Routing duplo `modeling` (latade + laecon) e handoff de feature engineering

**Status:** accepted
**Date:** 2026-06-05
**Decisor:** LACOUNCIL (supermaioria, 4/4 SIM, 100%)
**Proposal:** bf91c407-94b8-463f-a0e5-3d73bfaf6c68
**Implements:** diff em `registry/needs-to-capabilities.yaml` (linhas 34-36) + `projects/previsao-concursos/project.yaml` (needs)

---

## Contexto

A need `modeling` no registry roteava apenas para `[latade]`. `latade` cobre SQL/DuckDB
e modelagem dimensional, mas não tem stack de ML clássico (sklearn, xgboost, shap,
optuna). O ML real vive em `laecon` (BASIC até 2026-07-04).

O primeiro projeto a evidenciar o gap foi `previsao-concursos` (POC de ML empírico
por banca/cargo), que precisava de `modeling` para features de frequência histórica
mas só via `laecon` poderia rodar sklearn/xgboost com bootstrap.

A lacuna forçava o orchestrator a inventar capability selection — violando
Hard Rule #4 ("routing é determinístico, orchestrator não inventa capability selection").

## Decisão

1. **Registry (`registry/needs-to-capabilities.yaml`):** `modeling.primary: [latade, laecon]`.
2. **Projeto (`projects/previsao-concursos/project.yaml`):** adicionada need
   `predictive-modeling` além de `modeling`, para que projetos 100% preditivos
   tenham routing sem ambiguidade.
3. **Não alteradas:** demais needs ML (`ml`, `data-science`, `econometrics`,
   `nps-driver-analysis`, `causal-inference`, `predictive-modeling`) continuam
   roteando para `[laecon]` como primary.

## Handoff latade ↔ laecon (owner de feature engineering compartilhado)

Para evitar ping-pong entre capabilities, ficou definido:

| Owner | Responsabilidade | Exemplos |
|---|---|---|
| **`latade`** | Dados crus → tabela analítica modelada (gold layer). Enriquecimento determinístico, joins, agregações, type casting, DQ checks, split temporal. | `silver_questoes`, `gold_features_agg_por_banca`, `train_validation_split`. |
| **`laecon`** | Features derivadas do modelo, encoders, lag features, seleção de variáveis, tuning, treinamento, interpretação, export de predição. | `tfidf_topics`, `target_encoding_banca`, `lag_rolling_window`, SHAP, optuna, model.pkl. |
| **Limite** | A `gold layer` de `latade` é a única entrada aceita por `laecon.train_*`. `laecon` não lê bronze/silver. |

Convenção: nome da tabela gold é o contrato. Se a feature não cabe em
agregação SQL determinística, ela é derivada em `laecon` a partir da gold table.

## Fallback explícito (laecon BASIC)

`laecon` está em BASIC até 2026-07-04. Vários tools retornam
`not_implemented_yet`. Regra:

- Se `laecon.*` retornar `not_implemented_yet`, o orchestrator **deve** reportar
  ao usuário e parar (não improvisar workaround com outra tool). Não há fallback
  silencioso para `latade` — o usuário precisa decidir se aceita o estado
  atual da capability ou se reformula o brief.
- A exceção é o **boot check**: `subagent_boot_check.py` já detecta laecon
  imatura e bloqueia o dispatch antes do mid-task failure.

## Consequências

- **Positivo:** routing determinístico preservado; projeto `previsao-concursos`
  pode rodar sem contornar a registry; demais projetos ML (`ml`,
  `data-science`, `predictive-modeling`) já estavam corretos.
- **Risco:** projetos que pedem `modeling` puramente dimensional (e.g. data
  warehouse) podem, em tese, receber `laecon` como candidato. Mitigação: o
  orchestrator seleciona pelo brief; o delivery-reviewer audita; o
  `padroes-entrega.md` P0 bloqueia entrega sem artefatos compatíveis com o brief.
- **Padrão detectado:** "data prep (latade) + ML/empirical (laecon) é
  separado de fato". Promovido para conhecimento transversal a partir de
  ≥1 projeto (revisar após mais 1-2 projetos se a pattern se sustenta).

## Referências

- Proposta LACOUNCIL: `bf91c407-94b8-463f-a0e5-3d73bfaf6c68` (aprovada 2026-06-05).
- Voto `data-architect`: alerta sobre owner de feature engineering — endereçado acima.
- Voto `delivery-reviewer`: pediu ADR curto + cláusula de fallback — ambos atendidos.
- Voto `dashboard-designer`: contrato de saída único do modelo — responsabilidade
  de `laecon` (campos, tipos, IC, versões) uniforme entre capabilities.
- Voto `automation-engineer`: workflow n8n com `laecon` retreino — não escopo desta ADR.
- ADR-002: criação da `laecon` capability.
