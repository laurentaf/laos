# Subagent result contract

**Source:** LACOUNCIL proposal `dbc88097-2ef3-475d-bc10-1ebf76027150`
(aprovada 4/4 SIM, maioria, 2026-06-09)

**Purpose:** Reduce orchestrator context pollution from subagent dispatches.
Every `task` dispatch previously returned full subagent output into the
orchestrator context. After 2-3 rounds, context was 30-40% full from
return values alone. The orchestrator is a coordinator, not a worker —
it needs verdicts, not full results.

## Receipt schema

Every subagent returns ONLY a compact receipt to the orchestrator:

```yaml
status: ok | error          # enum, required
summary: str                # max 2 lines, required — must be actionable
details_path: str           # path to full output file, required
task_id: str                # dispatch task ID (ses_xxx format), required
error_class: str            # optional — only on status: error
```

### Field rules

- **status** — `ok` means the task completed successfully. `error`
  means it failed or was blocked. No other values.
- **summary** — max 2 lines. Must be actionable: state what was
  created/changed/measured, not just "done". See examples below.
- **details_path** — absolute path to the full output file. Always
  under `artifacts/<project>/reviews/<task-id>.md`.
- **task_id** — the dispatch task ID passed in the dispatch payload.
- **error_class** — optional. Values: `timeout`, `auth_failure`,
  `validation_error`, `missing_data`, `mcp_failure`, `permission_denied`.
  Enables the orchestrator to route errors without reading the full file.

## Where detail files go

```
artifacts/<project>/reviews/<task-id>.md
```

- `reviews/` is the subdirectory for full subagent output files.
- `task-id` matches the `task_id` in the receipt.
- The orchestrator reads the receipt, drills into the detail file only
  when needed (error investigation, deeper verification, or user request).

## When the orchestrator drills into details

| Receipt status | Orchestrator action |
|---|---|
| `ok` | Act on summary. Drill into details only if user asks or deeper verification needed. |
| `error` | Always read the detail file. Route based on `error_class` if present. |
| `ok` + `summary` ambiguous | Read the detail file to clarify before proceeding. |

## Summary examples

### Good (actionable)

- `Dashboard wireframe created, 3 pages, 847 lines, artifacts/design/wireframe-v2.html`
- `SQL model spec written: dim_customer grain=customer_id, 4 partition strategies, 2 DQ rules`
- `N8N workflow exported: daily-report-email.json, trigger=schedule, SLA=5min`
- `WDL verdict READY, 3/3 on 3-Q, plan_id=linkedin-content-q3, verified_by=delivery-reviewer`
- `Capability scaffold created: laecon, 17 files, registry updated, BASIC status`
- `Data gap reported: orders_2026q2 missing (API 401), awaiting user decision`

### Bad (not actionable)

- `Done`
- `Task completed successfully`
- `Finished`
- `Working on it`

The summary must allow the orchestrator to decide at a glance whether
to drill in, route elsewhere, or move on.

## Error class routing

The `error_class` field enables fast routing without reading the file:

| error_class | Orchestrator routing |
|---|---|
| `timeout` | Retry with longer timeout or escalate |
| `auth_failure` | Check credentials / ask user |
| `validation_error` | Read details, fix, re-dispatch |
| `missing_data` | Follow Hard Rule #11 (synthetic data protocol) |
| `mcp_failure` | Check MCP health, ask user to restart |
| `permission_denied` | Check permissions / escalate |

## Atomicity

The detail file write must complete BEFORE the receipt is returned.
The orchestrator must never receive a receipt pointing to a non-existent
file.

## Examples

### Successful dispatch

```yaml
status: ok
summary: "Dim customer model spec written: grain=customer_id, 12 columns, 2 partition strategies, 3 DQ rules"
details_path: "E:/projects/myproject/artifacts/reviews/ses_abc123.md"
task_id: "ses_abc123"
```

### Failed dispatch

```yaml
status: error
summary: "Latade MCP returned 401 on execute_sql; credentials missing in .env"
details_path: "E:/projects/myproject/artifacts/reviews/ses_def456.md"
task_id: "ses_def456"
error_class: "auth_failure"
```

### Blocked dispatch (missing data)

```yaml
status: error
summary: "orders_2026q2 table empty (0 rows); cannot build sales model without real data"
details_path: "E:/projects/myproject/artifacts/reviews/ses_ghi789.md"
task_id: "ses_ghi789"
error_class: "missing_data"
```
