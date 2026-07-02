"""lacouncil tests — unit + smoke tests for the Confidence Escalation Ladder.

LACOUNCIL d3095fa3-4570-413c-82b4-47442a90e947. Implements CEL-IC-3:
unit tests for `log()`, `detect_user_question_patterns`,
`create_proposal_from_pattern`, migration idempotence, and a smoke
test E2E.

Run with:
    uv run --directory F:/Projetos/Laos/lacouncil python -m pytest tests/ -v

Or from the lacouncil repo root:
    cd ../lacouncil && uv run pytest tests/ -v
"""
