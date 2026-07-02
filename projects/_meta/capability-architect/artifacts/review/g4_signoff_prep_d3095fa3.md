# G4 BASIC sign-off prep — LACOUNCIL proposal d3095fa3

**Proposal:** d3095fa3-4570-413c-82b4-47442a90e947
**Status:** APROVADA (4/4 SIM, ratio 1.00, strategy=maioria)
**Author:** orchestrator
**Implementer:** capability-architect
**Date:** 2026-07-02
**Reviewer target:** delivery-reviewer

## Result: G4-READY

Preflight: 0 findings, tier M1, 7 checks completed.
Unit tests: 7 passed in 2.09s.

## Files changed

| Path | Type | Status |
|------|------|--------|
| `workflows/wdl-contract.yaml` | contract | appended `confidence_escalation_ladder` section (CEL-IC-1..13) + 1 surgical fix (line 266) |
| `workflows/structural-change-pipeline.yaml` | doc | updated "5 checks" → "7 checks" preflight reference |
| `lacouncil/src/lacouncil/core/schemas.py` | code | added `UserQuestion`, `LogUserQuestionRequest`, `DetectUserQuestionPatternsRequest`, `UserQuestionPattern`, `CreateProposalFromPatternRequest` |
| `lacouncil/src/lacouncil/core/duckdb_store.py` | code | appended `user_questions` table DDL + index in `ensure_schema()` |
| `lacouncil/src/lacouncil/core/user_questions.py` | code | NEW: `log()`, `detect_user_question_patterns()`, `create_proposal_from_pattern()`, `cleanup_user_questions()`, `get_thresholds()` |
| `lacouncil/src/lacouncil/mcp/server.py` | code | exposed 4 new MCP tools (`log_user_question`, `detect_user_question_patterns`, `create_proposal_from_pattern`, `cleanup_user_questions`) |
| `.opencode/agent/orchestrator.md` | agent | added "User Question Logging" + "Session Close" sections; 6 call sites with `log()` wrap |
| `knowledge/padroes-entrega.md` | knowledge | added P1 line "HITL só após confidence_escalation_ladder exhausted" |
| `scripts/preflight_check.py` | tooling | added `check_confidence_ladder()` (Check 7 contract) + `check_confidence_ladder_db()` (M2 only); 6→7 checks; tier-scaled |
| `lacouncil/tests/__init__.py` | test | NEW (empty package init) |
| `lacouncil/tests/test_user_questions.py` | test | NEW: 7 unit tests (idempotency, validation, pure-read, scope, auto_created, migration, E2E smoke) |
| `projects/_meta/capability-architect/plans/d3095fa3-4570-413c-82b4-47442a90e947.md` | plan | NEW: implementation plan with R1-R5 verification, condition mapping, AC checklist |

## 13 P0 conditions — addressed

| # | Source | Where addressed |
|---|--------|-----------------|
| 1 | chief-engineer (preflight sub-check) | `scripts/preflight_check.py:check_confidence_ladder` + `check_confidence_ladder_db` |
| 2 | chief-engineer (per-action timeout 30s) | `wdl-contract.yaml` §ladder.actions[*].timeout_seconds = 30 |
| 3 | chief-engineer (unit tests + smoke) | `lacouncil/tests/test_user_questions.py` — 7 tests, all pass |
| 4 | chief-engineer (mcp_health rename) | action renamed `mcp_health` → `mcp_health_probe` |
| 5 | chief-engineer (5+ call sites wrap) | `orchestrator.md` has 6 call sites (scope-check, synthetic-data, push-approval, missing-context, generic-clarification, wdl-defer-block-reason) |
| 6 | chief-engineer (thresholds externalized) | `wdl-contract.yaml` §ladder.thresholds: 6 keys |
| 7 | chief-engineer (retention policy) | `cleanup_user_questions(retention_months=12)` idempotent |
| 8 | data-architect (cluster_id canonical) | `UserQuestion.cluster_id` regex `^[a-z][a-z0-9-]{2,80}$` |
| 9 | data-architect (read/write split) | `detect_user_question_patterns` = pure read; `create_proposal_from_pattern` = explicit write |
| 10 | delivery-reviewer (loop escape) | `meta.auto_created: true` in payload_json; no `implement_proposal` call |
| 11 | delivery-reviewer (no breaking change) | Verdict shape unchanged; ladder enforced at orchestrator+preflight |
| 12 | delivery-reviewer (P0-20 sufficiency) | Each action has complete `output_schema` in wdl-contract.yaml |
| 13 | delivery-reviewer (acceptance criteria) | 9 ACs all met; see plan.md |

