"""LAOS CLI — control plane surface.

Commands:
  laos doctor        system + schema health
  laos projects      list portfolio (Trello-board data)
  laos run           start a run (wraps a stage; persists state)
  laos resume        resume an incomplete run from last persisted step
  laos status        show runs status
  laos cost          cost per project/model/phase
  laos trace         step-by-step of a run
  laos verify        check deliverables exist per project.yaml
  laos gaps          capability gaps per project needs
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from laos.db import schema
from laos.core import needs as needs_mod
from laos.core import run_state
from laos.core import pipeline

STATUS_LABELS = {
    "not_started": "não-iniciado",
    "planning": "planejando",
    "running": "rodando",
    "awaiting_decision": "aguardando-decisão",
    "completed": "pronto-para-shipar",
    "failed": "falhou",
}


# ─── doctor ───────────────────────────────────────────────────────────


def cmd_doctor(_args: argparse.Namespace) -> int:
    print("LAOS doctor")
    print("=" * 50)
    root = needs_mod._find_laos_root()
    print(f"root:       {root}")
    print(f"laos ver:   {__import__('laos').__version__}")

    # registry routing map
    try:
        routing = needs_mod.load_routing_map(root)
        print(f"registry:   OK ({len(routing)} needs mapped)")
    except Exception as e:  # noqa: BLE001
        print(f"registry:   FAIL ({e})")
        return 1

    # schema
    try:
        con = schema.connect()
        missing, present = schema.verify_schema(con)
        if missing:
            print(f"schema:     FAIL (missing tables: {missing})")
            return 1
        print(f"schema:     OK ({len(present)} tables) @ {schema.db_path()}")
    except Exception as e:  # noqa: BLE001
        print(f"schema:     FAIL ({e})")
        return 1

    print("-" * 50)
    print("DOCTOR_PASS")
    return 0


# ─── projects (portfolio board data) ──────────────────────────────────


def cmd_projects(args: argparse.Namespace) -> int:
    root = needs_mod._find_laos_root()
    projects_dir = root / "projects"
    con = schema.connect()
    print(f"{'project':<28} {'status':<22} {'last_run':<26}")
    print("-" * 76)
    for pdir in sorted(projects_dir.iterdir()):
        py = pdir / "project.yaml"
        if not py.exists():
            continue
        data = _load_yaml(py)
        name = data.get("project_name", pdir.name)
        row = con.execute(
            "SELECT status, last_run_id FROM projects WHERE project_id=?",
            [name],
        ).fetchone()
        status = row[0] if row else data.get("status", "not_started")
        last_run = (row[1] or "")[:24] if row else "-"
        label = STATUS_LABELS.get(status, status)
        print(f"{name:<28} {label:<22} {last_run:<26}")
    return 0


def _load_yaml(path: Path) -> dict:
    import yaml

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:  # noqa: BLE001
        data = {}
    return data if isinstance(data, dict) else {}


# ─── run / resume ─────────────────────────────────────────────────────


def cmd_run(args: argparse.Namespace) -> int:
    """Run a project's stages with auto-resume (resumes incomplete run)."""
    root = needs_mod._find_laos_root()
    py = root / "projects" / args.project / "project.yaml"
    if not py.exists():
        print(f"RUN_ERR: {py} not found")
        return 1
    pipe = pipeline.RunPipeline(args.project, py)
    run_id = pipe.run(force_new=args.force_new)
    print(f"RUN_DONE: {run_id} (status: completed)")
    return 0


def cmd_resume(args: argparse.Namespace) -> int:
    """Resume an incomplete run from the last persisted step."""
    root = needs_mod._find_laos_root()
    project = args.project or _project_for_run(args.run_id)
    if not project:
        print("RESUME_ERR: specify --project or --run-id")
        return 1
    py = root / "projects" / project / "project.yaml"
    if not py.exists():
        print(f"RESUME_ERR: {py} not found")
        return 1
    pipe = pipeline.RunPipeline(project, py)
    run_id = pipe.resume()
    if not run_id:
        print("RESUME_NOTHING: no incomplete run for project")
        return 1
    print(f"RESUME_DONE: {run_id}")
    return 0


def _project_for_run(run_id: str | None) -> str | None:
    if not run_id:
        return None
    rs = run_state.RunState()
    try:
        row = rs.con.execute(
            "SELECT project_id FROM runs WHERE run_id=?", [run_id]
        ).fetchone()
        return row[0] if row else None
    except Exception:  # noqa: BLE001
        return None


# ─── status / cost / trace ────────────────────────────────────────────


