# Plano Detalhado: career-ops como External Skill Source (Opção B)

**Versão:** 1.0
**Criado por:** GLM 5.2 (orchestrator)
**Executor:** DeepSeek V4 Flash (capability-architect)
**Data:** 2026-07-01
**Estratégia LACOUNCIL:** supermaioria (3/4 SIM mínimo)
**Git sync regime:** A (push obrigatório na mesma sessão)

---

## Premissas (não negociáveis)

1. **Upstream é fonte única.** `santifer/career-ops` é clonado como repo irmão em `F:/Projetos/career-ops/`. LAOS nunca escreve dentro dele. Atualização = `git pull`.
2. **Sem wrapper MCP.** career-ops é um skill system agnóstico de CLI (slash commands dentro de AI CLIs). Não é embrulhável em MCP. 3 tentativas falharam (ADR-003, ADR-013, ADR-014).
3. **Fora do registry.** career-ops NÃO é uma capability LAOS. Não entra em `registry/capabilities.yaml`. Não entra em `registry/needs-to-capabilities.yaml`. É uma ferramenta externa consumida diretamente (como `git`, `uv`, `npx`).
4. **Anti-drift via skill.** A skill `.opencode/skills/career-ops/SKILL.md` é o único mecanismo anti-drift. Sua `description` (frontmatter) deve cobrir todos os termos de matching: curriculo, CV, resume, vaga, job, career, offer, cover letter, carta, LinkedIn, entrevista, interview, ATS, PDF, scan, tracker, application, batch, pipeline.
5. **Cleanup total.** Tudo que referencia lacareerops e não é mais utilizado deve ser excluído. Sem arquivar, sem deixar "para histórico". ADR-014 incluso — deletado inteiro por decisão do usuário; os 4 outros substrate fixes são mudanças de código já aplicadas, o ADR é documentação histórica.
6. **Conselho completo.** Pipeline LACOUNCIL formal com 4 votos. Sem bypass inline.

---

## Estrutura do clone

```
F:/Projetos/career-ops/         ← clone de santifer/career-ops (repo irmão, NÃO submodule)
F:/Projetos/Laos/               ← LAOS (este repo)
F:/Projetos/lacareerops/        ← DELETAR (fork legado ADR-003, morto)
```

O clone `F:/Projetos/career-ops/` contém o workspace do career-ops com:
- `.opencode/skills/` + `commands/` (skills nativas do career-ops para OpenCode)
- `modes/` (14 modos: scan, pdf, cover, batch, tracker, apply, pipeline, etc.)
- `config/` (cv.md, profile.yml — gitignored, cada usuário configura os seus)
- `dashboard/` (Go TUI opcional)

---

## Fase 0 — LACOUNCIL Investigação + Proposta

**Quem executa:** orchestrator (direto, WDL-exempt per Hard Rule 8.4)
**Ferramenta:** `lacouncil.investigate()` + `lacouncil.create_proposal()`

### Step 0.1 — Investigação formal (5 Whys + Fishbone)

Chamar `lacouncil.investigate` com o seguinte gap:

```
gap: "O wrapper MCP lacareerops (3 tentativas: ADR-003 fork, ADR-013 submodule+hub, ADR-014 inline) nunca foi funcional porque career-ops é um skill system de slash commands, não uma CLI embrulhável em subprocess MCP. O wrapper Python chama `npx -y career-ops` mas o package npm é `@santifer/career-ops` (nome errado) e mesmo se corrigido, career-ops não aceita subcommands como `evaluate --job X` — é acionado via slash commands dentro de AI CLIs. O usuário quer usar o upstream santifer/career-ops diretamente, mantendo-o como fonte de atualização, sem wrapper."
```

### Step 0.2 — Criar proposta formal

Chamar `lacouncil.create_proposal` com:

