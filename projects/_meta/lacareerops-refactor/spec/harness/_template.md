# HARNESS — `<feature-name>`

> **Stub-por-design.** This is template `_template.md` mirrored from
> `registry/spec-templates/spec/harness/_template.md`. **Canonical
> ownership**: LAOS-global registry. Local edits violate §6
> (Imutabilidade) of `knowledge/sdd-principles.md`.
>
> For the lacareerops-refactor meta-project, the harness table is
> implicit in: SDD scaffold files + LACOUNCIL proposal
> `ba9a9bd7-...` + delivery-reviewer sign-off (P0 walk).

## Truth-table

| Hypothesis | Expected signal | Observed | Valid? |

## Risks

1. **Risk 1** — Mitigation:
2. **Risk 2** — Mitigation:
3. **Risk 3** — Mitigation:

## Rollback conditions

- If `<previous_state>` resumes, revert to `<previous_commit>`.
- If `<other_condition>` triggers, run `<rollback_command>`.

## Positive control

A passing run produces:
- A: `<artifact_path>` exists with size > `<threshold>`.
- B: log contains `<signal>`.
- C: ground-truth source matches `<comparison_target>`.

## Negative control

A failing run produces:
- A: error message contains `<specific_substring>`.
- B: rollback invoked (visible in log).
- C: `SUBMODULE_SHA.txt` unchanged from `previous_state`.