def cmd_status(_args: argparse.Namespace) -> int:
    con = schema.connect()
    rows = con.execute(
        "SELECT run_id, project_id, status, cost_usd, errors, "
        "started_at FROM runs ORDER BY started_at DESC LIMIT 20"
    ).fetchall()
    print(f"{'run_id':<24} {'project':<24} {'status':<10} {'cost':<8} {'errs':<5}")
    print("-" * 75)
    for r in rows:
        cost = f"${r[3]:.4f}" if r[3] else "-"
        print(f"{r[0]:<24} {r[1]:<24} {r[2]:<10} {cost:<8} {r[4]:<5}")
    return 0


def cmd_cost(args: argparse.Namespace) -> int:
    con = schema.connect()
    if args.project:
        rows = con.execute(
            "SELECT project_id, status, cost_usd, tokens, errors, retries "
            "FROM runs WHERE project_id=? ORDER BY started_at DESC",
            [args.project],
        ).fetchall()
    else:
        rows = con.execute(
            "SELECT project_id, status, cost_usd, tokens, errors, retries "
            "FROM runs ORDER BY started_at DESC"
        ).fetchall()
    print(f"{'project':<24} {'status':<10} {'cost_usd':<10} {'tokens':<10} {'errs':<6}")
    print("-" * 62)
    for r in rows:
        print(f"{r[0]:<24} {r[1]:<10} {r[2]:<10.4f} {r[3]:<10} {r[4]:<6}")
    return 0


def cmd_trace(args: argparse.Namespace) -> int:
    con = schema.connect()
    try:
        summary = con.execute(
            "SELECT run_id, project_id, status, cost_usd, tokens, errors "
            "FROM runs WHERE run_id=?", [args.run_id]
        ).fetchone()
    except Exception as e:  # noqa: BLE001
        print(f"TRACE_ERR: {e}")
        return 1
    if not summary:
        print(f"TRACE_NONE: run {args.run_id} not found")
        return 1
    print(f"run {summary[0]} | project={summary[1]} | status={summary[2]} "
          f"| cost=${summary[3]:.4f} | tokens={summary[4]} | errors={summary[5]}")
    steps = con.execute(
        "SELECT step_type, agent, status, error_class, tool, ts "
        "FROM steps WHERE run_id=? ORDER BY ts", [args.run_id]
    ).fetchall()
    for s in steps:
        err = f" [{s[3]}]" if s[3] else ""
        print(f"  {s[0]:<20} {s[1]:<16} {s[2]:<10} {s[4]}{err}  {s[5]}")
    return 0


# ─── verify (guaranteed check — P0: existence + spec match; P4: full) ──


def cmd_verify(args: argparse.Namespace) -> int:
    """Check deliverables declared in project.yaml exist, load, pass tests."""
    from laos.verify import engine

    root = needs_mod._find_laos_root()
    results, all_ok = engine.verify_project(root, args.project)
    if not results:
        print("VERIFY_NONE: no deliverables declared")
        return 0
    print(f"{'deliverable':<32} {'exists':<8} {'imports':<8} {'test':<6} {'spec':<6}")
    print("-" * 62)
    for r in results:
        print(f"{r.deliverable:<32} "
              f"{'OK' if r.exists else 'MISSING':<8} "
              f"{'OK' if r.imports else 'FAIL':<8} "
              f"{'OK' if r.passes_test else 'FAIL':<6} "
              f"{'OK' if r.spec_match else 'NO':<6}")
        for n in r.notes:
            print(f"    {n}")
    print("-" * 62)
    print("VERIFY_PASS (ready-to-ship)" if all_ok else "VERIFY_FAIL")
    return 0 if all_ok else 1


# ─── gaps (capability gaps — P0: registry-based; P4: MCP probe) ────────


