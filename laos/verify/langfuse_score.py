"""LAOS verifier -> Langfuse score bridge.

Posts a verification score per deliverable to Langfuse so the
"check garantido" result is visible alongside LLM traces.

POST /api/public/scores — standalone score with trace/observation
optional. We attach to project name via metadata (no trace id since
verification isn't an LLM call). If Langfuse is down, this degrades
silently (verification still persists in DuckDB).
"""

from __future__ import annotations

import base64
import json
import pathlib
import urllib.error
import urllib.request

from laos.verify import engine

LANGFUSE_URL = "http://localhost:3000"
PK = "lf_pk_laos_9b8a7c6d5e4f"
SK = "lf_sk_laos_0f1e2d3c4b5a"


def _auth_header() -> str:
    token = base64.b64encode(f"{PK}:{SK}".encode()).decode()
    return f"Basic {token}"


def _langfuse_up() -> bool:
    try:
        with urllib.request.urlopen(f"{LANGFUSE_URL}/api/public/health", timeout=3):
            return True
    except Exception:  # noqa: BLE001
        return False


def post_score(
    project_id: str,
    result: engine.VerifyResult,
) -> bool:
    """Post a standalone score. Creates a verification trace first (the
    scores API requires a traceId), then attaches the score to it.
    Returns True on success (or Langfuse down)."""
    if not _langfuse_up():
        return False
    headers = {
        "Content-Type": "application/json",
        "Authorization": _auth_header(),
    }
    # 1. create a minimal trace (verification isn't an LLM call)
    trace_payload = {
        "name": f"verify:{result.deliverable}",
        "timestamp": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "metadata": {
            "project_id": project_id,
            "deliverable": result.deliverable,
            "skipped": result.skipped,
        },
    }
    try:
        req = urllib.request.Request(
            f"{LANGFUSE_URL}/api/public/traces",
            data=json.dumps(trace_payload).encode(),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            trace = json.loads(resp.read())
            trace_id = trace.get("id")
    except Exception:  # noqa: BLE001
        return False

    # 2. attach the score to the trace
    payload = {
        "name": f"verify:{result.deliverable}",
        "value": 1.0 if result.ok else 0.0,
        "traceId": trace_id,
        "comment": "; ".join(result.notes) or (
            "ok" if result.ok else "failed verification"
        ),
        "dataType": "NUMERIC",
        "metadata": {
            "project_id": project_id,
            "deliverable": result.deliverable,
            "skipped": result.skipped,
        },
    }
    req = urllib.request.Request(
        f"{LANGFUSE_URL}/api/public/scores",
        data=json.dumps(payload).encode(),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200 or resp.status == 201
    except Exception:  # noqa: BLE001
        return False


def post_project_scores(project_id: str, results: list[engine.VerifyResult]) -> int:
    """Post scores for all results. Returns count posted."""
    posted = 0
    for r in results:
        if post_score(project_id, r):
            posted += 1
    return posted
