# ADR-015: career-ops as External Skill Source

**Status:** accepted (pending LACOUNCIL supermaioria ratification)
**Date:** 2026-07-01
**Decisor:** LACOUNCIL (supermaioria, ≥ 3/4 SIM)
**Proposal:** 2dded628-e2f4-4d3f-8e5f-a349c32c019d
**Deletes:** ADR-003-lacareerops-creation (deletado), ADR-013-lacareerops-submodule (deletado), ADR-014-substrate-recovery (deletado)

---

## Contexto

3 tentativas de embrulhar career-ops (skill system agnóstico de CLI, MIT,
mantido por Santiago Fernández de Valderrama) em wrapper MCP falharam:

1. **ADR-003** (2026-06-13): Fork privado `laurentaf/career-ops` + wrapper
   Python que chama `npx -y career-ops` via subprocess. Falhou: o package
   npm é `@santifer/career-ops` (nome errado) e career-ops não é uma CLI
   com subcommands — é um skill system de slash commands.
2. **ADR-013** (2026-06-19): Hub `laurentaf/lacareerops-hub` + git submodule
   + tool `career_ops_sync` com smoke test. Falhou: hub nunca clonado
   localmente, wrapper nunca rodou, submodule adicionou complexidade sem
   resolver o anti-pattern do wrapper.
3. **ADR-014** (2026-06-24): Substrate recovery inline. Deletado — referências
   a lacareerops tornavam o ADR obsoleto; os 4 outros substrate fixes são
   mudanças de código independentes.

LACOUNCIL e65617ec (2026-07-01, 4/4 SIM) deprecated lacareerops,
reconhecendo que o anti-pattern é o wrapper MCP em si — career-ops não
é embrulhável por construção.

O usuário quer usar o upstream santifer/career-ops diretamente no
workspace, mantendo o upstream como fonte única de atualização.

---

## Decisão

Tratar career-ops como **external skill source**, não como capability MCP.

### Componentes

1. **Clone irmão** de `santifer/career-ops` em `F:/Projetos/career-ops/`
   (não fork, não submodule, não wrapper). Upstream = fonte única.
   Atualização: `git pull`. LAOS nunca escreve dentro do clone.

2. **Skill do OpenCode** em `.opencode/skills/career-ops/SKILL.md`:
   - Router/pointer (não reimplementação)
   - `description` do frontmatter cobre todos os termos de matching
     (curriculo, CV, vaga, job, career, offer, etc.)
   - Instrui: NUNCA escrever CV/carta/avaliação inline no LAOS
   - Aponta para o workspace `F:/Projetos/career-ops/`

3. **Knowledge entry** `knowledge/external-tools.md` documentando
   career-ops como ferramenta externa (não capability, não MCP, não
   registry).

4. **Permissão path** `../career-ops/**` no `opencode.jsonc`.

5. **Sem registry entry.** career-ops NÃO entra em
   `registry/capabilities.yaml` nem em `registry/needs-to-capabilities.yaml`.
   Não é uma capability LAOS; é uma ferramenta externa consumida
   diretamente (como git, uv, npx).

6. **Cleanup total** de todo rastro do lacareerops (ver Implementation abaixo).

### Por que não option (a) — registry entry com kind: external-skill-source

A option (a) colocaria career-ops no `capabilities.yaml` com
`mcp_server: null`. Isso cria um caminho de dispatch quebrado: o loop do
orchestrator (need → capability → despacha subagente via MCP) encontra
`mcp_server: null` e não sabe o que fazer. O LLM pode tentar despachar
um subagente que não tem MCP pra chamar, falhar, e driftar para inline
— exatamente o que queremos evitar. A option (b) elimina esse caminho
quebrado por construção: career-ops não está no routing, o único caminho
é a skill do OpenCode.

### Por que não manter wrapper e consertar

Mesmo corrigindo o package name para `@santifer/career-ops`, career-ops
não aceita subcommands como `evaluate --job X --profile Y`. É um skill
system acionado via slash commands dentro de AI CLIs. O wrapper subprocess
não consegue invocar os modos do career-ops. 3 tentativas falharam pelo
mesmo motivo estrutural.

---

## Alternativas Consideradas

