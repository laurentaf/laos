"""LACOUNCIL CLI — Typer entry point.

Dispatches:
  - `lacouncil health`        diagnostic
  - `lacouncil proposal ls`   list proposals
  - `lacouncil proposal show <proposal_id>`
  - `lacouncil proposal create --json @file.json` (admin; normally orchestrator-only)
  - `lacouncil vote register <proposal_id> <voter> <sim|nao|abstencao> [--justificativa ...]`
  - `lacouncil vote tally <proposal_id>`
  - `lacouncil pattern detect` (3Q detection)
  - `lacouncil project record --json @file.json`
  - `lacouncil mcp`           print the MCP server command (used by opencode.jsonc)
                                or launch the FastMCP server in-process.

The CLI is the human/admin interface. Specialists use the MCP server.
"""

from __future__ import annotations

import sys


def _ensure_utf8_stdout() -> None:
    """Force UTF-8 on sys.stdout if reconfigure is available.

    Safe to call multiple times. No-op if:
      - sys.stdout is not a TextIOWrapper (captured, redirected, frozen)
      - reconfigure raises (wrapped by colorama, IPython, etc.)

    Rationale (LACOUNCIL b43ca63d C-B1):
      sys.stdout.reconfigure(encoding="utf-8") does not exist on:
      - colorama-wrapped streams (Windows < 3.10 with colorama)
      - IPython/Jupyter captured streams
      - PyInstaller frozen streams
      - pytest capture (capsys, capfd)
      The guard hasattr+try/except makes reconfigure no-op in those edge
      cases instead of AttributeError fatal. Idempotent in UTF-8 environments.
    """
    out = sys.stdout
    if not hasattr(out, "reconfigure"):
        return
    try:
        out.reconfigure(encoding="utf-8")
    except (ValueError, OSError, AttributeError):
        # ValueError: closed stream
        # OSError: pipe/redirect on Windows
        # AttributeError: wrapped stream (defensive — hasattr should catch)
        pass


_ensure_utf8_stdout()

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from lacouncil import __version__, __status__
from lacouncil.core.duckdb_store import (
    connect,
    detect_patterns as _detect_patterns,
    get_proposal,
    list_projects,
    list_proposals,
    record_project,
    register_vote,
    upsert_proposal,
)
from lacouncil.core.schemas import (
    CreateProposalRequest,
    Estrategia,
    Proposal,
    ProposalStatus,
    RecordProjectRequest,
    RegisterVoteRequest,
    VoteValue,
)
from lacouncil.core.voting import (
    compute_tally,
    default_strategy_for_category,
    tally_votes as _tally_votes,
)

app = typer.Typer(
    name="lacouncil",
    help="LACOUNCIL — In-Memory Structural Improvement Engine for LAOS",
    no_args_is_help=True,
)
console = Console()

# Subcommands:
proposal_app = typer.Typer(help="Gestão de propostas de mudança estrutural.")
vote_app = typer.Typer(help="Operações de voto do Conselho.")
project_app = typer.Typer(help="Registro de projetos concluídos.")
pattern_app = typer.Typer(help="Detecção de padrões recorrentes.")
app.add_typer(proposal_app, name="proposal")
app.add_typer(vote_app, name="vote")
app.add_typer(project_app, name="project")
app.add_typer(pattern_app, name="pattern")


# ──────────────────────────────────────────────────────────────────────────────
# Top-level
# ──────────────────────────────────────────────────────────────────────────────


@app.command()
def version():
    """Printa versão e status."""
    typer.echo(f"{__version__} ({__status__})")


@app.command()
def health():
    """Health check simples: confirma conexão DuckDB + schema migration."""
    try:
        con = connect()
        row = con.execute("SELECT 1 AS ok").fetchone()
        con.close()
        ok = row[0] == 1
        console.print(f"[green]OK[/green] ping={ok} v{__version__} status={__status__}")
    except Exception as exc:  # noqa: BLE001
        console.print(f"[red]FAIL[/red] {exc}")
        sys.exit(1)


@app.command()
def mcp(
    transport: str = typer.Option("stdio", help="stdio | sse | ws"),
):
    """Lança o FastMCP server em stdio (default) ou outro transporte."""
    try:
        from lacouncil.mcp import server as mcp_server  # noqa: WPS433 (late import)
    except ImportError as exc:
        console.print(f"[red]MCP server import failed[/red] {exc}")
        sys.exit(1)
    mcp_server.main(transport=transport)


