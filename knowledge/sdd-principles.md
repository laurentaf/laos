# SDD Principles — Spec-Driven Development no LAOS

**Status:** vigente (origem: proposta LACOUNCIL `f9b636fc-5ca9-4860-94ca-3a6b43c6862c`,
unanimidade 4/4, 2026-06-05)

**Cross-references:**
- `knowledge/padroes-entrega.md` — checklist P0/P1/P2 que operacionaliza esta página
- `registry/spec-templates/` — templates canônicos (proveniência LATADE, cópias literais)
- `LATADE/spec/` — fonte de verdade upstream dos templates
- `LATADE/.opencode/templates/specs/` — templates LATADE de segundo nível (PLAN, TASKS, GSD, ADR, HARNESS)

---

## 1. Princípio fundador: POC ≠ zero-shot

> **POC ≠ zero-shot.** POC é exploração estruturada com scaffold mínimo;
> zero-shot é geração de saída sem rastro. Toda POC LAOS produz o
> scaffold da Missão 0. O resto é opcional até o 1º estágio decisório.

Isto vira **regra operacional** (Missão 0 do `padroes-entrega.md`):
qualquer projeto LAOS, inclusive POCs com `external_delivery: false`,
produz o esqueleto SDD antes de qualquer artefato técnico. A distinção
é:

| Modo | Saída | Rastro | Quando |
|---|---|---|---|
| **Zero-shot** | artefato cru | nenhum | proibido no LAOS |
| **POC estruturada (Missão 0)** | scaffold mínimo + exploração | 8 fixos + 1 condicional | default em projetos LAOS |
| **Produção** | scaffold + estágios completos | scaffold + todos os artefatos do workflow | após 1º estágio decisório |

A operacionalização está em duas camadas:

1. **Conceitual (este arquivo):** "POC é exploração com scaffold"
2. **Mecânica (`subagent_boot_check.py` 6ª dimensão):** sub-check `skeleton`
   valida a matriz per-file #2 abaixo. Falha → exit 1 com mensagem
   acionável. Gate objetivo, não gate subjetivo.

---

## 2. Matriz per-file de "conteúdo mínimo aceito"

Referência canônica dos **9 arquivos** do SDD scaffold. Implementada
mecanicamente no `subagent_boot_check.py` 6ª dimensão, sub-check
`skeleton`. Proveniência: LATADE (cópia literal dos templates).

| # | Arquivo | Tamanho mín. | Seções obrigatórias | Aceita stub? |
|---|---|---:|---|---|
| 1 | `spec/constitution.md` | 400 chars | "Princípios" (≥3), "Scope", "Non-goals" (≥2) | não |
| 2 | `spec/todo.md` | 100 chars | ≥ 1 task `- [ ]` (1ª task = o próprio Stage 0) | não |
| 3 | `spec/adr/_template.md` | cópia literal do LATADE | n/a (é o template) | **sim — stub-por-design** |
| 4 | `spec/adr/README.md` | 80 chars | "ADR Index" + nota "vazio até 1º ADR real" | não |
| 5 | `spec/harness/_template.md` | cópia literal do LATADE | n/a (é o template) | **sim — stub-por-design** |
| 6 | `spec/specs/000-bootstrap/spec.md` | 400 chars | "Contexto", "Decisão inicial", "Critérios de pronto" | não |
| 7 | `contract.md` | 250 chars | espelha `project.yaml` em prosa | não |
| 8 | `README.md` (raiz do child repo) | 400 chars | "O que é", "Como rodar", "Onde está o quê" | não |
| 9 | `spec/design-direction.md` *(condicional)* | 300 chars | 1 parágrafo + 2-3 princípios macro | não |

**Condicionalidade do item 9:** o gate só exige `spec/design-direction.md`
quando `needs:` contém `dashboard` ou `design`. Para projetos sem essas
needs, o arquivo **não existe** e o gate não reclama (INFO-only).

