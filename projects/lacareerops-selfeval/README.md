# lacareerops-selfeval

Auditoria estratégica do posicionamento de Laurent Ferreira no mercado
de AI Data Engineer / Data Specialist em 2026.

## O que é este projeto

Projeto agentic-adhoc que cruza três fontes — CV do usuário,
portfolio GitHub da `laurentaf` e mercado real (job descriptions +
wage benchmarks) — para produzir 5 eixos de análise:

1. **Tools gaps** — o que o mercado de AI Data Engineer pede em 2026
2. **Portfolio audit** — qualidade projeto-a-projeto do `laurentaf`
3. **Curriculum gaps** — matriz 3 zonas (tenho-fortalece / tenho-trocar / falta-aprender)
4. **LinkedIn strategy** — avaliação da ideia do usuário + 30 posts + visuais
5. **Wage bands** — faixas salariais para negociação em entrevistas

Inputs:
- CV em `F:\projects\LAOS\user_input_data\Laurent_Ferreira_*.docx`
- Repos públicos `github.com/laurentaf/*`
- Market data via `exa`/`context7` MCPs

## Como rodar

```bash
# Pré-flight (após scaffold concluído):
uv run python scripts/preflight_check.py projects/lacareerops-selfeval

# Sub-agent boot check antes de cada dispatch:
uv run python scripts/subagent_boot_check.py <subagent> --project-name lacareerops-selfeval
```

Stages detalhados em `spec/todo.md`. Constitution em `spec/constitution.md`.
Decisões registradas em `spec/adr/`.

## Onde está o quê

| Lugar | Contém |
|-------|--------|
| `spec/constitution.md` | 9 princípios constitucionais do projeto |
| `spec/todo.md` | Stages 0-8 com sub-tasks |
| `spec/specs/000-bootstrap/spec.md` | Spec inicial (contexto, decisão, critérios de pronto, scope) |
| `spec/adr/` | ADRs (template + index vazio; primeiros ADRs após Stage 3) |
| `spec/design-direction.md` | Direção visual para os 30 LinkedIn visuals |
| `spec/harness/_template.md` | Template para harnesses de sub-agentes |
| `contract.md` | Resumo em prosa: brief, needs, deliverables, capabilities |
| `project.yaml` | Contrato estruturado (autoritativo para o orchestrator) |
| `artifacts/cv/`           | CV parsed (input) |
| `artifacts/market/`        | tools-gaps, wage-bands |
| `artifacts/portfolio/`     | github-audit, curriculum-gaps, repos-inventory |
| `artifacts/linkedin/`      | strategy-evaluation, 30-posts-backlog, visuals-deck.html |

## Status

**2026-06-21** — SDD scaffold criado. Aguardando WDL preflight gate via
`workflow-decomposer` (Stage 1).

> Este projeto é `external_delivery: false` (auto-avaliação); ainda
> assim, passa pelo review do `delivery-reviewer` para validar pelo
> padroes-entrega.md antes do close.
