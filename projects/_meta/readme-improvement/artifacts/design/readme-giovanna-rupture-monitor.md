<!--
  giovanna-rupture-monitor — Stock-Out Monitor by Region
  README.md  |  github.com/laurentaf/giovanna-rupture-monitor
  Brand: Inventory data you can trust.
  Tone: Practical, data-driven, bilingual.
  Adapted from the LAOS README (20/20) inline-HTML pattern.
-->

<div align="center" style="margin-top:48px;margin-bottom:24px;">

<!-- Emblem: rupture / stock-out indicator -->
<svg width="72" height="72" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-bottom:4px;">
  <rect x="4" y="4" width="56" height="56" rx="12" stroke="#e84393" stroke-width="1.5" fill="none" opacity="0.3"/>
  <!-- Bar graph going down (stock-out) -->
  <rect x="14" y="36" width="8" height="18" rx="2" fill="#e84393" opacity="0.3"/>
  <rect x="26" y="26" width="8" height="28" rx="2" fill="#e84393" opacity="0.5"/>
  <rect x="38" y="18" width="8" height="36" rx="2" fill="#e84393" opacity="0.7"/>
  <!-- Alert dot -->
  <circle cx="50" cy="16" r="4" fill="#e84393" opacity="0.9"/>
  <circle cx="50" cy="16" r="2" fill="#fff" opacity="0.8"/>
</svg>

<br/>

# Giovanna Rupture Monitor

<p style="margin:12px 0;">
  <img src="https://img.shields.io/badge/Python-%E2%89%A53.10-3776AB?style=flat&logo=python&logoColor=fff" alt="Python 3.10+"/>
  &nbsp;
  <img src="https://img.shields.io/badge/Status-PRODUCTION-00C853?style=flat" alt="Status: PRODUCTION"/>
  &nbsp;
  <img src="https://img.shields.io/badge/License-MIT-31c754?style=flat" alt="License: MIT"/>
  &nbsp;
  <img src="https://img.shields.io/badge/Stack-API%20|%20pandas%20|%20Docker-0984e3?style=flat" alt="Stack: API | pandas | Docker"/>
  &nbsp;
  <img src="https://img.shields.io/badge/Dashboard-HTML%2FCSS-ff7675?style=flat" alt="Dashboard: HTML/CSS"/>
  &nbsp;
  <a href="https://github.com/laurentaf/laos"><img src="https://img.shields.io/badge/Ecosystem-LAOS-6c5ce7?style=flat" alt="LAOS Ecosystem"/></a>
</p>

<br/>

### 3-Stage ETL Pipeline &bull; Stock-Out Analysis &bull; 4,150 Regions

<p style="font-size:0.85em;color:#636e72;">
  EN: 3-stage ETL pipeline that fetches retail inventory data, computes stock-out (ruptura) by region, and outputs actionable CSV reports.
  <br/>
  PT: Pipeline ETL de 3 estágios que coleta dados de inventário, calcula a taxa de ruptura por região e gera relatórios CSV acionáveis.
</p>

<hr style="width:48px;margin:24px auto;border:none;border-top:2px solid #e84393;opacity:0.3;"/>

</div>

> **Where is the product missing — and by how much?**  
> The Giovanna Rupture Monitor answers this in minutes. A 3-stage ETL pipeline ingests retail inventory data from the DataMission API, computes stock-out rates per region, and produces ranked CSV reports. Built for Lojas Giovanna — deployed daily via CI/CD.

---

## O que é / What It Is

**PT:** Pipeline ETL de 3 estágios para monitoramento de ruptura de estoque das **Lojas Giovanna**. Consome dados da API DataMission, calcula a taxa de ruptura (stock-out) por região e gera relatórios CSV priorizados. Cada execução analisa milhares de regiões em segundos.

