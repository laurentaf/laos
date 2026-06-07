# Política de fabricação de dados (synthetic data)

> Hard Rule #11 do `AGENTS.md` (2026-06-07). Esta knowledge entry
> detalha a operação: modos de permissão, schema de metadados,
> exemplos, exceções, e trilha de auditoria.

## 1. O anti-pattern que esta regra fecha

Agentes (subagentes da LAOS e o orchestrator) operam em um mundo
onde dados podem estar **ausentes** (API off, credencial expirada,
permissão negada, tabela vazia, schema incompatível). A reação
natural do LLM diante de um gap é **inventar** valores plausíveis
para preencher — é a mesma heurística que produz "hallucination" em
texto livre, transposta para o domínio de dados.

**Por que é perigoso:**
- Um valor sintético pode acabar em uma agregação, dashboard, ou
  pipeline de produção sem que ninguém perceba.
- O usuário lê o dashboard e toma uma decisão de negócio baseada
  em um número inventado.
- O modelo não distingue "valor plausível" de "valor real" — a
  plausibilidade é justamente o que torna o erro silencioso.
- A LACOUNCIL não tem como auditar (a DuckDB só registra o que o
  agente fez, não a proveniência dos números).

**Princípio Fagan 1976 (referência):** defeitos injetados no início
do pipeline (discovery/data-model) são ordens de magnitude mais
baratos de prevenir do que de detectar downstream. Esta regra é o
"prevention stage" — bloquear a injeção, não tentar detectá-la no
sign-off (que já viu casos onde synthetic data passou).

## 2. Quem é responsável

| Papel | Responsabilidade |
|-------|------------------|
| **Subagente (data-architect, dashboard-designer, automation-engineer, capability-architect, ou qualquer futuro)** | Detecta gap de dados reais. **PÁRA.** Reporta ao orchestrator com mensagem acionável (qual dado falta, por que falta, qual seria o substitute sintético, qual escopo). **NÃO** gera synthetic data por iniciativa própria. |
| **Orchestrator** | Recebe o report do subagente. Faz a mediação com o usuário: "Subagente X precisa de <dado Y>. Sem ele, a entrega fica incompleta. Você autoriza gerar synthetic data? Escopo: <paths>. Marque: <justificativa>." Default se silêncio do usuário = **NÃO**. Repassa a decisão ao subagente. |
| **Usuário** | Única autoridade que pode conceder permissão. Decide por ocorrência (per-ask) ou por projeto (project-scoped). Loga a decisão. |

**Subagentes não falam com o usuário diretamente** (não têm
acesso ao loop conversacional). Sempre via orchestrator.

## 3. Modos de permissão

### 3.1. Per-ask (default, strict)

É o comportamento default. Não exige configuração.

**Fluxo:**
1. Subagente detecta que precisa de `<dado>` mas não consegue
   recuperá-lo (API off, permissão negada, etc.).
2. Subagente reporta ao orchestrator:
   ```
   gap: missing <dado>
   reason: <API X retornou 401 / tabela Y vazia / schema Mismatch>
   proposed synthetic: <descrição do que seria gerado>
   scope: <artifact paths que conteriam o dado>
   recommendation: <stop | wait_for_user | use_alternative_source>
   ```
3. Orchestrator pergunta ao usuário literalmente:
   "Subagente X precisa de `<dado>`. Sem ele, a entrega fica
   incompleta. Você autoriza gerar synthetic data?"
4. Usuário responde: yes / no / use_alt_source / scope=<path>
5. Orchestrator repassa ao subagente.
6. Se "yes": subagente gera, marca o artefato com frontmatter
   (ver §4), continua.
7. Se "no": subagente para, reporta a interrupção, orchestrator
   decide se a entrega fica pendente, é cancelada, ou usa
   alternative source.

### 3.2. Project-scoped (opt-in, less strict)

O `project.yaml` declara upfront que o projeto aceita synthetic
data em escopo delimitado. Útil para projetos de desenvolvimento
ou POC onde o usuário já sabe que dados reais não estão disponíveis
ou não são necessários.

