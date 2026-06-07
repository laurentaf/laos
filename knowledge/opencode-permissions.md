# Permissões de subagente no opencode

Convenção transversal sobre como o opencode materializa a autonomia
dos subagentes em acesso real a filesystem. Estende a proposta
LACOUNCIL `518b82d5` (charter-autonomy) com a 4ª camada das 4 que
compõem a autonomia.

Pré-requisitos de leitura: nenhum. Este doc é a fonte canônica
sobre `external_directory` em LAOS.

---

## 1. Modelo de 4 camadas (de 518b82d5 + 4a9f07c3)

A autonomia de um subagente é a composição de 4 camadas
**independentes e complementares**. Cada uma responde a uma pergunta
diferente; falha em uma derruba a autonomia inteira.

| # | Camada | Pergunta que responde | Onde vive |
|---|--------|----------------------|-----------|
| 1 | **Charter persistente** | "Quem sou eu? Qual é meu escopo?" | `.opencode/agent/<name>.md` (corpo do prompt) |
| 2 | **Tool readiness** | "Tenho o que preciso para trabalhar?" | `scripts/subagent_boot_check.py` (venv, daemon, MCP, paths, env) |
| 3 | **Task brief curto** | "O que fazer neste dispatch específico?" | Brief injetado pelo orchestrator no `task` tool |
| 4 | **Runtime permission** | "A quais paths de filesystem posso tocar sem confirmação?" | `permission.external_directory` no frontmatter do agent file + `permission.external_directory` no `opencode.jsonc` |

A camada 4 (esta convenção) é a única que **materializa** a
autonomia das camadas 1–3 em bytes no disco. Sem ela, o subagente
"sabe" o que fazer (charter) e "tem" as ferramentas (boot check),
mas é interrompido por um prompt de "Permissão necessária" toda vez
que toca um path legítimo. É o failure mode que a proposta
`4a9f07c3` fecha.

Analogia: o subagente é o recebedor de mercadoria de um depósito.
- Camada 1: o recibo de função (charter) — "recebo LATADE e LADESIGN"
- Camada 2: a checklist do turno (boot) — "tenho carrinho, leitor de código, balança"
- Camada 3: a nota fiscal do lote de hoje (brief) — "receber 12 caixas do projeto X"
- Camada 4: a autorização de acesso ao portão (external_directory) — "posso entrar no portão 3 e 5, não no 7"

Sem a camada 4, o recebedor fica parado no portão pedindo senha
para cada carrinho, mesmo tendo recibo + checklist + nota.

---

## 2. Semântica de `external_directory`

### 2.1. Per-agent override top-level

Por design do opencode, o `permission:` no frontmatter de um
subagente **sobrescreve inteiramente** o `permission:` de cima
(top-level, no `opencode.jsonc`). O orchestrator pode ter
`external_directory` com 50 paths; se o subagente declara o próprio
`external_directory` com 3, são os 3 que valem para ele.

**Consequência:** não dá pra "herdar" regras do orchestrator para o
subagente. Cada subagente que escreve em filesystem precisa
**declarar** seu próprio allowlist.

### 2.2. Glob semantics

O opencode usa glob estilo fnmatch (não gitignore). As implicações
práticas:

- `**` casa múltiplos segmentos de path, inclusive zero.
- `*` casa um segmento sem `/`.
- A primeira regra que casa vence (não é union).
- `"*": "ask"` é o **default**; entries específicas depois dele
  sobrescrevem por match.

Exemplo (orchestrator):

```jsonc
"external_directory": {
  "*": "ask",                  // qualquer path não listado → pergunta
  "../latade/**": "allow",     // repo LATADE → libera
  "../lan8n/**": "allow",      // repo LAN8N → libera
  "../_commomdata/**": "allow" // dados cross-project → libera
}
```

### 2.3. Dotfile caveat (o ponto sensível)

Globs do tipo `**` em algumas implementações **não casam** paths
que começam com `.` (dotfile convention do Unix). No Windows isso
é menos óbvio, mas diretórios como `.od/`, `.venv/`, `.git/` são
**dotfiles pela convenção** e podem ser silenciosamente excluídos
de um `**` se a implementação do glob for literalista.