**EN:** 3-stage ETL pipeline for stock-out monitoring at **Lojas Giovanna**. Ingests inventory data via DataMission API, computes rupture rate by region, and outputs prioritized CSV reports. Each run analyzes thousands of regions in seconds.

**Por que existe:** Ruptura de estoque é uma das maiores perdas no varejo físico — cada item indisponível representa venda perdida, queda de satisfação e distorção de alocação. Este pipeline responde onde o produto está faltando e em quanto, antes que o impacto financeiro se acumule.

---

## Resultados / Results

<div align="center" style="margin:24px 0;">

<table style="border-collapse:separate;border-spacing:0;min-width:480px;">
  <tr>
    <td align="center" style="padding:12px 20px;border:1px solid #e84393;border-radius:8px 0 0 8px;border-right:none;width:33%;">
      <div style="font-size:1.6em;font-weight:700;color:#e84393;">4,150</div>
      <div style="font-size:0.75em;opacity:0.5;">Regions Analyzed</div>
    </td>
    <td align="center" style="padding:12px 20px;border:1px solid #e84393;border-right:none;width:33%;">
      <div style="font-size:1.6em;font-weight:700;color:#e84393;">20,000</div>
      <div style="font-size:0.75em;opacity:0.5;">Records Ingested</div>
    </td>
    <td align="center" style="padding:12px 20px;border:1px solid #e84393;border-radius:0 8px 8px 0;width:33%;">
      <div style="font-size:1.6em;font-weight:700;color:#e84393;">5.37%</div>
      <div style="font-size:0.75em;opacity:0.5;">Avg Stock-Out Rate</div>
    </td>
  </tr>
</table>

</div>

### Top 3 Regions with Highest Stock-Out

| # | Region | Avg Stock-Out | Max Stock-Out |
|---|--------|:-------------:|:-------------:|
| 1 | **Abreu de Gomes** | 🔴 33.33% | 66.67% |
| 2 | **Abreu de Pimenta** | 🔴 33.33% | 66.67% |
| 3 | **Martins de da Rocha** | 🔴 33.33% | 66.67% |

---

## Pipeline Architecture

```mermaid
flowchart TB
    subgraph Stage1["Stage 1 — Ingestion"]
        A[DataMission API<br/>GET /projects/{id}/dataset] --> B[requests.get<br/>headers: Bearer token]
        B --> C[raw_data.json<br/>10,000 records]
    end

    subgraph Stage2["Stage 2 — Processing"]
        C --> D[build_demand_forecast<br/>pandas DataFrame]
        D --> E[compute_ruptura<br/>groupby by region<br/>mean + max]
    end

    subgraph Stage3["Stage 3 — Report"]
        E --> F[print_summary<br/>Top 3 regions]
        E --> G[rupture_report.csv<br/>4,150 regions analyzed]
    end

    style Stage1 fill:#e8439320,stroke:#e84393,stroke-width:1px
    style Stage2 fill:#e8439320,stroke:#e84393,stroke-width:1px
    style Stage3 fill:#e8439320,stroke:#e84393,stroke-width:1px
```

<div align="center" style="margin:24px 0;">

