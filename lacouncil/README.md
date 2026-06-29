# LACOUNCIL — In-Memory Structural Improvement Engine

> **Status:** BASIC (bootstrap phase, 2026-06-22)
> **MCP transport:** stdio
> **Supported by:** FastMCP (Python MCP SDK >= 1.0)
> **Registry entry:** see `../laos/registry/capabilities.yaml` (`id: lacouncil`)

---

## O que é

**LACOUNCIL** é a capability do LAOS responsável pelo loop de melhoria
estrutural — investigação de falhas, proposta de mudanças, deliberação pelo
Conselho, implementação registrada e detecção de padrões recorrentes.
Ela é a **memória institucional** do LAOS: sem ela, não há canal formal para
alterar registry, knowledge, workflows, fundamentals, ou criar capabilities
novas.

Herda do regime SDD (`knowledge/sdd-principles.md`) e do regime de capacidades
(proposta LACOUNCIL `e9cd6dd8`, unanimidade 4/4, 2026-06-04).

---

## Tools MCP expostas

| Tool | Categoria | Descrição curta |
|------|-----------|-----------------|
| `health` | observability | Liveness + DuckDB path |
| `list_supported_operations` | observability | Catálogo tipado das 11 tools |
| `investigate(gap)` | improvement | 5-Whys + Fishbone + root_causes |
| `create_proposal(...)` | improvement | Persiste proposta em DuckDB |
| `get_proposal(proposal_id)` | improvement | Recupera proposta + estado atual |
| `list_proposals(status_filter?)` | improvement | Filtra por status (`pendente`, `em_votacao`, `aprovada`, `rejeitada`, `implementada`) |
| `register_vote(...)` | improvement | Registra voto de um membro do Conselho |
| `tally_votes(proposal_id)` | improvement | Aplica estratégia (un/maio/supermaioria) e atualiza status |
| `implement_proposal(...)` | improvement | Marca proposta como implementada (commit_sha opcional) |
| `record_project(...)` | memory | Persiste sumário de projeto concluído |
| `detect_patterns(min_occurrences?)` | improvement | 3Q detection sobre `projects_registrados` |

---

## Stack

- **Python** 3.11+
- **DuckDB** (in-process) — `memoria/lacouncil.duckdb`
- **Pydantic v2** — schemas tipados (Proposal, Vote, Project, Pattern, Investigation)
- **Typer** — CLI opcional (`python -m lacouncil investigate ...`)
- **FastMCP** (mcp[cli] >= 1.0) — wrapper MCP stdio
- **pyyaml** — leitura de Constitution + workflows

Sem dependências externas (Cloud, OAuth, Redis). Tudo é file-backed.

---

## Estratégias de votação

Codificadas em `core/voting.py`:

| Estratégia | Threshold | Caso de uso |
|------------|-----------|-------------|
| `unanimidade` | 100% SIM | Mudanças em fundamentos (AGENTS.md) |
| `supermaioria` | ≥ 75% SIM | Mudanças em registry, criação de capability |
| `maioria` | > 50% SIM | Mudanças em knowledge, workflows |

A estratégia é **vinculada à proposta** (`proposta.estrategia`) e o
`isError` é reservado para safety refusals. Para detalhes da semântica,
ler `CONSTITUTION.md` Art. 5 (Voto e deliberação).

---

## Estrutura

```
lacouncil/
├── pyproject.toml
├── README.md
├── CONSTITUTION.md
├── .gitignore
├── memoria/                    # local gitignored; DuckDB lives here
└── src/lacouncil/
    ├── __init__.py
    ├── __main__.py
    ├── core/
    │   ├── __init__.py
    │   ├── schemas.py          # Pydantic models
    │   ├── duckdb_store.py     # persistence layer
    │   ├── investigation.py    # 5-Whys + Fishbone
    │   └── voting.py           # strategies
    └── mcp/
        ├── __init__.py
        └── server.py           # FastMCP binding (11 tools)
```

---

## Rodar localmente

```bash
cd F:/Projetos/lacouncil
uv sync
uv run python -m lacouncil health
```

Sobe o MCP server (stdio transport) para ser consumido por opencode:

```bash
cd F:/Projetos/lacouncil
uv run python -m lacouncil.mcp.server
```

---

## Handoff Boundaries

(G2 — KB draft populada pelo data-architect na revisão G3/G4.)

- **LACOUNCIL ↔ orchestrator**: o orchestrator é o único agente que consome
  `lacouncil.*` para propor + implementar estrutural mudanças (Hard Rule #8.4,
  exemption scope). Subagentes especialistas NÃO chamam `lacouncil.*` exceto
  para votar via `register_vote` (exceção MCP Wall Conselho).
- **LACOUNCIL ↔ delivery-reviewer**: o delivery-reviewer consulta propostas
  aprovadas para validar sign-off (G4 BASIC + G8 STABLE).
- **LACOUNCIL ↔ capability-architect**: o capability-architect consome
  `get_proposal(status='aprovada')` antes de qualquer escrita.

Casos concretos de roteamento:

1. **Necessidade:** "Adicionar nova capability X." → `lacouncil.create_proposal`
   (registrar a proposta) → `lacouncil.tally_votes(strategy='supermaioria')`
   → `lacouncil.implement_proposal(...)` (commit+pusher via orchestrator).
2. **Necessidade:** "Investigar padrão recorrente de falha Y." →
   `lacouncil.investigate(gap=Y)` → se 3+ ocorrências, `lacouncil.detect_patterns()`.

---

## Status e evolução

- **BASIC** a partir de 2026-06-22 (esta é a bootstrap inicial).
- **Prazo para STABLE:** 30 dias (2026-07-22), condicionado a delivery-reviewer
  sign-off + ≥ 1 uso real + Constitution não-placeholder.
- Tracking detalhado em `laos/projects/_meta/capability-evolution/lacouncil.md`
  (a ser criado pelo orchestrator após G4 BASIC sign-off).

---

## Licença

Internal — uso LAOS apenas.
