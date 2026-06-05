# ADR-008: SDD scaffold obrigatório em todo projeto LAOS — Missão 0

**Status:** accepted
**Date:** 2026-06-05
**Decisor:** LACOUNCIL (unanimidade, 4/4 SIM, 100%)
**Proposal:** `f9b636fc-5ca9-4860-94ca-3a6b43c6862c`
**Implementer:** capability-architect

---

## Contexto

Projetos LAOS de domínio chegavam ao `delivery-reviewer` com artefatos técnicos
sólidos mas sem o esqueleto SDD que o resto do sistema pressupõe. Causa-raiz
tripla:

1. **P1 em vez de P0** no `padroes-entrega.md` — scaffold era "desejável", não
   bloqueante. Projetos pulavam e ninguém barrava.
2. **Sem gate estrutural no `subagent_boot_check.py`** — o boot check validava
   venvs, MCPs, paths, env vars, mas nunca checava se o esqueleto SDD existia.
3. **Sem Stage 0 nos 3 workflows** — `dashboard-completo.yaml`, `etl-puro.yaml`,
   `apresentacao-executiva.yaml` iam direto do brainstorm para o estágio
   produtivo sem criar a estrutura mínima.

Princípio fundacional que vira regra: **POC ≠ zero-shot** (POC é exploração
estruturada com scaffold mínimo; zero-shot é geração de saída sem rastro).

### Histórico da proposta

- **v1** (`e6e9e063`, estrategia=maioria): draft abandonado.
- **v2** (`6bc77c47`, estrategia=unanimidade): **REJEITADA** 3-1. O
  `delivery-reviewer` vetou com 3 ambiguidades materiais e citou o precedente
  `203b8baa`. Os outros 3 votaram SIM mas cada um levantou 1-3 flags.
- **v3** (`f9b636fc`, esta): APROVADA 4/4 unanimidade. Endereça 7 ambiguidades
  com critérios operacionais.

---

## Decisão

Adotar a estrutura `spec/` da capability **LATADE** como template canônico do
SDD skeleton LAOS, e tornar sua criação **obrigatória** como **Missão 0**
(pós-brainstorm, pré-design) em **todo** projeto LAOS, inclusive POCs com
`external_delivery: false`.

### 8 arquivos fixos + 1 condicional

| Arquivo | Origem | Aceita stub? |
|---------|--------|-------------|
| `spec/constitution.md` | cópia LATADE | não |
| `spec/todo.md` | cópia LATADE | não |
| `spec/adr/_template.md` | cópia literal LATADE | sim (stub-por-design) |
| `spec/adr/README.md` | template LAOS | não |
| `spec/harness/_template.md` | cópia literal LATADE | sim (stub-por-design) |
| `spec/specs/000-bootstrap/spec.md` | cópia LATADE | não |
| `contract.md` | novo (espelha project.yaml) | não |
| `README.md` (raiz do child repo) | novo | não |
| `spec/design-direction.md` | **condicional** (só se needs ∋ dashboard\|design) | não |

### 7 ambiguidades fechadas na v3

1. **Matriz per-file** — chars mínimos + cabeçalhos obrigatórios = gate
   mecânico, não subjetivo. Implementado na 6ª dimensão do
   `subagent_boot_check.py` (sub-check `skeleton`).
2. **ADR-mínimo-1 com gatilho temporal** — exige ≥ 1 ADR real **após** o 1º
   estágio decisório; antes disso, `_template.md` + `README.md` bastam.
   Sub-check `first-real-adr` gated.
3. **`artifacts/review/checklist.md`** — reclassificado como output do
   `delivery-reviewer`, não P0 do projeto.
4. **Unificação de ADRs** — `artifacts/decisions/` morto; path único
   `spec/adr/NNN-<slug>.md`.
5. **Design direction como arquivo separado** — `spec/design-direction.md`
   condicional, não seção no `constitution.md`.
6. **Mapeamento spec/specs ↔ artifacts/data** — seção "Data dependencies"
   com link relativo; sem duplicação.
7. **Nome canônico do tracker** — `spec/todo.md` (alinhado ao LATADE).

### Retroativo

Aplicado **somente** quando o `delivery-reviewer` tocar um projeto existente
durante sign-off ou auditoria normal. Sem varredura ativa de projetos parados.

---

## Alternativas Consideradas

### A) Manter scaffold como P1 (status quo)

Rejeitado. Projetos continuavam chegando ao reviewer sem esqueleto. P1 =
"desejável" na prática = "ninguém faz".

### B) Gate subjetivo (reviewer avalia caso a caso)

Rejeitado. O `delivery-reviewer` vetou a v2 explicitamente por isso: gate
subjetivo vira teatro (o revisor sempre aprova porque não há critério
determinístico). A matriz per-file com chars + headers resolve.

### C) Scaffold completo (todos os arquivos com conteúdo final)