<table style="border-collapse:separate;border-spacing:0;min-width:480px;">
  <tr>
    <td colspan="3" align="center" style="padding:0 0 8px 0;">
      <div style="display:inline-block;border:1.5px solid #e84393;border-radius:8px;padding:12px 24px;text-align:center;">
        <div style="font-weight:700;font-size:1em;letter-spacing:0.04em;color:#e84393;">3-Stage ETL Pipeline</div>
        <div style="font-size:0.8em;opacity:0.5;">Python · pandas · requests · DataMission API</div>
      </div>
    </td>
  </tr>
  <tr><td colspan="3" align="center" style="padding:0;"><div style="width:1.5px;height:14px;background:#e84393;opacity:0.2;margin:0 auto;"></div></td></tr>
  <tr>
    <td align="center" style="padding:0 8px;width:33%;">
      <div style="border:1px solid #e84393;border-radius:6px;padding:8px 14px;text-align:center;">
        <div style="font-weight:600;font-size:0.85em;letter-spacing:0.02em;">Stage 1</div>
        <div style="font-size:0.7em;opacity:0.5;">API Ingestion<br/><code>fetch_data()</code></div>
      </div>
    </td>
    <td align="center" style="padding:0 8px;width:33%;">
      <div style="border:1px solid #e84393;border-radius:6px;padding:8px 14px;text-align:center;">
        <div style="font-weight:600;font-size:0.85em;letter-spacing:0.02em;">Stage 2</div>
        <div style="font-size:0.7em;opacity:0.5;">Transform &amp; Aggregate<br/><code>process_inventory()</code></div>
      </div>
    </td>
    <td align="center" style="padding:0 8px;width:33%;">
      <div style="border:1px solid #e84393;border-radius:6px;padding:8px 14px;text-align:center;">
        <div style="font-weight:600;font-size:0.85em;letter-spacing:0.02em;">Stage 3</div>
        <div style="font-size:0.7em;opacity:0.5;">Report &amp; Export<br/><code>save_report()</code></div>
      </div>
    </td>
  </tr>
</table>

</div>

### Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Orchestration | Sequential `main.py` | Simplicity for MVP — no Airflow/Prefect overhead |
| Raw format | JSON | Fidelity to API schema, preserves all fields |
| Analytics | pandas | Mature ecosystem for CI/CD and prototyping |
| Auth | `.env` + Bearer token | Portable, no cloud dependency |
| Dashboard | HTML/CSS/JS | Self-contained, no server needed |

> 📖 Full ADR: [`decisions/ADR-001-rupture-pipeline.md`](decisions/ADR-001-rupture-pipeline.md)

---

## Dashboard

A self-contained HTML dashboard visualizes stock-out results with interactive filters.

<div align="center" style="margin:24px 0;">
  <table style="border-collapse:separate;border-spacing:0;min-width:480px;">
    <tr>
      <td align="center" style="padding:20px;border:1px dashed #e84393;border-radius:8px;opacity:0.6;">
        <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="4" y="8" width="40" height="32" rx="4" stroke="#e84393" stroke-width="1.5" fill="none" opacity="0.4"/>
          <line x1="12" y1="20" x2="36" y2="20" stroke="#e84393" stroke-width="1" opacity="0.3"/>
          <rect x="12" y="24" width="6" height="12" rx="1" fill="#e84393" opacity="0.3"/>
          <rect x="22" y="18" width="6" height="18" rx="1" fill="#e84393" opacity="0.5"/>
          <rect x="32" y="12" width="6" height="24" rx="1" fill="#e84393" opacity="0.7"/>
        </svg>
        <br/>
        <span style="font-size:0.85em;opacity:0.5;">[ Screenshot: Dashboard showing regional stock-out rates ]</span>
      </td>
    </tr>
  </table>
</div>

**Dashboard features:**
- Regional rupture rate visualization (bar chart)
- Summary cards (total regions, avg stock-out, worst performer)
- Data quality status indicator
- Export-ready insights

Open locally:
```bash
# Windows
start dashboard/index.html
# Mac
open dashboard/index.html
```

---

## Stack & Technologies

| Technology | Version | Role |
|------------|---------|------|
| Python | ≥ 3.10 | Runtime |
| pandas | ≥ 2.0.0 | DataFrames, aggregations |
| requests | ≥ 2.31.0 | HTTP API client |
| DataMission | — | Retail inventory data source |
| Docker | — | Containerized deployment |
| HTML/CSS/JS | — | Self-contained dashboard |

**Minimal deps:** Only **2 external packages** — lightweight, portable, reproducible.

---

## Qualidade de Dados / Data Quality

6 data quality rules enforced in the pipeline, split between blockers and warnings:

