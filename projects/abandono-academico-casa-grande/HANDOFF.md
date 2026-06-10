# Handoff — 2026-06-10

## Project: abandono-academico-casa-grande

**Status:** All 4 stages COMPLETE. DELIVERABLE (pending Round 9 review after LAOS-side sync fixes).

### What happened (summary of all sessions)

#### ADR-003: Dataset Reversal DataMission → OULAD
- Original pipeline used DataMission API (1000 records, 7 cols, SUSPENDED target)
- Reversed to OULAD (Open University Learning Analytics Dataset) — 32.593 students, 7 CSVs, CC-BY 4.0
- All code, specs, dashboard, and documentation updated to OULAD

#### Stage 1: OULAD Ingestion + Feature Engineering
- 7 OULAD CSVs → DuckDB bronze (7 tables, 10.9M rows)
- 2 silver tables (deduplicated)
- gold_oulad_features: 32.593 rows x 26 cols
- 6 DQ baseline checks — all PASS
- ETL documented in artifacts/data/etl_oulad.sql

#### Stage 2: Predictive Model + Evaluation
- RandomForest + LogisticRegression + Dummy baseline (5-fold CV)
- RF: 87.5% accuracy, 93.7% recall (dropout), 0.954 ROC-AUC
- Statistical significance: RF vs Dummy p=0.001; RF vs LR p=0.084 (ns)
- Model saved to src/model.pkl
- Comprehensive documentation in artifacts/data/model.md

#### Stage 3: ETL SQL + Documentation
- artifacts/data/etl_oulad.sql with bronze→silver→gold pipeline
- artifacts/data/model.md with schema, ML results, feature importance

#### Stage 4: Dashboard + Interactive Simulation
- Dashboard in artifacts/dashboard/index.html (self-contained HTML, dark theme)
- OULAD metrics: accuracy 87.5%, recall 93.7%, ROC-AUC 0.954
- 5 interactive sliders: last_activity_day, assessment_count, avg_assessment_score, total_clicks, days_active
- Feature importance chart (top 15 features)
- Target distribution, conclusions section

#### LACOUNCIL proposals
- d6c79133 — Baseline DQ checks (APPROVED 4/4, 2026-06-09)
- a4fe9faa + 7fd94c1a — WDL v1 (project predates, not retroactively applied)

### Current state of child repo (laurentaf/abandono-academico-casa-grande)

**Code:**
- `src/main.py` — full pipeline: DuckDB load → DQ checks → feature engineering → train → evaluate
- 6 DQ functions: check_nulls, check_columns, check_types, check_duplicates, check_target_balance, check_bounds
- `_guard_empty()` at 6 pipeline call sites
- Pandas `.cat.codes` encoding (not sklearn LabelEncoder)
- Model saved to `src/model.pkl` (not `models/`)

**Specs:**
- `spec/adr/001-classificador-baseline.md` — RandomForest (Superseded by ADR-003)
- `spec/adr/002-model-path-and-encoding.md` — model path + encoding change
- `spec/adr/003-dataset-reversal-oulad.md` — DataMission → OULAD migration
- `artifacts/data/model.md` — comprehensive (35KB): schema, ML results, feature importance, statistical tests
- `artifacts/dq/checks.md` — DQ-01 to DQ-06 with severity escalation
- `artifacts/dashboard/index.html` — OULAD dashboard (40KB self-contained)

**Review history:** 8 rounds total. Round 7 FAIL (DataMission remnants in dashboard) → Round 8 FAIL (7 LAOS-side stale files + 1 stale checkbox). All fixes committed in Round 8.

### Key decisions to preserve

- **RandomForest** is the baseline classifier (ADR-001) — do NOT switch to LogisticRegression
- **Pandas `.cat.codes`** for categorical encoding — not sklearn LabelEncoder (ADR-002)
- **Model path: `src/model.pkl`** — not `models/model.pkl` (ADR-002)
- **OULAD dataset** — NOT DataMission (ADR-003). DataMission API is dead; do not reference it.
- **Target: final_result binarizado** (Withdrawn=1, others=0), 31.2% positive class
- **DQ checks are MEDIUM default**, HIGH when dependent stage needs them (knowledge/data-quality-baseline.md)
- **DQ checks are P1** — blocks external delivery, not internal (padroes-entrega.md)

### Dataset: OULAD

- Source: https://analyse.kmi.open.ac.uk/open_dataset
- 7 CSVs: studentInfo, studentVle, studentAssessment, studentRegistration, assessments, courses, vle
- 32.593 students, 7 modules, 22 presentations (2013-2014)
- License: CC-BY 4.0 (Kuzilek et al., Nature Scientific Data, 2017)
- Local path: `data/oulad/` (gitignored, `.gitkeep` preserved)

### Git state

- LAOS: `main`, pushed (8 Round 8 fix commits: 5 LAOS-side file syncs + 3 remaining)
- Child repo: `main`, pushed (3 Round 8 fix commits: checklist + todo.md checkbox)