- **titulo:** "career-ops como External Skill Source — eliminação do wrapper MCP lacareerops"
- **autor:** "orchestrator (GLM 5.2), em atendimento a requisição do usuário Laurent"
- **contexto:** "3 tentativas de embrulhar career-ops (skill system agnóstico de CLI, MIT, mantido por Santiago Fernández de Valderrama) em wrapper MCP falharam: ADR-003 (fork privado + wrapper Python, 2026-06-13), ADR-013 (hub + submodule + career_ops_sync tool, 2026-06-19), ADR-014 (substrate recovery inline, 2026-06-24). LACOUNCIL e65617ec (4/4 SIM, 2026-07-01) deprecated lacareerops reconhecendo o anti-pattern. Diagnóstico raiz: o wrapper Python em F:/Projetos/lacareerops/mcp/server.py chama `npx -y career-ops` (package inexistente no npm — o correto é `@santifer/career-ops`) e mesmo se corrigido, career-ops não é uma CLI com subcommands — é um skill system de slash commands que roda dentro de AI CLIs (Claude Code, OpenCode, Gemini CLI, Qwen, Copilot). career-ops não é embrulhável em MCP por construção. O usuário quer usar o upstream santifer/career-ops diretamente no workspace, mantendo o upstream como fonte única de atualização."
- **mudanca:** "1) Clonar santifer/career-ops como repo irmão em F:/Projetos/career-ops/ (não fork, não submodule, não wrapper). Upstream = fonte única. Atualização via `git pull`. 2) Criar skill .opencode/skills/career-ops/SKILL.md (router/pointer, não reimplementação). A description do frontmatter cobre todos os termos de matching (curriculo, CV, vaga, job, career, offer, cover letter, carta, LinkedIn, entrevista, interview, ATS, PDF, scan, tracker, application, batch, pipeline). A skill instrui: NUNCA escrever CV/carta/avaliação inline no LAOS; usar career-ops workspace em F:/Projetos/career-ops/. 3) Criar knowledge/external-tools.md documentando career-ops como ferramenta externa (não capability LAOS, não MCP, não no registry). 4) Adicionar permissão path `../career-ops/**` no opencode.jsonc. 5) Cleanup completo de todo rastro do lacareerops: deletar clone legado F:/Projetos/lacareerops/, remover entrada MCP morta do opencode.jsonc, remover entrada deprecated do capabilities.yaml, remover bloco de comentário deprecated do needs-to-capabilities.yaml, deletar ADR-003, ADR-013 e ADR-014 (superseded/deletados), deletar meta-projetos lacareerops/ e lacareerops-refactor/, deletar capability-evolution/lacareerops.md, deletar knowledge/handoff-lacareerops.md, deletar artifacts/wdl/lacareerops-refactor-001/ e artifacts/wdl/career-ops-capability/. 6) Criar ADR-015 documentando a nova arquitetura skill-source. 7) Atualizar AGENTS.md removendo referências a lacareerops. 8) Deletar repos GitHub legados (laurentaf/career-ops, laurentaf/lacareerops-hub, laurentaf/lacareerops)."
- **impacto:** "career-ops fica visível no workspace LAOS via skill do OpenCode (não via registry/capabilities.yaml). Anti-drift garantido: quando usuário menciona CV/vaga/curriculo, a skill carrega e instrui a usar career-ops workspace, não inline. Atualização pelo upstream: `git pull` em F:/Projetos/career-ops/ — sem sync tool, sem pin, sem wrapper. Hard Rule #3 preservada: career-ops não é capability LAOS, é ferramenta externa consumida diretamente (como git, uv, npx). Limpeza completa de todo rastro do lacareerops evita confusão futura."
- **alternativas:** "1) (a) Manter career-ops no registry com kind: external-skill-source, mcp_server: null — rejeitado porque cria caminho de dispatch quebrado (mcp_server: null confunde o loop do orchestrator que espera despachar subagente via MCP; o LLM pode tentar o caminho MCP, falhar, e driftar para inline). 2) Manter wrapper MCP e tentar consertar (corrigir package name para @santifer/career-ops) — rejeitado: 3 tentativas falharam pelo mesmo anti-pattern; career-ops não é embrulhável em MCP por construção (não tem subcommands CLI, é skill system de slash commands). 3) Não fazer nada (deixar deprecated sem cleanup) — rejeitado: deixa entulho (clone legado, ADRs superseded, entrada MCP morta apontando para path inexistente) que causa confusão e viola a premissa do usuário de excluir tudo que não é utilizado."
- **categoria:** "laos"
- **estrategia:** "supermaioria"

**Verificação Fase 0:**
- `lacouncil.get_proposal(proposal_id=<id_retornado>)` retorna a proposta com status "aberta"
- O `proposal_id` retornado é anotado para as fases seguintes

---

## Fase 1 — Votação do Conselho

**Quem executa:** orchestrator despacha 4 Conselheiros (governance mode, WDL-exempt per LACOUNCIL 726be80b)
**Estratégia:** supermaioria (≥ 3/4 SIM)

Despachar os 4 Conselheiros em paralelo via `task` tool, cada um com um brief curto (5-15 linhas) contendo:
- O `proposal_id` da Fase 0
- A instrução: "Leia a proposta. Vote SIM, NÃO, ou ABSTENCAO via `lacouncil.register_vote()`. Justifique em 3-5 linhas."
- O detalhamento da mudança (contexto + mudança + alternativas) para que o Conselheiro possa votar informado

### Brief para cada Conselheiro (pode ser o mesmo texto, adapta só o destinatário)

```
Projeto: career-ops-skill-source (meta-projeto estrutural)
Proposal ID: <proposal_id da Fase 0>

A proposta substitui o wrapper MCP lacareerops (deprecated, 3 ADRs falhados) por clone direto do upstream santifer/career-ops + skill do OpenCode como router. career-ops fica FORA do registry (não é capability MCP, é ferramenta externa). Cleanup total de todo rastro do lacareerops.

Mudança: clone irmão santifer/career-ops em F:/Projetos/career-ops/ + skill .opencode/skills/career-ops/SKILL.md + knowledge/external-tools.md + cleanup completo (deletar clone legado, ADRs superseded, meta-projetos, entrada MCP morta) + ADR-015.

Alternativas rejeitadas: (a) registry entry com mcp_server: null (cria caminho de dispatch quebrado → drift); manter wrapper (3 falhas, anti-pattern); não fazer nada (deixa entulho).

Vote via lacouncil.register_vote(proposal_id=<id>, voter=<seu_nome>, voto=<SIM|NAO|ABSTENCAO>, justificativa=<3-5 linhas>).
```

### Step 1.1 — Despachar data-architect
- `subagent_type: "data-architect"`
- `description: "Vote career-ops proposal"`
- Vote como `data-architect`

### Step 1.2 — Despachar dashboard-designer
- `subagent_type: "dashboard-designer"`
- `description: "Vote career-ops proposal"`
- Vote como `dashboard-designer`

### Step 1.3 — Despachar automation-engineer
- `subagent_type: "automation-engineer"`
- `description: "Vote career-ops proposal"`
- Vote como `automation-engineer`