1. **(a) Registry entry com kind: external-skill-source, mcp_server: null.**
   Rejected. Cria caminho de dispatch quebrado. Ver análise acima.

2. **Manter wrapper MCP e corrigir package name.** Rejected. career-ops
   não é uma CLI com subcommands; é um skill system de slash commands.
   O wrapper não consegue invocar os modos. 3 falhas provam o anti-pattern.

3. **Não fazer nada (deixar deprecated sem cleanup).** Rejected. Deixa
   entulho (clone legado, ADRs superseded, entrada MCP morta apontando
   para path inexistente) que causa confusão.

4. **Submodule em vez de clone irmão.** Rejected. Submodule adiciona
   complexidade de pin/sync que é desnecessária quando LAOS nunca escreve
   dentro do repo. Clone irmão + `git pull` é mais simples.

---

## Consequências

### Positivas

- career-ops funciona nativamente (clone direto do upstream, sem wrapper)
- Anti-drift garantido via skill do OpenCode (description cobre todos os termos)
- Atualização trivial: `git pull` (sem sync tool, sem pin, sem smoke test)
- Hard Rule #3 preservada (career-ops não é capability LAOS)
- Limpeza completa elimina confusão futura
- Sem custo de manutenção de wrapper MCP

### Custos e responsabilidades

- Usuário deve `git pull` periodicamente em `F:/Projetos/career-ops/`
  para atualizações do upstream
- career-ops não aparece em `/list-capabilities` (correto — não é capability)
- Projetos LAOS não podem declarar `needs: [cv-generation]` etc. (correto —
  career-ops é ferramenta de uso do usuário, não deliverable de projeto)

### Riscos

- **Risco 1:** Usuário esquece de `git pull` e fica em versão stale.
  Mitigação: nenhuma (é escolha do usuário; upstream é público e estável).
- **Risco 2:** career-ops upstream muda quebra de compatibilidade.
  Mitigação: `git reset --hard <sha-anterior>` no clone.
- **Risco 3:** Usuário pede "gera meu CV" e o agente drifta para inline.
  Mitigação: a skill description cobre todos os termos de matching; o
  OpenCode carrega a skill antes de responder.

---

## Implementation

### Criado
- `F:/Projetos/career-ops/` — clone de santifer/career-ops
- `.opencode/skills/career-ops/SKILL.md` — skill router
- `knowledge/external-tools.md` — documentação da ferramenta externa
- `../career-ops/**` permissão no `opencode.jsonc`

### Deletado (cleanup total)
- `F:/Projetos/lacareerops/` — clone legado do fork ADR-003
- `projects/_meta/lacareerops/` — meta-projeto ADR-003
- `projects/_meta/lacareerops-refactor/` — meta-projeto ADR-013
- `projects/_meta/capability-evolution/lacareerops.md` — tracking file
- `projects/_meta/adr/ADR-003-lacareerops-creation.md` — superseded
- `projects/_meta/adr/ADR-013-lacareerops-submodule.md` — superseded
- `knowledge/handoff-lacareerops.md` — handoff boundaries
- `artifacts/wdl/lacareerops-refactor-001/` — WDL verdict do refactor abortado
- `artifacts/wdl/career-ops-capability/` — bypass manifest
- Entrada MCP `lacareerops` no `opencode.jsonc`
- Permissão `E:/projects/lacareerops-hub/**` no `opencode.jsonc`
- Entrada `lacareerops` no `registry/capabilities.yaml`
- Bloco de comentário deprecated no `registry/needs-to-capabilities.yaml`
- `projects/_meta/adr/ADR-014-substrate-recovery-2026-06-24.md` — ADR histórico deletado; referências a lacareerops o tornavam obsoleto
- `AGENTS.md` — referências a lacareerops removidas

---

## Referências

- LACOUNCIL proposal: 2dded628-e2f4-4d3f-8e5f-a349c32c019d
- LACOUNCIL deprecation: e65617ec-5b61-4d03-b6e8-365a84ca8286 (4/4 SIM, 2026-07-01)
- Upstream: https://github.com/santifer/career-ops
- WDL verdict: artifacts/wdl/career-ops-skill-source-001/verdict.yaml
- ADR-014 (substrate recovery, deletado)
- Skill: .opencode/skills/career-ops/SKILL.md
- Knowledge: knowledge/external-tools.md
