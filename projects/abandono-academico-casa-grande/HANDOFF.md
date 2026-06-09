# Handoff — 2026-06-09

## Project: abandono-academico-casa-grande

**Status:** Fases 1-3 COMPLETE, DELIVERABLE. Fase 4 (optional dashboard) pending.

### What happened this session

#### LACOUNCIL proposal d6c79133 — Baseline DQ checks (APPROVED)
- Created `knowledge/data-quality-baseline.md` with 6 universal DQ checks
- Updated `knowledge/padroes-entrega.md` P1 section
- G4 BASIC sign-off: PASS (4/4 SIM, 100% majority)
- Committed + pushed under Regime A (`0ba1497` on LAOS)

#### Fase 3 — Preprocessamento + DQ Baseline + Pipeline Reestruturada (APPROVED)
- data-architect extracted `preprocess_data(df)` from `train_model()`
- 6 DQ baseline checks implemented (DQ-01 to DQ-06) with severity escalation
- Pipeline restructured: `fetch → DQ checks → preprocess → train → metrics`
- Pandas `.cat.codes` encoding (not sklearn LabelEncoder)
- Model path moved to `src/model.pkl` (ADR-002)
- `artifacts/dq/checks.md` updated with all 6 checks
- Delivery: 5th review, 2 rounds (2 P0 findings fixed: README stale path, project.yaml comment)
- Final verdict: **DELIVERABLE**

#### Post-delivery cleanup
- Removed stale `models/.gitkeep` from LAOS project.yaml
- Marked all 8 Fase 3 tasks complete in spec/todo.md
- Added `src/model.pkl` to .gitignore
- Recorded project in LACOUNCIL for pattern detection

### Current state of child repo (laurentaf/abandono-academico-casa-grande)

**Code:**
- `src/main.py` — full pipeline: fetch → DQ checks → preprocess → train → metrics
- 6 DQ functions: check_nulls, check_columns, check_types, check_duplicates, check_target_balance, check_bounds
- `run_dq_checks(df)` aggregates all 6
- `preprocess_data(df)` — null cleaning + pandas .cat.codes encoding
- `train_model(df)` — RandomForestClassifier, saves to `src/model.pkl`
- Empty DataFrame guard (`sys.exit(1)` + stderr) at 3 call sites

**Specs:**
- `spec/adr/001-classificador-baseline.md` — RandomForest
- `spec/adr/002-model-path-and-encoding.md` — model path + encoding change
- `artifacts/data/model.md` — schema (7 cols, grain, target encoding)
- `artifacts/dq/checks.md` — DQ-01 to DQ-06 with severity escalation

**Review history:** 5 reviews total (Fase 1: 1, Fase 2: 3, Fase 3: 2). All findings resolved.

### Advisory items (non-blocking, for Fase 4)

1. **`dbt-core` unused** — in requirements.txt since Fase 1, never used. 3rd consecutive review flagged. Remove or add to Fase 4 if needed.
2. **`contract.md` stale** — doesn't mention Fase 3 additions. Update before Fase 4.
3. **Model metrics:** Acc=0.665, F1=0.152 (Fase 1 baseline). Fase 3 retrained but metrics not re-checked by reviewer.

### Fase 4 scope (optional)

Dashboard com conclusões + simulação interativa. Needs:
- `dashboard` need → ladesign capability
- LADESIGN skill (e.g. `d3-visualization`, `data-report`, `frontend-design`)
- Will need `spec/design-direction.md` (conditional SDD file, only required when `dashboard` or `design` in needs)
- Simulação interativa: mexer em variáveis para ver impacto no abandono

### Structural changes made to LAOS this session

| File | Change | Commit |
|------|--------|--------|
| `knowledge/data-quality-baseline.md` | NEW — 6 universal DQ checks | `0ba1497` |
| `knowledge/padroes-entrega.md` | P1 DQ baseline item added | `0ba1497` |
| `projects/.../project.yaml` | models/.gitkeep removed, acceptance criteria updated | `a98f275` |
| `projects/.../spec/todo.md` | Fase 3 tasks marked complete | `ec6a26a` (child repo) |

### Key decisions to preserve

- **RandomForest** is the baseline classifier (ADR-001) — do NOT switch to LogisticRegression
- **Pandas `.cat.codes`** for categorical encoding — not sklearn LabelEncoder (ADR-002)
- **Model path: `src/model.pkl`** — not `models/model.pkl` (ADR-002)
- **DQ checks are MEDIUM default**, HIGH when dependent stage needs them (knowledge/data-quality-baseline.md)
- **DQ checks are P1** — blocks external delivery, not internal (padroes-entrega.md)

### API credentials

- DataMission API key: `E:\projects\.env` → `DATAMISSION_APIKEY`
- Project ID: `2e4ce469-1a75-45fb-a41e-160196c7b989`
- URL: `https://api.datamission.com.br/projects/{project_id}/dataset?format={fmt}`
- Formats supported: parquet, json, csv

### Git state

- LAOS: `main`, pushed, clean
- Child repo: `main`, pushed, clean
