# previsao-concursos

> Plataforma web que prevê os assuntos mais prováveis por matéria
> em concursos públicos brasileiros, usando histórico de provas da
> banca avaliadora (FCC e FGV, cargo Auditor Fiscal).

**Status:** POC 100% local. Stage 1 (discovery) e Stage 2 (data-model)
concluídos em 2026-06-05. Próximo: Stage 3 (design via
`dashboard-designer`).

---

## O que é

A POC implementa um pipeline medallion (bronze → silver → gold) em
DuckDB que ingere editais e provas anteriores das bancas FCC e FGV,
agrega por (banca, cargo, matéria, assunto, sub-assunto, ano) e
expõe uma **probabilidade empírica** de cada sub-assunto cair em um
concurso futuro. A UI (dashboard do candidato) consome essa view
para gerar um **roteiro hierárquico** Matéria > Assunto > Sub-assunto
ordenado do mais provável para o menos.

**Diferencial:** tagging determinístico (hierarquia do edital +
dicionário de sinônimos) — LLM **proibido** no caminho de predição.
ML empírico (laecon: xgboost + shap) com split temporal obrigatório
(2022-2024 treino, 2025-2026 validação).

**Stack:** LATADE (DuckDB + SQL) + LAECON (ML) + LADESIGN (UI) +
LAN8N (refresh mensal) + EXA (descoberta de provas).

## Como rodar

### Pré-requisitos

- Python 3.11+ com `uv` instalado
- Node 20+ (para LADESIGN daemon)
- Acesso ao GitHub (`GITHUB_TOKEN` em env OS)
- Child repo clonado em `E:\projects\laurentaf\previsao-concursos\`

### Setup

```powershell
# LAOS root
cd E:\projects\LAOS
uv sync                                        # instala deps LAOS

# Capabilities (cada uma tem pyproject próprio)
cd E:\projects\latade; uv sync
cd E:\projects\laecon; uv sync
cd E:\projects\lan8n;   uv sync

# LADESIGN (Node-based)
cd E:\projects\ladesign; pnpm install
```

### Validar scaffold (Missão 0)

```powershell
cd E:\projects\LAOS
uv run python scripts\preflight_check.py projects\previsao-concursos
uv run python scripts\subagent_boot_check.py data-architect --project-name previsao-concursos
uv run python scripts\subagent_boot_check.py dashboard-designer --project-name previsao-concursos
```

Saída esperada: exit code 0 nos 3 comandos.

### Despachar subagentes (exemplo: data-architect no Stage 2)

Via orchestrator (LAOS), nunca direto. Brief-curto 5-15 linhas,
output path sob `projects/previsao-concursos/artifacts/`.

## Onde está o quê

```
E:\projects\LAOS\projects\previsao-concursos\
├── project.yaml                # contrato (brief, needs, deliverables, repo)
├── contract.md                 # espelho do project.yaml em prosa
├── README.md                   # este arquivo
├── spec\                       # SDD scaffold (Missão 0)
│   ├── constitution.md         # Principles / Scope / Non-goals
│   ├── todo.md                 # tracker de tasks (Stage 0 em diante)
│   ├── design-direction.md     # direção visual (condicional: design)
│   ├── adr\                    # ADRs reais (001-, 002-, ...) + _template + README
│   ├── harness\_template.md     # stub-by-design (copiado do LATADE)
│   └── specs\000-bootstrap\spec.md
└── artifacts\                  # output dos subagentes (vai pro child repo)
    ├── discovery\requirements.md          # Stage 1 (data-architect)
    ├── data\model.md                      # Stage 2 (data-architect)
    ├── data\sql-stubs\001-medallion.md
    ├── data\strategies\{scraping,chunking}.md
    ├── dq\checks.md
    ├── design\                            # Stage 3 (dashboard-designer, próximo)
    ├── pipeline\                          # custom: scrap + chunk
    ├── ml\                                # custom: classical-ml (laecon)
    ├── dashboard\                         # custom: study-plan
    ├── automation\                        # Stage 5 (automation-engineer)
    └── review\checklist.md                # Stage 6 (delivery-reviewer)
```

**Tudo em `artifacts/` é commitado no child repo
[`laurentaf/previsao-concursos`](https://github.com/laurentaf/previsao-concursos)**,
não em LAOS. O mirror aqui em `LAOS/projects/previsao-concursos/`
contém apenas o contrato e o spec scaffold (Hard Rule #1 LAOS).

### Cross-references

- `LAOS/registry/needs-to-capabilities.yaml` — routing determinístico.
- `LAOS/registry/capabilities.yaml` — catálogo de capabilities.
- `LAOS/knowledge/padroes-entrega.md` — checklist de entrega.
- `LAOS/knowledge/sdd-principles.md` — princípio fundacional POC ≠ zero-shot.
- `LAOS/projects/_meta/adr/ADR-005-modeling-routing-laecon.md` — decisão
  LACOUNCIL `bf91c407` (modeling → laecon).
- `LAOS/projects/_meta/adr/ADR-006-mcp-boot-smoke-test.md` — decisão
  LACOUNCIL `f82d6261` (latade boot check fix).
