# Contract — lacareerops capability creation

## Parties

- **LAOS** (orchestration layer) — implements structural changes approved by LACOUNCIL
- **capability-architect** — implements LACOUNCIL-approved proposal `2f1ccd2d-7d0a-44fc-8382-24c3e16ebd0c`
- **LACOUNCIL** — approved the proposal on 2026-06-13 (3 SIM + 1 ABSTENCAO)

## Capability delivered

**Name:** lacareerops
**Kind:** domain (automation/career)
**Repo:** github.com/laurentaf/lacareerops (PRIVATE)
**Status:** BASIC

### What was created

1. **GitHub private repo** `laurentaf/lacareerops` — hosts the capability
2. **MCP server** `mcp/server.py` — 7 tools (health, list_supported_operations, career_ops_evaluate, career_ops_generate_pdf, career_ops_scan_portals, career_ops_batch_process, career_ops_tracker_list)
3. **Config templates** — `config/profile.example.yml`, `config/cv.example.md`
4. **Dependencies** — `pyproject.toml`, `requirements.txt`, `.gitignore`
5. **README** — ≥400 chars, reproduzível
6. **Meta-project** at `projects/_meta/lacareerops/` with project.yaml, constitution, todo, ADR scaffold
7. **Registry entries** — capabilities.yaml, needs-to-capabilities.yaml, opencode.jsonc
8. **ADR** — `projects/_meta/adr/ADR-003-lacareerops-creation.md`
9. **Capability-evolution** — `projects/_meta/capability-evolution/lacareerops.md`
10. **KB Handoff Boundaries** — `knowledge/handoff-lacareerops.md`

## Obligations

- **capability-architect:** deliver G1-G8 per binding-conditions.md, hand off to delivery-reviewer for G4 sign-off
- **delivery-reviewer:** validate G1-G8, issue BASIC sign-off (or reject with actionable feedback)
- **LACOUNCIL:** track proposal implementation in DuckDB via `lacouncil.record_project()`

## Privacy guarantee

LACAREEROPS repo is **PRIVATE**. No user data (CV, salary, career history) is ever transmitted to external APIs. Each user configures their own `config/cv.md` and `profile.yml`.

## Next step

Delivery-reviewer G4 BASIC sign-off. After sign-off: commit + push per Regime A (LACOUNCIL 391a8179).

---

Created: 2026-06-13
Proposal: 2f1ccd2d-7d0a-44fc-8382-24c3e16ebd0c