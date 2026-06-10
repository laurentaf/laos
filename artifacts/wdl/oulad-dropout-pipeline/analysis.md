# WDL v1 Plan Analysis — oulad-dropout-pipeline

**Plan ID:** oulad-dropout-pipeline
**Project:** abandono-academico-casa-grande
**Generated:** 2026-06-09
**Contract:** wdl_version: 1

---

## 1. Request Summary

The project is a full ML pipeline for dropout prediction using the OULAD dataset (32,593 students, 7 CSVs, Open University, CC-BY 4.0). The previous iteration (DataMission dataset) failed due to noise. The pivot to OULAD provides a published, validated dataset with temporal signals (VLE daily clicks).

**Needs declared:** data, etl, ml, predictive-modeling, data-quality, dashboard
**Capabilities routed:** latade (data/etl/dq), laecon (ml/predictive-modeling), ladesign (dashboard)

---

## 2. 3-Q Granularity Scoring

### Q1: Clear Input — Score: 3/3

**Bounded.** Dataset location known (`E:\projects\abandono-academico-casa-grande\data\oulad\`), 7 CSVs enumerated, target variable defined (final_result → binarized dropout), deliverables listed, needs mapped to capabilities. No ambiguity in scope.

### Q2: Validatable Success — Score: 3/3

**Binary.** Every deliverable is pass/fail:
- `src/main.py` runs end-to-end pipeline ✓/✗
- `artifacts/data/model.md` documents data model ✓/✗
- `artifacts/dq/checks.md` has 6 DQ baseline checks ✓/✗
- `artifacts/dashboard/index.html` is interactive ✓/✗
- `README.md` exists (PT-BR, portfolio) ✓/✗
- Model achieves measurable accuracy on holdout ✓/✗

### Q3: Single Type of Reasoning — Score: 2/3

**Mixed.** The project combines three reasoning types across three capabilities:
- **Extract + Build** (latade): CSV ingestion, bronze→silver→gold ETL, DQ checks
- **Synthesize** (laecon): scikit-learn model training, feature importance, evaluation
- **Build + Design** (ladesign): interactive HTML dashboard with sliders

This is not a single reasoning type. However, per the anti-pattern clause (DD condition 2), the pipeline is ONE project lifecycle, not three tasks. The `temporal` signal does not multiply phases.

### Total: 8/9 — Readiness: `partial`

The 3/3/2 score meets the readiness floor (≥2 on all dimensions) but not the full readiness floor (3/3/3). Caveat: mixed reasoning is inherent to ML pipeline projects and does not indicate decomposition failure.

---

## 3. Decomposition Signal Analysis

| Signal | Fires? | Evidence |
|--------|--------|----------|
| conjunction | YES | "ingestion AND profiling AND SQL" + "ETL AND DQ" + "model AND evaluation" + "dashboard AND simulation" |
| plural_criteria | YES | Accuracy, precision, recall, F1, dashboard interactivity, DQ coverage — ≥6 success metrics |
| multi_owns | YES | 3 capabilities: latade (data/etl/dq), laecon (ml), ladesign (dashboard) |
| temporal | YES | data → model → dashboard sequential pipeline |

**All 4 signals fire.** Per contract: "two_or_more_fire: lacouncil.detect_patterns" — called and returned.

### detect_patterns findings

- `etl` and `data` are the most common needs (5 occurrences each)
- `latade` and `lacouncil` are the most used capabilities (7 each)
- Failure pattern: artifacts placed in LAOS path instead of child repo (Hard Rule #2 violation)
- **Action for this plan:** All artifacts MUST go to child repo (`laurentaf/abandono-academico-casa-grande`), not `projects/abandono-academico-casa-grande/`

### Anti-pattern clause application

The `temporal` signal fires because data → model → dashboard is sequential. But per the anti-pattern clause:

> "A linear pipeline (data → design → ship) is one project lifecycle, not three tasks. The 2/3 floor must not be used to multiply project phases."

**Decision:** Do NOT decompose into 3 separate sub-plans. This is ONE plan with capability-split tasks. The temporal signal is acknowledged but does not multiply the verdict.

---

## 4. Capability Split (G-VERDICT-10)

Per the cross-capability calibration, the plan splits by owning capability:

### Task Group A — latade (data-architect)
- **T1: Data Ingestion** — Load 7 CSVs from `data/oulad/` into DuckDB bronze layer
- **T2: ETL Pipeline** — bronze → silver (dedup, type cast) → gold (aggregated features)
- **T3: DQ Baseline** — 6 checks: null profiling, column existence, type validation, duplicate detection, target balance, range/bounds
- **Deliverables:** `artifacts/data/model.md`, `artifacts/dq/checks.md`
- **Route:** data → latade (primary), context7 (optional)

### Task Group B — laecon (capability-architect → specialist)
- **T4: Feature Engineering** — Merge 7 CSVs on student_id + code_module + code_presentation; engineer temporal features (VLE click patterns)
- **T5: Model Training** — scikit-learn classifier (LogisticRegression / RandomForest), train/test split, cross-validation
- **T6: Evaluation** — Accuracy, precision, recall, F1, confusion matrix, feature importance
- **Deliverables:** `src/main.py` (pipeline), model artifacts in child repo
- **Route:** ml + predictive-modeling → laecon (primary), latade (optional)
- **Gap:** laecon is BASIC (not STABLE). MCP server functional but workflows less validated. TTL: 2 cycles.

### Task Group C — ladesign (dashboard-designer)
- **T7: Dashboard Build** — Interactive HTML with model conclusions, feature importance chart, simulation sliders, responsive layout
- **Deliverables:** `artifacts/dashboard/index.html`
- **Route:** dashboard → ladesign (primary), latade + context7 (optional)

### Sequencing

```
T1 (ingestion) → T2 (ETL) → T3 (DQ) → T4 (features) → T5 (train) → T6 (evaluate) → T7 (dashboard)
```

This is a linear dependency chain. Each task depends on the previous. No parallelism possible in the core pipeline.

---

## 5. Risk Assessment

### R1: Previous DataMission Failure (HIGH)
The project failed before with a noisy dataset. OULAD is published in Nature Sci. Data and validated by the research community. **Mitigation:** Statistical validation before full pipeline build. T3 (DQ checks) must confirm dataset quality before T5 (training).

### R2: laecon BASIC Status (MEDIUM)
laecon is BASIC, not STABLE. MCP server exists and is functional, but workflows are less battle-tested. **Mitigation:** Use laecon for model training; if MCP tools fail, fall back to direct scikit-learn in `src/main.py`. Gap acknowledged with TTL=2 cycles.

### R3: Artifact Path Violation (MEDIUM)
detect_patterns found prior Hard Rule #2 violations (artifacts in LAOS instead of child repo). **Mitigation:** All deliverables must go to `laurentaf/abandono-academico-casa-grande/`, never to `projects/abandono-academico-casa-grande/`.

### R4: Dataset Merge Complexity (LOW-MEDIUM)
7 CSVs need merging on student_id + code_module + code_presentation. Some tables have many-to-many relationships (studentVle has multiple rows per student per day). **Mitigation:** T2 (ETL) must document merge strategy and handle cardinality.

### R5: Dashboard Interactivity (LOW)
Simulation sliders require frontend logic. ladesign has extensive skills for this. **Mitigation:** Use ladesign frontend-design or design-taste-frontend skill.

---

## 6. Stage Recommendations

Based on the analysis, the recommended execution plan follows the project.yaml stages with capability routing:

| Stage | Tasks | Capability | Deliverables |
|-------|-------|------------|-------------|
| 1: Ingestion + ETL | T1, T2 | latade (data-architect) | Bronze/silver/gold tables |
| 2: DQ Validation | T3 | latade (data-architect) | artifacts/dq/checks.md |
| 3: Feature Engineering + Training | T4, T5 | laecon (specialist) | src/main.py, model |
| 4: Evaluation + Dashboard | T6, T7 | laecon + ladesign | artifacts/dashboard/index.html |

**Critical gate:** Stage 2 (DQ) must pass before Stage 3 (ML). If DQ checks fail, the pipeline stops and the orchestrator surfaces the gap to the user.

---

## 7. Prior Verdicts

One prior verdict exists for this project: `f4a9c2e1-7b3d-4e8f-a1c6-9d2e5f8b7a04` (READY, dashboard-only task). This new plan supersedes it — the prior verdict scoped only the dashboard build; this plan covers the full pipeline.

---

## 8. Cross-Validation

This analysis was produced by `workflow-decomposer` (planner_id). Per G-VERDICT-2, the `verified_by` field is set to `delivery-reviewer` (bootstrap cross-validator). The delivery-reviewer will countersign during its G4 sign-off cycle.
