# Capability-Architect Receipt — LACOUNCIL d3095fa3 (Confidence Escalation Ladder + User Question Log)

**Status:** `implemented`
**Proposal ID:** `d3095fa3-4570-413c-82b4-47442a90e947`
**Plan file:** `projects/_meta/capability-architect/plans/d3095fa3-4570-413c-82b4-47442a90e947.md`
**G4 prep doc:** `projects/_meta/capability-architect/artifacts/review/g4_signoff_prep_d3095fa3.md`
**Preflight:** 0 findings, tier M1, 7 checks completed
**Unit tests:** 7/7 passed in 2.05s

## Summary (2 lines, actionable)
Implemented Confidence Escalation Ladder (wdl-contract.yaml §ladder + 4 new
MCP tools + user_questions table + 6 call sites in orchestrator + Check 7
in preflight + 13 P0 conditions all met).

## Files changed (12)

| File | Change |
|------|--------|
| `workflows/wdl-contract.yaml` | +`confidence_escalation_ladder` section (CEL-IC-1..13) + 1-char YAML fix (line 266) |
| `workflows/structural-change-pipeline.yaml` | "5 checks" → "7 checks" preflight reference |
| `lacouncil/src/lacouncil/core/schemas.py` | +`UserQuestion` + 4 request/response models |
| `lacouncil/src/lacouncil/core/duckdb_store.py` | +`user_questions` table DDL + `(cluster_id, asked_at)` index |
| `lacouncil/src/lacouncil/core/user_questions.py` | NEW: `log()`, `detect_*`, `create_proposal_from_pattern`, `cleanup_user_questions` |
| `lacouncil/src/lacouncil/mcp/server.py` | +4 MCP tools (15 total, was 11) |
| `.opencode/agent/orchestrator.md` | +Confidence Escalation Ladder section (6 call sites + Session Close) |
| `knowledge/padroes-entrega.md` | +P1 line: HITL só após ladder exhausted |
| `scripts/preflight_check.py` | +Check 7 `check_confidence_ladder` + `check_confidence_ladder_db` (M2) |
| `lacouncil/tests/__init__.py` | NEW (empty) |
| `lacouncil/tests/test_user_questions.py` | NEW: 7 unit tests + E2E smoke |
| `projects/_meta/capability-architect/plans/d3095fa3-*.md` | NEW: implementation plan |

## 13 P0 conditions — all addressed

1. **preflight sub-check** — `scripts/preflight_check.py:check_confidence_ladder` + `_db` (M2)
2. **per-action timeout 30s** — `wdl-contract.yaml` §ladder.actions[*].timeout_seconds
3. **unit tests + smoke** — `lacouncil/tests/test_user_questions.py` (7/7 pass)
4. **mcp_health → mcp_health_probe** — chief-engineer condition #4 (name collision avoided)
5. **5+ call sites wrap** — orchestrator.md has 6 documented call sites
6. **thresholds externalized** — `wdl-contract.yaml` §ladder.thresholds (6 keys)
7. **retention policy** — `cleanup_user_questions(retention_months=12)` idempotent
8. **cluster_id canonical** — regex `^[a-z][a-z0-9-]{2,80}$` (kebab-case, 3-80 chars)
9. **read/write split** — `detect_*` pure read; `create_proposal_from_pattern` explicit write
10. **loop escape** — `meta.auto_created: true`; no `implement_proposal` call
11. **no breaking change** — verdict shape unchanged; ladder at orchestrator+preflight layer
12. **P0-20 sufficiency** — each action has complete `output_schema` in wdl-contract.yaml
13. **9 acceptance criteria** — all in plan.md checklist

## 9 acceptance criteria — all met

AC-1 (contract section) ✓, AC-2 (table+index) ✓, AC-3 (3 functions) ✓,
AC-4 (Pydantic v2 model) ✓, AC-5 (6 call sites) ✓, AC-6 (P1 line) ✓,
AC-7 (tests) ✓, AC-8 (YAML thresholds) ✓, AC-9 (preflight Check 7) ✓.

## Pre-existing issue fixed

Line 266 of `wdl-contract.yaml` had unquoted `:` in flow-style YAML that
broke the entire parse. Replaced colon with hyphen: `ADR-003 R5 - separation
of duties`. The fix is necessary for the new Check 7 to validate the
ladder section; without it, preflight returns `CEL_LADDER_A: wdl-contract.yaml invalido`.

## R1–R5 compliance

- **R1** verified: proposal status `aprovada`, 4/4 SIM, ratio 1.00 (queried
  in `F:/Projetos/Laos/lacouncil/src/memoria/lacouncil.duckdb`).
- **R2** no project artifacts (only structural files + tests).
- **R3** no Conselho voting (only read-only `get_proposal` via local DuckDB).
- **R4** no originating structural changes (proposal is the source).
- **R5** no subagent prompt edits (only `orchestrator.md` which is primary, not subagent).

## Notes for orchestrator

- **Push (Regime A):** the orchestrator is responsible for `git add` + `git commit` + `git push` after delivery-reviewer G4 sign-off (per LACOUNCIL 391a8179).
- **Migration:** the `user_questions` table was applied at runtime in the LAOS-side mirror DB
  (`F:/Projetos/Laos/lacouncil/memoria/lacouncil.duckdb`) so the M2 preflight DB sub-check
  can verify. The runtime lacouncil MCP (via `LACOUNCIL_DB_PATH`) will re-apply the same
  idempotent migration on its next `connect()`.
- **Condition #11 (no breaking change):** `recommendation: ask_user` was NOT added to the verdict
  schema (would require supermaioria). The ladder is enforced at the orchestrator + preflight
  layer; the DEFER verdict's `block_reason` remains the surface for "still blocked".
- **G4 sign-off depends on delivery-reviewer.** Until then, the changes are local-only and
  should not be pushed.