### Step 1.4 — Despachar delivery-reviewer
- `subagent_type: "delivery-reviewer"`
- `description: "Vote career-ops proposal"`
- Vote como `delivery-reviewer`

### Step 1.5 — Talliar votos

Chamar `lacouncil.tally_votes(proposal_id=<id>)`.

**Verificação Fase 1:**
- Resultado: ≥ 3/4 SIM → aprovada (supermaioria)
- Se < 3/4 SIM → parar, reportar ao usuário, não prosseguir

---

## Fase 2 — WDL Preflight Gate

**Quem executa:** orchestrator despacha workflow-decomposer
**Mandatório:** Hard Rule #8 (specialist dispatch exige verdict READY)

### Step 2.1 — Despachar workflow-decomposer

Despachar `workflow-decomposer` com:
- `subagent_type: "workflow-decomposer"`
- `description: "WDL plan career-ops"`
- Payload:
  ```
  plan_id: career-ops-skill-source-001
  project: career-ops-skill-source
  needs: [improvement]
  brief_context: "Substituir wrapper MCP lacareerops (deprecated) por clone direto santifer/career-ops + skill OpenCode. Cleanup total. Opção B (fora do registry). LACOUNCIL proposal <id> aprovada supermaioria."
  prior_verdicts: []
  ```

### Step 2.2 — Verificar verdict

Ler `artifacts/wdl/career-ops-skill-source-001/verdict.yaml`.

**Verificação Fase 2:**
- `state: READY` → prosseguir para Fase 3
- `state: DEFER` → corrigir os gaps apontados, re-despachar workflow-decomposer
- `state: ESCALATE` → parar, reportar ao usuário

---

## Fase 3 — Implementação

**Quem executa:** capability-architect (com verdict READY da Fase 2)
**Namespace MCP permitido:** `lacouncil.*`, `github.*`
**Paths permitidos para escrita:** `projects/_meta/career-ops-skill-source/`, `projects/_meta/adr/`, `registry/`, `knowledge/`, `.opencode/`, `AGENTS.md`
**Verdict WDL:** anexar `[verdict.yaml, plan_id=career-ops-skill-source-001, verified_by=workflow-decomposer]` no dispatch

### Step 3.1 — Clonar santifer/career-ops

**Ação:** Clonar o upstream como repo irmão (não dentro do LAOS, não como submodule).

**Comando:**
```bash
git clone https://github.com/santifer/career-ops.git F:/Projetos/career-ops
```

**Verificação:**
```bash
# Confirmar que o clone existe e tem a estrutura esperada
ls F:/Projetos/career-ops/.opencode/skills/
ls F:/Projetos/career-ops/modes/
ls F:/Projetos/career-ops/commands/

# Confirmar que o remote é o upstream (não um fork)
git -C F:/Projetos/career-ops remote -v
# Deve mostrar: origin  https://github.com/santifer/career-ops.git
```

**Se falhar:** Verificar conectividade com GitHub. Se o repo for privado (não é, é MIT público), configurar credenciais. Não prosseguir sem o clone.

### Step 3.2 — Criar skill .opencode/skills/career-ops/SKILL.md

**Ação:** Criar a skill router que previne drift. O diretório `.opencode/skills/` não existe ainda — criar.

**Conteúdo do arquivo** `F:/Projetos/Laos/.opencode/skills/career-ops/SKILL.md`:

```markdown
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
  at F:/Projetos/career-ops/). Do NOT generate CV, resume, cover letter,
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
F:/Projetos/career-ops/
```

Este e um clone direto do upstream `santifer/career-ops`. LAOS nunca
escreve dentro deste repo. Atualizacao e via `git pull`.

## Como usar

### Opcao 1 — Sessao separada no workspace career-ops (recomendado)

Quando o usuario quer trabalhar com career-ops (avaliar vaga, gerar CV,
escanear portais, etc.):

1. Instrua o usuario a abrir uma sessao OpenCode separada em
   `F:/Projetos/career-ops/`
2. Nessa sessao, os slash commands do career-ops estao disponiveis
   nativamente (`/career-ops scan`, `/career-ops pdf`, etc.)
3. O career-ops gerencia seu proprio config/ (cv.md, profile.yml),
   tracker, PDFs — tudo dentro do workspace dele

### Opcao 2 — Executar comandos a partir do workspace LAOS

Se precisar executar career-ops a partir da sessao LAOS:

1. Use `run_command` com `cwd: "F:/Projetos/career-ops"`
2. Exemplo: `run_command(command="npx @santifer/career-ops scan", cwd="F:/Projetos/career-ops")`
3. Os artefatos (PDFs, avaliacoes, tracker) ficam em `F:/Projetos/career-ops/`,
   NAO em `projects/<name>/artifacts/`

## Regra absoluta

NUNCA escreva conteudo de CV, resume, cover letter, ou avaliacao de vaga
inline no LAOS. Esses artefatos pertencem ao career-ops workspace. Se o
usuario pedir "gera meu CV" ou "avalia essa vaga", voce:

1. Carrega esta skill (ja feita se voce esta lendo isto)
2. Informa que career-ops e a ferramenta correta
3. Orienta para o workspace `F:/Projetos/career-ops/` (Opcao 1 ou 2 acima)

## Atualizacao

Para atualizar o career-ops para a ultima versao do upstream:

```bash
git -C F:/Projetos/career-ops pull
```

