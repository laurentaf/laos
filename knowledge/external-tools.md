# Ferramentas externas

Ferramentas que o LAOS consome diretamente (sem wrapper MCP, sem registry
entry, sem needs routing). Sao ferramentas de uso do usuario, nao capabilities
de deliverable de projeto.

## career-ops

- **Repo:** https://github.com/santifer/career-ops (MIT, publico)
- **Autor:** Santiago Fernandez de Valderrama
- **Clone local:** F:/projects/career-ops/ (repo irmao, nao fork, nao submodule)
- **Tipo:** Skill system agnostico de CLI (14 modos: scan, pdf, cover, batch,
  tracker, apply, pipeline, contacto, deep, training, project, etc.)
- **CLIs suportados:** Claude Code, OpenCode, Gemini CLI, Qwen, Copilot
- **Atualizacao:** `git -C F:/projects/career-ops pull` (upstream = fonte unica)
- **Skill LAOS:** .opencode/skills/career-ops/SKILL.md (router/pointer)
- **NÃO e:** capability LAOS, MCP server, registry entry, needs-routable
- **Artefatos:** ficam em F:/projects/career-ops/ (nao em projects/<name>/artifacts/)

### Por que nao e uma capability MCP

career-ops e um skill system de slash commands, nao uma CLI com subcommands.
3 tentativas de wrapper MCP falharam (ADR-003, ADR-013, ADR-014 — todos
deletados/superseded por ADR-015). O wrapper Python chamava `npx -y career-ops`
(package npm inexistente; o correto e `@santifer/career-ops`) e mesmo se
corrigido, career-ops nao aceita subcommands — e acionado via slash commands
dentro de AI CLIs.

### Como usar

1. Abrir sessao OpenCode em F:/projects/career-ops/ (recomendado)
2. Ou executar comandos via `run_command(cwd="F:/projects/career-ops")`
3. Slash commands: `/career-ops scan`, `/career-ops pdf`, `/career-ops tracker`,
   `/career-ops batch`, `/career-ops apply`, etc.

### Configuracao do usuario

Cada usuario configura seus proprios `config/cv.md` e `config/profile.yml`
dentro de `F:/projects/career-ops/config/`. Esses arquivos sao gitignored
pelo proprio career-ops. LAOS nao gerencia nem armazena esses dados.

### Historico

- ADR-003 (fork + wrapper, 2026-06-13) — deletado, superseded por ADR-015
- ADR-013 (hub + submodule, 2026-06-19) — deletado, superseded por ADR-015
- ADR-014 (substrate recovery, 2026-06-24) — deletado
- LACOUNCIL e65617ec (deprecated, 2026-07-01, 4/4 SIM)
- ADR-015 (external skill source, 2026-07-01) — arquitetura atual