Rejeitado. Overkill para POCs. O scaffold é **mínimo** — conteúdo suficiente
para que o gate mecânico passe e o projeto tenha rastro, não para que o
constitution esteja 100% final.

---

## Consequências

### Positivas

- Todo projeto LAOS nasce com rastro estrutural (POC ≠ zero-shot).
- Gate mecânico (existência + chars + headers) elimina subjetividade.
- Templates são cópias literais do LATADE — operador copia, não inventa.
- ADR-mínimo-1 com gatilho temporal destrava POCs em discovery.
- Unificação de paths (`spec/adr/`) elimina confusão.

### Custos

- ~10–15min adicionais no kickoff (8 arquivos fixos + 1 condicional).
- Meta-audit skip patch necessário no `subagent_boot_check.py`: quando
  `project.yaml` não existe (meta-audits, ad-hoc reviews), a 7ª dimensão
  pula com INFO, não FAIL. Escopo estrito: ausência de `project.yaml` é
  o único trigger; projetos reais sempre têm `project.yaml`.

### Riscos

| Risco | Mitigação |
|-------|-----------|
| Sensação de burocracia para POCs | Matriz fixa + templates copy/paste reduzem campo aberto |
| 9º arquivo condicional parece overhead | Gate só ativa quando needs ∋ dashboard\|design |
| Meta-audit skip vira backdoor | Escopo estrito: só quando `project.yaml` ausente. Projetos reais sempre têm. |

---

## Implementação

### Arquivos criados/modificados (23 files, 2026-06-05)

**Knowledge (4)**
- `knowledge/sdd-principles.md` — novo (POC ≠ zero-shot + matriz per-file)
- `knowledge/padroes-entrega.md` — editado (P1→P0, gatilho temporal, reclassificação review/checklist, path único ADRs)
- `knowledge/stack-decisions.md` — editado (6ª dimensão boot check documentada)
- `knowledge/opencode-permissions.md` — novo (4-layer autonomy model)

**Workflows (3)**
- `workflows/dashboard-completo.yaml` — Stage 0 inserido
- `workflows/etl-puro.yaml` — Stage 0 inserido
- `workflows/apresentacao-executiva.yaml` — Stage 0 inserido

**Agent files (4)**
- `.opencode/agent/data-architect.md` — spec/adr/ path migration
- `.opencode/agent/dashboard-designer.md` — spec/adr/ path migration
- `.opencode/agent/automation-engineer.md` — spec/adr/ path migration
- `.opencode/agent/delivery-reviewer.md` — review/checklist ownership clause

**Scripts (2)**
- `scripts/subagent_boot_check.py` — 6ª dimensão + 7ª dimensão (child-repo-skeleton) + meta-audit skip patch
- `scripts/preflight_check.py` — SDD scaffold references atualizadas

**Registry (9+ templates)**
- `registry/spec-templates/README.md` — índice
- `registry/spec-templates/spec/constitution.md` — cópia LATADE
- `registry/spec-templates/spec/todo.md` — cópia LATADE
- `registry/spec-templates/spec/adr/_template.md` — cópia LATADE
- `registry/spec-templates/spec/harness/_template.md` — cópia LATADE
- `registry/spec-templates/spec/specs/000-bootstrap/spec.md` — cópia LATADE
- `registry/spec-templates/opencode-templates/` — 6 templates LATADE (.opencode)

**Config (1)**
- `.opencode/opencode.jsonc` — whitelist para `uv run python scripts/subagent_boot_check.py *`

### Validação executada (2026-06-05)

| Validação | Resultado |
|-----------|-----------|
| Boot check delivery-reviewer | PASS (exit 0, 7ª dim skip: meta-audit) |
| Preflight check | PASS (5/5, 0 findings) |
| G4 BASIC sign-off (delivery-reviewer) | DELIVERABLE — 15/17 EXPLICITLY_VERIFIED, 2 N/A, 0 VIOLATED |

### Advisory do delivery-reviewer

`spec/adr/README.md` é exigido pela matriz mas não tinha template em
`registry/spec-templates/spec/adr/`. **Corrigido** neste commit: template
README.md criado no diretório canônico.

---

## Referências

- Proposta LACOUNCIL: `f9b636fc-5ca9-4860-94ca-3a6b43c6862c` (4/4 SIM, unanimidade, 100%)
- Proposta v1 (abandonada): `e6e9e063`
- Proposta v2 (rejeitada): `6bc77c47`
- ADR-003: Criação do capability-architect
- ADR-006: Smoke-test `*.health()` (6ª dimensão do boot check)
- ADR-007: Reclassificar LADESIGN MCP smoke-test
- Binding conditions: `projects/_meta/capability-architect/binding-conditions.md`
- Capability-evolution: `projects/_meta/capability-architect/capability-evolution.md`
- Precedente de unanimidade rejeitada: `203b8baa`