LAOS nao pinna versao, nao tem sync tool, nao tem smoke test wrapper.
O upstream e a fonte unica. Se uma atualizacao quebrar algo, o usuario
pode fazer `git -C F:/Projetos/career-ops reset --hard <sha-anterior>`.

## Por que nao e uma capability MCP

3 tentativas de embrulhar career-ops em wrapper MCP falharam (ADR-003
fork, ADR-013 submodule+hub, ADR-014 inline). career-ops nao e uma CLI
com subcommands — e um skill system de slash commands. O wrapper Python
chamava `npx -y career-ops` (package inexistente; o correto e
`@santifer/career-ops`) e mesmo se corrigido, career-ops nao aceita
subcommands como `evaluate --job X`. A abordagem skill-source elimina o
wrapper por construcao.

Detalhes: ADR-015 (career-ops as external skill source).
```

**Verificação:**
```bash
# Confirmar que o arquivo existe
ls F:/Projetos/Laos/.opencode/skills/career-ops/SKILL.md

# Confirmar que o frontmatter tem name e description
head -20 F:/Projetos/Laos/.opencode/skills/career-ops/SKILL.md
```

### Step 3.3 — Criar knowledge/external-tools.md

**Ação:** Documentar career-ops como ferramenta externa (referência canônica).

**Conteúdo do arquivo** `F:/Projetos/Laos/knowledge/external-tools.md`:

```markdown
# Ferramentas externas

Ferramentas que o LAOS consome diretamente (sem wrapper MCP, sem registry
entry, sem needs routing). Sao ferramentas de uso do usuario, nao capabilities
de deliverable de projeto.

## career-ops

- **Repo:** https://github.com/santifer/career-ops (MIT, publico)
- **Autor:** Santiago Fernandez de Valderrama
- **Clone local:** F:/Projetos/career-ops/ (repo irmao, nao fork, nao submodule)
- **Tipo:** Skill system agnostico de CLI (14 modos: scan, pdf, cover, batch,
  tracker, apply, pipeline, contacto, deep, training, project, etc.)
- **CLIs suportados:** Claude Code, OpenCode, Gemini CLI, Qwen, Copilot
- **Atualizacao:** `git -C F:/Projetos/career-ops pull` (upstream = fonte unica)
- **Skill LAOS:** .opencode/skills/career-ops/SKILL.md (router/pointer)
- **NÃO e:** capability LAOS, MCP server, registry entry, needs-routable
- **Artefatos:** ficam em F:/Projetos/career-ops/ (nao em projects/<name>/artifacts/)

### Por que nao e uma capability MCP

career-ops e um skill system de slash commands, nao uma CLI com subcommands.
3 tentativas de wrapper MCP falharam (ADR-003, ADR-013, ADR-014 — todos
deletados/superseded por ADR-015). O wrapper Python chamava `npx -y career-ops`
(package npm inexistente; o correto e `@santifer/career-ops`) e mesmo se
corrigido, career-ops nao aceita subcommands — e acionado via slash commands
dentro de AI CLIs.

### Como usar

1. Abrir sessao OpenCode em F:/Projetos/career-ops/ (recomendado)
2. Ou executar comandos via `run_command(cwd="F:/Projetos/career-ops")`
3. Slash commands: `/career-ops scan`, `/career-ops pdf`, `/career-ops tracker`,
   `/career-ops batch`, `/career-ops apply`, etc.

### Configuracao do usuario

Cada usuario configura seus proprios `config/cv.md` e `config/profile.yml`
dentro de `F:/Projetos/career-ops/config/`. Esses arquivos sao gitignored
pelo proprio career-ops. LAOS nao gerencia nem armazena esses dados.

### Historico

- ADR-003 (fork + wrapper, 2026-06-13) — deletado, superseded por ADR-015
- ADR-013 (hub + submodule, 2026-06-19) — deletado, superseded por ADR-015
- ADR-014 (substrate recovery, 2026-06-24) — deletado
- LACOUNCIL e65617ec (deprecated, 2026-07-01, 4/4 SIM)
- ADR-015 (external skill source, 2026-07-01) — arquitetura atual
```

**Verificação:**
```bash
ls F:/Projetos/Laos/knowledge/external-tools.md
```

### Step 3.4 — Cleanup opencode.jsonc

**Ação:** Remover entrada MCP morta do lacareerops + adicionar permissão path para career-ops.

**Edit 3.4a — Remover bloco MCP lacareerops (linhas 78-93):**

Usar a ferramenta `edit` com:

- `filePath: "F:/Projetos/Laos/.opencode/opencode.jsonc"`
- `oldString:` (o bloco inteiro de comentário + entry, das linhas 78 a 93):

```
    // LACAREEROPS — job search optimization (career-ops CLI wrapper).
    // Repo: github.com/laurentaf/lacareerops-hub (PRIVATE hub; replaces legacy
    // fork github.com/laurentaf/career-ops per LACOUNCIL proposal
    // ba9a9bd7-3686-4d6e-9f1b-3efc46f37a8c, 2026-06-19, supermaioria 4/4 SIM).
    // Architecture: hub + git submodule (upstream `santifer/career-ops` pinned
    // at SUBMODULE_SHA.txt). 8 MCP tools: health, list, evaluate, generate_pdf,
    // scan_portals, batch_process, tracker, career_ops_sync (pin advance +
    // 4-check smoke + auto-rollback). Each user configures own profile.yml +
    // cv.md in `config/` (gitignored). Status: BASIC (v1.1.0, 2026-06-19).
    // Deadline STABLE: 2026-07-13. ADR-013 = submodule + sync tool architecture.
    "lacareerops": {
      "type": "local",
      "command": ["uv", "run", "python", "E:/projects/lacareerops-hub/mcp/server.py"],
      "enabled": true,
      "env": {}
    },

