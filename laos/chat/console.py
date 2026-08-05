"""LAOS chat — build project context + run text console.

The console answers two things the board cannot:
  1. "what's next / review errors" — the LLM gets the REAL project state
     (phases, runs, errors, deliverables, gaps) as context and reasons
     about it.
  2. "insert items" — slash commands mutate the DuckDB state:
       /todo <text>      add a todo
       /fases            show phases
       /erros            show run errors
       /gaps             show capability gaps
       /run              run the pipeline (background)
       /verify           verify deliverables
       /decidir <q>      add a pending decision
       /status <novo>    change project status
     Plain text (no slash) goes to the LLM with project context.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import threading
import uuid
import urllib.request
from datetime import datetime, timezone

from laos.db import schema

LITELLM_URL = "http://localhost:4000/v1/chat/completions"
LITELLM_KEY = "sk-laos-master"
MODEL = "deepseek-v4-flash"
CREATE_NO_WINDOW = 0x08000000


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


# ─── context builder ─────────────────────────────────────────────────


def project_context(project_id: str) -> str:
    """Human-readable snapshot of the project state (what the LLM sees)."""
    con = schema.connect()
    lines = [f"# Projeto: {project_id}"]

    prow = con.execute(
        "SELECT status, ready_to_ship FROM projects WHERE project_id=?",
        [project_id],
    ).fetchone()
    lines.append(f"Status: {prow[0] if prow else 'não registrado'}"
                 f" | ship-ready: {bool(prow[1]) if prow else False}")

    phases = con.execute(
        "SELECT phase, name, status, cost_usd, tokens, errors "
        "FROM phases WHERE project_id=? ORDER BY phase", [project_id],
    ).fetchall()
    if phases:
        lines.append("\n## Fases (do mais recente para o próximo):")
        for p in phases:
            lines.append(f"  - fase {p[0]} {p[1]}: {p[2]} "
                         f"(custo ${p[3]:.4f}, {p[4]} tokens, {p[5]} erros)")
    else:
        lines.append("\n## Fases: nenhuma registrada ainda.")

    runs = con.execute(
        "SELECT run_id, status, cost_usd, errors, started_at FROM runs "
        "WHERE project_id=? ORDER BY started_at DESC LIMIT 5", [project_id],
    ).fetchall()
    if runs:
        lines.append("\n## Runs recentes:")
        for r in runs:
            lines.append(f"  - {r[0]}: {r[1]} (custo ${r[2]:.4f}, "
                         f"{r[3]} erros, {r[4]})")
    else:
        lines.append("\n## Runs: nenhuma.")

    errs = con.execute(
        "SELECT s.run_id, s.step_type, s.error_class, s.tool "
        "FROM steps s WHERE s.status='failed' AND s.run_id IN "
        "(SELECT run_id FROM runs WHERE project_id=?) ORDER BY s.ts DESC LIMIT 5",
        [project_id],
    ).fetchall()
    if errs:
        lines.append("\n## Últimos erros:")
        for e in errs:
            lines.append(f"  - {e[0]} [{e[1]}]: {e[2]} (tool: {e[3]})")
    else:
        lines.append("\n## Erros: nenhum registrado.")

    dels = con.execute(
        "SELECT name, exists_, passes_test FROM deliverables "
        "WHERE project_id=?", [project_id],
    ).fetchall()
    if dels:
        lines.append("\n## Deliverables (verificação):")
        for d in dels:
            lines.append(f"  - {d[0]}: {'existe' if d[1] else 'faltando'} / "
                         f"{'passou' if d[2] else 'falhou'}")
    else:
        lines.append("\n## Deliverables: nenhum verificado.")

    gaps = con.execute(
        "SELECT need, missing_capability FROM capability_gaps WHERE project_id=?",
        [project_id],
    ).fetchall()
    if gaps:
        lines.append("\n## Gaps de capability:")
        for g in gaps:
            lines.append(f"  - {g[0]}: falta {g[1]}")

    decs = con.execute(
        "SELECT question FROM decisions WHERE project_id=? AND status='pending'",
        [project_id],
    ).fetchall()
    if decs:
        lines.append("\n## Decisões pendentes:")
        for d in decs:
            lines.append(f"  - {d[0]}")

    return "\n".join(lines)


# ─── slash commands (deterministic, no LLM) ─────────────────────────


def _cmd_planejar(project_id: str, extra: str) -> str:
    """Gera o plano do projeto (LLM) e registra cada fase como ToDo.

    O usuário confere a lista de ToDos faseados, remove/adiciona com
    /todo-del e /todo, e só então decide rodar (/run).
    """
    from laos.plan import planner

    root = _laos_root()
    py = root / "projects" / project_id / "project.yaml"
    if not py.exists():
        return f"project.yaml não encontrado para {project_id}"
    try:
        data = planner.load_contract(project_id)
    except Exception as e:  # noqa: BLE001
        return f"erro lendo contrato: {e}"
    try:
        analysis = planner.deep_think(data)
        phases = planner.build_plan(data, analysis)
    except Exception as e:  # noqa: BLE001
        return f"erro gerando plano: {type(e).__name__}: {e}"

    con = schema.connect()
    # limpa todos do plano anterior para não duplicar
    con.execute("DELETE FROM todos WHERE project_id=? AND source='plano'",
                [project_id])
    added = []
    for p in phases:
        tid = f"todo_{uuid.uuid4().hex[:8]}"
        stage = p.get("stage", 0)
        name = p.get("name", "?")
        spec = (p.get("spec") or "")[:160]
        text = f"[Fase {stage}] {name}: {spec}"
        con.execute(
            "INSERT INTO todos (project_id, todo_id, text, source) "
            "VALUES (?,?,?,'plano')", [project_id, tid, text],
        )
        added.append(tid)

    out = [
        f"PLANO GERADO: {len(added)} fases registradas como ToDos.",
        "",
        "Confira abaixo — remova com /todo-del <id>, adicione com /todo <texto>.",
        "Quando estiver bom, rode /run para executar em ordem.",
        "",
        "/todos para ver a lista completa.",
    ]
    return "\n".join(out)


def run_command(project_id: str, line: str) -> str:
    """Handle /slash commands. Returns response text."""
    parts = line.strip().split(" ", 1)
    cmd = parts[0].lower()
    rest = parts[1].strip() if len(parts) > 1 else ""
    con = schema.connect()

    if cmd in ("/todo", "/t"):
        if not rest:
            return "uso: /todo <texto>"
        tid = f"todo_{uuid.uuid4().hex[:8]}"
        con.execute(
            "INSERT INTO todos (project_id, todo_id, text, source) "
            "VALUES (?,?,?,'console')", [project_id, tid, rest],
        )
        return f"todo adicionado: {rest}"
    if cmd == "/todo-del":
        if not rest:
            return "uso: /todo-del <id ou parte do texto>"
        # remove by id or by text substring
        row = con.execute(
            "SELECT todo_id FROM todos WHERE project_id=? AND "
            "(todo_id=? OR text LIKE ?) LIMIT 1",
            [project_id, rest, f"%{rest}%"],
        ).fetchone()
        if not row:
            return f"todo não encontrado: {rest}  (use /todos para ver os ids)"
        con.execute("DELETE FROM todos WHERE project_id=? AND todo_id=?",
                    [project_id, row[0]])
        return f"todo removido: {rest}"
    if cmd == "/todos":
        rows = con.execute(
            "SELECT todo_id, text, done, source FROM todos WHERE project_id=?",
            [project_id],
        ).fetchall()
        if not rows:
            return "sem todos. use /planejar para gerar as fases como todos, ou /todo <texto>"
        lines = []
        for r in rows:
            mark = "[x]" if r[2] else "[ ]"
            lines.append(f"  {mark} {r[0]} {r[1]}  ({r[3]})")
        return "\n".join(lines)
    if cmd == "/planejar":
        return _cmd_planejar(project_id, rest)
    if cmd == "/todos-limpar":
        n = con.execute(
            "DELETE FROM todos WHERE project_id=? AND source='plano'",
            [project_id],
        ).fetchone()
        return f"todos do plano removidos ({n[0] if n else 0})"
    if cmd == "/fases":
        rows = con.execute(
            "SELECT phase, name, status, cost_usd, tokens, errors "
            "FROM phases WHERE project_id=? ORDER BY phase", [project_id],
        ).fetchall()
        return "\n".join(
            f"fase {r[0]} {r[1]}: {r[2]} (${r[3]:.4f}, {r[4]} tok, {r[5]} err)"
            for r in rows) or "sem fases"
    if cmd == "/erros":
        rows = con.execute(
            "SELECT s.run_id, s.step_type, s.error_class FROM steps s "
            "WHERE s.status='failed' AND s.run_id IN "
            "(SELECT run_id FROM runs WHERE project_id=?) "
            "ORDER BY s.ts DESC LIMIT 10", [project_id],
        ).fetchall()
        return "\n".join(f"{r[0]} [{r[1]}]: {r[2]}" for r in rows) or "sem erros"
    if cmd == "/gaps":
        rows = con.execute(
            "SELECT need, missing_capability FROM capability_gaps "
            "WHERE project_id=?", [project_id],
        ).fetchall()
        return "\n".join(f"{r[0]} -> falta {r[1]}" for r in rows) or "sem gaps"
    if cmd == "/status":
        if not rest:
            return "uso: /status <not_started|planning|running|awaiting_decision|completed|failed>"
        con.execute(
            "INSERT INTO projects (project_id, name, status) VALUES (?,?,?) "
            "ON CONFLICT (project_id) DO UPDATE SET status=?",
            [project_id, project_id, rest, rest],
        )
        return f"status -> {rest}"
    if cmd == "/decidir":
        if not rest:
            return "uso: /decidir <pergunta pendente>"
        did = f"dec_{uuid.uuid4().hex[:8]}"
        con.execute(
            "INSERT INTO decisions (project_id, decision_id, question, "
            "cluster_id, status) VALUES (?,?,?,'console','pending')",
            [project_id, did, rest],
        )
        return f"decisão pendente adicionada: {rest}"
    if cmd == "/verify":
        from laos.verify import engine

        root = _laos_root()
        try:
            results, ok = engine.verify_project(root, project_id)
            summary = "\n".join(
                f"  {r.deliverable}: {'OK' if r.ok else 'FALHA'}"
                for r in results
            )
            return f"verify: {'TUDO OK' if ok else 'HÁ FALHAS'}\n{summary}"
        except Exception as e:  # noqa: BLE001
            return f"verify falhou: {type(e).__name__}: {e}"
    if cmd == "/run":
        py = _laos_root() / "projects" / project_id / "project.yaml"
        if not py.exists():
            return f"project.yaml não encontrado para {project_id}"
        from laos.core import pipeline

        def _bg():
            try:
                pipe = pipeline.RunPipeline(project_id, py,
                                            runner=pipeline.costed_runner)
                pipe.run(force_new=True)
            except Exception:  # noqa: BLE001
                pass

        threading.Thread(target=_bg, daemon=True).start()
        return "run iniciado em background — /fases em ~15s"
    if cmd == "/help":
        return ("comandos: /planejar · /todos · /todo <texto> · /todo-del <id> · "
                "/todos-limpar · /fases · /erros · /gaps · /status <novo> · "
                "/decidir <pergunta> · /verify · /run · /help\n\n"
                "/planejar: gera as fases do projeto como ToDos (confira, "
                "edite com /todo-del e /todo, depois /run)\n"
                "texto livre (sem /) vai para a LLM com o contexto do projeto")
    return f"comando desconhecido: {cmd} (/help para a lista)"


# ─── LLM chat ────────────────────────────────────────────────────────


def _cached_reply(project_id: str, message: str) -> str | None:
    """Return the cached assistant reply for this exact prompt, if any.

    Consistency: the same user message in the same project always yields
    the same answer (no token cost, no variance). We look for a PAIR
    (user=message, assistant) that already exists — the assistant reply
    that came after a previous identical user message.
    """
    try:
        con = schema.connect()
        # find a previous user message equal to this one
        rows = con.execute(
            "SELECT msg_id FROM chat_messages WHERE project_id=? AND role='user' "
            "AND content=? ORDER BY ts DESC",
            [project_id, message],
        ).fetchall()
        # the most recent one is the current in-flight message (reply not
        # written yet); use the SECOND most recent, which has a reply
        prev_ids = [r[0] for r in rows]
        if len(prev_ids) < 2:
            return None
        prev_id = prev_ids[1]
        # assistant reply that came AFTER the previous user message
        # (compare by ts — msg_id is a uuid, not chronological)
        arow = con.execute(
            "SELECT content FROM chat_messages WHERE project_id=? AND role='assistant' "
            "AND ts > (SELECT ts FROM chat_messages WHERE msg_id=?) "
            "ORDER BY ts ASC LIMIT 1",
            [project_id, prev_id],
        ).fetchone()
        if not arow:
            return None
        return arow[0]
    except Exception:  # noqa: BLE001
        return None


def chat(project_id: str, message: str) -> str:
    """Send a message to the LLM with the project context baked in.

    Deterministic: temperature 0 + exact-prompt cache. The same message
    in the same project always returns the same answer.
    """
    cached = _cached_reply(project_id, message)
    if cached is not None:
        return cached
    ctx = project_context(project_id)
    system = (
        "Você é o console de planejamento do LAOS. O usuário está "
        "evoluindo este projeto e precisa de ajuda para decidir as "
        "próximas fases, revisar erros e planejar. Use o contexto "
        "real do projeto abaixo (NUNCA invente dados). Responda em "
        "português, direto, com próximos passos concretos quando "
        "aplicável.\n\n"
        "REGRA DE ESCOPO: se o pedido for GRANDE (ex: 'um sistema tipo "
        "YouTube', 'um app completo', 'uma plataforma'), NUNCA tente "
        "descrever o sistema inteiro numa resposta. Em vez disso:\n"
        "  1. Responda com o ESQUELETO do MVP: arquitetura em 3-5 linhas, "
        "   modelo de dados central, e 4-6 FASES razoáveis para construir "
        "   o MVP (cada fase = 1 artefato entregável).\n"
        "  2. Diga que cada fase pode ser aprofundada sob pedido, e que "
        "   /planejar transforma as fases em ToDos.\n"
        "  3. NÃO liste dezenas de features — foque no MVP iterável.\n"
        "Pedidos pequenos (uma pergunta, uma fase) responda direto.\n\n"
        f"--- CONTEXTO DO PROJETO ---\n{ctx}"
    )
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": message},
        ],
        # output budget for planning answers (phases, steps, reasoning).
        # 1024 was cutting long plans mid-response; the input context
        # window is separate (1M) and unaffected.
        "max_tokens": 8192,
        "temperature": 0.6,
    }
    req = urllib.request.Request(
        LITELLM_URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {LITELLM_KEY}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:  # noqa: BLE001
        return f"ERRO ao chamar a LLM: {type(e).__name__}: {str(e)[:300]}"


def handle(project_id: str, message: str) -> str:
    """Entry point: slash command or LLM chat."""
    if message.strip().startswith("/"):
        return run_command(project_id, message)
    return chat(project_id, message)


def _laos_root() -> pathlib.Path:
    from laos.core import needs

    return needs._find_laos_root()


# ─── persistence of console messages ─────────────────────────────────


def save_message(project_id: str, role: str, content: str) -> None:
    con = schema.connect()
    mid = f"msg_{uuid.uuid4().hex[:8]}"
    con.execute(
        "INSERT INTO chat_messages (project_id, msg_id, role, content, ts) "
        "VALUES (?,?,?,?,current_timestamp)",
        [project_id, mid, role, content],
    )


def recent_messages(project_id: str, limit: int = 30) -> list[dict]:
    con = schema.connect()
    rows = con.execute(
        "SELECT role, content, ts FROM chat_messages "
        "WHERE project_id=? ORDER BY ts DESC LIMIT ?",
        [project_id, limit],
    ).fetchall()
    return [dict(zip(["role", "content", "ts"], r)) for r in reversed(rows)]