**Implicação para LAOS:** o daemon LADESIGN grava em
`E:\projects\ladesign\.od\projects\*` durante `start_run`. Um
allowlist `../ladesign/**` deveria cobrir `.od/`, mas a
implementação do glob no opencode runtime **pode** não casar o
`.od/` por causa do dotfile caveat. Por isso:

- A allowlist **explicita** paths com dot-directory: `../ladesign/.od/**`
  em vez de confiar em `../ladesign/**` casar tudo.
- `scripts/subagent_boot_check.py` faz um smoke-test real de
  write/read/delete em um probe path com dot-directory para validar
  que o OS não bloqueia o acesso (e documenta a limitação: o glob
  semantics definitivo é testado em dispatch real, ver proposta
  `4a9f07c3` critério de aceitação #6).

---

## 3. Tabela de paths conhecidos por subagente

Estado em 2026-06-07 (atualizado por Hard Rule #10, AGENTS.md).
Todos os 7 subagentes (orchestrator, data-architect,
dashboard-designer, automation-engineer, delivery-reviewer,
capability-architect, workflow-decomposer) compartilham
`E:/projects/**` como allowlist comum (regra Hard #10).
A entrada explícita antiga `E:/projects/_commomdata/**` foi
subsumida pelo umbrella `E:/projects/**` (qualquer path que case
inclui `_commomdata`).

| Subagente | Paths de leitura (charter) | Paths de escrita (charter) | Bash `git *` | Dot-directory no escopo? |
|-----------|----------------------------|----------------------------|--------------|--------------------------|
| `data-architect` | `../latade/**`, `E:/projects/**` | `projects/<name>/artifacts/{data,pipeline,dq}/` (workspace) | allow | não |
| `dashboard-designer` | `../ladesign/**`, `E:/projects/**` | `projects/<name>/artifacts/{design,deck}/` (workspace) + `../ladesign/.od/**` (daemon storage) | allow | **sim — `.od/`** |
| `automation-engineer` | `../lan8n/**`, `../n8n/**`, `E:/projects/**` | `projects/<name>/artifacts/automation/` (workspace) | allow | não |
| `delivery-reviewer` | `E:/projects/**` (read-only; `edit: deny` no frontmatter) | (nenhum) | deny (bash: deny) | não |
| `capability-architect` | `E:/projects/**`, `../<capability>/**` para cada capability conhecida | `projects/_meta/**` (workspace) + capability repos existentes (latade, lan8n, lacouncil, laengine, laecon, ladesign) | allow | não |
| `orchestrator` | já coberto em `opencode.jsonc` (top-level) | já coberto em `opencode.jsonc` (top-level) | allow | n/a (config em JSONC) |
| `workflow-decomposer` | `../lacouncil/**`, `E:/projects/**` | `artifacts/wdl/<plan-id>/` (workspace) | allow | não |

**Convenção aplicada:** `E:/projects/**` é o "leio/escrevo tudo no
diretório de projetos" — para contexto de outros projetos, capability
repos, e cross-project grounding data (`_commomdata`).
`projects/<name>/artifacts/<subclass>/` é o **escritório oficial**
e não precisa de `external_directory` porque está dentro do
workspace (LAOS).

**Bash `git *` allow** (Hard Rule #10, 2026-06-07): todos os
subagentes com `bash: allow` no frontmatter recebem `git *` no
allowlist. `delivery-reviewer` mantém `bash: deny` (read-only por
design). `rm -rf *` continua denylisted em todos.

---

## 4. Regra dos 2 pressupostos do usuário

> "Se sabe o que faz, onde, como e seus limites → faz; se não →
> não faz."

Codificada em duas camadas:

1. **`external_directory` allowlist** (config): define o **onde** o
   subagente pode tocar sem perguntar. O "onde" carrega o "limite"
   implícito.
2. **Charter do subagente** (escopo semântico): define o **o que** o
   subagente faz. Combinado com o allowlist, o "se sabe o que faz
   e onde" fica materializado.

Em dispatch: o subagente que tem um path in-charter (coberto pelo
seu allowlist) deve **agir** sem prompt. O subagente que tem um
path out-of-charter (não coberto) deve **parar e reportar** — é
gap de config, não decisão de runtime.

**Por que isso importa:** um subagente que pede permissão para
**toda** operação está externalizando para o humano uma decisão
que pode ser tomada por config. Isso é anti-pattern (próxima
seção).

---

## 5. Anti-pattern: "ask" genérico como default

**Sintoma:** `external_directory: { "*": "ask" }` sem entries
específicas.

**Por que é ruim:** força o humano a decidir, em runtime, sobre
acesso a paths que o charter do subagente já autoriza. Toda vez
que o `data-architect` lê um CSV em `E:\projects\previsao-concursos\data\`,
o humano recebe "Permissão necessária". O humano responde "sim"
mecanicamente → degrada para 100% confirmation, que é o oposto de
autonomia calibrada.

**Como corrigir:** toda allowlist `"*": "ask"` deve ter
**acompanhamento** de paths específicos `allow` que cubram o escopo
declarado no charter. Se a allowlist cresce para mais de ~5
entries por subagente, é sinal de que o charter está largo demais
(separar escopo) ou de que o subagente está sendo usado fora do
charter (re-routing via orchestrator).

**Quando `"*": "ask"` É correto:** quando o subagente é o
**orchestrator** (default-agent), que tem escopo amplo e merece
confirmação humana para paths novos. Ou quando o subagente está
em modo de auditoria e queremos aprovação explícita.

---

## 6. Smoke test (Check 6 do `subagent_boot_check.py`)

`scripts/subagent_boot_check.py` ganhou o Check 6 (a partir da
proposta `4a9f07c3`):

1. **Parse de frontmatter** — lê `.opencode/agent/<name>.md`,
   extrai o bloco `permission.external_directory` via PyYAML.
2. **Cobertura do charter** — compara os paths da allowlist
   extraída com a lista canônica em
   `SUBAGENT_CHARTERS[name].external_directory_required_paths`.
   Se algum path do charter não estiver coberto → BLOCKED.
3. **Smoke-test de dotfile** — se o charter declara algum path
   com dot-directory (ex.: `../ladesign/.od/**`), o boot check
   tenta `create → write → read → delete` um arquivo probe
   naquele path para validar acesso do OS. Reporta PASS/FAIL
   com o erro literal se houver.

**Limitação conhecida:** o smoke-test valida acesso do OS, não
semântica de glob do opencode runtime. O teste definitivo do glob
acontece em dispatch real (proposta `4a9f07c3` critério de
aceitação #6 e #7). O boot check captura a maior parte dos
failure modes em config-time; o resto é catch em runtime.

---

## 7. Como evoluir a allowlist

Quando um path novo precisa ser acessível:

1. **Verifique que o path é in-charter.** Releia o `.opencode/agent/<name>.md`
   do subagente. Se o path não bate com o escopo declarado, pare —
   é gap de charter, não gap de config.
2. **Adicione a entry no `permission.external_directory`** do
   subagent file. Se for workspace (`projects/<name>/...`), nada
   precisa ser feito (já é permitido). Se for externo, adicione.
3. **Rode `subagent_boot_check.py`** para confirmar cobertura.
4. **Se o path tem dot-directory** (ex.: nova pasta `.cache/`),
   adicione o smoke-test target na função
   `smoke_test_external_directory` do boot check.
5. **Documente** o novo path na tabela §3 deste arquivo.

Quando uma entry é removida (path deixa de ser necessário):

1. Remova do frontmatter do subagent.
2. Mantenha a entrada em `SUBAGENT_CHARTERS[<name>].external_directory_required_paths`
   se a remoção é temporária; remova se a remoção é definitiva.
3. Rode boot check — se falhar, é porque algum path charter ainda
   depende dessa entry.

---

## 8. Como este doc evolui

Mudanças neste arquivo são **mudança de convenção transversal** —
exigem nova proposta LACOUNCIL com estratégia **maioria** (regra
de `knowledge/`, ver AGENTS.md §"Hard rules"). Mudanças em
`SUBAGENT_CHARTERS` no `subagent_boot_check.py` são ajuste
operacional, não precisam de proposta, mas devem ser revisadas pelo
delivery-reviewer (P0 walk do item P0-9 do `padroes-entrega.md`).
