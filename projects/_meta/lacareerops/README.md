# lacareerops — meta-project

> **Status:** BASIC (v1.1.0 hub + submodule); awaiting G4 sign-off after
> Loop 2 cleanup (2026-06-20). GH-side README of legacy repos archived.

## O que é

This meta-project implements **LACOUNCIL proposal `2f1ccd2d-7d0a-44fc-8382-24c3e16ebd0c`**
(2026-06-13, supermaioria 3/4 SIM + 1 ABSTENCAO) and the refactor
extension **LACOUNCIL proposal `ba9a9bd7-3686-4d6e-9f1b-3efc46f37a8c`**
(2026-06-19, supermaioria 4/4 SIM): replaces the legacy fork
`laurentaf/career-ops` with a **hub + git submodule + auto-sync tool**
architecture for the capability `lacareerops` — LAOS native integration
of `santifer/career-ops` (the upstream Node.js job-search CLI).

The canonical capability repo is now `laurentaf/lacareerops-hub`
(PRIVATE) with `career_ops_sync` advancing the submodule pin through
a 4-check smoke battery + automatic rollback. Architectural decision
ratified at `projects/_meta/adr/ADR-013-lacareerops-submodule.md`.

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

# 4. (Optional) confirm privacy invariants
#    cat .gitignore  # excludes config/*.yml, config/*.md (except *.example.*)
```

## Onde está o quê

| Path | O que |
|------|-------|
| `github.com/laurentaf/lacareerops-hub` | The capability hub (PRIVATE, v1.1.0) |
| `hub/mcp/server.py` | The MCP server with 8 tools (incl. `career_ops_sync`) |
| `hub/.gitmodules` + `SUBMODULE_SHA.txt` | Submodule pinned at upstream `santifer/career-ops` SHA |
| `hub/config/` | User private configs (gitignored: `*.yml`, `*.md`, except `*.example.*`) |
| `projects/_meta/lacareerops/project.yaml` | Meta-project contract |
| `projects/_meta/lacareerops/spec/constitution.md` | Capability Constitution |
| `projects/_meta/lacareerops/spec/todo.md` | Capability todo (BASIC→STABLE roadmap) |
| `projects/_meta/lacareerops/contract.md` | Parties + obligations |
| `projects/_meta/adr/ADR-003-lacareerops-creation.md` | ADR creation |
| `projects/_meta/adr/ADR-013-lacareerops-submodule.md` | ADR submodule refactor |
| `projects/_meta/lacareerops-refactor/` | Loop 1 refactor meta-project |
| `projects/_meta/capability-evolution/lacareerops.md` | Lifecycle tracker |
| `registry/capabilities.yaml` | Capability registry (lacareerops entry) |
| `registry/needs-to-capabilities.yaml` | Routing (career-* needs → lacareerops) |
| `knowledge/handoff-lacareerops.md` | Engineering handoff (Submodule architecture section) |
| `.opencode/opencode.jsonc` | MCP launch config (lacareerops entry → hub) |
| `artifacts/review/checklist.md` | Reviewer output (Loop 2 cleanup sign-off) |

## Privacidade (SC-1/SC-2/SC-3)

- `config/profile.yml` e `config/cv.md` ficam em `hub/config/` e são
  **gitignored** (`config/*.yml`, `config/*.md`, exceto `*.example.*`).
- Cada usuário **configura localmente** após clone; só `*.example.*` ships.
- `lacouncil.record_project` nunca toca config files.
- Hub repo é **PRIVATE** (`github.com/laurentaf/lacareerops-hub`).
- Upstream `santifer/career-ops` é público; não exponha dados do
  usuário nas chamadas CLI.

## Lifecycle

- **Created:** 2026-06-13 (proposal `2f1ccd2d`, supermaioria).
- **Loop 1 refactor:** 2026-06-19 (proposal `ba9a9bd7`, supermaioria 4/4 SIM).
- **Loop 2 cleanup:** 2026-06-20 (this delivery — drift LAOS↔hub reconciled,
  legacy GitHub README notice pushed on `career-ops` + `lacareerops`).
- **BASIC sign-off:** pending delivery-reviewer G4 sign-off.
- **STABLE target:** 2026-07-13. Conditions: ≥1 real project used lacareerops
  + delivery-reviewer STABLE sign-off.
- **M2 target:** 2026-08-13 (auto-submission + interview tracker).

## Status legend

- ✅: completed
- ⏳: pending (orchestrator or downstream agent)
- 🚫: blocked
- ❌: rejected/finding
- 🔍: investigation pending
