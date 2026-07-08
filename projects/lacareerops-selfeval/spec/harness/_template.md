# Harness Template — lacareerops-selfeval

> **Cada sub-agente que receber um deliverável deste projeto deve ser
> amarrado a este harness.** Substituir este preâmbulo pelo harness
> específico da task (copia deste template e completa).

---

## Contexto do Projeto

Projeto: **lacareerops-selfeval** (`projects/lacareerops-selfeval/`).
Brief: avaliar Laurent Ferreira contra o mercado AI Data Engineer em
2026 em 5 eixos (tools gaps, portfolio audit, curriculum gaps, LinkedIn
strategy, wage bands). Ver `spec/constitution.md` para princípios
constitucionais.

## Escopo deste Harness

- Deliverável específico:
- Sub-agente:
- Capabilities Used:
- Output esperado (path relativo a `projects/lacareerops-selfeval/`):
- Validação (acceptance criteria):

## Regras

- **Nenhuma dado sintético** (Constitution Art. VI + AGENTS.md Hard #11).
  Se faltar dado real, PARAR e reportar ao orchestrator.
- **Não escrever código de implementação** em LAOS (Hard Rule #1).
  Análises aqui são Markdown estruturado.

## Fontes / Input Pontuais

- `F:\projects\LAOS\user_input_data\Laurent_Ferreira_Engenheiro_de_dados_para_Inteligencia_Artificial_2026.docx`
- `projects/lacareerops-selfeval/artifacts/cv/parsed-cv.md` (quando existir)
- `projects/lacareerops-selfeval/artifacts/portfolio/repos-inventory.md` (idem)
- `https://github.com/laurentaf` (audit)

## Output path template

`projects/lacareerops-selfeval/<path conforme project.yaml deliverables>`

Devolver compact receipt via `lacouncil.record_vote`-style receipt por
chat (ver `knowledge/subagent-result-contract.md`).
