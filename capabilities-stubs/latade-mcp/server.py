"""LATADE stub MCP server.

Temporary placeholder that exposes the surface shape the
`data-architect` subagent expects. Replace with the real implementation
in the LATADE repo (`../latade/mcp/server.py`) when ready.

Runs via the LAOS venv:
    uv run python capabilities-stubs/latade-mcp/server.py
"""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("latade")


@mcp.tool()
def health() -> dict:
    """Liveness probe. Always returns ok with a timestamp stub."""
    return {"status": "ok", "stub": True, "capability": "latade"}


@mcp.tool()
def list_supported_operations() -> list[dict]:
    """Catalog of operations this stub claims to support.

    The real server must keep this in sync with its actual tools.
    """
    return [
        {"op": "query_warehouse", "status": "planned", "repo": "../latade"},
        {"op": "model_spec_from_brief", "status": "planned", "repo": "../latade"},
        {"op": "data_quality_check", "status": "planned", "repo": "../latade"},
        {"op": "bi_artifact_export", "status": "planned", "repo": "../latade"},
    ]


@mcp.tool()
def placeholder(operation: str, payload: dict | None = None) -> dict:
    """Catch-all for ops not yet implemented. Real server should reject
    unknown ops instead of answering, but the stub pretends to help so
    downstream tests can exercise the wiring."""
    return {
        "stub": True,
        "operation": operation,
        "echoed_payload": payload or {},
        "message": "latade stub - implement in ../latade/mcp/server.py",
    }


@mcp.resource("latade://capability")
def capability() -> dict:
    return {
        "id": "latade",
        "kind": "domain",
        "mcp_server": "latade",
        "status": "stub",
        "owns": ["sql.*", "data.*", "bi.*"],
        "real_server": "../latade/mcp/server.py",
    }


if __name__ == "__main__":
    mcp.run()
