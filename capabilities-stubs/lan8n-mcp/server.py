"""LAN8N stub MCP server.

Temporary placeholder that mirrors what the automation-engineer
subagent needs until the real LAN8N repo ships its own MCP
(`../n8n/mcp/server.py`).

Runs via the LAOS venv:
    uv run python capabilities-stubs/lan8n-mcp/server.py
"""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("lan8n")


@mcp.tool()
def health() -> dict:
    """Liveness probe."""
    return {"status": "ok", "stub": True, "capability": "lan8n"}


@mcp.tool()
def list_supported_operations() -> list[dict]:
    return [
        {"op": "list_workflow_templates", "status": "planned", "repo": "../n8n"},
        {"op": "compose_workflow", "status": "planned", "repo": "../n8n"},
        {"op": "export_workflow_json", "status": "planned", "repo": "../n8n"},
        {"op": "schedule_workflow", "status": "planned", "repo": "../n8n"},
    ]


@mcp.tool()
def placeholder(operation: str, payload: dict | None = None) -> dict:
    """Stub catch-all. Real server should reject unknown ops."""
    return {
        "stub": True,
        "operation": operation,
        "echoed_payload": payload or {},
        "message": "lan8n stub - implement in ../n8n/mcp/server.py",
    }


@mcp.resource("lan8n://capability")
def capability() -> dict:
    return {
        "id": "lan8n",
        "kind": "domain",
        "mcp_server": "lan8n",
        "status": "stub",
        "owns": ["automation.*", "integration.*"],
        "real_server": "../n8n/mcp/server.py",
    }


if __name__ == "__main__":
    mcp.run()
