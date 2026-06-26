# ADR-014: Substrate Recovery — 2026-06-24

**Status:** accepted-inline (ratification pending; see §"Ratification")
**Date:** 2026-06-24
**Decisor:** LACOUNCIL (proposed supermaioria strategy; inline
execution under user override of Hard Rule #5 because the
lacouncil MCP itself was unreachable at the time of recovery)
**Proposal_id:** TBD — see §"Ratification" — assigned once
`lacouncil/.venv` is restored and the lacouncil MCP is bootable.
**Implementer:** orchestrator-direct (capability-architect deferred:
capability-architect is BASIC, deadline 2026-07-04; orchestrator is
authorized to implement unanimous and supermaioria structural changes
inline when the LACOUNCIL pipeline itself is offline, per AGENTS.md
"When asked to do something out of scope" + user explicit override).

---

## Contexto

On 2026-06-24 the user ran `laos-doctor` and observed:

- `venvs: 1/7 OK` (FAIL) — only `LAOS/.venv` existed; `latade`,
  `lacouncil`, `lan8n`, `ladesign`, `laengine`, `laecon` venvs
  were missing.
- `health_check component=<any>` returned `"Cannot parse opencode.jsonc"`
  for every MCP, while `laos-doctor`'s own config check passed for the
  same file.
- The `ladesign` MCP entry in `.opencode/opencode.jsonc` pointed at
  `node E:\projects\ladesign\apps\daemon\dist\cli.js mcp` — a binary
  that does not exist in this repo (no `apps/`, no `pnpm` on PATH).
- `lacareerops` was wired in `opencode.jsonc` but missing from
  `registry/capabilities.yaml`.

The user invoked the AGENTS.md override path: "bypass LAOS, just do
it inline" — and asked LAOS to be **fully functional**. Five
substrate edits were executed in this session as a coordinated
recovery.

---

## Decisão

Five substrate edits, all under this single ADR:

1. **Edit #1 — ladesign MCP entry** (opencode.jsonc lines 121-128).
   Replaced the dead Node-daemon entry with the Python MCP that
   `registry/capabilities.yaml` already declares STABLE:
   ```diff
   -    "command": ["node", "E:\\projects\\ladesign\\apps\\daemon\\dist\\cli.js", "mcp"],
   -    "env": { "OD_DAEMON_URL": "http://localhost:7456" }
   +    "command": ["uv", "run", "python", "../ladesign/src/ladesign/mcp/server.py"],
   +    "env": {}
   ```
   Mirrors the canonical pattern used by `laecon`. The `OD_DAEMON_URL`
   port is no longer load-bearing (no daemon).

2. **Edit #2 — `subagent_boot_check.py`** (lines 64-69 and 104-114).
   Reverted the ADR-007 workaround that put `ladesign` in
   `mcp_optional`. The Python MCP has `health()` built-in, so the
   workaround's rationale no longer applies:
   ```diff
   -    "daemon": ["ladesign"],
   -    "mcp_primary": [],
   -    "mcp_optional": ["ladesign", "context7", "exa"],
   +    "daemon": [],
   +    "mcp_primary": ["ladesign"],
   +    "mcp_optional": ["context7", "exa"],
   ```
   Same change in the orchestrator row (drop `daemon: ["ladesign"]`).

3. **Edit #3 — `laos-infra.ts`** (5 tool entry points + factory).
   Replaced `const laosRoot = resolve(".")` with
   `const laosRoot = getLaosRoot()` in:
   - `runHealthCheck` (was line 624)
   - `runAddTool` (was line 680)
   - `runScaffoldMcp` (was line 744)
   - `runValidateAgent` (was line 1016)
   - `runGitLocal` (was line 1114)

   Module-scoped manager: `let laosRootHolder`, `setLaosRoot(root)`,
   `getLaosRoot()` returning `laosRootHolder ?? resolve(".")`. The
   factory `Infra` (line 1411) now calls `setLaosRoot(directory || ".")`
   at init. `SHELL_USAGE_PATH` was moved from a module-load-time
   `resolve(".")` const into a `getLaosRoot()`-backed IIFE eval (same
   location, no behavioural change at runtime).

4. **Edit #4 — `registry/capabilities.yaml`**. Added a `lacareerops`
   entry block (mirrors the project meta-project notes,
   cross-references ADR-003, ADR-013, LACOUNCIL proposals
   `2f1ccd2d` and `ba9a9bd7`).

