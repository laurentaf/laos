# Implementation Report — career-ops External Skill Source (Phase 3)

**Executor:** capability-architect
**Date:** 2026-07-01
**Proposal:** 2dded628-e2f4-4d3f-8e5f-a349c32c019d (aprovada 3/3 SIM, supermaioria)
**WDL Verdict:** artifacts/wdl/career-ops-skill-source-001/verdict.yaml (state: READY)

---

## Summary

All 16 implementation steps from the plan executed successfully. Complete cleanup of lacareerops remnants, new skill-based architecture deployed.

---

## Steps Completed

### Step 3.1 — Clone santifer/career-ops ✅
Cloned https://github.com/santifer/career-ops.git to F:/Projetos/career-ops/
Remote verified: origin → santifer/career-ops

### Step 3.2 — Create skill router ✅
Created .opencode/skills/career-ops/SKILL.md
Frontmatter description covers all matching terms (CV, vaga, job, etc.)
Instructions: never generate inline, always route to career-ops workspace

### Step 3.3 — Create knowledge/external-tools.md ✅
Created knowledge/external-tools.md documenting career-ops as external tool
Includes historical context (ADR-003, ADR-013, ADR-014 superseded by ADR-015)

### Step 3.4 — Edit opencode.jsonc ✅
3.4a: Removed lacareerops MCP server block (was lines 77-93)
3.4b: Replaced "E:/projects/lacareerops-hub/**": "allow" → "../career-ops/**": "allow"

### Step 3.5 — Edit capabilities.yaml ✅
Removed lacareerops entry (lines 151-175): id, kind, mcp_server, repo, status, owns, notes
Now connects lacouncil entry directly to ladesign entry

### Step 3.6 — Edit needs-to-capabilities.yaml ✅
Removed deprecated career comment block (lines 69-77)
alerts: block now connects directly to # Modeling & ML needs

### Step 3.7 — Delete meta-projects ✅
git rm -r projects/_meta/lacareerops/ (7 files)
git rm -r projects/_meta/lacareerops-refactor/ (10 files)

### Step 3.8 — Delete ADR-003 & ADR-013 ✅
git rm projects/_meta/adr/ADR-003-lacareerops-creation.md
git rm projects/_meta/adr/ADR-013-lacareerops-submodule.md
Kept: ADR-003-capability-architect-creation.md (not related to lacareerops)

### Step 3.9 — Delete ADR-014 ✅
git rm projects/_meta/adr/ADR-014-substrate-recovery-2026-06-24.md

### Step 3.10 — Delete handoff KB ✅
git rm knowledge/handoff-lacareerops.md

### Step 3.11 — Delete capability evolution tracking ✅
git rm projects/_meta/capability-evolution/lacareerops.md

### Step 3.12 — Delete WDL artifact remnants ✅
git rm -r artifacts/wdl/lacareerops-refactor-001/ (5 files)
git rm artifacts/wdl/career-ops-capability/bypass-manifest.yaml
Verified: career-ops-capability/ directory empty

### Step 3.13 — Delete external clone ✅
Verified no unpushed commits in F:/Projetos/lacareerops/
Deleted using Python shutil.rmtree (uv run)
Also git rm'd leftover projects/lacareerops-selfeval/artifacts/review/checklist.md

### Step 3.14 — Create ADR-015 ✅
Created projects/_meta/adr/ADR-015-career-ops-external-skill-source.md
Documents: context (3 failed wrappers), decision (external skill source), 
components (clone, skill, KB, permission), cleanup summary

### Step 3.15 — Update AGENTS.md ✅
Searched for lacareerops references in AGENTS.md — none found (no changes needed)

### Step 3.16 — Final grep for residues ✅
Found remaining lacareerops references in:
- projects/_meta/career-ops-skill-source/plan.md (acceptable: plan definition)
- projects/_meta/adr/ADR-015-career-ops-external-skill-source.md (acceptable: historical context)
- artifacts/wdl/career-ops-skill-source-001/* (acceptable: WDL plan artifacts for THIS plan)
- projects/_meta/substrate-recovery-inline/* (acceptable: historical votes, not in scope)

Fixed additional references:
- README.md: updated CAREEROPS link from laurentaf/career-ops → santifer/career-ops
- bootstrap-laos/project.yaml: removed predecessor reference to deleted meta-project

---

## Files Created (3)
- .opencode/skills/career-ops/SKILL.md
- knowledge/external-tools.md
- projects/_meta/adr/ADR-015-career-ops-external-skill-source.md

## Files Deleted via git rm (30)
All lacareerops-related files: meta-projects, ADRs, handoff KB, capability evolution, WDL artifacts

## Files Modified (4)
- .opencode/opencode.jsonc (removed MCP entry + updated path permission)
- registry/capabilities.yaml (removed lacareerops entry)
- registry/needs-to-capabilities.yaml (removed deprecated comment)
- README.md (updated CAREEROPS link)
- projects/_meta/bootstrap-laos/project.yaml (removed predecessor reference)

## Files Unchanged
- AGENTS.md (no lacareerops references found)
