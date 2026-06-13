# Todo — lacareerops capability creation

**Status:** IN_PROGRESS
**Started:** 2026-06-13
**Deadline BASIC→STABLE:** 2026-07-13

---

## Milestones

### M0 — Scaffold (✅ 2026-06-13)
- [x] LACOUNCIL proposal approved (2f1ccd2d, supermaioria, 2026-06-13)
- [x] GitHub private repo created (laurentaf/lacareerops)
- [x] MCP server scaffold (mcp/server.py, 7 tools)
- [x] pyproject.toml + requirements.txt
- [x] config/profile.example.yml + config/cv.example.md
- [x] .gitignore
- [x] README.md (≥400 chars)
- [x] Meta-project project.yaml
- [x] Constitution.md (skeleton)
- [x] ADR created
- [x] Capability-evolution tracking
- [x] Handoff Boundaries (G5)
- [x] Registry updated (capabilities.yaml + needs-to-capabilities.yaml)
- [x] opencode.jsonc updated

### G4 — BASIC delivery-reviewer sign-off (⏳ pending)
- [ ] Run delivery-reviewer against all M0 deliverables
- [ ] delivery-reviewer issues BASIC sign-off
- [ ] Update needs-to-capabilities.yaml with routing (after sign-off per G4)
- [ ] Commit + push all changes (Regime A — LACOUNCIL 391a8179)

### G7 — STABLE delivery-reviewer sign-off (⏳ 2026-07-13)
- [ ] ≥1 real project used lacareerops
- [ ] All conditions from proposal delivered
- [ ] Constitution non-placeholder
- [ ] delivery-reviewer issues STABLE sign-off
- [ ] status promoted to STABLE in capabilities.yaml

### M2 — Interview tracker + auto-submission (⏳ 2026-08-13)
- [ ] `career_ops_interview_tracker` tool
- [ ] `career_ops_submit` tool (if security review passes)

---

## Blockers

- Nenhum no momento.

---

## Notes

- automation-engineer é domain-specialist reviewer (G3) para KB + contracts
- delivery-reviewer sign-off G4 pendente — não atualizar needs-to-capabilities.yaml para routing real antes do sign-off (G4 requirement)