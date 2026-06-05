# registry/spec-templates/

**Status:** Vigente (origem: proposta LACOUNCIL `f9b636fc-5ca9-4860-94ca-3a6b43c6862c`,
unanimidade 4/4, 2026-06-05)

**Cross-references:**
- `knowledge/sdd-principles.md` — princípio fundacional "POC ≠ zero-shot",
  matriz per-file §2, política de imutabilidade §6
- `knowledge/padroes-entrega.md` — checklist P0 §"Estrutura do projeto"
- `scripts/subagent_boot_check.py` — 6ª dimensão `child-repo-skeleton`
  (sub-check `skeleton`) consome estes templates

---

## O que é

Templates canônicos do **SDD scaffold** (Missão 0) de todo projeto LAOS.
São cópias literais dos templates da capability **LATADE** (que inventou
e mantém o template upstream). O orquestrador da LAOS lê estes
arquivos para criar a estrutura `spec/`, `contract.md`, `README.md` no
child repo do projeto no Stage 0 do workflow.

**Dois sub-árvores:**

| Sub-árvore | Proveniência | Função |
|---|---|---|
| `spec/` | `LATADE/spec/` (cópia literal) | Estrutura do SDD — constitution, todo, ADR, HARNESS, 1ª spec |
| `opencode-templates/specs/` | `LATADE/.opencode/templates/specs/` (cópia literal) | Templates de segundo nível — TASKS, SPEC, GSD, PLAN, ADR, HARNESS |

## Proveniência (data da cópia)

- **Data:** 2026-06-05
- **Origem upstream:** `LATADE` (repo local `E:/projects/latade/`)
- **Autor da cópia:** `capability-architect` (subagente, proposta
  LACOUNCIL `2f42afe6-71d5-4ef8-a88a-1339d72ec501` ativa desde
  2026-06-04 BASIC)
- **Proposta autorizadora:** `f9b636fc-5ca9-4860-94ca-3a6b43c6862c`
  (unanimidade 4/4)

### Arquivos copiados (11 total)

**De `LATADE/spec/`:**

1. `constitution.md` → `spec/constitution.md`
2. `todo.md` → `spec/todo.md`
3. `adr/_template.md` → `spec/adr/_template.md` *(stub-by-design)*
4. `harness/_template.md` → `spec/harness/_template.md` *(stub-by-design)*
5. `specs/001-example/spec.md` → `spec/specs/000-bootstrap/spec.md`
   *(renomeado de "001-example" para "000-bootstrap" para sinalizar
   que é a spec de bootstrap do projeto, não uma feature)*

**De `LATADE/.opencode/templates/specs/`:**

6. `TASKS_TEMPLATE.md` → `opencode-templates/specs/TASKS_TEMPLATE.md`
7. `SPEC_TEMPLATE.md` → `opencode-templates/specs/SPEC_TEMPLATE.md`
8. `GSD_TEMPLATE.md` → `opencode-templates/specs/GSD_TEMPLATE.md`
9. `PLAN_TEMPLATE.md` → `opencode-templates/specs/PLAN_TEMPLATE.md`
10. `ADR_TEMPLATE.md` → `opencode-templates/specs/ADR_TEMPLATE.md`
11. `HARNESS_TEMPLATE.md` → `opencode-templates/specs/HARNESS_TEMPLATE.md`

Os 11 arquivos são cópias literais. Qualquer divergência entre o
conteúdo daqui e o conteúdo do LATADE upstream indica drift não
sincronizado (não intencional; o sync só é válido via nova proposta
LACOUNCIL — ver §abaixo).

## Política de drift (NÃO sincronizar automaticamente)

**Regra:** Os templates em `registry/spec-templates/` **não sincronizam
automaticamente** com o LATADE upstream. Cada nova sincronização é
uma decisão deliberada que exige **nova proposta LACOUNCIL** com
estratégia **unanimidade** (analogia a fundamentos — o scaffold é
fundacional).

**Razão:** LATADE pode evoluir seus templates (e vai). O LAOS não
quer puxar mudanças acidentalmente — cada sync é uma decisão
deliberada do Conselho, com:
- Análise do diff (o que mudou no LATADE?)
- Decisão do que adotar / descartar / adaptar para o LAOS
- Atualização da matriz per-file em `knowledge/sdd-principles.md` §2
  (chars mínimos e cabeçalhos podem mudar)
- Atualização do `subagent_boot_check.py` 6ª dimensão
  (sub-checks `skeleton` e `first-real-adr`)

**Sincronização manual permitida apenas em:**
- Hotfix de bug no template (quebra de parsing, header faltando) —
  ainda exige LACOUNCIL, mas com `estrategia: maioria` se unânime
  parecer overkill.

## Política de imutabilidade (no projeto, não no registry)

Uma vez que o orchestrator copia um template deste registry para
dentro do child repo do projeto (e.g., `projeto/spec/constitution.md`),
esse arquivo **cópia** deixa de ser stub e vira editável (com
conteúdo real). Mas o template **original** aqui no registry
permanece imutável: subagentes de projeto **não devem** editar
`registry/spec-templates/`.

**Subagentes de projeto** que precisarem modificar um template:
- Errado: editar `registry/spec-templates/spec/constitution.md`
  diretamente.
- Certo: copiar o template para o child repo (`child/spec/constitution.md`)
  e editar a cópia.

A separação de poderes é a mesma da R5 do capability-architect
(`projects/_meta/capability-architect/binding-conditions.md`):
capability-architect tem autoridade sobre `registry/`; subagentes
de projeto só mexem em `projects/<name>/`.

## Como usar (do lado do orchestrator)

Pseudo-fluxo do Stage 0 (Missão 0):

```python
# orchestrator's Stage 0 dispatcher (informational)
src = LAOS_ROOT / "registry" / "spec-templates" / "spec" / "todo.md"
dst = child_repo / "spec" / "todo.md"
dst.parent.mkdir(parents=True, exist_ok=True)
dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
# ... repete para os 8 fixos + 1 condicional
# Em seguida, roda o gate: subagent_boot_check.py 6ª dimensao
```

Para projetos com `needs: dashboard|design`, copiar também
`spec/design-direction.md` (criado a partir de stub mínimo —
gate valida `>= 300 chars`).

Para projetos com Constitution **adaptada** (não cópia literal),
o orchestrator pode injetar o artigo I do projeto
(e.g., "Missão 0 é obrigatória") no topo do `constitution.md`
copiado, **antes** de escrever no child repo. Isso ainda respeita
a imutabilidade do registry (o original fica intacto; a cópia
no child repo é do projeto).

## Auditoria de drift (verificação periódica)

Para detectar drift não intencional, o orchestrator pode rodar
periodicamente:

```bash
diff -r E:/projects/latade/spec/ E:/projects/LAOS/registry/spec-templates/spec/ \
  --brief --ignore-trailing-cr
diff -r E:/projects/latade/.opencode/templates/specs/ \
  E:/projects/LAOS/registry/spec-templates/opencode-templates/specs/ \
  --brief --ignore-trailing-cr
```

Se houver diff, significa que o LATADE upstream mudou e o LAOS
**não sincronizou** (intencional ou esquecido). Reportar via
LACOUNCIL para deliberar sobre a próxima sync.
