"""LACOUNCIL — In-Memory Structural Improvement Engine.

The public surface of the package. Used by:
- `lacouncil.mcp.server` (the FastMCP binding)
- `lacouncil.__main__` (the Typer CLI)
- direct imports in tests / scripts
"""

from __future__ import annotations

__all__ = ["__version__", "__status__"]

__version__ = "0.1.0"
__status__ = "BASIC"  # bootstrap