def cmd_gaps(args: argparse.Namespace) -> int:
    """Capability gaps: needs resolved to capabilities + MCP health probe."""
    import subprocess
    import sys as _sys

    root = needs_mod._find_laos_root()
    py = root / "projects" / args.project / "project.yaml"
    if not py.exists():
        print(f"GAPS_ERR: {py} not found")
        return 1
    data = _load_yaml(py)
    needs = data.get("needs", []) or []
    if not needs:
        print("GAPS_NONE: no needs declared")
        return 0
    try:
        resolved = needs_mod.resolve_needs(needs, root)
    except KeyError as e:
        print(f"GAPS_BLOCKED: {e}")
        return 1
    print(f"{'need':<24} {'primary':<28} {'status':<10}")
    print("-" * 64)
    # unique primary capabilities to probe
    caps = needs_mod.primary_capabilities_for(needs, root)
    cap_status: dict[str, str] = {}
    for c in caps:
        # probe via MCP health when the tool exists; else mark unknown
        ok = _probe_mcp(c)
        cap_status[c] = "OK" if ok else "DOWN/UNKNOWN"
    for need, info in resolved.items():
        prim = ",".join(info.get("primary", []))
        statuses = [cap_status.get(c, "?") for c in info.get("primary", [])]
        status = "/".join(statuses)
        print(f"{need:<24} {prim:<28} {status:<10}")
    print("-" * 64)
    down = [c for c, s in cap_status.items() if s != "OK"]
    if down:
        print(f"GAPS_FOUND: capability MCP down/unavailable: {down}")
        return 1
    print("GAPS_PASS: all capability MCPs healthy")
    return 0


def _probe_mcp(cap: str) -> bool:
    """Best-effort MCP health probe from .opencode/opencode.jsonc.

    Textual block scan (robust against jsonc comment/URL quirks):
    find the block starting at '"<cap>":' and check for 'enabled: false'.
    Remote type is assumed healthy.
    """
    root = needs_mod._find_laos_root()
    cfg = root / ".opencode" / "opencode.jsonc"
    if not cfg.exists():
        return True
    try:
        text = cfg.read_text(encoding="utf-8")
    except OSError:
        return True
    # find the entry block for this capability: from the marker to the
    # next top-level key (line starting with two spaces + quote + key)
    marker = f'"{cap}":'
    idx = text.find(marker)
    if idx == -1:
        return True  # not declared -> assume platform/ok
    rest = text[idx:]
    # next key boundary: a line like '    "something": {' at column >= 2
    import re as _re

    m = _re.search(r'\n\s{2,}"[a-z0-9-]+":\s*\{', rest[10:])
    end = idx + 10 + (m.start() if m else 800)
    block = text[idx:end]
    if '"type": "remote"' in block:
        return True
    if '"enabled": false' in block:
        return False
    return True


# ─── entry point ──────────────────────────────────────────────────────


def cmd_backup(args: argparse.Namespace) -> int:
    """Backup + push versionado (substitui _backup_A.py + git_commit_push).

    Steps:
      1. git add -A (tudo rastreado)
      2. git commit com mensagem datada (se houver mudanças)
      3. git push origin main
    Registra o backup na tabela runs (project_id='_backup') para auditoria.
    """
    import subprocess
    import sys as _sys
    from datetime import datetime

    root = needs_mod._find_laos_root()
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    rs = run_state.RunState()
    run_id = rs.start_run("_backup")

    def _git(*args: str) -> tuple[int, str]:
        r = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True, text=True, creationflags=0x08000000, timeout=300,
        )
        return r.returncode, (r.stdout or "") + (r.stderr or "")

    step = rs.start_step("backup_commit", "laos", tool="git")
    code, out = _git("add", "-A")
    if code != 0:
        rs.end_step(step, "failed", error_class="git_add")
        print(f"BACKUP_FAIL: git add: {out}")
        return 1
    code, out = _git("commit", "-m", f"backup: {ts} (laos backup)")
    if code != 0 and "nothing to commit" not in out.lower():
        rs.end_step(step, "failed", error_class="git_commit")
        print(f"BACKUP_FAIL: git commit: {out}")
        return 1
    rs.end_step(step, "completed")

    step = rs.start_step("backup_push", "laos", tool="git")
    code, out = _git("push", "origin", "main")
    if code != 0:
        rs.end_step(step, "failed", error_class="git_push")
        print(f"BACKUP_FAIL: git push: {out}")
        return 1
    rs.end_step(step, "completed")
    rs.complete_run("completed")
    print(f"BACKUP_DONE: {ts} (run {run_id})")
    return 0


def cmd_handoff(args: argparse.Namespace) -> int:
    """Delivery handoff report: 20 itens para quem esta shipando."""
    from laos.check import handoff

    report = handoff.handoff_report(args.project)
    print(handoff.format_report(report))
    return 0 if report["ready_for_client"] else 1


