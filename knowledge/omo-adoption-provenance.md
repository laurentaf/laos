# OmO → LAOS Adoption Provenance

Tracks which project, pain point, or external source originated each
feature adopted from oh-my-openagent (OmO) or inspired by LAOS project
experience.

**Created:** 2026-06-09
**Source:** Comparative analysis of OmO vs LAOS + historical project pain points

---

## Feature Provenance Matrix

| # | Feature | Origin Type | Source Project / External | Pain Point | Evidence |
|---|---------|-------------|--------------------------|------------|----------|
| 1 | **Agentic Framework Modes** (Sequential / Parallel / Consensus) | User requirement + OmO Team Mode | OmO `src/features/team-mode/` | Sequential dispatch is slow when multiple independent deliverables can run simultaneously. Consensus mode needed for model comparison (e.g., run 3-5 econometric models, evaluator picks best). | User: "was a requisite for LAOS, I don't know why it's not implemented". OmO: 12 `team_*` tools, git worktree isolation, mailbox messaging, tmux viz. LAOS projects: `previsao-concursos` (needs data + ML + design + automation — prime parallel candidate), `abandono-academico-casa-grande` (needs data + ML + dashboard — parallel would cut time). |
| 2 | **Hashline Edit** (content-hash anchored edits) | OmO port | OmO `packages/hashline-core/` | Line-number edits fail ~93% of the time in long files. Agent reads file, file changes (drift), edit corrupts wrong line. | OmO: 6.7% → 68.3% success rate. LAOS projects: `previsao-concursos` (long spec/model files), `abandono-academico-casa-grande` (long main.py), `giovanna-rupture-monitor` (long pipeline files). Every LAOS project hits this. |
| 3 | **Write-Existing-File Guard** | OmO `write-existing-file-guard` + LAOS Hard Rule #1 | OmO `src/hooks/write-existing-file-guard/` + Hard Rule #1 ("Never put implementation code in LAOS") | Hard Rule #1 is checked at review time by delivery-reviewer, not at invocation time. Agent can write implementation files and only discover the violation hours later. | OmO: `tool.execute.before` blocks Write to unread files. LAOS: padroes-entrega.md P0 checks but no mechanical enforcement. Project `giovanna-rupture-monitor` had synthetic data artifacts without frontmatter (Hard Rule #11 gap). |
| 4 | **MCP Namespace Wall** | LAOS WDL contract + OmO pattern | LACOUNCIL proposal `a4fe9faa` (WDL v1) | Workflow-decomposer must NOT call latade/ladesign/lan8n MCPs. Currently enforced by prompt only — LLM can ignore the wall. | WDL-R1 in `workflows/wdl-contract.yaml` + `workflow-decomposer.md` §"MCP namespaces you must NOT call". No mechanical enforcement exists. |
| 5 | **WDL Gate Enforcement** | LAOS Hard Rule #8 + OmO pattern | LACOUNCIL proposal `a4fe9faa` + `7fd94c1a` | Specialist dispatch without READY verdict bypasses the entire WDL preflight gate. Currently enforced by orchestrator prompt compliance. | Hard Rule #8.1: "Specialist dispatch is conditional on verdict.yaml with state: READY". Hard Rule #8.2: trust-score penalty on bypass. Penalty is recorded but gate isn't mechanically checked. |
| 6 | **Todo Continuation Enforcer** | OmO `todo-continuation-enforcer` | OmO `src/hooks/todo-continuation-enforcer/` | Subagents go idle after 1-2 deliverables instead of completing the full WDL plan. Agent stops mid-task and waits for user prompt. | OmO: 2s countdown → inject continuation. LAOS projects: `abandono-academico-casa-grande` stage 3 (DQ checks + pipeline restructure) — agent stopped after first DQ check, didn't complete all 6. `emanuella-stock-ingestion` — agent completed ingestion but skipped transform stage. |
| 7 | **Session Recovery** (full system, per-project state) | OmO `session-recovery` + `boulder-state` + user requirement | OmO `src/hooks/session-recovery/` + `packages/boulder-state/` | Long orchestrator sessions (WDL + dispatch + review) crash on lost tool results, thinking block errors, context compaction. No recovery — entire pipeline restarts. | User: "full system, every project must have his own states". OmO: 3-layer system (structural recovery + boulder state + compaction guard). LAOS: no session recovery exists. Project `previsao-concursos` (4 capabilities, 9 needs) would be the most affected — long session, many specialists, high crash probability. |
| 8 | **Context Compaction Preservation** | OmO `compaction-todo-preserver` + `experimental.session.compacting` | OmO `src/hooks/compaction-todo-preserver/` | After context compaction, LAOS loses: current project name, active WDL verdicts, trust scores, dispatch state. Agent "forgets" where it was. | OpenCode native: `experimental.session.compacting` hook can inject persistent context. LAOS currently doesn't use this hook at all. |
| 9 | **Runtime Fallback** | OmO `runtime-fallback` | OmO `src/hooks/runtime-fallback/` | Provider errors (429 rate limit, 500 server error) kill the session. No reactive fallback — agent just stops. | OmO: configurable per-session with `max_fallback_attempts`, `cooldown_seconds`, `timeout_seconds`. LAOS: no fallback mechanism. Long sessions with multiple specialist dispatches are especially vulnerable. |
| 10 | **Comment Checker** | OmO `packages/comment-checker-core/` | OmO `packages/comment-checker-core/` | AI slop in comments — low-value, auto-generated, placeholder comments that language models insert. | OmO: detects net-new comments on Write/Edit, appends warning. LAOS-specific extension: also flag synthetic data frontmatter violations (Hard Rule #11). |
| 11 | **IntentGate for LAOS** | OmO `keyword-detector` | OmO `src/hooks/keyword-detector/` | Subagent dispatches lack needs-specific context. Data-architect gets a generic brief instead of the full data-architect protocol. | OmO: keyword detection → mode-specific prompt injection. LAOS: already knows needs at session start (from project.yaml) — can auto-inject without keyword detection. Project `previsao-concursos` has 9 needs — intent gate would ensure each specialist gets the right protocol. |
| 12 | **Doctor Command** | OmO `src/cli/doctor/` + LAOS `subagent_boot_check.py` | OmO `src/cli/doctor/` | No holistic system diagnostic. `subagent_boot_check.py` only validates 5 dimensions per-subagent. No MCP health check, no model availability check, no plugin status check. | OmO: 7 checks (system, config, TUI plugin, tools, models, team mode, codex). LAOS: `subagent_boot_check.py` (5 dimensions: venv, daemon, MCP, paths, env). Gap: no holistic diagnostic. |
| 13 | **Plan Format Validator** | OmO `plan-format-validator` | OmO `src/hooks/plan-format-validator/` | WDL `verdict.yaml` and `plan.json` can be malformed (missing `state`, `verified_by`, `plan_id`). Malformed verdicts pass the WDL gate check because the check is string-based, not schema-validated. | WDL contract `workflows/wdl-contract.yaml` defines verdict schema but no mechanical validator exists. |
| 14 | **Empirical Consensus** (evaluator picks best) | User requirement + LAOS econometrics experience | User insight + `abandono-academico-casa-grande` (ML model selection) | When multiple models compete for the same problem, there's no structured way to compare and pick the best. Currently, the data-architect just picks one. | User: "do 3 to 5 models and a chief evaluate which model has a better model fit to the data". Project `abandono-academico-casa-grande` (predictive modeling) — would benefit from running 3-5 models and evaluating. Project `previsao-concursos` (classical-ml stage) — same. LAECON capability has the models (scikit-learn, xgboost, shap) but no evaluation framework. |
| 15 | **Skill-Embedded MCPs** | OmO skill-embedded MCP pattern | OmO skill system | LAOS skills are static SKILL.md files — no on-demand MCP servers per skill. Limits what skills can do (no tool execution, no API calls). | User: "as a tech debt, low priority". OmO: skills can declare MCP dependencies, spun up on demand. LADESIGN daemon has the infrastructure for this. |

---

## Historical Project Pain Points

### `emanuella-stock-ingestion` (Luan Emanuella)
- **Pain:** Agent stopped after ingestion stage, skipped transform and dbt prep stages
- **Feature needed:** Todo Continuation Enforcer (#6)
- **Pain:** API token handling — no mechanical check for `.env` protection
- **Feature needed:** Write Guard (synthetic data + secret scanning) (#3)

### `giovanna-rupture-monitor` (Giovanna Rupture)
- **Pain:** Synthetic data artifacts created without frontmatter marking
- **Feature needed:** Write Guard (Hard Rule #11 enforcement) (#3)
- **Pain:** Docker pipeline is long and fragile — session crashes mid-build
- **Feature needed:** Session Recovery (#7)

### `abandono-academico-casa-grande` (Casa Grande Dropout)
- **Pain:** Long main.py — line-number edits kept targeting wrong lines
- **Feature needed:** Hashline Edit (#2)
- **Pain:** Agent stopped after first DQ check, didn't complete all 6
- **Feature needed:** Todo Continuation Enforcer (#6)
- **Pain:** Model selection was arbitrary — no comparison framework
- **Feature needed:** Empirical Consensus (#14)

### `previsao-concursos` (Barbosa Exam Prediction)
- **Pain:** 9 needs across 4 capabilities — sequential dispatch is very slow
- **Feature needed:** Parallel mode (#1)
- **Pain:** ML model comparison (FCC vs FGV, different feature sets) — no evaluation framework
- **Feature needed:** Empirical Consensus (#14)
- **Pain:** Very long session (data + ML + design + automation) — high crash probability
- **Feature needed:** Session Recovery (#7) + Context Compaction Preservation (#8)
- **Pain:** Each specialist gets a generic brief — needs intent-specific prompt injection
- **Feature needed:** IntentGate (#11)

### `brasfoot-poc` (Brasfoot Game)
- **Pain:** Game simulation + UI are independent — could run in parallel
- **Feature needed:** Parallel mode (#1)

### `laos-brand` (LAOS Brand Identity)
- **Pain:** Design deliverables are subjective — multiple variants would help
- **Feature needed:** Consensus mode — Empirical (chief-designer evaluates) (#14)

---

## External Sources

| Source | What it contributed | URL |
|--------|-------------------|-----|
| oh-my-openagent (OmO) | 15 features analyzed, 13 adopted (2 skipped: Agent Category Routing, /init-deep) | https://github.com/code-yeongyu/oh-my-openagent |
| OpenCode native plugin system | Hook infrastructure (`tool.execute.before/after`, `session.idle`, `experimental.session.compacting`) — LAOS was using 0 of these | https://opencode.ai/docs/plugins/ |
| LACOUNCIL proposals | WDL gate (a4fe9faa, 7fd94c1a), SDD scaffold (f9b636fc), Hard Rules #1-#11 | `lacouncil/memoria/lacouncil.duckdb` |
| User insights | Agentic modes as requisite, Empirical Consensus for model evaluation, full session recovery, per-project state | Session 2026-06-09 |