**Sintaxe no `project.yaml`:**
```yaml
data_policy:
  allow_synthetic: true
  scope:
    - "artifacts/data/raw_data.json"  # path específico
    - "artifacts/dev/**"              # glob
    - "wireframes"                    # classe
  decided_at: 2026-06-07T10:00:00Z
  decided_by: laurent@laurentaf.dev
  reason: "POC against public demo API; real data not available"
```

**Comportamento:**
- Dentro do escopo: subagente pode usar synthetic data sem per-ask.
  Ainda assim DEVE marcar cada artefato com frontmatter
  (`synthetic: true, granted_by: project_yaml, granted_at:
  <criado_em do project.yaml ou decided_at do data_policy>`).
- Fora do escopo: comportamento per-ask normal.
- Ausência do bloco `data_policy`: equivalente a
  `allow_synthetic: false` (modo per-ask).

**Quando usar:**
- POCs que rodam contra mock APIs (`giovanna-rupture-monitor`
  é o exemplo canônico — `--local` mode usa `data/raw_data.json`
  sintético, declarado upfront no spec).
- Projetos de demonstração onde dados reais não existem ou são
  confidenciais demais para o contexto.
- Ambientes de staging isolados.

**Quando NÃO usar:**
- Entregas para cliente externo (Regime B, P0 em
  `padroes-entrega.md`).
- Análise de negócio real onde os números alimentam decisão.
- Pipelines que alimentarão modelos de ML em produção.

### 3.3. Aceitável sem permissão (always allowed)

Três categorias onde synthetic data não exige o flow de
permissão, mas **ainda exige marcação** se o artefato for
eventualmente promovido a produção:

1. **Test fixtures** sob `tests/` (qualquer framework). Marcados
   por convenção do framework (`conftest.py`, `fixtures/`, etc.).
2. **Wireframe mockups** explicitamente rotulados
   `mock, not for production` no header da página ou no frontmatter
   do design artifact.
3. **Documentation examples** em `docs/`, knowledge entries, ou
   READMEs.

**Atenção:** mesmo nestas categorias, se o artefato for copiado
para um path de produção (`artifacts/data/`, `artifacts/design/`,
`artifacts/automation/`, `artifacts/deck/`, `artifacts/pipeline/`,
`artifacts/dq/`), o flow per-ask se aplica retroativamente.

## 4. Schema de metadados

Todo artefato que contém synthetic data — em qualquer modo de
permissão — DEVE carregar um bloco de metadados identificável.
O mecanismo depende do tipo de artefato.

### 4.1. Artefatos textuais (SQL, Markdown, YAML, JSON, HTML)

**Frontmatter YAML** no topo do arquivo:

```yaml
---
synthetic: true
granted_by: <user | project_yaml>
granted_at: 2026-06-07T10:00:00Z
reason: "API X retornou 401; sem credencial válida em CI"
scope: "artifacts/data/raw_data.json"
expires_at: 2026-07-07T10:00:00Z  # opcional: re-validação
---
```

### 4.2. Artefatos binários (parquet, csv, xlsx, png)

**Sidecar metadata file** com mesmo nome + `.meta.yaml`:

```
artifacts/data/raw_data.parquet
artifacts/data/raw_data.parquet.meta.yaml
```

Conteúdo do sidecar:

```yaml
synthetic: true
granted_by: laurent@laurentaf.dev
granted_at: 2026-06-07T10:00:00Z
reason: "POC dev mode; dados reais requerem ShadowTraffic API"
scope: "artifacts/data/raw_data.json"
source_artifact: "artifacts/data/raw_data.json"  # se derivado
regenerate_command: "uv run python scripts/gen_synthetic.py"
expires_at: 2026-07-07T10:00:00Z
```

### 4.3. Workflows n8n (JSON)

**Bloco `meta` no topo do workflow JSON** (n8n suporta campo
customizado no nó, ou annotation no workflow-level):

```json
{
  "name": "Daily Report Email",
  "meta": {
    "synthetic": true,
    "granted_by": "laurent@laurentaf.dev",
    "granted_at": "2026-06-07T10:00:00Z",
    "reason": "n8n flow test against mock API"
  },
  "nodes": [...]
}
```

### 4.4. Design artifacts (HTML, SVG, Figma export)

**Frontmatter YAML** (HTML/SVG) ou **metadata layer** (Figma):

