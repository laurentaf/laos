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

## LAN8N local-first

- Rodamos n8n self-hosted (`npx n8n` ou Docker) durante MVP.
- `N8N_API_URL` default = `http://localhost:5678/api/v1`.
- `n8n-community` MCP fica desligado até a API estar habilitada e a
  key gerada.
- Migrar para n8n cloud só quando houver razão concreta (multi-device,
  triggers webhook expostos publicamente, etc).

## Verificação de venv (ambiente virtual Python)

**Regra:** Todo agente/subagente que executa código Python DEVE verificar se o venv
correto existe e está syncado antes de rodar qualquer comando.

### Protocolo

1. **Detectar venv do projeto** — Cada projeto tem seu venv:
   - LAOS: `.venv/` (criado via `uv sync`)
   - LATADE: `../latade/.venv/`
   - LACOUNCIL: `../lacouncil/.venv/`
   - LAENGINE: usa `.venv/` herdado do LAOS via `uv run`

2. **Verificar existência** — Testar `Test-Path <projeto>/.venv/Scripts/python.exe`
   antes de executar qualquer script Python no projeto.

3. **Verificar sync** — Se o `pyproject.toml` foi modificado após a criação do venv,
   rodar `uv sync` antes de executar.

4. **Reutilizar vs criar** — Sempre reutilizar o venv existente do projeto. Só criar
   um novo se o projeto explicitamente pedir um ambiente isolado diferente. Cada
   capability repo (latade, lacouncil, lan8n, ladesign, laengine) tem seu próprio
   venv gerenciado por `uv`.

### Onde se aplica

| Projeto | Venv | Gerenciado por | Atalho MCP |
|---------|------|---------------|------------|
| LAOS | `.venv/` | `uv sync` no LAOS | `uv run python ...` |
| LATADE | `../latade/.venv/` | `uv sync` no latade | `..\\latade\\.venv\\Scripts\\python` |
| LACOUNCIL | `../lacouncil/.venv/` | `uv sync` no lacouncil | `..\\lacouncil\\.venv\\Scripts\\python` |
| LAENGINE | Herda do LAOS | `uv run` via LAOS | `uv run python ../laengine/...` |

## Alinhamento com Confidence Protocol do LATADE

O LACOUNCIL adota o **Agreement Matrix** definido pelo LATADE
(`../latade/AGENT_SYSTEM.md` + `../latade/src/core/confidence.py`) para
calcular confiança em decisões estruturais.

O Conselho usa `lacouncil.calculate_confidence(kb_has_pattern, mcp_agrees)`
para avaliar cada proposta antes da votação. Scores alimentam os trust_scores
no DuckDB do LACOUNCIL.

### Mapeamento

| Agreement Matrix | Base Score | Ação LACOUNCIL |
|---|---|---|
| KB ✅ + MCP ✅ (HIGH) | 0.95 | Executa sem restrição |
| KB ✅ + MCP ❌ (CONFLICT) | 0.50 | Investigação obrigatória |
| KB ✅ + MCP 🤷 (MEDIUM) | 0.75 | Prossegue com cautela |
| KB ❌ + MCP ✅ (MCP_ONLY) | 0.85 | Prossegue, confia no MCP |
| KB ❌ + MCP 🤷 (LOW) | 0.50 | Pergunta ao usuário |

### Thresholds por tipo de decisão

| Categoria | Score mínimo | Ação se abaixo |
|---|---|---|
| CRITICAL (fundamentos) | 0.98 | RECUSA + explica |
| IMPORTANT (registry) | 0.95 | PERGUNTA ao usuário |
| STANDARD (workflows) | 0.90 | PROSSEGUE com disclaimer |
| ADVISORY (propostas) | 0.80 | PROSSEGUE livremente |

## Quando criar uma capability nova

Critérios cumulativos:
1. Aparece em ≥ 2 projetos distintos.
2. Tem conhecimento próprio (prompts, padrões, exemplos) que não é
   transversal.
3. Tem ações que podem ser ferramentas MCP (não só leitura).

Se falta qualquer um, fica como Skill local na capability mais próxima
ou como entrada em `knowledge/` aqui.