def cmd_plan(args: argparse.Namespace) -> int:
    """Planning phase: preenche lacunas do contrato, propoe fases, salva.

    `laos plan <proj>` — analisa o project.yaml, detecta gaps, usa a LLM
    para propor o workflow esperado (fases ordenadas com specs), salva o
    contrato completo. `--run` dispara o pipeline ao final.
    """
    from laos.plan import planner

    try:
        result = planner.plan_project(args.project, brief=args.brief)
    except FileNotFoundError as e:
        print(f"PLAN_ERR: {e}")
        return 1
    except Exception as e:  # noqa: BLE001
        print(f"PLAN_ERR: {type(e).__name__}: {e}")
        return 1

    print(f"PLAN_DONE: {result['project_id']} | status={result['status']}")
    print(f"  gaps encontrados: {len(result['gaps_found'])}")
    for g in result["gaps_found"]:
        print(f"    - {g}")

    # análise profunda (passada 1) — prova que a LLM pensou antes
    analysis = result.get("analysis") or {}
    if analysis:
        print(f"\n  ANÁLISE PROFUNDA:")
        print(f"    modelo de dados: {str(analysis.get('modelo_dados',''))[:200]}")
        for q in (analysis.get("perguntas_abertas") or []):
            print(f"    ? {q[:120]}")
        for r in (analysis.get("regras_negocio") or [])[:3]:
            print(f"    • regra: {r[:120]}")
        for r in (analysis.get("riscos") or [])[:3]:
            print(f"    ⚠ risco: {r[:120]}")

    print(f"\n  fases propostas: {result['phases_proposed']}")
    for d in result["contract"].get("deliverables", []) or []:
        print(f"    fase {d.get('stage')} {d.get('name')}: {d.get('label','')}")

    if args.run and result["status"] in ("planned", "ready"):
        print("\n[laos plan] disparando run...")
        from laos.core import pipeline, runners

        root = needs_mod._find_laos_root()
        py = root / "projects" / args.project / "project.yaml"
        pipe = pipeline.RunPipeline(args.project, py, runner=runners.llm_artifact_runner)
        run_id = pipe.run(force_new=True)
        print(f"RUN_DONE: {run_id}")
    return 0


def cmd_server(_args: argparse.Namespace) -> int:
    """Start the portfolio board server (background, windowless)."""
    import subprocess
    import sys as _sys

    proc = subprocess.Popen(
        [_sys.executable, "-m", "uvicorn", "laos.web.app:app",
         "--host", "127.0.0.1", "--port", "7331"],
        cwd=str(needs_mod._find_laos_root()),
        creationflags=0x08000000 | 0x00000008,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    print(f"SERVER_STARTED pid={proc.pid} -> http://127.0.0.1:7331")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="laos", description="LAOS control plane")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("doctor", help="system + schema health")
    sub.add_parser("projects", help="list portfolio projects")

    p_run = sub.add_parser("run", help="run project stages with auto-resume")
    p_run.add_argument("project", help="project name (projects/<name>)")
    p_run.add_argument("--force-new", action="store_true",
                       help="start a new run even if one is incomplete")

    p_resume = sub.add_parser("resume", help="resume an incomplete run")
    p_resume.add_argument("--run-id", dest="run_id", default=None)
    p_resume.add_argument("--project", default=None)

    sub.add_parser("status", help="show run status")

    p_cost = sub.add_parser("cost", help="cost per project")
    p_cost.add_argument("--project", default=None)

    p_trace = sub.add_parser("trace", help="step-by-step of a run")
    p_trace.add_argument("run_id")

    p_verify = sub.add_parser("verify", help="check deliverables exist")
    p_verify.add_argument("project")

    p_gaps = sub.add_parser("gaps", help="capability gaps per project needs")
    p_gaps.add_argument("project")

    sub.add_parser("server", help="start the portfolio board (http://127.0.0.1:7331)")

    p_backup = sub.add_parser("backup", help="backup versionado + push (git add/commit/push)")

    p_handoff = sub.add_parser("handoff", help="relatorio de entrega (20 itens p/ ship)")
    p_handoff.add_argument("project")

    p_plan = sub.add_parser("plan", help="fase de planejamento: preenche lacunas e propoe fases")
    p_plan.add_argument("project")
    p_plan.add_argument("--brief", default=None,
                        help="brief para projeto novo (se project.yaml nao existe)")
    p_plan.add_argument("--run", action="store_true",
                        help="dispara o pipeline apos planejar")

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handlers = {
        "doctor": cmd_doctor,
        "projects": cmd_projects,
        "run": cmd_run,
        "resume": cmd_resume,
        "status": cmd_status,
        "cost": cmd_cost,
        "trace": cmd_trace,
        "verify": cmd_verify,
        "gaps": cmd_gaps,
        "server": cmd_server,
        "backup": cmd_backup,
        "handoff": cmd_handoff,
        "plan": cmd_plan,
    }
    handler = handlers.get(args.command)
    if not handler:
        parser.print_help()
        return 2
    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
