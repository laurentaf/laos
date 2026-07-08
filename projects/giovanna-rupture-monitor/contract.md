# Contract – Giovanna Rupture Monitor (LAOS-side mirror)

> Mirror file. The **canonical contract** is in `project.yaml` at the same
> path. This file exists to satisfy `knowledge/sdd-principles.md` §2
> (Missão 0 — SDD Scaffold) which requires a prose `contract.md` mirroring
> `project.yaml` for human readers.

## Brief
Monitorar a ruptura de estoque por região nas Lojas Giovanna, com dados
sintéticos ShadowTraffic, pipeline ETL em 3 estágios, relatório CSV
agregado por região e dashboard HTML interativo. Dockerizado: único
`docker compose up` (ou `docker run`) produz dashboard funcional em
`http://localhost:8000/dashboard.html`.

## Needs
- `etl`
- `data`
- `data-quality`
- `dashboard`
- `presentation`

(All 5 routes resolve in `registry/needs-to-capabilities.yaml` → latade +
ladesign primary; context7 optional.)

## Deliverables
Per `project.yaml` `deliverables:`:
- `main.py` — pipeline ETL em 3 estágios (modo `--local`)
- `generate_shadowtraffic_data.py` — gerador de dados sintéticos
  determinístico (seed 42, 27 cidades)
- `data/raw_data.json` — dataset sintético consumido pelo pipeline
- `data/rupture_report.csv` — relatório agregado por cidade
- `dashboard.html` — dashboard interativo servindo o dashboard
- `Dockerfile` + `docker-compose.yml` + `entrypoint.sh` — containerização
- `data/quality_rules.md` — 8 regras DQ documentadas (DQ-01..DQ-08)
- `README.md` — instruções Docker e local
- `spec/adr/001-rupture-pipeline.md` — ADR do stack & arquitetura
- `spec/adr/002-empty-dataframe-guards.md` — ADR dos guards anti-IndexError

## Capabilities Used
- **latade** (primary) — modeling, data engineering, data quality
- **ladesign** (optional) — dashboard, SVG visual layout
- **context7** (optional) — lookups during implementation

## Repo
https://github.com/laurentaf/giovanna-rupture-monitor

## Status
In remediation (P0 commit pending). The 2026-06-07 delivery reviewer's
`review/checklist.md` declared DELIVERABLE, but the GitHub-head README
contained (a) a broken mermaid block parse error from a `{id}` label,
(b) DataMission-era prose that no longer matched the rewritten
ShadowTraffic-only pipeline, (c) a fabricated `.github/workflows/ingest.yml`
reference. This contract reflects the **target** state, post-fix.
