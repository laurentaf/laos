# Stack decisions

Decisões transversais sobre tooling. Decisões específicas de domínio
ficam nas capability repos.

## Runtime / package management

- **Python**: `uv` para tudo (envs, deps, scripts).
  - LAOS tem `pyproject.toml` próprio. `uv sync` cria `.venv` local.
  - Stub MCP servers e scripts rodam via `uv run python <arquivo>`,
    que usa automaticamente o venv local.
- **Node**: `npx -y <pacote>` para tools de uso pontual (MCPs npm).
  Sem `package.json` em LAOS.

## MCP

- Toda capacidade de domínio expõe MCP server na própria repo,
  preferencialmente em `<repo>/mcp/server.py`.
- LAOS não hospeda lógica de capacidade. As entradas em
  `.opencode/opencode.jsonc` apenas apontam para os servers.
- Para credenciais:
  - Use `{env:NAME}` em `opencode.jsonc`.
  - Variáveis específicas do projeto LAOS ficam em `.env` local
    (ignorado por git).
  - Variáveis transversais (como `GITHUB_TOKEN`) ficam em **OS env**,
    nunca duplicadas em `.env`.

## Versionamento de capacidades

- Capacidades evoluem independente. LAOS pina por path relativo (`../`),
  não por tag ou submódulo no MVP.
- Se ficar caótico, migrar para git submodules com SHAs específicos
  por projeto (custo de fricção alto - só fazer quando necessário).

## Modelos LLM

- Não fixar modelo em agentes ou comandos. Deixar herdar do
  `default_agent` ou da config global. Fixar só quando o agente exige
  capacidade específica (ex: visão, raciocínio longo).

## Escolha entre platform MCPs

- **Web search**: `exa` > builtin (mais profundidade + extração + OAuth).
- **Docs de libs**: `context7` sempre antes de acreditar em
  conhecimento do modelo.
- **Repo ops**: `github` MCP para criar/comentar issues e PRs. Para
  operações locais (`git status`, `git diff`), o `bash` builtin basta.

## n8n local-first

- Rodamos n8n self-hosted (`npx n8n` ou Docker) durante MVP.
- `N8N_API_URL` default = `http://localhost:5678/api/v1`.
- `n8n-community` MCP fica desligado até a API estar habilitada e a
  key gerada.
- Migrar para n8n cloud só quando houver razão concreta (multi-device,
  triggers webhook expostos publicamente, etc).

## Quando criar uma capability nova

Critérios cumulativos:
1. Aparece em ≥ 2 projetos distintos.
2. Tem conhecimento próprio (prompts, padrões, exemplos) que não é
   transversal.
3. Tem ações que podem ser ferramentas MCP (não só leitura).

Se falta qualquer um, fica como Skill local na capability mais próxima
ou como entrada em `knowledge/` aqui.
