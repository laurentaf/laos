"""LAOS core — needs resolution (pure function).

Resolves a project's abstract `needs` to concrete capabilities via
`registry/needs-to-capabilities.yaml`. Deterministic — the orchestrator
walks this map; it never invents capability selection.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

REGISTRY_REL = "registry/needs-to-capabilities.yaml"


def _find_laos_root(start: Path | None = None) -> Path:
    """Walk up to the LAOS root (AGENTS.md + projects/ present)."""
    p = (start or Path.cwd()).resolve()
    for ancestor in [p, *p.parents]:
        if (ancestor / "AGENTS.md").exists() and (ancestor / "projects").is_dir():
            return ancestor
    return p


def load_routing_map(root: Path | None = None) -> dict[str, Any]:
    """Load the needs->capabilities routing map."""
    laos_root = _find_laos_root(root)
    path = laos_root / REGISTRY_REL
    if not path.exists():
        raise FileNotFoundError(f"Routing map not found: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} root must be a mapping")
    return data


def resolve_needs(
    needs: list[str],
    root: Path | None = None,
) -> dict[str, dict[str, list[str]]]:
    """Resolve a list of needs to capabilities.

    Returns {need: {"primary": [...], "optional": [...]}}.
    Raises KeyError listing unresolved needs (per Hard Rule: never
    invent capability selection — fail loudly).
    """
    routing = load_routing_map(root)
    missing = [n for n in needs if n not in routing]
    if missing:
        raise KeyError(
            f"Unresolved needs (not in registry/needs-to-capabilities.yaml): "
            f"{missing}. Fix: rename the need or add a routing rule."
        )
    return {n: routing[n] for n in needs}


def primary_capabilities_for(needs: list[str], root: Path | None = None) -> list[str]:
    """Unique list of primary capabilities across all needs (order preserved)."""
    resolved = resolve_needs(needs, root)
    out: list[str] = []
    for info in resolved.values():
        for cap in info.get("primary", []):
            if cap not in out:
                out.append(cap)
    return out