```yaml
---
synthetic: true
kind: wireframe
label: "mock, not for production"
granted_by: laurent@laurentaf.dev
granted_at: 2026-06-07T10:00:00Z
---
```

## 5. Trilha de auditoria

Toda concessão de permissão — per-ask ou project-scoped — deve
ser logada. Duas formas complementares:

### 5.1. LACOUNCIL record (DuckDB)

`lacouncil.record_project()` ganha um novo campo opcional
`data_policy_grants: [{...}]`. A função já existe; este é um
extension, não uma breaking change.

### 5.2. Project-level audit log

`projects/<name>/artifacts/review/data-policy.md` (criado pelo
delivery-reviewer no sign-off, não pelo projeto) lista:

```markdown
# Data-policy audit — <project>

| Artefato | Synthetic? | Granted by | Granted at | Reason | Scope |
|----------|------------|------------|------------|--------|-------|
| artifacts/data/raw_data.json | yes | project_yaml | 2026-06-07 | POC dev | artifacts/data/** |
| artifacts/data/orders_2026q2.parquet | no | (real data) | — | — | — |
```

O `delivery-reviewer` preenche este arquivo no sign-off
(`review/checklist.md` ganha seção P0-15 "data policy compliance").

## 6. Enforcement

### 6.1. Pelo subagente (charter)

Cada subagente que produz artefatos de dados tem a regra no
charter (ver §7). A regra é parte do escopo do subagente, não
config externa.

### 6.2. Pelo `preflight_check.py`

Novo check 7 (`synthetic-data-audit`):
- Lista todos os artefatos em `artifacts/{data,design,automation,
  pipeline,dq,deck}/`.
- Para cada um que pareça conter dados (CSV, JSON, Parquet,
  HTML com dados embedded), verifica se tem frontmatter
  `synthetic: true` OU sidecar `.meta.yaml`.
- Se tem dados sem marcação → BLOCKED com mensagem
  acionável por arquivo.

### 6.3. Pelo `delivery-reviewer` (sign-off)

Adiciona P0-15 ao checklist (`padroes-entrega.md`):
> P0-15: nenhum artefato em `artifacts/{data,design,automation,
> pipeline,dq,deck}/` contém dados sem marcação de proveniência.
> Synthetic data SEM `synthetic: true` frontmatter = P0 violation.

`delivery-reviewer` cita o `exit_code` do preflight check 7 no
G4 sign-off (mesmo padrão do WDL-IC-10).

### 6.4. Pela LACOUNCIL (patterns)

`lacouncil.detect_patterns()` (M2 WDL) ganha um signal
adicional: contar projetos onde a regra foi violada no mês.
Se ≥ 3 violações em 30 dias → LACOUNCIL cria proposta
automática para endurecer a regra (exigir regenerate_command
em todo sidecar, ou bloquear synthetic data em
`artifacts/automation/` exceto para n8n test flows).

## 7. Cross-references nas charters dos subagentes

| Subagente | Seção do charter que ganha |
|-----------|----------------------------|
| `orchestrator` | "User mediation for missing data" — protocolo exato de pergunta + repasse |
| `data-architect` | "Missing data protocol" — stop, report, await decision; modos per-ask e project-scoped |
| `dashboard-designer` | "Sample data for wireframes" — permitido APENAS com `mock, not for production` label; parar para dados reais |
| `automation-engineer` | "Test data for flow validation" — fixtures permitidos com sidecar; flows de produção requerem dados reais |
| `capability-architect` | Não produz artefatos de dados; meta-structural. (Sem mudança.) |
| `workflow-decomposer` | Não produz artefatos de dados. (Sem mudança.) |
| `delivery-reviewer` | "P0-15 data policy compliance" — verifica marcação em todo artefato de produção |

## 8. Exemplos

### 8.1. Exemplo 1 — data-architect bloqueado por API off

```
[Subagente data-architect] → [Orchestrator]
gap: missing API token for ShadowTraffic
reason: env var SHADOWTRAFFIC_TOKEN not set in this CI run
proposed synthetic: gerar 1000 rows plausíveis em
  artifacts/data/raw_data.json com schema ShadowTraffic
scope: artifacts/data/raw_data.json
recommendation: stop_until_user_decision
```