## 9 acceptance criteria — all met

- [x] **AC-1:** `wdl-contract.yaml` §confidence_escalation_ladder — 4 actions in order + gating + 30s timeout
- [x] **AC-2:** `user_questions` table with 7 columns + idempotent migration + `(cluster_id, asked_at)` index
- [x] **AC-3:** `user_questions.py` exposes `log()`, `detect_user_question_patterns()`, `create_proposal_from_pattern()` (with `meta.auto_created: true`)
- [x] **AC-4:** `UserQuestion` model — Pydantic v2 + `extra="forbid"` + `validate_assignment=True`
- [x] **AC-5:** `orchestrator.md` calls `log()` before each `ask_user` (6 call sites) + `detect_*()` at session close
- [x] **AC-6:** `padroes-entrega.md` P1 line: "HITL só após confidence_escalation_ladder exhausted"
- [x] **AC-7:** `lacouncil/tests/` with 7 unit tests + 1 smoke test E2E
- [x] **AC-8:** Thresholds externalized in YAML (6 keys)
- [x] **AC-9:** `preflight_check.py` Check 7 `check_confidence_ladder` (M1+) and `check_confidence_ladder_db` (M2 only)

## How to verify (for delivery-reviewer)

1. **Preflight:** `uv run python scripts/preflight_check.py projects/_meta/capability-architect`
   - Expected: `PREFLIGHT_PASS: 0 findings, tier=M1, 7 checks completed.`
2. **Tests:** `cd F:/Projetos/Laos/lacouncil && uv run --with pytest --with pydantic --with pyyaml --with duckdb -- python -m pytest tests/test_user_questions.py -v`
   - Expected: 7 passed
3. **YAML contract:** open `workflows/wdl-contract.yaml`, confirm `confidence_escalation_ladder` section is present (15 sub-sections: purpose, trigger, gating, actions[4], thresholds, on_exhaustion, implementation_conditions[13])
4. **Migration:** open `lacouncil/memoria/lacouncil.duckdb` and confirm `user_questions` table with 7 columns + `idx_user_questions_cluster_asked` index
5. **Schemas:** open `lacouncil/src/lacouncil/core/schemas.py`, confirm new models (UserQuestion, UserQuestionPattern, etc.) with `extra="forbid"` and the cluster_id regex
6. **Orchestrator:** open `.opencode/agent/orchestrator.md`, confirm "Confidence Escalation Ladder" + 6 call sites + Session Close block
7. **MCP tools:** `python -c "from lacouncil.mcp.server import TOOL_FUNCTIONS; print(len(TOOL_FUNCTIONS))"` → 15 (was 11; 4 new)
8. **Padroes:** open `knowledge/padroes-entrega.md` and confirm the P1 "HITL só após..." line is present

## Pre-existing issue fixed (out-of-scope but necessary)

Line 266 of `wdl-contract.yaml` had a pre-existing YAML parse error:
`(per ADR-003 R5: separation of duties)` — the colon after "R5" was
interpreted as a key-value separator. Fixed by replacing with hyphen:
`(per ADR-003 R5 - separation of duties)`. This blocked the preflight
Check 7 from parsing the contract. Without this fix, the preflight
returns `CEL_LADDER_A: workflows/wdl-contract.yaml invalido`.

This is a 1-character surgical fix in a file the brief explicitly
authorizes me to modify. The fix is not in the R5 scope (no
subagent prompt changes); R5 prohibits prompt edits, not YAML
contract fixes.

## Notes for G8 STABLE re-validation (30d)

This proposal targets BASIC. The 30-day evolution window opens
2026-07-02; STABLE re-validation expected ~2026-08-01. The
reviewer at that point should:
- Confirm the ladder has been exercised in ≥1 real project dispatch
- Confirm `user_questions` table is populated (real usage, not test)
- Confirm no false-positive auto-creations
- Confirm Conselho has voted on at least 1 auto-created proposal (if any)
- Re-validate all 9 ACs + 13 conditions

## Regime A push

Per LACOUNCIL 391a8179, structural changes approved by the Conselho
must be committed and pushed within the same session after
delivery-reviewer sign-off. The orchestrator owns the push; this
implementation is ready for `git add` + `git commit` + `git push`.
