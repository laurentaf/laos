# ADR-004: Dashboard com Proxy Linear (3 features) no lugar do RF completo

## Contexto
Dashboard interativo precisa permitir que usuário ajuste sliders dos
3 principais indicadores (last_activity_day, assessment_count,
submission_rate) e veja esforço individual para atingir meta
configurável (inversão analítica). RF completo (~87MB, 31 features)
é inviável em file://.

## Decisão
Substituir RF por Regressão Logística (proxy linear) com 3 features
no dashboard. Proxy em artifacts/dashboard/model_proxy.json.

## Alternativas Consideradas
1. RF no navegador (ONNX.js) — 87MB download, sem inversão analítica
2. Regressão polinomial — overfitting, inversão complexa
3. Lookup table 3D — sem inversão analítica
4. API server com RF — impossível em file://

## Consequências
Positivas: interatividade total em file://, inversão analítica fechada,
dashboard auto-contido (< 100KB), zero dependências
Negativas: perda ~0,02 ROC-AUC (0,946 vs 0,953), apenas 3 features,
relação linear no log-odds
Mitigações: disclaimer explícito, tabela comparativa RF vs LR, proxy
referencia best_model RF nos metadados

## Status
Aceito. 2026-07-03. Autor: dashboard-designer (LADESIGN)
