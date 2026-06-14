# ADR-001: LAOS Infrastructure Tools (laos.infra)

## Status
Aprovada e implementada (LACOUNCIL 6481da60, 2026-06-14)

## Contexto
5 categorias de operação usavam shell direto (bash/powershell) em vez de
ferramentas MCP dedicadas, violando o Hard Rule #3 ("Capabilities are reached
only through MCP") e gastando ~200-500 tokens por operação:

1. **Corrigir ferramenta** — curl, docker logs, ps aux via shell
2. **Expandir ferramenta** — editar opencode.jsonc manual + restart manual
3. **Criar ferramenta nova** — mkdir + write server.py do zero
4. **Download binário** — curl/wget/Invoke-WebRequest (WDL gate bloqueia)
5. **Validar agente** — WDL inventa agentes inexistentes (ex: "general")

## Decisão
Estender o plugin `laos-doctor` existente para `laos-infra.ts` com 5 tools
adicionais, eliminando shell para estas operações. As tools são expostas
como custom tools do plugin (não requerem MCP server separado).

Tools criadas:
- `health_check(component)` — diagnostica MCP individual (substitui curl)
- `add_tool(component, tool_spec)` — adiciona tool a capability (dry-run)
- `scaffold_mcp(name, tools[])` — scaffold de MCP server novo
- `download_file(url, dest_path, headers?)` — download seguro de binários
- `validate_agent(dispatch_type)` — valida agente vs .opencode/agent/

## Alternativas
1. **MCP server separado** — criar server.py em laos.infra/mcp/ seria mais
   pesado e adicionaria latência. Plugin é mais leve e não requer processo
   separado.
2. **Manter shell** — viola HR#3 e gasta mais tokens. Rejeitado.

## Consequências
- Positivo: HR#3 compliance, economia de tokens (~200-500 → ~40-80/op)
- Positivo: validate_agent evita WDL inventar agentes inexistentes
- Positivo: download_file sem WDL block para binários
- Risco: add_tool requer implementação do handler no repo da capacidade
  (dry-run mostra o que fazer, mas não implementa)
- Manutenção: laos-infra.ts deve ser atualizado se novos agentes forem
  adicionados ao .opencode/agent/ (validate_agent lê runtime, mas aliases
  knownAliases precisam ser mantidos)