**Stub-por-design (#3, #5):** `_template.md` do ADR e `_template.md` do
HARNESS são cópias literais do LATADE e **não precisam** de seção
obrigatória — eles **são** a seção. São aceitos como estão, sem
modificação (a proposta LACOUNCIL proíbe edição desses arquivos sem
nova votação).

**Comportamento do gate (sub-check `skeleton`):**

- Para cada arquivo da matriz, checa: (a) existência, (b) tamanho
  mínimo em chars, (c) presença dos cabeçalhos de seção
  obrigatórias (regex case-insensitive).
- Falha qualquer um → `BLOCKED:` com mensagem acionável, e.g.:
  `spec/todo.md tem 80 chars; precisa ≥ 100 e ≥ 1 task `- [ ]`.`
- Tamanhos são contados no `wc -m` do arquivo (não bytes).

---

## 3. Os 4 artefatos mínimos (resumo)

A matriz #2 lista 9 arquivos. Deles, **4** carregam a substância
mínima de uma POC estruturada:

1. **`spec/todo.md`** — task tracker; 1ª task = Missão 0. Stages
   seguintes adicionam tasks; a estrutura existe desde o kickoff.
2. **`spec/adr/`** — registro de decisões. Antes do 1º estágio
   decisório, só `_template.md` + `README.md` (índice vazio). Depois,
   ≥ 1 ADR real numerado a partir de `001-*.md`.
3. **`contract.md`** — espelha `project.yaml` em prosa (brief,
   needs, deliverables, capabilities_used, repo). É a "promessa
   do projeto" legível sem YAML.
4. **`spec/harness/_template.md`** — template de reconciliação
   numérica. Em POC sem decisão, fica como stub-por-design; em
   produção, é instanciado como `HARNESS-NNN-*.md`.

Os outros 5 (constitution, ADR README, 000-bootstrap/spec, README do
child repo, design-direction) são o **esqueleto de leitura e
orientação** — sem eles, o projeto é "artefato sem rosto".

---

## 4. Regra temporal: "Stage 0 produz estrutura; stages seguintes produzem conteúdo"

**Convenção canônica:**

- **Stage 0 (SDD Scaffold):** produz o esqueleto — 8 fixos + 1
  condicional — **todos com conteúdo mínimo da matriz #2**. Não
  produz decisão, não produz modelo, não produz ADR real.
- **Stage 1+ (Discovery / Data-Model / Design / Build / etc.):**
  produz o **conteúdo**. A primeira decisão de um desses estágios
  (data-model, design ou build — o que vier primeiro) **gera o
  gatilho temporal** do ADR-mínimo-1.
- **Antes do gatilho:** `_template.md` + `README.md` em `spec/adr/`
  é aceito. Sub-check `first-real-adr` é INFO-only.
- **Depois do gatilho:** ≥ 1 ADR real `001-*.md` é obrigatório.
  Sub-check `first-real-adr` vira FAIL se ausente.

O gatilho é **detectado operacionalmente** pelo boot check
contando ADRs em `spec/adr/` (excluindo `_template.md` e
`README.md`): se count > 0, o 1º decisório já passou. TODO futuro:
campo explícito `current_stage` em `project.yaml` (hoje não existe;
o signal é o ADR existente).

---

## 5. Cross-reference LATADE `spec/`

LATADE é a capability que inventou e mantém o template canônico do
SDD. O esqueleto da Missão 0 é **derivado do LATADE**, com
adaptações:

- `spec/constitution.md` é uma **fundação cross-capability** do
  LAOS, não uma cópia da Constitution do LATADE. O Constitution do
  LATADE (9 Artigos sobre medallion/test-first/idempotência) é
  específico de data; o Constitution do LAOS é meta-estrutural.
- `spec/todo.md`, `spec/adr/_template.md`, `spec/harness/_template.md`
  são **cópias literais** do LATADE (templates imutáveis, ver
  §6).
- `spec/specs/000-bootstrap/spec.md` segue a estrutura do LATADE
  `spec/specs/001-example/spec.md` (1ª spec do projeto, usada como
  bootstrap).

**Convenção de drift (proposta LACOUNCIL):** os templates em
`registry/spec-templates/` **não sincronizam automaticamente** com
o LATADE upstream. Nova cópia = nova proposta LACOUNCIL. Razão:
LATADE pode evoluir seus templates, e o LAOS não quer puxar
mudanças acidentalmente — cada sync é uma decisão deliberada do
Conselho.

---

## 6. Política de imutabilidade

Os 4 arquivos marcados como **stub-por-design** (`spec/adr/_template.md`,
`spec/harness/_template.md`) e o 1 marcado como **template canônico**
(`spec/specs/000-bootstrap/spec.md` derivado de `001-example`)
**não são editáveis por subagentes de projeto**. Eles são
carregados verbatim de `registry/spec-templates/` (que por sua vez
é cópia literal de LATADE).

Se um operador precisar modificar um template:

1. Reporta ao orchestrator com o trecho a alterar.
2. Orchestrator decide se é específico do projeto (vira spec
   local, não template) ou se é evolução do template (vira
   proposta LACOUNCIL para regerar `registry/spec-templates/`).

Edição direta dos templates em `registry/spec-templates/` é
**violação estrutural** (mesmo nível de severidade que R2 — não
escrever artefatos de projeto).

---

## 7. Como adicionar um novo arquivo à matriz

Não é tarefa trivial. Adicionar um arquivo à matriz per-file #2
exige:

1. Identificar o gap em ≥ 2 projetos LAOS distintos.
2. Propor LACOUNCIL com `dominio: laos`, `estrategia: unanimidade`
   (analogia a fundamentos — o scaffold é fundacional).
3. Provar que o gate mecânico é determinístico (chars + regex de
   cabeçalho), não subjetivo.
4. Atualizar: `subagent_boot_check.py` 6ª dimensão, `workflows/*.yaml`
   (3 arquivos), `padroes-entrega.md` (seção "Estrutura do projeto"),
   este arquivo (matriz #2), `registry/spec-templates/README.md`
   (proveniência).

A barreira é proposital. A matriz cresce devagar; é mais fácil
manter coerência do que consertar drift.
