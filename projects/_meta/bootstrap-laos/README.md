# bootstrap-laos — Meta-project

> **Status: active — 2026-06-22**
> **Runner: human** (not LAOS-orchestrator)
> **Scope: workspace-infrastructure**

## Brief

Bootstrap do ecossistema LAOS no PC do usuário: clonar `lacouncil`, sync venvs via `uv`, instalar LADESIGN Node daemon. Necessário para que o structural-change pipeline funcione (LACOUNCIL precisa de um runtime MCP ativo).

## Por que isso existe

`laos-doctor` reportou `venvs: 1/7 OK` e `workspace: 6/8` com `lacouncil` ausente. Sem `lacouncil`, não há canal para:

- `lacouncil.investigate(...)` (5-Whys + Fishbone)
- `lacouncil.create_proposal(...)` (registrar a proposta)
- `register_vote`, `tally_votes`, `apply` (Conselho deliberação)
- `record_project(...)` (memória de longo prazo)

Sem esses, o pipeline estrutural-Change para a adição de `sql.databricks` ao LATADE **não roda**.

## O que é bootstrapped

| Capability | Estado pré | Comando de bootstrap |
|---|---|---|
| lacouncil | ausente | `git clone https://github.com/laurentaf/lacouncil F:\Projetos\lacouncil` |
| latade | repo presente, `.venv` ausente | `uv --directory F:\Projetos\latade sync` |
| lacouncil | (acima) | `uv --directory F:\Projetos\lacouncil sync` |
| lan8n | repo presente, `.venv` ausente | `uv --directory F:\Projetos\lan8n sync` |
| ladesign | repo presente, daemon CLI ausente | `pnpm --dir F:\Projetos\ladesign install` |
| laecon | repo presente | `uv --directory F:\Projetos\laecon sync` |
| laengine | repo presente | `uv --directory F:\Projetos\laengine sync` |

## Por que o usuário corre (não o orchestrator)

Hard Rule #10 (AGENTS.md) garante permissões para arquivos em `E:/projects/**`. Ele diz:

> File operations under E:/projects/** (read, write, edit, create, delete)

Mas **clonar um repo inteiro de github.com** não é uma operação de file-system rotineira — é adicionar conteúdo de uma origem externa ao workspace, criar branches, configurar remotes. É diferente de um `mv` ou um `echo`.

Por convenção, operações que mudam o perfil do workspace são **human-driven**. O orchestrator escreve receitas. O humano roda.

## Como rodar

### Pré-requisitos

- `uv` no PATH (doctor já confirmou `uv 0.9.27`)
- `git` no PATH
- `pnpm` no PATH (opcional; só para LADESIGN)
- `node` 22+ (já confirmado)

### Comando direto (PowerShell)

```powershell
cd F:\Projetos\Laos
pwsh -File .\scripts\bootstrap_laos.ps1
```

ou dry-run primeiro:

```powershell
pwsh -File .\scripts\bootstrap_laos.ps1 -DryRun
```

### Saída esperada

Após ~5-10min (depende de velocidade de rede + dependency resolution):

```
=== lacouncil: uv sync ===
Resolved N packages in X.Xs
Installed M packages in X.Xs
OK: uv sync lacouncil (in-memory structural improvement engine)

=== latade: uv sync ===
Resolved ...
OK: uv sync latade (data engineering)

=== ladesign: pnpm install ===
Lockfile is up to date, resolution step is skipped
Already up to date

OK: pnpm install --dir ladesign

=== laos-doctor verification ===
[PASS] system: 4/4 runtimes OK
[PASS] config: 12/12 entries OK
[PASS] plugins: 13/13 expected present
[PASS] mcp_health: 8/10 OK
[PASS] venvs: 7/7 venvs OK
[PASS] models: 2/2 OK
[PASS] workspace: 8/8 OK
```

## Pós-bootstrap

1. **Salvar o disco** — `laos-doctor` deve retornar todos os checks PASS ou WARN (sem FAIL).
2. **Reportar ao orchestrator** — eu cross-verifico e seleciono o próximo passo:
   - Continuar com `lacouncil.investigate(gap='sql.databricks missing')`
   - Iniciar a proposta LACOUNCIL estrutural.
3. **Clear badge cache**: nenhuma operação adicional.

## Risco residual

Cenários onde o bootstrap pode falhar:

- **gh auth expired**: clone falha com `repository not found`. Re-login com `gh auth login`.
- **Disk full**: `uv sync` pode falhar com `OSError: [Errno 28]`. Verifique espaço (~5GB livre necessário).
- **Rate limit durante uv resolve**: rodar `uv --directory ... sync --offline` após primeiro sync.

## Verificação cruzada

```powershell
git -C F:\Projetos\lacouncil log --oneline -1
Test-Path F:\Projetos\latade\.venv\Scripts\python
Test-Path F:\Projetos\ladesign\apps\daemon\dist\cli.js
```

Todos três devem retornar sucesso.
