# lacareerops-refactor — meta-project

> **Status:** BASIC sign-off pending (Regime A push). 4 hub commits
> deployed; LAOS structural files staged; opencode.jsonc G5 remediated.

## O que é

This meta-project implements **LACOUNCIL proposal `ba9a9bd7-3686-4d6e-9f1b-3efc46f37a8c`**
(2026-06-19, supermaioria 4/4 SIM): replaces the legacy fork
`laurentaf/career-ops` with a **hub + git submodule + auto-sync tool**
architecture. Architectural decision ratified at
`projects/_meta/adr/ADR-013-lacareerops-submodule.md`.

The capability this serves (`lacareerops`) keeps career-ops
auto-updateable: `career_ops_sync` advances the submodule pin with
a 4-check smoke battery + automatic rollback if the new SHA breaks
the wrapper.

## Como rodar (do zero)

```bash
# 1. Clone the hub repo (PRIVATE)
gh repo clone laurentaf/lacareerops-hub E:/projects/lacareerops-hub

# 2. Initialize submodule (pinned SHA recorded in SUBMODULE_SHA.txt)
cd E:/projects/lacareerops-hub
git submodule update --init --recursive

# 3. Verify smoke test
uv run python mcp/server.py --tool health
npx -y @santifer/career-ops@$(cat SUBMODULE_SHA.txt) --help

# 4. (Optional) adopt into LAOS by editing
#    .opencode/opencode.jsonc to point command at hub path.
#    See G5 binding condition in
#    projects/_meta/capability-architect/binding-conditions.md.

# 5. (Optional) confirm privacy invariants
#    cat .gitignore  # excludes config/*.yml, config/*.md, config/SNAPSHOT_*/
```

## Onde está o quê

| Path | O que |
|------|-------|
| `github.com/laurentaf/lacareerops-hub` | The capability hub (PRIVATE, 4 commits deployed) |
| `hub/mcp/server.py` | The MCP server with 8 tools (incl. `career_ops_sync`) |
| `hub/.gitmodules` + `SUBMODULE_SHA.txt` | Submodule pinned at upstream `santifer/career-ops` SHA `9d1404f3...` |
| `hub/docs/adr/ADR-013-...md` | ADR mirror (canonical = LAOS-side) |
| `hub/config/` | User private configs (gitignored: `*.yml`, `*.md`, `SNAPSHOT_*/`) |
| `projects/_meta/adr/ADR-013-lacareerops-submodule.md` | Canonical ADR (LAOS-side) |
| `registry/capabilities.yaml` | Capability registry entry (hub URL) |
| `knowledge/handoff-lacareerops.md` | Engineering handoff notes (Submodule architecture section) |
| `projects/_meta/capability-evolution/lacareerops.md` | Lifecycle tracker (loop 1 entry added) |
| `artifacts/wdl/lacareerops-refactor-001/` | WDL preflight artifacts (analysis.md, plan.json, verdict.yaml) |
| `artifacts/review/checklist.md` | G4 BASIC sign-off (delivery-reviewer output) |

## Privacidade (SC-1/SC-2/SC-3)

- `config/profile.yml` e `config/cv.md` ficam em `hub/config/` e são
  **gitignored** (`config/*.yml`, `config/*.md`, !`*example*`,
  `config/SNAPSHOT_*/`).
- Cada usuário **configura localmente** após clone; só `*.example.*` ships.
- `lacouncil.record_project` nunca toca config files.

## Lifecycle

- **Created:** 2026-06-19 (proposal `ba9a9bd7`, supermaioria 4/4).
- **BASIC sign-off:** pending (delivery-reviewer G4 after remediated
  findings).
- **STABLE target:** 2026-07-13. Conditions: 9 stages complete +
  capability-evolution evidence per `projects/_meta/capability-evolution/lacareerops.md`.

## Status legend

- ✅: completed
- ⏳: pending (orchestrator or downstream agent)
- 🚫: blocked
- ❌: rejected/finding
- 🔍: investigation pending