```

- `newString:` (string vazia — remover o bloco inteiro, incluindo a linha em branco depois)

**Atenção:** O `oldString` acima deve ser copiado EXATAMENTE como aparece no arquivo, preservando indentação (espaços, não tabs) e quebras de linha. Se o `edit` falhar com "oldString not found", ler o arquivo novamente com `read` nas linhas 78-93 e copiar o conteúdo exato.

**Edit 3.4b — Substituir permissão path lacareerops-hub por career-ops:**

- `filePath: "F:/Projetos/Laos/.opencode/opencode.jsonc"`
- `oldString:` `      "E:/projects/lacareerops-hub/**": "allow"`
- `newString:` `      "../career-ops/**": "allow"`

**Verificação:**
```bash
# Confirmar que lacareerops nao aparece mais no opencode.jsonc
grep -c "lacareerops" F:/Projetos/Laos/.opencode/opencode.jsonc
# Deve retornar 0

# Confirmar que career-ops path foi adicionado
grep "career-ops" F:/Projetos/Laos/.opencode/opencode.jsonc
# Deve mostrar a linha ../career-ops/**": "allow"
```

### Step 3.5 — Cleanup capabilities.yaml

**Ação:** Remover a entrada deprecated do lacareerops (linhas 151-175).

**Edit:**

- `filePath: "F:/Projetos/Laos/registry/capabilities.yaml"`
- `oldString:` (o bloco inteiro da entrada, linhas 151-175 + linha em branco antes de `  - id: ladesign`):

```
  - id: lacareerops
    kind: domain
    mcp_server: lacareerops
    repo: https://github.com/laurentaf/lacareerops-hub
    status: deprecated
    owns:
      - career.evaluation
      - career.cv-pdf
      - career.portal-scan
      - career.batch
      - career.tracker
      - career.sync (career_ops_sync — submodule pin advance with smoke + rollback; see ADR-013)
    notes: |
      ⛔ DEPRECATED per LACOUNCIL e65617ec (2026-07-01, 4/4 SIM).
      The lacareerops MCP wrapper was never functional locally — the hub repo was
      never cloned, the MCP server never ran, and all 8 promised tools were
      unreachable. The submodule architecture (ADR-013) added complexity without
      solving the wrapper anti-pattern. The original upstream
      `santifer/career-ops` is actively maintained and directly usable via npx.
      Career needs (career-evaluation, cv-generation, job-scan, career-tracker)
      were removed from needs-to-capabilities.yaml — compose existing capabilities
      or use career-ops CLI directly instead.
      Historical ADRs preserved: ADR-003 (creation), ADR-013 (submodule refactor),
      ADR-014 (substrate recovery). Meta-projetos mantidos como registro histórico.
      LACOUNCIL proposal e65617ec-5b61-4d03-b6e8-365a84ca8286.

```

- `newString:` (string vazia)

**Atenção:** Preservar a indentação exata (2 espaços para `- id:`, 4 espaços para `kind:`, etc.). Se o `edit` falhar, ler o arquivo novamente e copiar exatamente.

**Verificação:**
```bash
grep -c "lacareerops" F:/Projetos/Laos/registry/capabilities.yaml
# Deve retornar 0
```

### Step 3.6 — Cleanup needs-to-capabilities.yaml

**Ação:** Remover o bloco de comentário deprecated (linhas 69-77).

**Edit:**

- `filePath: "F:/Projetos/Laos/registry/needs-to-capabilities.yaml"`
- `oldString:`

```
# ─── Career / job search needs (DEPRECATED: lacareerops) ─────
# Removed per LACOUNCIL e65617ec (2026-07-01, 4/4 SIM).
# The lacareerops MCP wrapper was never functional.
# Use `npx @santifer/career-ops` directly or compose existing capabilities.
# career-evaluation → lacareerops (removed)
# cv-generation     → lacareerops (removed)
# job-scan          → lacareerops (removed)
# career-tracker    → lacareerops (removed)

```

- `newString:` (string vazia — junta o bloco `alerts:` com o bloco `# ─── Modeling & ML needs`)

**Verificação:**
```bash
grep -c "lacareerops\|career-ops" F:/Projetos/Laos/registry/needs-to-capabilities.yaml
# Deve retornar 0
```

### Step 3.7 — Deletar meta-projetos lacareerops

**Ação:** Deletar os diretórios de meta-projetos relacionados ao lacareerops.

**Comandos:**
```bash
# Meta-projeto ADR-003 (creation)
rm -rf F:/Projetos/Laos/projects/_meta/lacareerops/

# Meta-projeto ADR-013 (refactor)
rm -rf F:/Projetos/Laos/projects/_meta/lacareerops-refactor/
```

**Atenção:** O comando `rm -rf` é bloqueado pelo opencode allowlist. Usar alternativa:
- Se em Windows/PowerShell: `Remove-Item -Recurse -Force F:/Projetos/Laos/projects/_meta/lacareerops/`
- Se via git: `git -C F:/Projetos/Laos rm -r projects/_meta/lacareerops/`

**Verificação:**
```bash
# Confirmar que os diretórios não existem mais
ls F:/Projetos/Laos/projects/_meta/lacareerops/  # deve falhar
ls F:/Projetos/Laos/projects/_meta/lacareerops-refactor/  # deve falhar
```