# ──────────────────────────────────────────────────────────────────────────────
# Proposal subcommands
# ──────────────────────────────────────────────────────────────────────────────


@proposal_app.command("ls")
def proposal_list(
    status: Optional[str] = typer.Option(None, help="Filtro: pendente|em_votacao|aprovada|rejeitada|implementada"),
    limit: int = typer.Option(50, help="Max rows."),
):
    """Lista propostas registradas."""
    ps = ProposalStatus(status) if status else None
    rows = list_proposals(status=ps)
    if not rows:
        console.print("[yellow]nenhuma proposta encontrada[/yellow]")
        return
    table = Table(title=f"LACOUNCIL Proposals — {len(rows)} entries")
    for col in ("proposal_id", "titulo", "categoria", "estrategia", "status", "created_at"):
        table.add_column(col, style="cyan")
    for p in rows[:limit]:
        table.add_row(
            p.proposal_id[:8],
            (p.titulo[:48] + "...") if len(p.titulo) > 50 else p.titulo,
            p.categoria.value,
            p.estrategia.value,
            p.status.value,
            p.created_at[:19],
        )
    console.print(table)


@proposal_app.command("show")
def proposal_show(
    proposal_id: str = typer.Argument(...),
):
    """Detalhe de uma proposta."""
    p = get_proposal(proposal_id)
    if p is None:
        console.print(f"[red]não encontrada[/red] {proposal_id}")
        sys.exit(1)
    console.print_json(json.dumps(p.model_dump(), ensure_ascii=False, indent=2))


@proposal_app.command("create")
def proposal_create(
    titulo: str = typer.Option(..., help="Título (>=10 chars)."),
    descricao: str = typer.Option(..., help="Descrição (>=30 chars)."),
    categoria: str = typer.Option("other", help="fundamentos|registry|workflow|knowledge|capability|advisory|other"),
    estrategia: Optional[str] = typer.Option(None, help="Override default strategy."),
    autor: str = typer.Option("orchestrator", help="agent-id que submete."),
    contexto: str = typer.Option(..., help="Por que esta proposta existe agora (>=10 chars)."),
    mudanca: str = typer.Option(..., help="O que muda exatamente (>=10 chars)."),
    impacto: str = typer.Option("", help="Impacto esperado (incluindo risco)."),
    alternativas: str = typer.Option("", help="Alternativas consideradas."),
):
    """Registra uma nova proposta no DuckDB."""
    from lacouncil.core.schemas import Category

    cat_enum = Category(categoria.lower())
    strat_enum = (
        Estrategia(estrategia.lower()) if estrategia else default_strategy_for_category(categoria.lower())
    )

    req = CreateProposalRequest(
        titulo=titulo,
        descricao=descricao,
        categoria=cat_enum,
        estrategia=strat_enum,
        autor=autor,
        contexto=contexto,
        mudanca=mudanca,
        impacto=impacto,
        alternativas=alternativas,
    )
    p = Proposal(**req.model_dump())
    persisted = upsert_proposal(p)
    console.print(f"[green]OK[/green] proposal_id={persisted.proposal_id}")
    console.print_json(json.dumps(persisted.model_dump(), ensure_ascii=False, indent=2))


# ──────────────────────────────────────────────────────────────────────────────
# Vote subcommands
# ──────────────────────────────────────────────────────────────────────────────


@vote_app.command("register")
def vote_register(
    proposal_id: str = typer.Argument(...),
    voter: str = typer.Argument(..., help="agent-id (data-architect, dashboard-designer, automation-engineer, delivery-reviewer, orchestrator)."),
    voto: str = typer.Argument(..., help="sim|nao|abstencao"),
    justificativa: str = typer.Option("", help="<=2000 chars."),
):
    """Registra (ou sobrescreve) o voto de um membro do Conselho."""
    if voto.lower() not in {v.value for v in VoteValue}:
        console.print(f"[red]voto inválido[/red] {voto!r}; use sim|nao|abstencao")
        sys.exit(2)
    req = RegisterVoteRequest(
        proposal_id=proposal_id,
        voter=voter,
        voto=VoteValue(voto.lower()),
        justificativa=justificativa,
    )
    from lacouncil.core.schemas import Vote
    v = Vote(**req.model_dump())
    persisted = register_vote(v)
    console.print(f"[green]OK[/green] vote_id={persisted.vote_id}")


