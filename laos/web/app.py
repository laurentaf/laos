"""LAOS portfolio board — FastAPI + HTMX app.

A Trello-like view of all projects:
  GET  /                 board with 5 status columns
  GET  /projects/<id>    project detail (spec, cost, decisions, runs)
  POST /projects/new     scaffold a project from a workflow template
  GET  /healthz          liveness probe

Run:  uv run python -m laos.web.app
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from laos.web import portfolio

ROOT = Path(__file__).resolve().parent
TEMPLATES_DIR = ROOT / "templates"
STATIC_DIR = ROOT / "static"

app = FastAPI(title="LAOS Control Plane", version="0.2.0")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

STATUS_COLUMNS = [
    ("not_started", "Não iniciado"),
    ("planning", "Planejando"),
    ("running", "Rodando"),
    ("awaiting_decision", "Aguardando decisão"),
    ("completed", "Pronto para shipar"),
]


@app.get("/healthz", include_in_schema=False)
def healthz() -> dict:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def board(request: Request) -> HTMLResponse:
    projects = portfolio.list_projects()
    # bucket by status into columns
    columns = []
    for status, label in STATUS_COLUMNS:
        cols_projects = [p for p in projects if p["status"] == status]
        # unlisted statuses (e.g. 'active', 'delivered') go to first col
        if not columns:
            cols_projects = [p for p in projects
                             if p["status"] not in {s for s, _ in STATUS_COLUMNS}]
            columns.append((status, label, cols_projects))
        else:
            columns.append((status, label, cols_projects))
    return templates.TemplateResponse(
        request=request,
        name="board.html",
        context={"columns": columns, "total": len(projects)},
    )


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request) -> HTMLResponse:
    """Executive overview: whole portfolio at a glance (opção 3)."""
    projects = portfolio.list_projects()
    con = portfolio.schema.connect_readonly()

    # aggregates across all projects
    total_cost = sum(p["cost_usd"] for p in projects)
    total_tokens = sum(p["tokens"] for p in projects)
    total_errors = sum(p["errors"] for p in projects)
    total_runs = sum(p["run_count"] for p in projects)
    ship_ready = sum(1 for p in projects if p["ready_to_ship"])
    awaiting = [p for p in projects if p["status"] == "awaiting_decision"]
    running = [p for p in projects if p["status"] == "running"]
    not_started = [p for p in projects if p["status"] == "not_started"]

    # most expensive / most errors (top lists)
    by_cost = sorted(projects, key=lambda p: p["cost_usd"], reverse=True)[:5]
    by_errors = sorted(projects, key=lambda p: p["errors"], reverse=True)[:5]

    # capability health (probe from opencode.jsonc like laos gaps)
    cap_health = portfolio.probe_capability_health()

    # 8 itens de entrega por projeto (do handoff, para a dashboard)
    from laos.check import handoff as handoff_mod

    delivery = {}
    for p in projects:
        try:
            report = handoff_mod.handoff_report(p["name"])
            items = report["items"]
            delivery[p["name"]] = {
                "pasta": items.get("P1_onde_esta", {}).get("resposta"),
                "organizacao": items.get("P2_organizacao", {}).get("resposta"),
                "workflow": items.get("P3_workflow", {}).get("resposta"),
                "utilizar": items.get("P4_como_utilizar", {}).get("resposta"),
                "banco": items.get("P5_banco", {}).get("resposta"),
                "site": items.get("P6_site", {}).get("resposta"),
                "teste": items.get("P7_garantir_rodando", {}).get("resposta"),
                "ferramentas": items.get("P8_ferramentas", {}).get("resposta"),
                "ready": report.get("ready_for_client", False),
                "missing": report.get("missing_items", []),
            }
        except Exception:  # noqa: BLE001
            delivery[p["name"]] = {"ready": False, "missing": ["handoff erro"]}

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "projects": projects,
            "total_cost": total_cost,
            "total_tokens": total_tokens,
            "total_errors": total_errors,
            "total_runs": total_runs,
            "ship_ready": ship_ready,
            "awaiting": awaiting,
            "running": running,
            "not_started_count": len(not_started),
            "by_cost": by_cost,
            "by_errors": by_errors,
            "cap_health": cap_health,
            "delivery": delivery,
        },
    )


@app.get("/projects/{project_id}/handoff", response_class=HTMLResponse)
def project_handoff(request: Request, project_id: str) -> HTMLResponse:
    """Delivery report: 20 itens para quem esta shipando."""
    from laos.check import handoff

    if not portfolio.project_detail(project_id):
        return HTMLResponse("project not found", status_code=404)
    report = handoff.handoff_report(project_id)
    text = handoff.format_report(report)
    return templates.TemplateResponse(
        request=request,
        name="handoff.html",
        context={
            "p": portfolio.project_detail(project_id),
            "report": report,
            "text": text,
        },
    )


@app.get("/projects/{project_id}/console", response_class=HTMLResponse)
def project_console(request: Request, project_id: str) -> HTMLResponse:
    """Text console: LLM-aware planning + slash commands."""
    from laos.chat import console as chat_console

    if not portfolio.project_detail(project_id):
        return HTMLResponse("project not found", status_code=404)
    ctx = chat_console.project_context(project_id)
    history = chat_console.recent_messages(project_id)
    return templates.TemplateResponse(
        request=request,
        name="console.html",
        context={
            "p": portfolio.project_detail(project_id),
            "ctx": ctx,
            "history": history,
        },
    )


@app.post("/projects/{project_id}/console/send", response_class=HTMLResponse)
def console_send(request: Request, project_id: str, message: str = Form(...)) -> HTMLResponse:
    from laos.chat import console as chat_console

    chat_console.save_message(project_id, "user", message)
    reply = chat_console.handle(project_id, message)
    chat_console.save_message(project_id, "assistant", reply)
    return templates.TemplateResponse(
        request=request,
        name="console_thread.html",
        context={"reply": reply},
    )


@app.post("/projects/{project_id}/delete", response_class=HTMLResponse)
def delete_project_route(project_id: str) -> HTMLResponse:
    """Delete a project: DB state + archive folder (recoverable)."""
    result = portfolio.delete_project(project_id, archive_dir="projects_archived")
    return RedirectResponse(url="/", status_code=303)


@app.get("/projects/{project_id}", response_class=HTMLResponse)
def project_detail(request: Request, project_id: str) -> HTMLResponse:
    detail = portfolio.project_detail(project_id)
    if not detail:
        return HTMLResponse("project not found", status_code=404)
    return templates.TemplateResponse(
        request=request,
        name="project.html",
        context={"p": detail},
    )


@app.post("/projects/new", response_class=HTMLResponse)
def new_project(request: Request, project_name: str = Form(...)) -> HTMLResponse:
    root = portfolio._find_laos_root()
    pdir = root / "projects" / project_name
    pdir.mkdir(parents=True, exist_ok=True)
    py = pdir / "project.yaml"
    if not py.exists():
        py.write_text(
            "project_name: " + project_name + "\n"
            "brief: >\n"
            "  (preencher)\n"
            "needs: []\n"
            "deliverables: []\n"
            "status: not_started\n",
            encoding="utf-8",
        )
    return RedirectResponse(url=f"/projects/{project_name}", status_code=303)


# ─── edit actions (HTMX) ─────────────────────────────────────────────


@app.post("/projects/{project_id}/status", response_class=HTMLResponse)
def set_status(project_id: str, status: str = Form(...)) -> HTMLResponse:
    from laos.db import schema

    con = schema.connect()
    con.execute(
        "INSERT INTO projects (project_id, name, status) VALUES (?, ?, ?) "
        "ON CONFLICT (project_id) DO UPDATE SET status=?",
        [project_id, project_id, status, status],
    )
    return RedirectResponse(url=f"/projects/{project_id}", status_code=303)


@app.post("/projects/{project_id}/decisions/{decision_id}/decide",
          response_class=HTMLResponse)
def decide(project_id: str, decision_id: str,
           decided_value: str = Form(...)) -> HTMLResponse:
    from laos.db import schema

    con = schema.connect()
    con.execute(
        "UPDATE decisions SET status='decided', decided_value=?, "
        "decided_at=current_timestamp "
        "WHERE project_id=? AND decision_id=?",
        [decided_value, project_id, decision_id],
    )
    return RedirectResponse(url=f"/projects/{project_id}", status_code=303)


@app.post("/projects/{project_id}/todos/{todo_id}/toggle",
          response_class=HTMLResponse)
def toggle_todo(project_id: str, todo_id: str) -> HTMLResponse:
    from laos.db import schema

    con = schema.connect()
    con.execute(
        "UPDATE todos SET done = NOT done WHERE project_id=? AND todo_id=?",
        [project_id, todo_id],
    )
    return RedirectResponse(url=f"/projects/{project_id}", status_code=303)


# ─── actions (run/verify from the board) ─────────────────────────────


@app.post("/projects/{project_id}/actions", response_class=HTMLResponse)
def project_action(project_id: str, action: str = Form(...)) -> HTMLResponse:
    """Trigger a CLI action for the project: verify | run | gaps.
    Streams output back on the project page (non-blocking best effort).
    """
    import io
    import contextlib
    from laos import cli as laos_cli

    if action == "verify":
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            laos_cli.cmd_verify(
                type("A", (), {"project": project_id})()
            )
        return HTMLResponse(
            f"<div class='bg-slate-100 p-3 rounded text-xs whitespace-pre-wrap'>"
            f"{buf.getvalue()}</div>"
        )
    if action == "gaps":
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            laos_cli.cmd_gaps(
                type("A", (), {"project": project_id})()
            )
        return HTMLResponse(
            f"<div class='bg-slate-100 p-3 rounded text-xs whitespace-pre-wrap'>"
            f"{buf.getvalue()}</div>"
        )
    if action == "run":
        # run in background; return a note (user refreshes to see runs)
        import threading
        from laos.core import pipeline

        py = portfolio._find_laos_root() / "projects" / project_id / "project.yaml"

        def _run_bg():
            pipe = pipeline.RunPipeline(project_id, py,
                                        runner=pipeline.costed_runner)
            try:
                pipe.run(force_new=True)
            except Exception:  # noqa: BLE001
                pass

        t = threading.Thread(target=_run_bg, daemon=True)
        t.start()
        return HTMLResponse(
            "<div class='bg-emerald-50 p-3 rounded text-xs'>"
            "run iniciado em background — aguarde ~15s e recarregue para ver as fases.</div>"
        )
    return HTMLResponse("unknown action", status_code=400)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("laos.web.app:app", host="127.0.0.1", port=7331, reload=False)
