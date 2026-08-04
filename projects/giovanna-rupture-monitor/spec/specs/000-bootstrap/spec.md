# SPEC-001: Bootstrap — Giovanna Rupture Monitor

**Status:** ACEITO
**Version:** 1.0
**Authors:** Laurent (data engineer)
**Owner:** Laurent

---

## Contexto

Pipeline ETL para monitoramento de ruptura de estoque nas lojas Giovanna. Migração de DataMission API para ShadowTraffic (dados sintéticos determinísticos). Dashboard HTML consome CSV agregado por região com métricas IRC v2.

## 1. Executive Summary

Scaffold inicial do projeto: pipeline `main.py` com modo `--local`, dados sintéticos em `data/raw_data.json`, e dashboard HTML servido via Docker.

## 2. User Stories

### US-1
As a data engineer, I need to run the pipeline with local synthetic data so I can develop without API access.

## 3. Acceptance Criteria
- [x] Data ingested from local JSON
- [x] Schema validated (ShadowTraffic columns)
- [x] CSV output matches dashboard expectations

## 4. Sources

| Table | Schema |
|-------|--------|
| raw_data.json | regiao, produto, categoria, estoque_atual, giro_diario, cobertura_dias, irc, risco, critico |

## 5. Destination

### DDL
```sql
-- rupture_report.csv columns:
-- regiao, qtd_produtos, estoque_total, giro_medio, cobertura_media_dias,
-- irc_medio, qtd_critico, pct_critico, risco_predominante
```

## 6. Refresh Strategy

Mode: full-replace (deterministic regeneration)

## Decisão

Adotar ShadowTraffic como fonte de dados sintéticos em vez da DataMission API. Motivo: eliminar dependência de API externa, garantir reprodutibilidade determinística e permitir execução offline (`--local`). O formato JSON com colunas ShadowTraffic (regiao, produto, categoria, estoque_atual, giro_diario, cobertura_dias, irc, risco, critico) foi mantido para compatibilidade com o dashboard existente. Docker como formato de entrega único para eliminar problemas de ambiente.

## Critérios

- Pipeline executa end-to-end com `python main.py --local` sem erros.
- CSV de saída (`rupture_report.csv`) contém colunas esperadas pelo dashboard: regiao, qtd_produtos, estoque_total, giro_medio, cobertura_media_dias, irc_medio, qtd_critico, pct_critico, risco_predominante.
- Dashboard HTML renderiza corretamente os dados do CSV.
- `docker build && docker run` produz dashboard funcional acessível em `http://localhost:8000/dashboard.html`.
- Dados são determinísticos: execução repetida com mesmo `raw_data.json` produz mesmo resultado.