```
[Orchestrator] → [Usuário]
Subagente data-architect precisa de dados ShadowTraffic.
A env var SHADOWTRAFFIC_TOKEN não está setada neste CI.
Você autoriza gerar synthetic data?
- Escopo proposto: artifacts/data/raw_data.json
- Justificativa: POC dev mode; dados reais requerem ShadowTraffic API
(y / n / scope:<caminho> / use_alt_source:<X>)
```

Resposta: `n` → orchestrator reporta interrupção, projeto fica
pendente de configuração de credencial.

Resposta: `y` → data-architect gera, marca o JSON com frontmatter
`{synthetic: true, granted_by: laurent@..., granted_at: ...,
reason: "POC dev mode; ..."}`, continua.

### 8.2. Exemplo 2 — projeto giovanna-rupture-monitor (project-scoped)

`project.yaml` já documenta o uso de synthetic data em §US-1.
Atualização sugerida (retrofit mínimo):

```yaml
data_policy:
  allow_synthetic: true
  scope:
    - "data/raw_data.json"     # spec bootstrap já documenta
    - "artifacts/data/dev/**"  # convenção para POC dev mode
  decided_at: 2026-06-07T10:00:00Z
  decided_by: laurent@laurentaf.dev
  reason: "POC against public ShadowTraffic demo; real data not in CI"
```

Sem essa declaração, o data-architect deveria parar e perguntar
cada vez que precisasse do `raw_data.json` sintético.

### 8.3. Exemplo 3 — dashboard wireframe (always-allowed, marked)

`dashboard-designer` produz wireframe com 5 cards usando nomes
de regiões fictícios ("Região A", "Região B", ...). Frontmatter
do HTML:

```yaml
---
synthetic: true
kind: wireframe
label: "mock, not for production"
granted_by: laurent@laurentaf.dev
granted_at: 2026-06-07T10:00:00Z
---
```

Sem `label: "mock, not for production"` no header da página
(visível ao usuário), o `delivery-reviewer` falha o sign-off
com P0-15.

## 9. Migração de projetos existentes

Projetos com synthetic data não-marcada (ex.: `giovanna-rupture-
monitor` antes desta regra) ganham **retrofit passivo**:
- O `delivery-reviewer` exige retrofit ao tocar o projeto em
  sign-off ou auditoria normal.
- Sem varredura ativa de projetos parados (não é emergency).
- Quando o retrofit acontecer, o `granted_at` é a data do
  retrofit (não a data original de criação), e `reason` inclui
  `retrofit_per_data_fabrication_policy_v1`.

## 10. O que esta política NÃO cobre

- **PII / anonymization.** Synthetic data com PII (nomes reais,
  CPFs, etc.) é um problema separado. Ver `knowledge/data-
  conventions.md` §"PII handling" se aplicável. Esta regra é
  sobre **origem** do dado, não sobre seu conteúdo.
- **Data augmentation para ML.** Esta regra cobre artefatos de
  entrega, não datasets de treino. ML data augmentation tem
  suas próprias convenções (ver `laecon` quando STABLE).
- **Test mocks vs real data.** LATADE CONSTITUTION Art. X
  já exige "Tests against real data, not mocks" para
  assertions. Esta regra complementa para os SETUPS
  (fixtures) e para os artefatos de produção.

## 11. Histórico

| Data | Evento | Detalhe |
|------|--------|---------|
| 2026-06-07 | Proposta | Hard Rule #11 proposta como user-authorized, sem LACOUNCIL chain (mesmo padrão dos 3 skips) |
| 2026-06-07 | Implementation | Knowledge entry + padroes-entrega P0 + 4 subagent charters |
| TBD | LACOUNCIL ratification | Proposta formal maioria para converter user-override em regra formal |

## 12. Cross-references

- `AGENTS.md` Hard Rule #11 (a regra)
- `knowledge/padroes-entrega.md` P0-15 (enforcement)
- `LATADE/CONSTITUTION.md` Art. X "Tests against real data" (princípio-irmão)
- `knowledge/data-conventions.md` §"PII handling" (fronteira)
- `workflows/wdl-contract.yaml` §"exemption" (WDL exemption não se aplica a esta regra — synthetic data decision é sempre do usuário, não do workflow-decomposer)
