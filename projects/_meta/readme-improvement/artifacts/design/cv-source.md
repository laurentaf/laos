<!--
  Input artifact — Laurent's CV (source for README profile rewrite)
  Source: F:\cv_ats_enhanced.md (external, out of E:/projects/** scope)
  Copied by orchestrator on 2026-07-01 to make content accessible to dashboard-designer.
  This is an INPUT, not a deliverable. The deliverable is readme-laurentaf-profile.md.
-->

# Laurent Ferreira

**AI Data Engineer** | Data Architect & ML Engineer
Campinas, SP — Remote
(15) 9 9692-9635 | laurentalp@hotmail.com
github.com/laurentaf | linkedin.com/in/lauferreira

---

## Professional Summary

Specialist Data Engineer and ML Architect with deep expertise in AI-driven data pipeline orchestration, multi-agent systems, and MCP protocol architecture. Designed and implemented LAOS (Laurent Agent Operating System), a complete meta-OS for composable AI with 7 independent MCP capabilities, 11 specialized agent types, and deterministic governance routing. At healthcare operator Vera Cruz, architected Medallion Architecture (dbt + Oracle 19c + Databricks Lakehouse) integrating TASY ERP, Avaya telephony, and multi-agent AI orchestration for autonomous and secure data workflows. Delivered 6+ production projects spanning dropout prediction (87.5% accuracy), retail analytics (4,150 regions), NLP exam forecasting (1,236 questions), and IFRS17-compliant healthcare reporting. Strong domain expertise in supplementary healthcare (ANS-regulated), LGPD compliance, econometric modeling (OLS, GLM, logit, NPS driver analysis), and interpretable ML (SHAP, partial dependence).

---

## Technical Skills

### Data Engineering & Architecture
**SQL** (Oracle 19c, PostgreSQL, DuckDB, Azure SQL) | **dbt** (incremental models, medallion architecture) | **ETL/ELT Pipeline Design** | **Data Lakehouse** (Bronze -> Silver -> Gold) | **Databricks** + Microsoft Azure | **Data Governance & Privacy** (LGPD, IFRS17) | **Data Quality** (6-dimension baseline: null profiling, type validation, duplicate detection, bounds) | **MS Fabric** | **Data Warehouse Design** | **Cross-project Data Conventions** (shared _commomdata pattern)

### Machine Learning & Econometrics
**scikit-learn** | **xgboost** | **lightgbm** | **catboost** | **statsmodels** (OLS, GLM, ordered/grouped logit, probit) | **optuna** (hyperparameter optimization) | **SHAP** | **LIME** | **Partial Dependence Plots** | **Causal Inference** | **Time Series Forecasting** | **NPS Driver Analysis** | **Empirical Probability Modeling** | **Laplace Smoothing**

### AI Systems & Architecture
**Multi-Agent Orchestration** (11 agent types, namespace isolation, 3 dispatch modes) | **Model Context Protocol (MCP)** — wired 7+ domain MCP servers | **LLM Governance** (proposal lifecycle, voting, trust scores, DuckDB audit trail) | **Spec-Driven Development (SDD)** methodology | **WDL Preflight Gate** (tri-state verdict: READY/DEFER/ESCALATE with penalty system) | **Plugin Architecture** — 13 enforcement plugins (TypeScript, OpenCode hooks) | **Confidence Protocol** (Agreement Matrix: KB vs MCP alignment scoring)

### Automation & Integration
**n8n** (self-hosted, workflow composition, SLA-based automation) | **API Integration** (REST, webhooks) | **Batch Processing** | **Playwright** | **CI/CD** (pre-flight checks, boot validation, pre-push hooks, git sync regimes A/B) | **Docker** (containerized deliverables, single docker run deployments)

### Programming Languages
**Python** (>=3.11, primary: 48.2% of LAOS codebase) | **TypeScript** (44.7%, 13 plugins, 1,844-line infrastructure plugin) | **SQL** | **JavaScript** | **PowerShell** | **HTML/CSS** | **YAML**

### Tools & Platforms
**DuckDB** (embedded analytics, in-process OLAP) | **FastMCP** | **Pydantic v2** | **Typer CLI** | **uv** (Python package manager) | **pnpm** | **npx** | **OpenCode CLI** | **Power BI** | **Excel VBA** | **Git** | **GitHub Actions** | **Streamlit**

### Domain Platforms
**Oracle 19c** | **Azure Databricks** | **DuckDB** | **n8n** | **TASY ERP** | **Avaya** (telephony integration) | **MS Fabric**

---

## Professional Experience

### Senior BI Analyst | Vera Cruz Health Plan — Campinas/SP | 2021 - Present

**Data Pipeline Architecture & Multi-Agent AI Orchestration**
- Architected and implemented medallion data architecture (Bronze, Silver, Gold) using **dbt** + **Oracle 19c**, integrating **TASY ERP** for financial reporting production with Python automations and multi-agent **AI orchestration** — ensuring autonomous and secure workflows where AI accesses metadata only, never raw data.
- Led the operator's migration to **Databricks Lakehouse** within the economic group's cloud infrastructure (**Microsoft Azure**), conducting data quality improvement and migration strategy.
- Engineered **Big Data pipelines (10+ TB)** from diverse SQL and NoSQL sources with automated **dbt**, Oracle, and **MS Fabric** incremental jobs — optimizing performance while maintaining cost efficiency.
- Developed **strategic KPIs and executive dashboards** in Power BI for commercial, enrollment, administrative, sales, legal, medical auditing, and claims departments.

**IFRS17 Compliance & Data Governance**
- Led IFRS17 adaptation — rule revision, loss provision model adjustment, and audit support with Deloitte, KPMG, Grant Thornton, and MS Consulting.
- Implemented data governance framework (dictionary, versioning, access control, LGPD — Data Governance & Privacy).
- Created **executive templates and Power BI dashboards** for C-level with multi-source data (Oracle SQL, PostgreSQL, Excel, SharePoint, APIs).
- Optimized database views and queries — workloads that previously took weeks were reduced to **minutes with full traceability**.
- Built comparative dashboard for billing, delinquency, on-time payments, recovery, debt aging, and cost center with **RLS security per user**.

### Logistics Manager | Chez Violeta — Salto/SP | 2017 - 2021
- Developed store stock quality dashboard across 10 locations.
- Managed inventory, logistics, and purchasing for a 10-store retail chain with short life cycle products (women's fashion).
- Structured post-product pricing strategy in fast-cycle market.
- Professionalized digital channel to strategic level integrated with ERP; expanded to **Mercado Libre Full**.
- Direct team management (10+ seasonal staff in peak periods) and store supervisor coordination.
- Reduced logistics costs by **50%+** via transportation outsourcing.
- Implemented logistics performance and quality KPIs.

---

## Flagship Projects

### LAOS — Laurent Agent Operating System (github.com/laurentaf/laos)
*June 2026 · 115 commits in 19 days · Python/TypeScript*

Complete meta-operating system for composable AI. Features:
- **7 domain MCP capabilities**: LATADE (data engineering), LADESIGN (design), LAN8N (automation/n8n), LAECON (econometrics + ML), LAENGINE (game simulation), LACOUNCIL (governance)
- **11 specialized agent types** with namespace-isolated MCP access, 3 dispatch modes (sequential, parallel, consensus)
- **13 TypeScript enforcement plugins**: MCP Wall, WDL Gate, Guards, Recovery, Fallback, Intent Gate, Comment Checker, Format Guard, Plan Validator, Doctor, Infra (1,844 lines), Dispatch, Continuation
- **LACOUNCIL governance engine**: 14+ approved proposals, 3 voting strategies (unanimity/supermajority/majority), DuckDB audit trail, separation of powers (investigation -> proposal -> voting -> implementation -> sign-off)
- **WDL Preflight Gate**: Tri-state READY/DEFER/ESCALATE before any specialist dispatch with trust-score penalty system (-0.1/-0.3/-0.5 per bypass)
- **Spec-Driven Development (SDD)**: 9-file mandatory scaffold before any technical work
- **17 knowledge files**, 17 automation scripts, 4 declarative workflow templates
- **Full stack**: Python 48.2%, TypeScript 44.7%, SQL, YAML, PowerShell, HTML/CSS
- **License**: MIT | **Status**: Active development

### Academic Dropout Prediction — Universidade Casa Grande
*ML Pipeline · 87.5% accuracy · 93.7% recall · 32,593 students*

Binary classification pipeline predicting academic dropout using OULAD dataset. Features: demographics, registration, temporal VLE interactions, assessment data. Stack: scikit-learn, pandas, DuckDB, dbt. Delivered to client with HTML dashboard.

### Brazilian Public Exam Prediction — Previsao de Concursos
*NLP/ML · 1,236 questions · 27 contests · FCC/FGV*

Web platform predicting exam topics using hierarchical Bayesian approach with Laplace smoothing. Empirical probabilities per board/position (Auditor Fiscal target). No LLM hallucination — purely data-driven ranking. Stack: scikit-learn, xgboost, SHAP, optuna, BeautifulSoup, DuckDB.

### Retail Stock Rupture Monitor — Lojas Giovanna
*ETL + Analytics · 4,150 regions analyzed · 33% rupture detection*

Fully Dockerized ETL pipeline with synthetic data (ShadowTraffic by design). Calculates stock-out rates per region, generates CSV reports and interactive HTML dashboards. Single `docker run` produces complete functional deliverable.

### LAECON — Econometrics & Interpretable ML Capability
*Created 2026-06-04 · Promoted BASIC->STABLE in 10 days · 9 MCP tools*

Full econometrics + ML MCP capability: OLS, GLM (logit/probit), ordered/grouped models, NPS driver analysis, causal inference, time series. 926-line Constitution, 17 binding conditions from Conselho. Full Python ML stack: scikit-learn, statsmodels, xgboost, lightgbm, catboost, shap, lime, optuna.

### LAOS Brand System
*8 brand artifacts · Complete design system*

Narrative architecture (manifesto, taglines, voice & tone), visual identity (design tokens, palette #6c5ce7, typography), keynote deck, landing page. Brand thesis: "The laurel was exclusive. The intelligence doesn't have to be."

### Retail Stock Ingestion — Lojas Emanuella
*ETL Pipeline · SLA < 5 min · 3-stage medallion*

Weekly inventory forecast ingestion: API ingestion -> transformation -> dbt artifact preparation. Clean 3-stage pipeline with dbt-ready output. Delivered to client.

### Brasfoot Game POC
*Game Dev · 10 teams · 18 rounds · Full simulation*

Football management game POC with 10 Brazilian teams, round-robin league, text commentary match engine, live league table. HTML/JS + Python backend. Evolved into laengine capability.

---

## LACOUNCIL Governance — Structural Improvements

Author and architect of the LAOS governance engine. Key approved proposals:
- **SDD Scaffold Missao 0** (unanimity 4/4, 2026-06-05) — Mandatory 9-file SDD scaffold for every project
- **WDL v1 + Charter P0** (2 proposals, supermajority 4/4, 2026-06-06) — WDL preflight gate with penalty system, 16 deliverables
- **LAECON Capability** (supermajority 4/4, 2026-06-04) — Econometrics + ML, 17 binding conditions
- **Capability-Architect** (supermajority 4/4, 2026-06-04) — Meta-architect subagent, 16 binding conditions
- **Charter Autonomy** (supermajority 4/4, 9 consolidated amendments) — Subagent boot checks, short briefs
- **Structural Change Pipeline** (unanimity 4/4, 2026-06-19) — 7-stage meta-workflow with iteration clause
- **Git Sync Regime A/B** (majority 4/4) — Structural (mandatory push) vs domain (user-confirmed push)
- **Baseline DQ Checks** (majority 4/4, 2026-06-09) — 6 universal DQ baseline checks
- **LAOS Infra Tools** (supermajority 4/4, 2026-06-14) — laos.infra capability with 5 MCP tools
- **Debug Agent + explore_filesystem** (supermajority 4/4, 2026-06-19)
- **14+ total proposals** approved with full audit trail

NOTE: LACAREEROPS was discontinued on 2026-07-01 (LACOUNCIL proposal e65617ec). Do NOT include it in the README.

---

## Education

**Post-graduate — Business Management & Strategy** | UNICAMP (University of Campinas)
*Emphasis: Agile project management (Scrum, Kanban, Lean), strategic decision-making, corporate innovation*

**Bachelor of Arts — Economics** | UNICAMP (University of Campinas)

**Technical — Information Technology** | Colegio Objetivo

---

## Complementary Courses
- **Semana AI Data Engineer** — Data Engineering Academy (Apr/2026)
- **Building Trustworthy AI at 200km/h** — Google Developer Experts (Apr/2026)
- **ETL Pipeline with Python from Zero** — Jornada de Dados (2024)
- **Python** — Hashtag Treinamentos (2022)
- **Power BI** — Empowerdata (2021)
- **Excel VBA** — Sigma Treinamentos (2020)
- **Leadership & Resilience** — PUCRS (2021)
- **Innovative Business Modeling** — UNICAMP (2015)

---

## Languages
- **Portuguese** — Native
- **English** — Advanced (comprehension, speaking, fluent reading)

---

## Key Metrics Summary
- **6 domain projects** delivered in 3 verticals (healthcare, retail, education, gaming)
- **11 capability MCP servers** wired across data, design, automation, governance, econometrics, gaming
- **115 commits** in 19 days on LAOS alone
- **87.5% accuracy / 93.7% recall** on academic dropout prediction (32,593 students)
- **4,150 regions** analyzed in retail rupture monitoring
- **1,236 exam questions** modeled for public contest prediction
- **14+ LACOUNCIL proposals** authored and approved
- **13 TypeScript plugins** for mechanical enforcement
- **10+ TB** big data pipelines in healthcare environment
- **50%+ logistics cost reduction** via process optimization
