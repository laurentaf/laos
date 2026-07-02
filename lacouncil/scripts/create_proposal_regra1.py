"""
Create LACOUNCIL proposal: confidence_escalation_ladder + user_question_log.

Flow per AGENTS.md / lacouncil design:
  1. Build InvestigationResult (5-Whys + Fishbone).
  2. Persist via persist_investigation() -> sessoes_investigacao table.
  3. Create Proposal linked to session_id.
  4. Print proposal_id for downstream dispatch.

Run:  uv run --directory F:/Projetos/Laos/lacouncil python -m scripts.create_proposal_regra1
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure src is importable when running as a script
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


GAP = (
    "Regra 1 do LAOS (execute com máxima confiança; melhore a confiança antes de "
    "perguntar ao usuário) está codificada em AGENTS.md HR #11, "
    "knowledge/stack-decisions.md (Agreement Matrix) e workflows/wdl-contract.yaml "
    "(verdict tri-state) — mas a cascata não é executada mecanicamente. Quando o "
    "score de confiança é baixo (ex: 0.50 LOW) o sistema pode pular para perguntar "
    "ao usuário sem antes esgotar (a) KB lookup, (b) MCP health, (c) detect_patterns, "
    "(d) investigate. Falta enforcement, audit trail e detecção de padrões sobre "
    "perguntas repetidas ao usuário."
)


FIVE_WHYS = [
    "1. Por que o orchestrator às vezes pergunta ao usuário em vez de resolver? "
    "Porque a cascata de elevação de confiança não está codificada como workflow; "
    "ela é uma convenção espalhada entre AGENTS.md, stack-decisions.md e "
    "wdl-contract.yaml sem linkage explícito.",

    "2. Por que a cascata não é executada quando a confiança é baixa? "
    "Porque o wdl-contract.yaml só declara o verdict tri-state (READY/DEFER/ESCALATE); "
    "o caminho DEFER não tem um protocolo mandatório de ações; o orchestrator decide "
    "livremente entre investigar ou perguntar.",

    "3. Por que o orchestrator escolhe perguntar em vez de investigar? "
    "Porque perguntar é a ação de menor custo local — o orchestrator não tem "
    "mecanismo que torne a investigação obrigatória antes da pergunta.",

    "4. Por que não há mecanismo que force a investigação? "
    "Porque o Agreement Matrix tem limiares mas não tem actions acopladas; "
    "knowledge/stack-decisions.md é descritivo, não prescritivo.",

    "5. Por que a mesma pergunta se repete? "
    "Porque não há log das perguntas feitas ao usuário; lacouncil.detect_patterns() "
    "opera sobre projetos_registrados, não sobre interações com o usuário. "
    "Não há audit trail nem detecção de recorrência.",
]


FISHBONE = {
    "method": [
        "Cascata KB→MCP→detect_patterns→investigate→user não está em workflow declarativo",
        "Agreement Matrix em stack-decisions.md é descritivo, não prescritivo",
        "WDL verdict tri-state sem protocolo mandatório em DEFER",
    ],
    "machine": [
        "lacouncil.detect_patterns() só olha projetos_registrados",
        "Falta tabela user_questions no DuckDB do lacouncil",
        "Falta action step 'kb_query' / 'mcp_health' / 'investigate' no wdl-contract",
    ],
    "measurement": [
        "Sem contador de quantas perguntas foram feitas ao usuário por sessão",
        "Sem métrica de quantas perguntas viraram regra automaticamente",
        "Sem tracking de HITL-reduction rate ao longo do tempo",
    ],
    "manpower": [
        "Orchestrator decide livremente entre perguntar ou investigar",
        "Conselho só delibera em mudanças estruturais, não em padrão de uso",
    ],
    "material": [
        "Knowledge base tem princípios mas não tem actions acopladas",
        "Detect_patterns é genérico, não especializado em HITL patterns",
    ],
    "milieu": [
        "Falta linha em knowledge/opencode-permissions.md sobre 'no user question without prior investigation'",
        "Falta referência no wdl-contract.yaml linkando confidence < threshold a actions obrigatórias",
    ],
}


ROOT_CAUSES = [
    "Cascata de elevação de confiança é convenção dispersa, não workflow codificado.",
    "Sem audit trail de perguntas ao usuário, não há detecção de padrões HITL.",
    "Agreement Matrix tem thresholds mas não tem actions acopladas a scores baixos.",
]


PROPOSED_ACTION = (
    "Adicionar confidence_escalation_ladder em workflows/wdl-contract.yaml "
    "(KB→MCP→detect_patterns→investigate, todos obrigatórios antes de ask_user) "
    "+ tabela user_questions no DuckDB do lacouncil + auto-promote a regra quando "
    "detect_patterns encontra ≥3 ocorrências."
)


def main() -> None:
    inv = InvestigationResult(
        gap=GAP,
        five_whys=FIVE_WHYS,
        fishbone=FISHBONE,
        root_causes=ROOT_CAUSES,
        proposed_action=PROPOSED_ACTION,
    )
    persisted = persist_investigation(inv)
    print(f"investigation session_id={persisted.session_id}")

    titulo = (
        "Confidence Escalation Ladder + User Question Log "
        "(codifica Regra 1 do LAOS mecanicamente)"
    )
    descricao = (
        "Formalizar a Regra 1 do LAOS — execute com máxima confiança; melhore a "
        "confiança antes de perguntar ao usuário — em duas peças complementares: "
        "(1) confidence_escalation_ladder em workflows/wdl-contract.yaml, uma "
        "cascata mandatória que dispara quando o WDL verdict é DEFER ou "
        "confidence < threshold, executando em ordem (a) kb_lookup via lacouncil, "
        "(b) mcp_health probe, (c) detect_patterns, (d) investigate; só após "
        "esgotar as 4 camadas (ou cada uma retornar 'no improvement') o workflow "
        "pode emitir recommendation: ask_user. (2) Tabela user_questions no "
        "DuckDB do lacouncil (memoria/lacouncil.duckdb), auto-populada pelo "
        "orchestrator em cada pergunta ao usuário, com detect_patterns rodando "
        "ao fim da sessão; ≥3 ocorrências sobre a mesma classe de pergunta gera "
        "automaticamente uma proposta LACOUNCIL para formalizar como regra. "
        "Cobre o gap: princípio em convenção dispersa, sem enforcement, sem "
        "audit, sem detecção de recorrência."
    )
    contexto = (
        "LAOS Regra 1 foi declarada em sessão de 2026-07-02; orchestrator mapeou "
        "as 4 camadas já codificadas (KB local, MCP, WDL gate, subagente) e "
        "identificou 2 mecanismos faltantes para HITL-reduction mecânica. "
        "Hard Rule #7 (3+ ocorrências) já existe; basta aplicar à interação "
        "com o usuário."
    )
    mudanca = (
        "(1) Adicionar seção confidence_escalation_ladder em "
        "workflows/wdl-contract.yaml com 4 actions obrigatórias e ordem; "
        "gating: ask_user só pode ser emitido se as 4 retornarem "
        "no_improvement. (2) Adicionar tabela user_questions no schema "
        "DuckDB do lacouncil (migration idempotente); colunas: question_id "
        "UUID PK, question_text TEXT, context_json JSON, asked_at TIMESTAMP, "
        "answered_with TEXT, session_id VARCHAR. (3) Adicionar modelo "
        "UserQuestion em lacouncil/core/schemas.py. (4) Adicionar "
        "user_questions.py em lacouncil/core/ com log() e detect_user_question_"
        "patterns() (≥3 ocorrências → auto-create LACOUNCIL proposal). "
        "(5) Atualizar orchestrator.md para chamar log() antes de perguntar "
        "e rodar detect_user_question_patterns() no fim de cada sessão. "
        "(6) Adicionar linha em knowledge/padroes-entrega.md P1: 'HITL só "
        "após confidence_escalation_ladder exhausted'."
    )
    impacto = (
        "Positivo: reduz HITL automaticamente; princípio Regra 1 vira "
        "mecanismo em vez de convenção; audit trail permanente; permite "
        "medir HITL-reduction rate ao longo do tempo. Risco: auto-promoção "
        "prematura de regras com amostra insuficiente. Mitigação: limiar "
        "≥3 ocorrências (matches HR #7) + confidence ≥0.80 requerido para "
        "auto-create proposal. Files affected: workflows/wdl-contract.yaml, "
        "lacouncil/src/lacouncil/core/{duckdb_store,schemas}.py, novo "
        "lacouncil/src/lacouncil/core/user_questions.py, .opencode/agent/"
        "orchestrator.md, knowledge/padroes-entrega.md."
    )
    alternativas = (
        "(A) Documentar princípio em knowledge/ sem enforcement — rejeitada: "
        "mesmo gap, só escrito. (B) Serviço separado fora do lacouncil — "
        "rejeitada: viola HR #1 (no implementation in LAOS). (C) Só "
        "user_question_log sem confidence_escalation_ladder — rejeitada: "
        "detecta mas não enforça. (D) Limiar ≥5 em vez de ≥3 — rejeitada: "
        "HR #7 já estabelece ≥3 como padrão; manter consistência."
    )

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

    print(f"proposal_id={saved.proposal_id}")
    print(f"categoria={saved.categoria.value} estrategia={saved.estrategia.value}")
    print(f"status={saved.status.value}")
    print(f"created_by_session={saved.created_by_session}")
    print(f"signature={saved.signature[:16]}...")


if __name__ == "__main__":
    main()
