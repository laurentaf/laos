# Stack decisions

Decisões transversais sobre tooling. Decisões específicas de domínio
ficam nas capability repos.

## Runtime / package management

- **Python**: `uv` para tudo (envs, deps, scripts).
  - LAOS tem `pyproject.toml` próprio. `uv sync` cria `.venv` local.
  - Stub MCP servers e scripts rodam via `uv run python <arquivo>`,
    que usa automaticamente o venv local.
  - **Nunca criar `.venv` manualmente** quando `uv` está disponível.
    Se o repo já tem `.venv`, `uv sync` detecta e re-sincroniza.
    Ver `knowledge/discover-before-build.md` §1 (hierarquia de descoberta).
- **Node**: `npx -y <pacote>` para tools de uso pontual (MCPs npm).
  Sem `package.json` em LAOS.
- **Docker**: checar `docker ps` e `docker images` antes de criar
  ou baixar qualquer container. Preferir `docker compose` quando
  o projeto tem `docker-compose.yaml`.

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

## Boot check de subagente (subagent_boot_check.py)

**Regra:** Antes de despachar qualquer subagente, o orchestrator DEVE
rodar `uv run python scripts/subagent_boot_check.py <subagent> --project-name <name>`.
Substitui a regra anterior de "verificar venv antes de cada comando Python".
A checagem acontece **uma vez no boot**, não per-action.

### O que o boot check valida (5 dimensões)

1. **venv** — venv presente + syncado (pyproject não é mais novo que .venv). Cobre LAOS, latade, lacouncil, lan8n, ladesign, laengine, laecon.
2. **daemon** — para capabilities Node-based (LADESIGN), `node_modules` + `pnpm install` OK.
3. **MCP primário** — entry existe em `.opencode/opencode.jsonc` para cada MCP primário. Opcionais são lazy.
4. **paths** — `projects/<name>/artifacts/<subclass>/` criável para cada subclasse que o subagente produz.
5. **env** — env vars requeridas presentes (LATADE_DB_PATH, GITHUB_TOKEN, N8N_API_URL) ou com default documentado.

## Toolchain inventory (toolchain_inventory.py)

**Regra:** No início de cada ciclo de projeto (antes de needs
resolution), o orchestrator DEVE rodar
`uv run python scripts/toolchain_inventory.py`.
O output é um JSON que inventaria runtimes, package managers,
containers Docker, venvs existentes e configs de projeto no workspace.

### Por que existe

Resolve o problema de agents ignorarem o toolchain existente durante
o planning. Sem inventário, o agente sugere Java quando Python já
está configurado; sugere "vamos subir um DB" quando PostgreSQL já
está rodando. O inventário é **dados concretos**, não regra
documentada — agentes ignoram regras, não ignoram dados.

### O que inventaria

1. **Runtimes no PATH** — python, node, java, go, rustc, gcc, dotnet
2. **Package managers** — uv, pip, npm, pnpm, cargo, winget
3. **Docker** — disponível? containers rodando? imagens locais?
4. **Venvs existentes** — quais projetos já têm `.venv` sincronizado
5. **Configs de projeto** — pyproject.toml, package.json, docker-compose

### Como usar o output

- **Planning (Fase 1):** orchestrator inclui `summary` no dispatch
  brief do subagente. Subagente usa para decidir stack.
- **Execution (Fase 2):** subagente consulta `runtimes` e `venvs`
  antes de instalar algo (cascata de discover-before-build).

### Integração com o loop do orchestrator

```
1. Ler project.yaml
2. Rodar toolchain_inventory.py          ← NOVO
3. Resolver needs via registry
4. WDL preflight gate
5. Dispatch subagent (com inventário no brief)
6. ...
```

### Exit codes

- `0` — PASS, subagente pronto para dispatch.
- `1` — BLOCKED, com mensagens acionáveis por check (qual venv sync, qual `pnpm install`, qual env var setar).

### Quando rodar

- Antes de cada `task` dispatch do orchestrator.
- Após mudança em `pyproject.toml` de qualquer capability.
- Após mudança em `.opencode/opencode.jsonc` (MCP config).
- **Não** rodar per-action dentro do subagente (esse overhead acabou).

### Mid-task tool failure

Se um subagente recebe `4xx/5xx` mid-task: re-chama `*.health()`; se
falhar, **escala ao orchestrator** com mensagem acionável; **NÃO**
improvisar workaround com outra tool.

### Discover before build (Hard Rule, 2026-06-09)

Antes de qualquer setup (venv, Docker, CLI, arquivo), o agente DEVE
verificar se já existe. Cascata obrigatória em
`knowledge/discover-before-build.md` §1. Anti-pattern: instalar
quando já está no PATH, criar venv quando já existe, baixar
container quando já está rodando.

### Onde se aplica

| Subagente | venvs | daemon | MCPs primários | Saída |
|---|---|---|---|---|
| `data-architect` | laos, latade, lacouncil | — | latade | artifacts/{data,pipeline,dq}/ |
| `dashboard-designer` | laos, ladesign | ladesign (Node) | ladesign | artifacts/{design,deck}/ |
| `automation-engineer` | laos, lan8n | — | lan8n | artifacts/automation/ |
| `delivery-reviewer` | laos, lacouncil, latade | — | (none) | (read-only) |
| `orchestrator` | laos + 6 capabilities | ladesign | lacouncil | projects/_meta/ |

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