@vote_app.command("tally")
def vote_tally(
    proposal_id: str = typer.Argument(...),
):
    """Computa a tally para a proposta e atualiza status (aprovada|rejeitada)."""
    p = get_proposal(proposal_id)
    if p is None:
        console.print(f"[red]não encontrada[/red] {proposal_id}")
        sys.exit(1)
    from lacouncil.core.duckdb_store import update_proposal_status
    result = _tally_votes(proposal_id, p.estrategia)
    update_proposal_status(
        proposal_id,
        result.new_status,
        tally_summary=result.model_dump(),
    )
    console.print(
        f"[{'green' if result.passed else 'red'}]"
        f"proposal_id={proposal_id} -> {result.new_status.value} "
        f"(sim={result.votes['sim']} nao={result.votes['nao']} abst={result.votes['abstencao']} "
        f"ratio={result.ratio:.2f} threshold={result.threshold:.2f})"
    )


# ──────────────────────────────────────────────────────────────────────────────
# Pattern subcommands
# ──────────────────────────────────────────────────────────────────────────────


@pattern_app.command("detect")
def pattern_detect(
    min_occurrences: int = typer.Option(3, help="Limiar mínimo de ocorrências."),
):
    """Roda o 3Q detection e lista padrões identificados."""
    matches = _detect_patterns(min_occurrences=min_occurrences)
    if not matches:
        console.print("[yellow]nenhum padrão detectado[/yellow]")
        return
    table = Table(title=f"Padrões (>= {min_occurrences} ocorrências)")
    for col in ("pattern", "occurrences", "projects", "confidence"):
        table.add_column(col, style="cyan")
    for p in matches:
        table.add_row(
            p.pattern[:60],
            str(p.occurrences),
            ", ".join(p.projects[:5]) + ("..." if len(p.projects) > 5 else ""),
            f"{p.confidence:.2f}",
        )
    console.print(table)


# ──────────────────────────────────────────────────────────────────────────────
# Project subcommands
# ──────────────────────────────────────────────────────────────────────────────


@project_app.command("ls")
def project_list(
    limit: int = typer.Option(50, help="Max rows."),
):
    """Lista projetos registrados."""
    rows = list_projects()
    if not rows:
        console.print("[yellow]nenhum projeto registrado[/yellow]")
        return
    table = Table(title=f"Projetos — {len(rows)} entradas")
    for col in ("slug", "scope", "capabilities", "recorded_at"):
        table.add_column(col, style="cyan")
    for p in rows[:limit]:
        caps = ", ".join(p.capabilities_used)[:60]
        table.add_row(
            p.project_slug,
            (p.scope[:48] + "...") if len(p.scope) > 50 else p.scope,
            caps,
            p.recorded_at[:19],
        )
    console.print(table)


@project_app.command("record")
def project_record(
    project_slug: str = typer.Option(..., help="Identificador normalizado"),
    scope: str = typer.Option(..., help="Escopo do projeto (brief)."),
    capabilities: str = typer.Option(..., help="Lista comma-separated de capabilities."),
    deliverable_summary: str = typer.Option(..., help="Resumo do que foi entregue."),
    follow_up: str = typer.Option("", help="Próximos passos (se houver)."),
    follows_pattern: Optional[str] = typer.Option(None, help="Bucket de padrão (se aplicável)."),
):
    """Registra um projeto concluído para memória institucional."""
    req = RecordProjectRequest(
        project_slug=project_slug,
        scope=scope,
        capabilities_used=[c.strip() for c in capabilities.split(",") if c.strip()],
        deliverable_summary=deliverable_summary,
        follow_up=follow_up,
        follows_pattern=follows_pattern,
    )
    from lacouncil.core.schemas import Project
    proj = Project(**req.model_dump())
    persisted = record_project(proj)
    console.print(f"[green]OK[/green] project_id={persisted.project_id} slug={persisted.project_slug}")


# ──────────────────────────────────────────────────────────────────────────────
# Composition
# ──────────────────────────────────────────────────────────────────────────────


def main():
    app()


if __name__ == "__main__":
    main()