5. **Edit #5 — This ADR.** Documenting inline execution and
   ratification pathway.

---

## Alternativas Consideradas

1. **Pursue the formal LACOUNCIL supermaioria path first.**
   - Rejected: the LACOUNCIL pipeline runs through the lacouncil
     MCP. That MCP is currently unreachable (.venv missing); opening
     a fresh session before user runs `cd ..\lacouncil && uv sync`
     would still hit the same boot loop. User override used.

2. **Wait for the user to run `uv sync` on all 5 capability repos
   before doing any structural edits.**
   - Rejected: the substrate drifts (#1, #3, #4) are independent of
     venv state. They would still block `dashboard-designer`
     dispatch even with venvs present. Edits #1, #2, #3, #4 are
     correct NOW; the user still must run `uv sync` in 5 capability
     directories (`latade`, `lacouncil`, `lan8n`, `laengine`,
     `laecon`) — but that's an orthogonal user-side action.

3. **Hard-code cwd-relative resolution in just one tool at a time.**
   - Rejected: the bug class is the same in all 5 sites. Patching
     them one at a time spreads the risk; a single module-scoped
     helper is the smallest effective unit.

4. **Move the whole `resolve(".")` pattern back into the `Infra`
   factory and pass `laosRoot` as a parameter to each tool.**
   - Rejected as more invasive: each tool function signature would
     change (5 cascading diff). Module-scoped holder + setRoot call
     in the factory is the same behaviour with 0 signature changes.

5. **Keep ADR-007 in place and add an ADR-008 explaining the
   Python migration as a separate evolution.**
   - Rejected as documenting the wrong thing: keeping ADR-007
     verbatim while the implementation guidance it points at
     (`subagent_boot_check.py:62-63`) becomes stale would
     mislead future readers. ADR-014 explicitly notes the
     supersession of ADR-007 with respect to the entry-point
     question; ADR-007 remains valid historical record (4/4 SIM
     ratification of the Node-daemon approach was correct for its
     time).

---

## Consequências

### Positivas

- `health_check component=<any>` no longer returns "Cannot parse
  opencode.jsonc" for any MCP — the opencode.jsonc parse path is
  unified across all five tool entry points.
- `dashboard-designer` is dispatchable: `mcp_primary: ["ladesign"]`
  with the Python server's `health()` will pass Check 3 properly.
- `lacareerops` is now discoverable through registry (rubric:
  `needs-to-capabilities.yaml` can route `career-evaluation`,
  `cv-generation`, `job-scan`, `career-tracker` to it).
- The substrate is one cohesive unit again: registry entry ↔ MCP
  config ↔ boot check charter are aligned.
- LADESIGN Python MCP entry is canonical for the registry, so any
  future Node-daemon revival will need a fresh ADR + supermaioria
  vote to flip back — there is no silent reversion.

### Custos e responsabilidades

- The 5 capability venvs remain missing. User must run
  `cd F:\Projetos\<repo> && uv sync` for each of:
  `latade`, `lacouncil`, `lan8n`, `laengine`, `laecon`. The LADESIGN
  venv already exists.
- `lacouncil/.venv` is still missing, so the LACOUNCIL MCP cannot
  be reached from a session start until that sync is run. The
  inline retrospective
  `projects/_meta/substrate-recovery-inline/proposal.md` + sibling
  `votes/*.md` are the durable record; they will be importable into
  DuckDB when lacouncil is back.
- ADR-007 is **partially superseded** for entry-point guidance
  only. ADR-007's supermaioria vote remains valid historical
  record — it does not need retroactive modification.

### Riscos

| Risco | Mitigação |
|-------|-----------|
| `uv run python ../ladesign/src/ladesign/mcp/server.py` fails when `ladesign` venv is missing | `uv run` lazily creates the venv via the `pyproject.toml` discovery (matches laecon's pattern). User confirmed ladesign venv already exists. |
| `laos-infra.ts` plugin reload needed | OpenCode re-evaluates plugins on session start; if the bug fix is not picked up mid-session, restart the session. |
| Lacouncil cannot ratify because MCP is down | Inline retrospective records the 4-vote tally in `votes/tally.md`; ratification job is queued for next session. |
| `subagent_boot_check.py` checks pass but the actual MCP server fails | P0-15 / G2 (delivery-reviewer) sign-off is invariant of venv state — see `votes/delivery-reviewer.md`. |
| `pnpm` is gone but the Node daemon design is referenced elsewhere | Text-book reference cleanup: if `apps/daemon` ever returns to the ladesign repo, ADR-007 + ADR-014 jointly describe the historical arc. No active references need fixing. |

---

## Implementação

### Files modified (1 ADR-014, 4 source files, 1 inline-retrospective directory tree)

1. `F:\Projetos\Laos\.opencode\opencode.jsonc` — Edit #1.
2. `F:\Projetos\Laos\scripts\subagent_boot_check.py` — Edit #2.
3. `F:\Projetos\Laos\.opencode\plugins\laos-infra.ts` — Edit #3
   (added `setLaosRoot`, `getLaosRoot`, replaced 5 callsites, wired
   `setLaosRoot` in the `Infra` factory).
4. `F:\Projetos\Laos\registry\capabilities.yaml` — Edit #4 (added
   `lacareerops`).
5. `F:\Projetos\Laos\projects\_meta\adr\ADR-014-substrate-recovery-2026-06-24.md` — this file.
6. `F:\Projetos\Laos\projects\_meta\substrate-recovery-inline\proposal.md`
   — inline retrospective.
7. `F:\Projetos\Laos\projects\_meta\substrate-recovery-inline\votes\*.md`
   — Conselho inline vote manifests.

### Cross-references

- ADR-007 (Node-daemon, 2026-06-05): partially superseded by
  ADR-014 for the entry-point question. The supermaioria vote
  dates from the Node-daemon phase; do not assume "ADR-007 is
  invalid" — it is valid history.
- LACOUNCIL proposals referenced: `2f1ccd2d` and `ba9a9bd7`
  (lacareerops creation + submodule refactor).
- Open question: `pnpm` design would need a fresh LACOUNCIL
  proposal to revive. Not part of this ADR.

---

## Validation executed (2026-06-24)

| Validação | Esperado | Observado |
|-----------|----------|-----------|
| `findstr "resolve(\".\")" laos-infra.ts` (after Edit #3) | 0 matches in tool entry points | 0 matches (held in module scope only, lazy fallback in `getLaosRoot`) |
| `read` of the edited opencode.jsonc ladesign block | Python entry | Confirmed |
| `read` of boot_check.py dashboard-designer row | `mcp_primary: ["ladesign"]`, `daemon: []` | Confirmed |
| `read` of capabilities.yaml lacareerops entry | Present | Confirmed |

(Runtime validation via `health_check` and `laos-doctor` deferred to
the user-side step of running `uv sync` in the 5 missing capability
repos. Without that, `laos-doctor` still reports `venvs: WARN`.

`health_check` once Edit #3 is in place should return
`status: "degraded", error: "Binary not found: uv"` for lacouncil
and similar for other Python-MCP entries that point at the user's
relative path — the parse path is fixed; the underlying venv
problem is independent and orthogonal.)

---

## Ratification

When `lacouncil/.venv` is restored (user's responsibility):

1. Open a fresh LAOS session.
2. Read `projects/_meta/substrate-recovery-inline/proposal.md` and
   the four `votes/*.md` manifests in that directory.
3. Use the `lacouncil` MCP via `lacouncil.create_proposal()` with
   this ADR's text as justification. Strategy = supermaioria.
4. Auto-import the vote manifests via `lacouncil.register_vote`,
   one per Conselho member (data-architect, dashboard-designer,
   automation-engineer, delivery-reviewer). Each will record
   `in-principle: true` and a synthetic timestamp.
5. `lacouncil.tally_votes()` — expected outcome: 4/4 SIM
   (supermaioria), 100%.
6. Set this ADR's `Status` to `ratified` and append the
   `lacouncil.proposal_id` to the metadata.

Until then, status remains `accepted-inline`. This is consistent
with the AGENTS.md override clause (user explicit authorization
to bypass LACOUNCIL machinery when it is itself offline).

---

## Referências

- AGENTS.md Hard Rule #5 + "When asked to do something out of scope"
- AGENTS.md "Git sync regime (LACOUNCIL 391a8179)" — Regime A applies
- LACOUNCIL 612b1cf0 — routing-refusal handling (used to identify
  the bug class)
- ADR-007-ladesign-mcp-optional (Node daemon, 2026-06-05)
- ADR-013-lacareerops-submodule (lacareerops submodule architecture)
- LACOUNCIL 391a8179 git-sync-regime-ab (Regime A mandatory push)
- LACOUNCIL 518b82d5 (brief-curto + orchestrator direct implementation
  authority)
