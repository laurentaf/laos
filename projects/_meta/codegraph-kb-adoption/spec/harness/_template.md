# spec/harness/_template.md — Evaluation Harness Template

## Overview

[O que este harness avalia e por quê]

## Prerequisite

```bash
# Projeto deve estar indexado
cd <project-path>
codegraph init -i
# ou, para projetos já indexados:
codegraph status
```

## Eval Matrix

| Arm | Condição | Runs | Model | Effort |
|---|---|---|---|---|
| A (baseline) | Sem a mudança | ≥2 | sonnet | high |
| B (new) | Com a mudança | ≥2 | sonnet | high |

## Command

```bash
# Exemplo: run-all.sh analog
bash scripts/agent-eval/run-all.sh "<project-path>" "<task-prompt>"

# Exemplo: ab-new-vs-baseline.sh analog
bash scripts/agent-eval/ab-new-vs-baseline.sh "<project-path>" "<task-prompt>" [baseline-ref]
```

## Pass Criteria

- [ ] Arm B usa menos tool calls que Arm A (mediana, n≥2)
- [ ] Arm B Read/Grep = 0 dentro do budget do explorer's call tier
- [ ] Arm B wall-clock ≤ Arm A wall-clock
- [ ] Sem regressão em repo de controle (repositório que não muda com a feature)

## Output

Resultados em `artifacts/reviews/<run-id>.md` com:
- Duração por arm
- Tool calls por tipo (Read, Grep, mcp__codegraph__*, mcp__latade__*, etc.)
- Read/Grep counts
- Token total (soma por turn, não result.usage)

## Notes

- Sempre rodar n≥2 por arm — single run é muito ruidoso
- Não confiar em n=1 para decidir se mudança funciona
- Model floor: sempre sonnet para evals (não Opus/Fable)