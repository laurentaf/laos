---
name: career-ops
description: >-
  Use when the user mentions anything related to: curriculo, CV, resume,
  vaga, job, job offer, offer evaluation, job scan, portal scan, career
  tracking, application tracker, cover letter, carta de apresentacao,
  LinkedIn outreach, contato, entrevista, interview prep, batch
  evaluation, ATS, PDF generation for jobs, career dashboard, pipeline
  de candidaturas, job description analysis, salary evaluation, company
  research. Routes to the career-ops workspace (santifer/career-ops clone
  at F:/projects/career-ops/). Do NOT generate CV, resume, cover letter,
  or job evaluation content inline in LAOS — use career-ops slash commands
  instead.
---

# Career-Ops Router

## O que e

career-ops e um skill system agnostico de CLI (MIT, mantido por Santiago
Fernandez de Valderrama) que roda dentro de AI CLIs (Claude Code, OpenCode,
Gemini CLI, Qwen, Copilot). Tem 14 modos: scan, pdf, cover, batch, tracker,
apply, pipeline, contacto, deep, training, project, etc.

NÃO é uma capability LAOS. NÃO tem MCP server. NÃO esta no registry.
E uma ferramenta externa consumida diretamente, como git, uv, npx.

## Onde fica

O workspace do career-ops esta clonado em:

```
F:/projects/career-ops/
```

Este e um clone direto do upstream `santifer/career-ops`. LAOS nunca
escreve dentro deste repo. Atualizacao e via `git pull`.

## Como usar

### Opcao 1 — Sessao separada no workspace career-ops (recomendado)

Quando o usuario quer trabalhar com career-ops (avaliar vaga, gerar CV,
escanear portais, etc.):

1. Instrua o usuario a abrir uma sessao OpenCode separada em
   `F:/projects/career-ops/`
2. Nessa sessao, os slash commands do career-ops estao disponiveis
   nativamente (`/career-ops scan`, `/career-ops pdf`, etc.)
3. O career-ops gerencia seu proprio config/ (cv.md, profile.yml),
   tracker, PDFs — tudo dentro do workspace dele

### Opcao 2 — Executar comandos a partir do workspace LAOS

Se precisar executar career-ops a partir da sessao LAOS:

1. Use `run_command` com `cwd: "F:/projects/career-ops"`
2. Exemplo: `run_command(command="npx @santifer/career-ops scan", cwd="F:/projects/career-ops")`
3. Os artefatos (PDFs, avaliacoes, tracker) ficam em `F:/projects/career-ops/`,
   NAO em `projects/<name>/artifacts/`

## Regra absoluta

NUNCA escreva conteudo de CV, resume, cover letter, ou avaliacao de vaga
inline no LAOS. Esses artefatos pertencem ao career-ops workspace. Se o
usuario pedir "gera meu CV" ou "avalia essa vaga", voce:

1. Carrega esta skill (ja feita se voce esta lendo isto)
2. Informa que career-ops e a ferramenta correta
3. Orienta para o workspace `F:/projects/career-ops/` (Opcao 1 ou 2 acima)

## Atualizacao

Para atualizar o career-ops para a ultima versao do upstream:

```bash
git -C F:/projects/career-ops pull
```

LAOS nao pinna versao, nao tem sync tool, nao tem smoke test wrapper.
O upstream e a fonte unica. Se uma atualizacao quebrar algo, o usuario
pode fazer `git -C F:/projects/career-ops reset --hard <sha-anterior>`.

## Por que nao e uma capability MCP

3 tentativas de embrulhar career-ops em wrapper MCP falharam (ADR-003
fork, ADR-013 submodule+hub, ADR-014 inline). career-ops nao e uma CLI
com subcommands — e um skill system de slash commands. O wrapper Python
chamava `npx -y career-ops` (package inexistente; o correto e
`@santifer/career-ops`) e mesmo se corrigido, career-ops nao aceita
subcommands como `evaluate --job X`. A abordagem skill-source elimina o
wrapper por construcao.

Detalhes: ADR-015 (career-ops as external skill source).
