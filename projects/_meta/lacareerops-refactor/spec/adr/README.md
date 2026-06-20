# Architecture Decision Records — lacareerops-refactor

> **Cross-project delegation pattern.** This meta-project does NOT have
> canonical ADRs at `spec/adr/`. Real ADRs live in the LAOS-global
> canonical path:
> - `E:\projects\LAOS\projects\_meta\adr\ADR-013-lacareerops-submodule.md`
>
> **Reason:** lacareerops-refactor is a meta-project that **implements**
> the lacareerops capability refactor. Architectural decisions belong to
> the LAOS-global ADR registry (`projects/_meta/adr/`), not to a
> project-local spec. Mirroring would create drift and violate the ADR
> uniqueness rule (one canonical, many mirrors allowed).
>
> Pattern verified against siblings: `projects/_meta/readme-improvement/`
> follows the same `spec/adr/README.md` → `projects/_meta/adr/`
> delegation convention.

## Numbering

| LAOS canonical ADR | Project-level mirror | Status |
|--------------------|----------------------|--------|
| ADR-013-lacareerops-submodule.md | (mirrored at `lacareernops-hub/docs/adr/`) | accepted (2026-06-19) |

## When to write an ADR here

- If the meta-project introduces a pattern that applies **only** to
  meta-projects (e.g., how to scaffold a refactor meta-project →
  write here, do not clone-ADR from global).
- If the global ADR requires translation to local SDD vocabulary
  (`brief`, `needs`, `deliverables`) → write here as a meta-decision.

## When NOT to write an ADR here

- Architectural decisions affecting ≥ 1 capability or ≥ 1 domain →
  write to `projects/_meta/adr/` (LAOS canonical).
- Capability-specific runtime decisions (e.g., new tool semantics) →
  write inside the capability repo's own docs (e.g.,
  `lacareerops-hub/docs/design/`).
- Privacy/data policy → `knowledge/data-fabrication-policy.md` or
  descendant capability policy docs.

## Process

1. Open an ADR at LAOS-canonical first (`projects/_meta/adr/NNN-...md`).
2. Use the global `_template.md` there (not the meta-project's).
3. Vote and implement via LACOUNCIL (`lacouncil.create_proposal()`).
4. If the meta-project needs to leverage that decision locally, link
   from `spec/adr/README.md` (this file) as a delegation.
