# capability-architect (meta-project)

## O que é

Meta-projeto que criou o subagente `capability-architect` no LAOS — o agente responsável por implementar mudanças estruturais aprovadas pelo LACOUNCIL (novas capabilities, registry entries, workflows, knowledge, meta-projetos).

## Como rodar

Não há código para rodar. O capability-architect é um subagente dispatchado pelo orchestrator via `task(subagent_type="capability-architect")`.

Para validar o estado atual:
```bash
uv run python scripts/subagent_boot_check.py capability-architect --project-name _meta/capability-architect
uv run python scripts/preflight_check.py projects/_meta/capability-architect
```

## Onde está o quê

| Arquivo | O que é |
|---------|---------|
| `.opencode/agent/capability-architect.md` | Definição do agente (frontmatter + scope + R1–R5 + G1–G9) |
| `projects/_meta/capability-architect/project.yaml` | Contrato do meta-projeto |
| `projects/_meta/capability-architect/binding-conditions.md` | 14 condições vinculantes (R1–R5 + G1–G9) |
| `projects/_meta/capability-architect/capability-evolution.md` | Tracking BASIC → STABLE |
| `projects/_meta/capability-architect/contract.md` | Contrato em prosa |
| `projects/_meta/capability-architect/spec/` | SDD scaffold (Missão 0) |
| `projects/_meta/adr/ADR-003-capability-architect-creation.md` | ADR de criação |
| `projects/_meta/adr/ADR-009-git-sync-regime-ab.md` | ADR do regime A/B de git sync |

## Status

- **BASIC** desde 2026-06-04
- **STABLE** deadline: 2026-07-04
- M0 COMPLETE; M1 pending