| ID | Rule | Column | Severity |
|:--:|------|--------|:--------:|
| DQ-01 | NOT NULL | `region` | 🚫 blocker |
| DQ-02 | POSITIVE (≥ 1) | `current_stock` | 🚫 blocker |
| DQ-03 | POSITIVE (> 0) | `demand_forecast` | 🚫 blocker |
| DQ-04 | RANGE [-1, 1] | `ruptura` | ⚠️ warning |
| DQ-05 | NOT NULL | `order_id` | 🚫 blocker |
| DQ-06 | NOT NULL | `store_location` | 🚫 blocker |

**Protections:** Division-by-zero guard in `compute_ruptura()`, clamp in `build_demand_forecast()`.

Documentação completa: [`data/quality_rules.md`](data/quality_rules.md)

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/laurentaf/giovanna-rupture-monitor.git
cd giovanna-rupture-monitor

# 2. Configure
cp .env.example .env
# Add your DataMission API token to .env

# 3. Install
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt

# 4. Run
python main.py
# → 3-stage pipeline: fetch → process → report
```

### Docker

```bash
docker build -t giovanna-rupture-monitor .
docker run --env-file .env giovanna-rupture-monitor
```

### CI/CD

The pipeline runs daily at 06:00 UTC via GitHub Actions:
```yaml
# .github/workflows/ingest.yml
schedule: "0 6 * * *"
sla: "< 5 minutes per 10,000 records"
```

---

## Project Structure

```
giovanna-rupture-monitor/
├── main.py                  # 3-stage ETL pipeline
├── requirements.txt         # requests + pandas
├── Dockerfile               # Container image
├── .env.example             # Environment template
├── .gitignore
│
├── data/
│   ├── raw_data.json        # Raw API response
│   ├── rupture_report.csv   # Regional summary
│   └── quality_rules.md     # DQ baseline
│
├── dashboard/
│   └── index.html           # Self-contained dashboard
│
├── decisions/
│   └── ADR-001-rupture-pipeline.md
│
└── spec/
    ├── constitution.md
    └── todo.md
```

---

## Output

Each pipeline run produces:

| File | Description |
|------|-------------|
| `data/raw_data.json` | Raw JSON from DataMission API (10,000 records) |
| `data/rupture_report.csv` | Ranked by average stock-out rate per region |
| `data/quality_rules.md` | Documented quality checks (DQ-01 to DQ-06) |

---

## Contributing

| Escopo / Scope | Caminho / Path |
|--------|---------|
| **Bug / melhoria** | Abra uma [issue](https://github.com/laurentaf/giovanna-rupture-monitor/issues) |
| **Nova fonte de dados** | PR com spec + testes |
| **Documentação** | PR com descrição — sem gate |
| **Dashboard** | Melhorias visuais via PR com screenshot |

---

## License

<div style="margin:16px 0;">

**MIT** — veja [`LICENSE`](https://github.com/laurentaf/giovanna-rupture-monitor/blob/main/LICENSE) para o texto completo.

Inventory data you can trust — toda semana, automaticamente.

</div>

---

<div align="center" style="margin:36px 0;opacity:0.25;font-size:0.8em;">
<svg width="28" height="28" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-bottom:4px;">
  <rect x="4" y="4" width="56" height="56" rx="12" stroke="#e84393" stroke-width="1.5" fill="none" opacity="0.15"/>
  <rect x="16" y="32" width="6" height="16" rx="1" fill="#e84393" opacity="0.3"/>
  <rect x="26" y="24" width="6" height="24" rx="1" fill="#e84393" opacity="0.5"/>
  <rect x="36" y="16" width="6" height="32" rx="1" fill="#e84393" opacity="0.6"/>
</svg>
<br/>
Giovanna Rupture Monitor — parte do ecossistema <a href="https://github.com/laurentaf/laos" style="text-decoration:none;">LAOS</a>
</div>
