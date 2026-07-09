---
proposal_id: 0a539dd6-69fe-481e-b4ec-7f63b7e6e545
lens: data-architect
vote: sim
vote_id: b2e941f6-37c1-4d22-ac05-495565b7e260
voted_at: 2026-07-02T15:10:00-03:00
proposal_titulo: lacouncil config hygiene (DB path canonical + MCP command fix)
proposal_categoria: workflow
proposal_estrategia: maioria
---

# Conselho review — lens data-architect

## 1. Path resolution (parents[2] vs parents[3])

**Empirical validation executed** against the live filesystem:

```
File resolved: F:\Projetos\Laos\lacouncil\src\lacouncil\core\duckdb_store.py
parents[0] = F:\Projetos\Laos\lacouncil\src\lacouncil\core
parents[1] = F:\Projetos\Laos\lacouncil\src\lacouncil
parents[2] = F:\Projetos\Laos\lacouncil\src          <-- WRONG (legacy)
parents[3] = F:\Projetos\Laos\lacouncil              <-- CORRECT (repo root)
parents[4] = F:\Projetos\Laos
```

**Conclusion:** `parents[3]` is the canonical repo-root path. The directory
`F:\Projetos\Laos\lacouncil\memoria\` **already exists** and is ready to
host the canonical DuckDB. The current `parents[2]` value resolves to
`src/`, which is exactly where the legacy/orphan DB lives — confirming
the bug.

**Alignment check with `opencode.jsonc`:** The `LACOUNCIL_DB_PATH` env var
is already declared as `'{workspaceFolder}\\lacouncil\\memoria\\lacouncil.duckdb'`.
The `parents[3]` fix makes the **default** path match the **env var** path.
This eliminates the silent divergence between explicit override and default
behavior.

## 2. Unit test coverage (3 scenarios)

The proposed test cases:

1. `test_default_path_resolves_to_repo_root_memoria` — verifies default path
   is `<repo>/memoria/lacouncil.duckdb` (the **regression guard** for this
   specific bug).
2. `test_env_var_override_takes_precedence` — verifies `LACOUNCIL_DB_PATH`
   env var wins over the default.
3. `test_explicit_db_path_arg_wins` — verifies explicit `db_path=` argument
   wins over env var.

**Coverage assessment:** The 3 tests cover the **precedence chain** (the
actual logical content of `resolve_db_path`). This is **adequate for the
minimum viable hygiene fix**. The proposed tests are regression guards,
not exhaustive coverage — and that's the right scope for a config-hygiene
patch.

**Suggested follow-up tests (do NOT block this proposal):**

- `test_default_creates_memoria_dir_if_missing` — first-install safety.
  Without this, a fresh clone of lacouncil on a clean machine will raise
  `FileNotFoundError` until someone manually `mkdir memoria/`.
- `test_empty_env_var_falls_back_to_default` — Windows env var edge case
  (empty string vs unset).
- `test_concurrent_open_uses_duckdb_lock` — DuckDB has its own lock;
  test that a second process opens read-only or waits, not corrupts.
- `test_path_with_spaces_resolves_correctly` — Windows-typical paths like
  `C:\Program Files\...` (the current path has no spaces, but coverage
  matters for the contract).

These are scope creep for this fix and should land in a separate "harden
DB path resolution" proposal if anyone hits the failure modes.

## 3. Legacy DB at `src/memoria/lacouncil.duckdb`

**Empirical state:**

```
lacouncil/memoria exists:                       True   (canonical, empty)
lacouncil/src/memoria exists (legacy orphan):   True   (contains real data)
```

The legacy DB contains:
- Proposal `d3095fa3` (confidence_escalation_ladder)
- 4 votes from d3095fa3
- Trust scores for the Conselho members

**After the fix:** the active system (MCP + Python API + CLI) will read/write
the **empty canonical DB**. The legacy file becomes read-only history.

**Decision: orphan is acceptable for this fix scope.**

The proposal explicitly preserves the legacy file and does not delete it.
This is a **defensible trade-off**:

- **Pro (no migration):** minimal scope, no data-corruption risk during
  copy, the fix ships fast and unblocks MCP availability.
- **Con (no migration):** operational history is lost to the active system.
  Trust scores reset to 0. Proposals already in the system vanish.

**Recommendation:** Open a follow-up LACOUNCIL proposal
("`d3095fa3` data continuity migration") to do a one-time
`duckdb -> duckdb` copy of the relevant tables (propostas, votos,
trust_scores) AFTER this fix lands. This is a **separate concern** —
operational continuity is a data-fidelity question, not a config-hygiene
question. Mixing them in one proposal would inflate scope and risk.

## 4. Other data-lens findings

### Narrative gap (advisory, not blocking)

The proposal description says the fix "alinha com a convencao dos
outros MCPs". Empirical check:

```
latade/memoria exists:  False
```

`latade/memoria/` does not exist yet (latade likely has its DB somewhere
else, or hasn't been audited). The fix is **still correct** because:

1. It makes lacouncil internally consistent (default ↔ env var).
2. It matches the **declared** convention in `opencode.jsonc` env var.
3. It establishes the right pattern for future MCPs (latade, lan8n, etc.)
   to follow.

**Suggested follow-up:** add `memoria/` to the convention document
(`knowledge/data-conventions.md` or similar) so future MCPs don't
re-introduce the same bug.

### `uv run` → direct venv python change

This is primarily an **infra/MCP config** concern, not a data concern.
The data impact is **positive**: `mcp__lacouncil__*` tools become
available to the orchestrator without depending on `uv` in the
subprocess PATH, which means data-architect (and other Conselho
members) can use `lacouncil.get_proposal` and `lacouncil.register_vote`
via MCP instead of CLI. This was the proximate cause of the P2 advisory
on d3095fa3's G4 BASIC sign-off.

**Data lens approval:** the `uv run` → direct python change unblocks
governance flow for data subagents. Strongly supported.

## 5. Final vote and rationale

**Vote: SIM.**

The fix is **correct, minimal, and addresses real issues**:

- `parents[3]` is empirically the canonical path and the `memoria/`
  directory already exists.
- 3 tests cover the happy-path precedence chain — adequate for scope.
- Legacy DB orphan is a conscious trade-off, defensible for a
  minimum-viable fix.
- The MCP command change unblocks `mcp__lacouncil__*` for all
  Conselho members, including data-architect.

**No blocking concerns.** Follow-up proposals recommended for
(migration of d3095fa3 data, additional test coverage, convention
documentation) but none of them gate this fix.
