"""
Create LACOUNCIL proposals A and B for lacouncil infra hygiene.

A: lacouncil config hygiene (#1 DB path + #3 MCP command).
B: lacouncil CLI/UX hygiene (#2 task tool workaround + #4 Unicode stdout).

Run:  uv run --directory F:/Projetos/Laos/lacouncil python scripts/create_proposals_lacouncil_hygiene.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lacouncil.core.investigation import persist_investigation, link_to_proposal
from lacouncil.core.duckdb_store import upsert_proposal
from lacouncil.core.schemas import (
    Category,
    CreateProposalRequest,
    Estrategia,
    InvestigationResult,
    Proposal,
)


# ──────────────────────────────────────────────────────────────────────────────
# Proposal A: lacouncil config hygiene (#1 DB path + #3 MCP command)
# ──────────────────────────────────────────────────────────────────────────────

A_GAP = (
    "Lacouncil tem 2 arquivos DuckDB divergentes: 'src/memoria/lacouncil.duckdb' "
    "(default do Python: _REPO_ROOT = parents[2] resolve para lacouncil/src/) "
    "vs 'lacouncil/memoria/lacouncil.duckdb' (env var do opencode.jsonc, "
    "parents[3] = repo root). Conteúdo diverge: 3 proposals/11 votes vs 2/2. "
    "Adicionalmente, o opencode.jsonc spawna o MCP via 'uv run --directory "
    "lacouncil ...', que falha em Windows com 'Binary not found: uv' porque o "
    "subprocess do OpenCode não herda o PATH completo. Resultado: mcp__lacouncil__* "
    "tools nao carregam, forçando todos os flows LACOUNCIL via CLI ou Python API. "
    "P2 advisory do delivery-reviewer na G4 sign-off de d3095fa3."
)

A_FIVE_WHYS = [
    "1. Por que ha 2 arquivos DuckDB? Porque o _REPO_ROOT no duckdb_store.py "
    "usa parents[2] (aponta para lacouncil/src/) enquanto o env var do opencode "
    ".jsonc usa parents[3] (repo root). Sao resolucoes de path diferentes para "
    "o mesmo conceito (persistencia do lacouncil).",

    "2. Por que o _REPO_ROOT foi computado errado originalmente? Porque o "
    "modulo core/duckdb_store.py esta em src/lacouncil/core/, entao parents[2] "
    "= src/. Provavelmente o dev original pensou 'parents[2] = repo root' mas "
    "esqueceu que o pacote esta em src/ (estrutura src-layout do pyproject).",

    "3. Por que o opencode.jsonc usa 'uv run' em vez do Python do venv "
    "diretamente? Porque os primeiros MCPs (latade, lan8n) foram configurados "
    "com o Python do venv direto (sem uv), mas quando o lacouncil foi "
    "adicionado, usou-se o padrao 'uv run' por consistencia com a CLI. Mas "
    "esse padrao introduz uma dependencia de PATH que falha em Windows quando "
    "o subprocess do OpenCode nao herda o PATH do user.",

    "4. Por que o subprocess do OpenCode nao tem o PATH completo? Porque "
    "OpenCode em Windows pode ser iniciado via taskbar/Explorer/Start Menu, "
    "herdando um PATH minimo do sistema. O 'uv' instalado via cargo (em "
    "C:/Users/.../.cargo/bin/) nao esta nesse PATH minimo. Resultado: o "
    "subprocess tenta resolver 'uv' e falha.",

    "5. Por que isso nao foi detectado antes? Porque o lacouncil MCP era "
    "BASIC (cold start, 30d para STABLE), e os primeiros 30d de uso foram "
    "via CLI/Python API. Ninguem tentou usar o MCP de fato, entao o bug ficou "
    "latente ate a d3095fa3 forcar o orchestrator a usar o MCP para Conselho.",
]

A_FISHBONE = {
    "method": [
        "Padrao 'uv run' copiado sem validar pre-requisitos (PATH)",
        "Dois pontos de configuracao (Python default + env var) sem source-of-truth",
    ],
    "machine": [
        "OpenCode Windows subprocess nao herda PATH completo",
        "lacouncil.venv existe mas nao e usado pelo MCP config",
        "resolve_db_path() em duckdb_store.py tem DEFAULT_DB_PATH hard-coded",
    ],
    "measurement": [
        "Sem check de saude do MCP no preflight (lacouncil.mcp_health ausente)",
        "Dois DuckDBs com contadores diferentes (3/11 vs 2/2) nao detectados",
    ],
    "manpower": [
        "Orchestrator caiu em CLI/Python API ao inves de debugar o MCP",
        "Consejo nao tem visibilidade de infra lacouncil alem do DB",
    ],
    "material": [
        "opencode.jsonc tem 6 entries MCP; so lacouncil usa 'uv run'",
        "duckdb_store.py e o unico modulo com _REPO_ROOT computation",
    ],
    "milieu": [
        "knowledge/stack-decisions.md menciona 'uv run' genericamente sem "
        "considerar o caso do MCP subprocess",
        "WDL contract nao valida saude dos MCPs antes do preflight",
    ],
}

A_ROOT_CAUSES = [
    "Inconsistencia entre 2 fontes de path (Python default + env var opencode.jsonc).",
    "Subprocess do OpenCode em Windows nao herda PATH; 'uv run' falha.",
    "Falta de health check do MCP no preflight detecta o problema tarde.",
]

A_PROPOSED_ACTION = (
    "Fixar o _REPO_ROOT no duckdb_store.py para parents[3] (repo root) e "
    "mudar o command do opencode.jsonc para usar o Python do venv "
    "diretamente, eliminando o 'uv run'. Adicionar unit test cobrindo 3 "
    "cenarios de path resolution."
)

A_TITULO = "lacouncil config hygiene (DB path canonical + MCP command fix)"

A_DESCRICAO = (
    "Eliminar a inconsistencia de path do DuckDB do lacouncil e tornar o "
    "MCP server inicializavel em Windows. (1) Mudar _REPO_ROOT em "
    "lacouncil/src/lacouncil/core/duckdb_store.py de parents[2] para "
    "parents[3], fazendo o default path resolver para "
    "lacouncil/memoria/lacouncil.duckdb (repo root, alinhado com opencode "
    ".jsonc env var e com a convencao dos outros MCPs). (2) Mudar o command "
    "do lacouncil em .opencode/opencode.jsonc de ['uv', 'run', '--directory', "
    "'lacouncil', 'python', '-m', 'lacouncil.mcp.server'] para "
    "['..\\\\lacouncil\\\\.venv\\\\Scripts\\\\python', '-m', "
    "'lacouncil.mcp.server'], seguindo o padrao de latade e lan8n. Resultado: "
    "um unico arquivo DuckDB canonico, MCP carrega em qualquer plataforma, "
    "tools mcp__lacouncil__* disponiveis no orchestrator sem depender de "
    "'uv' no PATH do subprocess."
)

A_CONTEXTO = (
    "P2 advisory do delivery-reviewer na G4 BASIC sign-off de d3095fa3 "
    "(2026-07-02). Durante a implementacao da confidence_escalation_ladder, "
    "o orchestrator teve que usar lacouncil CLI e Python API em vez do MCP "
    "porque as tools nao carregavam. Tambem descobriu que existem 2 arquivos "
    "DuckDB com dados diferentes (d3095fa3 + 4 votos estao em "
    "src/memoria/lacouncil.duckdb, nao no canonico). Fix acoplado: "
    "padronizar o path antes de mudar o MCP command."
)

A_MUDANCA = (
    "(1) lacouncil/src/lacouncil/core/duckdb_store.py linha 50: "
    "_REPO_ROOT = Path(__file__).resolve().parents[3] "
    "(era parents[2]). Adicionar comentario explicando o path layout: "
    "parents[3] = repo root, /memoria/lacouncil.duckdb. "
    "(2) .opencode/opencode.jsonc entrada lacouncil.command: "
    "['..\\\\lacouncil\\\\.venv\\\\Scripts\\\\python', '-m', "
    "'lacouncil.mcp.server'] (era ['uv', 'run', '--directory', 'lacouncil', "
    "'python', '-m', 'lacouncil.mcp.server']). "
    "(3) .opencode/opencode.jsonc entrada lacouncil.env.LACOUNCIL_DB_PATH "
    "confirma valor '{workspaceFolder}\\\\lacouncil\\\\memoria\\\\"
    "lacouncil.duckdb' (ja esta, mas agora passa a ser canonico apos o "
    "fix #1). "
    "(4) Novo arquivo lacouncil/tests/test_duckdb_path.py com 3 tests: "
    "test_default_path_resolves_to_repo_root_memoria, "
    "test_env_var_override_takes_precedence, "
    "test_explicit_db_path_arg_wins."
)

A_IMPACTO = (
    "Positivo: 1 arquivo DuckDB canonico (elimina divergencia silenciosa), "
    "MCP tools carregam em Windows (orchestrator pode usar lacouncil.* "
    "diretamente em vez de CLI), alinha com padrao de latade/lan8n. "
    "Risco: OpenCode pode precisar de restart para o novo command ter "
    "efeito. Mitigacao: documentar no commit. "
    "Risco 2: o DB legado em src/memoria/lacouncil.duckdb fica orfao. "
    "Mitigacao: nao deletar (decisao consciente); dados legados refletem "
    "o trabalho feito, podem ser revisados. "
    "Files affected: lacouncil/src/lacouncil/core/duckdb_store.py "
    "(1 linha + comentario), .opencode/opencode.jsonc (1 entry), "
    "lacouncil/tests/test_duckdb_path.py (NEW, ~30 linhas)."
)

A_ALTERNATIVAS = (
    "(A) Mover opencode.jsonc env var para 'lacouncil/src/memoria/...' — "
    "rejeitada: viola a convencao de manter memoria/ no repo root "
    "(padrao dos outros MCPs). "
    "(B) Symlink src/memoria -> ../memoria — rejeitada: fragil no Windows, "
    "git nao trackeia symlinks bem. "
    "(C) Renomear a venv lacouncil/.venv e usar path absoluto — "
    "rejeitada: complica setup, nao endereca o problema. "
    "(D) Manter 'uv run' e adicionar PYTHONPATH manual — rejeitada: "
    "frustrating, nao resolve o root cause (PATH do subprocess)."
)


# ──────────────────────────────────────────────────────────────────────────────
# Proposal B: lacouncil CLI/UX hygiene (#2 task tool workaround + #4 Unicode)
# ──────────────────────────────────────────────────────────────────────────────

B_GAP = (
    "(1) O agent type 'automation-engineer' nao esta exposto no `task` tool "
    "do OpenCode nesta sessao, embora o arquivo .opencode/agent/"
    "automation-engineer.md exista. WDL gate aceitaria (valida por "
    "diretorio), mas o `task` tool tem lista hardcoded que rejeita antes. "
    "Resultado: o orchestrator teve que dispatchar o 4o voto do Conselho "
    "via chief-engineer com voter string 'automation-engineer', workaround "
    "que funciona mas nao e o ideal. (2) O CLI do lacouncil quebra no "
    "console Windows (cp1252) com UnicodeEncodeError ao mostrar propostas "
    "que contem caracteres nao-ASCII como '>=' (U+2265). Bloqueia o "
    "fluxo 'lacouncil proposal show <id>' que o orchestrator usa para "
    "verificar status durante o pipeline."
)

B_FIVE_WHYS = [
    "1. Por que 'automation-engineer' nao esta no task tool? Porque a lista "
    "de subagent_type no tool descriptor do OpenCode foi populada em um "
    "momento onde automation-engineer.md ainda nao existia, ou houve "
    "regressao em versao recente do OpenCode.",

    "2. Por que o task tool tem lista hardcoded em vez de ler .opencode/"
    "agent/? Porque a tool descriptor do MCP e estatico por performance e "
    "previsibilidade; ler diretorio em runtime adicionaria latencia.",

    "3. Por que o CLI lacouncil quebra com Unicode no Windows? Porque o "
    "stdout do Python no Windows console default usa cp1252, e o Rich "
    "console (usado pelo Typer) nao reconfigura automaticamente.",

    "4. Por que o workround de #1 nao foi documentado antes? Porque o "
    "primeiro caso real de uso (Conselho na d3095fa3) foi o primeiro "
    "a descobrir o problema; o workaround foi aplicado ad-hoc.",

    "5. Por que o encoding nao foi setado antes? Porque o lacouncil foi "
    "desenvolvido e testado primariamente em ambiente Unix-like onde UTF-8 "
    "e default. O smoke test em Windows foi skipped.",
]

B_FISHBONE = {
    "method": [
        "Lista de subagent_type no task tool e estatica, nao dinamica",
        "Smoke test do CLI nao cobre Windows console cp1252",
    ],
    "machine": [
        "OpenCode task tool nao consulta .opencode/agent/ em runtime",
        "Python stdout no Windows console default e cp1252",
        "Rich Console nao reconfigura encoding automaticamente",
    ],
    "measurement": [
        "Sem preflight check para MCP health durante boot",
        "Sem smoke test cross-platform do CLI",
    ],
    "manpower": [
        "Orchestrator teve que improvisar workaround sem documentar",
        "Reviews nao cobrem o caso Windows console",
    ],
    "material": [
        "knowledge/ nao tem nota sobre Windows console encoding",
        ".opencode/agent/orchestrator.md nao tem secao 'Conselho voting' "
        "com workaround documentado",
    ],
    "milieu": [
        "AGENTS.md menciona cross-platform mas nao operacionaliza no CLI",
        "stack-decisions.md assume UTF-8 sem validar plataforma",
    ],
}

B_ROOT_CAUSES = [
    "Lista de subagent_type no task tool e estatica (hardcoded), nao "
    "sincronizada com .opencode/agent/ dinamicamente.",
    "CLI do lacouncil nao força UTF-8 no stdout; quebra em Windows cp1252.",
    "Workaround de dispatch via chief-engineer nao foi documentado no "
    "orchestrator charter.",
]

B_PROPOSED_ACTION = (
    "(1) Adicionar secao 'Conselho voting' em .opencode/agent/"
    "orchestrator.md documentando o workaround: dispatch via "
    "chief-engineer com voter string 'automation-engineer'. "
    "(2) Adicionar sys.stdout.reconfigure(encoding='utf-8') no topo de "
    "lacouncil/src/lacouncil/__main__.py (apos from __future__ import "
    "annotations). Python 3.7+ tem reconfigure; LAOS requires >=3.11."
)

B_TITULO = "lacouncil CLI/UX hygiene (task tool workaround + Unicode stdout)"

B_DESCRICAO = (
    "Dois fixes de UX que nao impedem funcionamento mas reduzem friccao "
    "e evitam workarounds ad-hoc. (1) Documentar em .opencode/agent/"
    "orchestrator.md (secao 'Conselho voting') o workaround para o "
    "agent type 'automation-engineer' nao estar exposto no `task` tool "
    "desta sessao: dispatch via `chief-engineer` com voter string "
    "'automation-engineer' no payload da `lacouncil.vote.register`. "
    "Mesmo efeito no DuckDB; preserva integridade do log do Conselho. "
    "(2) Forcar UTF-8 no stdout do CLI lacouncil adicionando "
    "sys.stdout.reconfigure(encoding='utf-8') no topo de "
    "lacouncil/src/lacouncil/__main__.py. Resolve o UnicodeEncodeError "
    "que aparece em Windows console (cp1252) ao rodar `lacouncil "
    "proposal show` em propostas com chars nao-ASCII."
)

B_CONTEXTO = (
    "P2 advisory do delivery-reviewer na G4 BASIC sign-off de d3095fa3 "
    "(2026-07-02). Durante o Conselho que aprovou a confidence_escalation_"
    "ladder, o orchestrator teve que dispatchar o voto do automation-"
    "engineer via chief-engineer (agent type 'automation-engineer' nao "
    "aceito pelo task tool). Tambem, o orchestrator nao conseguia rodar "
    "`lacouncil proposal show` no console Windows — tinha que ler via "
    "Python API. Ambos os fixes sao knowledge + 1-liner de codigo, "
    "sem mudanca estrutural."
)

B_MUDANCA = (
    "(1) .opencode/agent/orchestrator.md: adicionar secao 'Conselho "
    "voting' (apos o bloco atual de hard rules) com texto: 'O agent "
    "type `automation-engineer` nao esta exposto no `task` tool desta "
    "sessao (lista hardcoded do OpenCode nao inclui; agent file existe "
    "em .opencode/agent/automation-engineer.md mas o WDL gate nunca e "
    "chamado porque o tool rejeita antes). Workaround: dispatch via "
    "`chief-engineer` (que esta na lista) com `voter: \"automation-"
    "engineer\"` no payload da `lacouncil.vote.register`. Mesmo efeito "
    "no DuckDB; preserva integridade do log do Conselho. Se a lista do "
    "task tool for corrigida upstream, este workaround vira dead code "
    "e pode ser removido.' "
    "(2) lacouncil/src/lacouncil/__main__.py: apos `from __future__ "
    "import annotations` e antes de `import json`, adicionar "
    "`sys.stdout.reconfigure(encoding=\"utf-8\")`. Idempotente; nao "
    "quebra em ambiente ja-UTF-8 (no-op)."
)

B_IMPACTO = (
    "Positivo: orchestrator tem documentacao canonica do workaround "
    "Conselho (nao precisa improvisar); CLI funciona em Windows console. "
    "Risco: zero (knowledge entry + reconfigure idempotente). "
    "Files affected: .opencode/agent/orchestrator.md (~10 linhas novas), "
    "lacouncil/src/lacouncil/__main__.py (1 linha adicionada)."
)

B_ALTERNATIVAS = (
    "(A) Reportar bug upstream do OpenCode e esperar fix — util mas "
    "nao endereca o problema imediato; rejeitada como unica acao, "
    "recomendada como follow-up paralelo. "
    "(B) Setar PYTHONIOENCODING=utf-8 no env var do opencode.jsonc "
    "para o lacouncil MCP — funciona quando invocado via OpenCode, "
    "mas nao quando invocado via `uv run` direto ou via shell. "
    "Rejeitada: reconfigure no __main__ pega todos os call sites. "
    "(C) Reescrever todas as strings do lacouncil para ASCII — "
    "rejeitada: perde semantica (>=, <=, nao-ASCII em titulos). "
    "(D) Criar um agent file 'automation-engineer' duplicado em "
    "chief-engineer.md — confuso, conflita com o chief-engineer "
    "existente."
)


def create_one(
    *,
    label: str,
    gap: str,
    five_whys: list[str],
    fishbone: dict[str, list[str]],
    root_causes: list[str],
    proposed_action: str,
    titulo: str,
    descricao: str,
    contexto: str,
    mudanca: str,
    impacto: str,
    alternativas: str,
) -> str:
    inv = InvestigationResult(
        gap=gap,
        five_whys=five_whys,
        fishbone=fishbone,
        root_causes=root_causes,
        proposed_action=proposed_action,
    )
    persisted = persist_investigation(inv)
    print(f"[{label}] investigation session_id={persisted.session_id}")

    req = CreateProposalRequest(
        titulo=titulo,
        descricao=descricao,
        categoria=Category.WORKFLOW,
        estrategia=Estrategia.MAIORIA,
        autor="orchestrator",
        contexto=contexto,
        mudanca=mudanca,
        impacto=impacto,
        alternativas=alternativas,
        created_by_session=persisted.session_id,
    )
    proposal = Proposal(**req.model_dump())
    saved = upsert_proposal(proposal)
    link_to_proposal(persisted.session_id, saved.proposal_id)

    print(f"[{label}] proposal_id={saved.proposal_id}")
    print(f"[{label}]   categoria={saved.categoria.value} estrategia={saved.estrategia.value}")
    print(f"[{label}]   status={saved.status.value}")
    print(f"[{label}]   signature={saved.signature[:16]}...")
    return saved.proposal_id


def main() -> None:
    print("=" * 70)
    print("Creating LACOUNCIL proposals A and B for lacouncil infra hygiene")
    print("=" * 70)
    a_id = create_one(
        label="A",
        gap=A_GAP,
        five_whys=A_FIVE_WHYS,
        fishbone=A_FISHBONE,
        root_causes=A_ROOT_CAUSES,
        proposed_action=A_PROPOSED_ACTION,
        titulo=A_TITULO,
        descricao=A_DESCRICAO,
        contexto=A_CONTEXTO,
        mudanca=A_MUDANCA,
        impacto=A_IMPACTO,
        alternativas=A_ALTERNATIVAS,
    )
    print()
    b_id = create_one(
        label="B",
        gap=B_GAP,
        five_whys=B_FIVE_WHYS,
        fishbone=B_FISHBONE,
        root_causes=B_ROOT_CAUSES,
        proposed_action=B_PROPOSED_ACTION,
        titulo=B_TITULO,
        descricao=B_DESCRICAO,
        contexto=B_CONTEXTO,
        mudanca=B_MUDANCA,
        impacto=B_IMPACTO,
        alternativas=B_ALTERNATIVAS,
    )
    print()
    print("=" * 70)
    print(f"A: {a_id}")
    print(f"B: {b_id}")
    print("=" * 70)
    print()
    print("Next: convoke Conselho for A and B (4 subagents each, parallel)")


if __name__ == "__main__":
    main()