### Step 3.8 — Deletar ADRs superseded

**Ação:** Deletar ADR-003 e ADR-013 (ambos inteiramente sobre lacareerops, superseded por ADR-015).

**Comandos:**
```bash
git -C F:/Projetos/Laos rm projects/_meta/adr/ADR-003-lacareerops-creation.md
git -C F:/Projetos/Laos rm projects/_meta/adr/ADR-013-lacareerops-submodule.md
```

**Verificação:**
```bash
ls F:/Projetos/Laos/projects/_meta/adr/ADR-003-lacareerops-creation.md  # deve falhar
ls F:/Projetos/Laos/projects/_meta/adr/ADR-013-lacareerops-submodule.md  # deve falhar
```

### Step 3.9 — Deletar ADR-014 (inteiro)

**Ação:** ADR-014 (substrate recovery) deletado inteiro por decisão do usuário. Contém referências a lacareerops que não devem permanecer. Os 4 outros substrate fixes (ladesign MCP fix, boot_check, laos-infra.ts) são mudanças de código já aplicadas e independentes — o ADR é documentação histórica, não funcional.

**Comando:**
```bash
git -C F:/Projetos/Laos rm projects/_meta/adr/ADR-014-substrate-recovery-2026-06-24.md
```

**Verificação:**
```bash
ls F:/Projetos/Laos/projects/_meta/adr/ADR-014-substrate-recovery-2026-06-24.md  # deve falhar
```

### Step 3.10 — Deletar artifacts/wdl remnants

**Ação:** Deletar os artifacts do WDL do refactor abortado.

**Comandos:**
```bash
git -C F:/Projetos/Laos rm -r artifacts/wdl/lacareerops-refactor-001/
git -C F:/Projetos/Laos rm artifacts/wdl/career-ops-capability/bypass-manifest.yaml
# Se o diretório career-ops-capability ficar vazio:
rmdir F:/Projetos/Laos/artifacts/wdl/career-ops-capability/  # ou git rm -r
```

**Verificação:**
```bash
ls F:/Projetos/Laos/artifacts/wdl/lacareerops-refactor-001/  # deve falhar
ls F:/Projetos/Laos/artifacts/wdl/career-ops-capability/  # deve falhar
```

### Step 3.11 — Deletar knowledge/handoff-lacareerops.md

**Ação:** Deletar o arquivo de handoff boundaries do lacareerops.

**Comando:**
```bash
git -C F:/Projetos/Laos rm knowledge/handoff-lacareerops.md
```

**Verificação:**
```bash
ls F:/Projetos/Laos/knowledge/handoff-lacareerops.md  # deve falhar
```

### Step 3.12 — Deletar capability-evolution/lacareerops.md

**Ação:** Deletar o tracking file de evolution do lacareerops.

**Comando:**
```bash
git -C F:/Projetos/Laos rm projects/_meta/capability-evolution/lacareerops.md
```

**Verificação:**
```bash
ls F:/Projetos/Laos/projects/_meta/capability-evolution/lacareerops.md  # deve falhar
```

### Step 3.13 — Deletar clone legado F:/Projetos/lacareerops/

**Ação:** Deletar o clone local do fork legado ADR-003 (server.py não funcional, sem commits locais úteis).

**Comando:**
```bash
Remove-Item -Recurse -Force F:/Projetos/lacareerops/
# OU
git -C F:/Projetos/lacareerops remote remove origin 2>$null; Remove-Item -Recurse -Force F:/Projetos/lacareerops/
```

**Atenção:** Este é um repo separado (não é parte do LAOS). Verificar antes de deletar:
```bash
# Confirmar que não há commits locais não pushed
git -C F:/Projetos/lacareerops log origin/main..HEAD --oneline
# Se retornar vazio, seguro deletar. Se houver commits, pausar e reportar.
```

**Verificação:**
```bash
ls F:/Projetos/lacareerops/  # deve falhar
```

### Step 3.14 — Criar ADR-015

**Ação:** Criar o ADR que documenta a nova arquitetura e superseeds ADR-003 e ADR-013.

**Conteúdo do arquivo** `F:/Projetos/Laos/projects/_meta/adr/ADR-015-career-ops-external-skill-source.md`:

```markdown
# ADR-015: career-ops as External Skill Source

**Status:** accepted (pending LACOUNCIL supermaioria ratification)
**Date:** 2026-07-01
**Decisor:** LACOUNCIL (supermaioria, ≥ 3/4 SIM)
**Proposal:** <proposal_id da Fase 0>
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
3. **ADR-014** (2026-06-24): Substrate recovery inline. Deletado — referências a lacareerops tornavam o ADR obsoleto; os 4 outros substrate fixes são mudanças de código independentes.

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
- Entrada MCP `lacareerops` no `opencode.jsonc` (linhas 78-93)
- Permissão `E:/projects/lacareerops-hub/**` no `opencode.jsonc` (linha 270)
- Entrada `lacareerops` no `registry/capabilities.yaml` (linhas 151-175)
- Bloco de comentário deprecated no `registry/needs-to-capabilities.yaml` (linhas 69-77)
- `projects/_meta/adr/ADR-014-substrate-recovery-2026-06-24.md` — ADR histórico deletado; referências a lacareerops o tornavam obsoleto
- `AGENTS.md` — referências a lacareerops removidas (ver Step 3.15)

---

## Referências

- LACOUNCIL proposal: <proposal_id da Fase 0>
- LACOUNCIL deprecation: e65617ec-5b61-4d03-b6e8-365a84ca8286 (4/4 SIM, 2026-07-01)
- Upstream: https://github.com/santifer/career-ops
- WDL verdict: artifacts/wdl/career-ops-skill-source-001/verdict.yaml
- ADR-014 (substrate recovery, deletado)
- Skill: .opencode/skills/career-ops/SKILL.md
- Knowledge: knowledge/external-tools.md
```

**Verificação:**
```bash
ls F:/Projetos/Laos/projects/_meta/adr/ADR-015-career-ops-external-skill-source.md
```

### Step 3.15 — Atualizar AGENTS.md

**Ação:** Procurar e remover quaisquer referências a lacareerops no AGENTS.md.

**Comando de busca:**
```bash
grep -n "lacareerops\|lacareer-ops\|career-ops" F:/Projetos/Laos/AGENTS.md
```

**Para cada ocorrência encontrada:**
- Se for na tabela de capabilities: a entrada já foi removida (não deve aparecer)
- Se for em texto corrido: editar para remover a referência ou substituir por
  referência ao ADR-015 / knowledge/external-tools.md
- Se for em Hard Rules: verificar se a regra ainda faz sentido sem lacareerops;
  se sim, editar; se não, remover

**Verificação:**
```bash
grep -c "lacareerops" F:/Projetos/Laos/AGENTS.md
# Idealmente 0. Se houver referências históricas que fazem sentido manter,
# documentar o motivo.
```

### Step 3.16 — Busca final por resíduos

**Ação:** Busca exaustiva por qualquer referência restante a lacareerops em todo o repo LAOS.

**Comando:**
```bash
grep -r "lacareerops" F:/Projetos/Laos/ --include="*.md" --include="*.yaml" --include="*.yml" --include="*.jsonc" --include="*.json" --include="*.py" --include="*.ts" -l
```

**Para cada arquivo encontrado:**
- Se for um arquivo que deveria ter sido deletado: confirmar que foi deletado
- Se for um arquivo que ainda referencia lacareerops: editar para remover
- **Exceção permitida:** o próprio ADR-015 e knowledge/external-tools.md podem
  mencionar lacareerops no contexto histórico (explicando o que foi substituído)

**Meta final:** zero referências funcionais a lacareerops. Referências históricas
apenas em ADR-015 e knowledge/external-tools.md.

---

## Fase 4 — Validação (delivery-reviewer)

**Quem executa:** orchestrator despacha delivery-reviewer (com verdict READY da Fase 2)
**Verificação:** G4 BASIC sign-off

### Step 4.1 — Preflight check mecânico

Antes de despachar o delivery-reviewer, rodar:

```bash
uv run python scripts/preflight_check.py projects/_meta/career-ops-skill-source
```

Se exit ≠ 0, corrigir os findings antes de prosseguir.

### Step 4.2 — Boot check

```bash
uv run python scripts/subagent_boot_check.py delivery-reviewer --project-name career-ops-skill-source
```

Se exit ≠ 0, corrigir antes de despachar.

### Step 4.3 — Despachar delivery-reviewer

- `subagent_type: "delivery-reviewer"`
- `description: "G4 sign-off career-ops"`
- Brief (curto, 5-15 linhas):
  ```
  Projeto: career-ops-skill-source (meta-projeto estrutural)
  Proposal ID: <proposal_id>
  Verdict WDL: artifacts/wdl/career-ops-skill-source-001/verdict.yaml (state: READY, verified_by: workflow-decomposer)

  Validar a implementação da Fase 3 contra knowledge/padroes-entrega.md.
  Foco: cleanup completo (nenhum resíduo de lacareerops), skill criada,
  knowledge/external-tools.md criado, ADR-015 publicado, ADR-014 editado,
  ADR-003 e ADR-013 deletados, opencode.jsonc limpo, capabilities.yaml limpo,
  needs-to-capabilities.yaml limpo.

  Output: artifacts/review/checklist.md com G4 sign-off (PASS ou FAIL com P0 violations).
  ```

### Step 4.4 — Se P0 violation: auto-retry (TD-2)

Se delivery-reviewer retornar P0 violations:
1. Ler os findings
2. Re-despachar o subagente que falhou com os findings anexados
3. Cap em 2 retries
4. Se após 2 retries ainda falhar: parar, reportar ao usuário

**Verificação Fase 4:**
- `artifacts/review/checklist.md` existe com G4 = PASS
- Nenhum P0 violation pendente

---

## Fase 5 — Git Push (Regime A)

**Quem executa:** orchestrator (direto)
**Regime:** A (mudança estrutural aprovada pelo Conselho + validada pelo delivery-reviewer → push obrigatório na mesma sessão)

### Step 5.1 — Stage all changes

```bash
git -C F:/Projetos/Laos add -A
```

### Step 5.2 — Verificar o diff

```bash
git -C F:/Projetos/Laos status
git -C F:/Projetos/Laos diff --cached --stat
```

**Confirmar que o diff inclui:**
- Novos arquivos: `.opencode/skills/career-ops/SKILL.md`, `knowledge/external-tools.md`, `projects/_meta/adr/ADR-015-career-ops-external-skill-source.md`, `projects/_meta/career-ops-skill-source/plan.md`
- Deletados: `projects/_meta/adr/ADR-003-lacareerops-creation.md`, `projects/_meta/adr/ADR-013-lacareerops-submodule.md`, `projects/_meta/adr/ADR-014-substrate-recovery-2026-06-24.md`, `knowledge/handoff-lacareerops.md`, `projects/_meta/capability-evolution/lacareerops.md`, meta-projetos lacareerops/, artifacts/wdl remnants
- Editados: `.opencode/opencode.jsonc`, `registry/capabilities.yaml`, `registry/needs-to-capabilities.yaml`, `AGENTS.md`

### Step 5.3 — Commit

```bash
git -C F:/Projetos/Laos commit -m "feat(career-ops): external skill source architecture (ADR-015)

Replace deprecated lacareerops MCP wrapper (3 failed attempts: ADR-003,
ADR-013, ADR-014) with direct clone of upstream santifer/career-ops as
external skill source. career-ops is a CLI-agnostic skill system, not
MCP-wrappable. Anti-drift via .opencode/skills/career-ops/SKILL.md.

LACOUNCIL proposal <proposal_id> (supermaioria, >= 3/4 SIM).
Delivery-reviewer G4 sign-off: PASS.
Regime A push (structural change, mandatory same-session).

Deleted: ADR-003, ADR-013, ADR-014.
New: ADR-015, skill, knowledge/external-tools.md.
Cleanup: all lacareerops remnants removed."
```

### Step 5.4 — Push

```bash
git -C F:/Projetos/Laos push origin main
```

**Verificação Fase 5:**
```bash
git -C F:/Projetos/Laos log --oneline -3
# Deve mostrar o commit no topo
git -C F:/Projetos/Laos status
# Deve mostrar "Your branch is up to date with 'origin/main'"
```

---

## Fase 6 — Cleanup GitHub remoto (mandatório)

**Ação:** Deletar os repos GitHub privados legados. Decisão do usuário: deletar (não arquivar).

### Repos a deletar

1. `github.com/laurentaf/career-ops` — fork privado ADR-003 (sem commits locais úteis além do mirror)
2. `github.com/laurentaf/lacareerops-hub` — hub ADR-013 (nunca funcional)
3. `github.com/laurentaf/lacareerops` — repo do wrapper ADR-003 (clone local deletado na Fase 3)

### Como deletar no GitHub

Usar MCP `github` tool para deletar cada repo:

1. Chamar `github.api` (ou ferramenta equivalente) para:
   ```bash
   # Opção via GitHub API (recomendada):
   # DELETE /repos/{owner}/{repo}
   # Owner: laurentaf
   # Repos: career-ops, lacareerops-hub, lacareerops
   ```
2. Confirmar que cada repo foi deletado:
   ```bash
   # Verificar que o repo não existe mais
   # (tentar acessar e receber 404)
   ```

**Atenção:** Deletar um repo GitHub é **irreversível**. Confirmar com o usuário imediatamente antes de executar cada deleção.

**Verificação Fase 6:**
- `curl https://api.github.com/repos/laurentaf/career-ops` retorna 404
- `curl https://api.github.com/repos/laurentaf/lacareerops-hub` retorna 404
- `curl https://api.github.com/repos/laurentaf/lacareerops` retorna 404

---

## Resumo de verificação final (após todas as fases)

```bash
# 1. Clone do career-ops existe
ls F:/Projetos/career-ops/.opencode/skills/

# 2. Skill do LAOS existe
ls F:/Projetos/Laos/.opencode/skills/career-ops/SKILL.md

# 3. Knowledge entry existe
ls F:/Projetos/Laos/knowledge/external-tools.md

# 4. ADR-015 existe
ls F:/Projetos/Laos/projects/_meta/adr/ADR-015-career-ops-external-skill-source.md

# 5. Zero resíduos de lacareerops (com exceções permitidas)
grep -r "lacareerops" F:/Projetos/Laos/ --include="*.md" --include="*.yaml" --include="*.jsonc" -l
# Deve retornar apenas: ADR-015, knowledge/external-tools.md
# (estes 2 arquivos mencionam lacareerops no contexto histórico)

# 6. Clone legado deletado
ls F:/Projetos/lacareerops/  # deve falhar

# 7. Git pushed
git -C F:/Projetos/Laos log --oneline -1
# Deve mostrar o commit da Fase 5
```

---

## Notas para o executor (DeepSeek V4 Flash)

1. **Ordem das fases é obrigatória.** Não pular fases. Não executar Fase 3 sem Fase 1 aprovada e Fase 2 READY.
2. **Cada edit deve ser precedido por um `read`** do arquivo alvo. O `edit` tool exige que o arquivo tenha sido lido antes.
3. **Se um `edit` falhar com "oldString not found"**, ler o arquivo novamente e copiar o oldString exatamente como aparece (preservando indentação, espaços, quebras de linha).
4. **Se um `edit` falhar com "Found multiple matches"**, adicionar mais linhas de contexto ao oldString para tornar a match única.
5. **Verificar após cada step.** Não acumular mudanças sem verificar.
6. **Se algo quebrar midway**, parar e reportar ao orchestrator (GLM 5.2). Não improvisar workaround.
7. **O plano é detalhado mas não exaustivo em edge cases.** Se aparecer uma situação não prevista, parar e reportar.
8. **Não modificar arquivos fora do escopo listado.** Paths permitidos para escrita: `projects/_meta/career-ops-skill-source/`, `projects/_meta/adr/`, `registry/`, `knowledge/`, `.opencode/`, `AGENTS.md`. Nenhum outro.
