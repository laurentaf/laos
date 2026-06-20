<!--
  LAN8N — Automation capability for LAOS
  README.md  |  github.com/laurentaf/lan8n
  Brand: Workflows, not scripts. Automation, not glue.
  Tone: Precise, operational, confident.
  Adapted from the LAOS README (20/20) inline-HTML pattern.
-->

<div align="center" style="margin-top:48px;margin-bottom:24px;">

<!-- Emblem: circuit / flow nodes -->
<svg width="72" height="72" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-bottom:4px;">
  <rect x="4" y="4" width="56" height="56" rx="12" stroke="#00b894" stroke-width="1.5" fill="none" opacity="0.3"/>
  <circle cx="14" cy="32" r="5" stroke="#00b894" stroke-width="2" fill="none"/>
  <circle cx="32" cy="16" r="5" stroke="#00b894" stroke-width="2" fill="none"/>
  <circle cx="50" cy="32" r="5" stroke="#00b894" stroke-width="2" fill="none"/>
  <circle cx="32" cy="48" r="5" stroke="#00b894" stroke-width="2" fill="none" opacity="0.5"/>
  <line x1="19" y1="32" x2="27" y2="22" stroke="#00b894" stroke-width="1.5" opacity="0.6"/>
  <line x1="27" y1="22" x2="45" y2="22" stroke="#00b894" stroke-width="1.5" opacity="0.6"/>
  <line x1="45" y1="22" x2="45" y2="40" stroke="#00b894" stroke-width="1.5" opacity="0.6"/>
  <line x1="45" y1="40" x2="27" y2="40" stroke="#00b894" stroke-width="1.5" opacity="0.6"/>
  <line x1="27" y1="40" x2="27" y2="48" stroke="#00b894" stroke-width="1.5" opacity="0.6"/>
  <line x1="19" y1="32" x2="27" y2="42" stroke="#00b894" stroke-width="1.5" opacity="0.4"/>
  <line x1="27" y1="42" x2="45" y2="42" stroke="#00b894" stroke-width="1.5" opacity="0.4"/>
  <line x1="45" y1="42" x2="45" y2="24" stroke="#00b894" stroke-width="1.5" opacity="0.4"/>
</svg>

<br/>

# LAN8N
### Workflows &bull; n8n Automation &bull; API Integrations &bull; Webhooks

<p style="margin:12px 0;">
  <img src="https://img.shields.io/badge/Python-%E2%89%A53.11-3776AB?style=flat&logo=python&logoColor=fff" alt="Python 3.11+"/>
  &nbsp;
  <img src="https://img.shields.io/badge/Status-STABLE-00b894?style=flat" alt="Status: STABLE"/>
  &nbsp;
  <img src="https://img.shields.io/badge/License-MIT-31c754?style=flat" alt="License: MIT"/>
  &nbsp;
  <img src="https://img.shields.io/badge/n8n-Compatible-00b894?style=flat&logo=n8n&logoColor=fff" alt="n8n Compatible"/>
  &nbsp;
  <a href="https://github.com/laurentaf/laos"><img src="https://img.shields.io/badge/Ecosystem-LAOS-6c5ce7?style=flat" alt="LAOS Ecosystem"/></a>
</p>

<hr style="width:48px;margin:24px auto;border:none;border-top:2px solid #00b894;opacity:0.3;"/>

</div>

> **Workflows, not scripts. Automation, not glue.**  
> LAN8N is the LAOS ecosystem's automation layer — composing, validating, and deploying n8n workflows through MCP-native tool calls. From scheduled data ingestion to multi-step API orchestrations, every automation is reproducible, versioned, and gated.

---

## What LAN8N Is

LAN8N is the automation capability for LAOS, wrapping n8n (self-hosted or cloud) behind a deterministic MCP interface. It abstracts away n8n's JSON complexity behind 6 focused tools — compose, validate, export, template, and orchestrate.

**Why LAN8N exists:** Automations are notoriously hard to version, review, and govern. LAN8N treats every workflow as a spec-first artifact: composed from blueprints, validated against quality gates, and exported as n8n-compatible JSON. No click-ops, no unrepeatable manual configuration.

**Key architecture:** Local-first by default. n8n runs self-hosted (`npx n8n` or Docker) during MVP. The `n8n-community` MCP provides raw API surface for advanced users.

---

## Architecture

<div align="center" style="margin:24px 0;">

<table style="border-collapse:separate;border-spacing:0;min-width:560px;">
  <tr>
    <td colspan="3" align="center" style="padding:0 0 8px 0;">
      <div style="display:inline-block;border:1.5px solid #00b894;border-radius:8px;padding:12px 24px;text-align:center;">
        <div style="font-weight:700;font-size:1em;letter-spacing:0.04em;color:#00b894;">LAN8N MCP Server</div>
        <div style="font-size:0.8em;opacity:0.5;">Python · n8n integration · spec-first workflow engine</div>
      </div>
    </td>
  </tr>
  <tr><td colspan="3" align="center" style="padding:0;"><div style="width:1.5px;height:14px;background:#00b894;opacity:0.2;margin:0 auto;"></div></td></tr>
  <tr>
    <td align="center" style="padding:0 8px;width:33%;">
      <div style="border:1px solid #00b894;border-radius:6px;padding:8px 14px;text-align:center;">
        <div style="font-weight:600;font-size:0.85em;letter-spacing:0.02em;">Compose &amp; Template</div>
        <div style="font-size:0.7em;opacity:0.5;">List · Get · Compose<br/>from blueprints</div>
      </div>
    </td>
    <td align="center" style="padding:0 8px;width:33%;">
      <div style="border:1px solid #fdcb6e;border-radius:6px;padding:8px 14px;text-align:center;">
        <div style="font-weight:600;font-size:0.85em;letter-spacing:0.02em;">Validate &amp; QA</div>
        <div style="font-size:0.7em;opacity:0.5;">Quality gates per<br/>phase · Node checks</div>
      </div>
    </td>
    <td align="center" style="padding:0 8px;width:33%;">
      <div style="border:1px solid #00b894;border-radius:6px;padding:8px 14px;text-align:center;">
        <div style="font-weight:600;font-size:0.85em;letter-spacing:0.02em;">Export &amp; Deploy</div>
        <div style="font-size:0.7em;opacity:0.5;">n8n-compatible JSON<br/>→ workflows/ directory</div>
      </div>
    </td>
  </tr>
</table>

</div>

---

## MCP Tools

<table style="width:100%;border-collapse:separate;border-spacing:0;font-size:0.9em;">
  <tr style="border-bottom:1px solid #00b894;opacity:0.4;">
    <th align="left" style="padding:10px 14px;font-weight:600;opacity:0.5;width:25%;">Tool</th>
    <th align="left" style="padding:10px 14px;font-weight:600;opacity:0.5;">Description</th>
  </tr>
  <tr><td style="padding:8px 14px;font-weight:500;"><code>list_workflow_templates</code></td><td style="padding:8px 14px;opacity:0.7;">Browse available workflow blueprints by category</td></tr>
  <tr><td style="padding:8px 14px;font-weight:500;"><code>get_workflow_template</code></td><td style="padding:8px 14px;opacity:0.7;">Inspect a specific template's structure and parameters</td></tr>
  <tr><td style="padding:8px 14px;font-weight:500;"><code>compose_workflow</code></td><td style="padding:8px 14px;opacity:0.7;">Build a workflow from template + parameters → full JSON</td></tr>
  <tr><td style="padding:8px 14px;font-weight:500;"><code>validate_workflow</code></td><td style="padding:8px 14px;opacity:0.7;">Validate a workflow definition against quality gates</td></tr>
  <tr><td style="padding:8px 14px;font-weight:500;"><code>export_workflow_json</code></td><td style="padding:8px 14px;opacity:0.7;">Export as n8n-compatible JSON to workflows/ directory</td></tr>
  <tr><td style="padding:8px 14px;font-weight:500;"><code>health</code></td><td style="padding:8px 14px;opacity:0.7;">Server liveness probe</td></tr>
  <tr><td style="padding:8px 14px;font-weight:500;"><code>list_supported_operations</code></td><td style="padding:8px 14px;opacity:0.7;">Full capability catalog</td></tr>
</table>

---

## Quick Start

```bash
# Install dependencies
uv sync

# Start the MCP server
uv run lan8n-server

# n8n (self-hosted, optional for local testing):
npx n8n start
```

### Requirements

<table style="font-size:0.85em;border-collapse:separate;border-spacing:0;">
  <tr><td style="padding:6px 12px;font-weight:500;">Python</td><td style="padding:6px 12px;opacity:0.6;">≥ 3.11</td></tr>
  <tr><td style="padding:6px 12px;font-weight:500;">Runtime</td><td style="padding:6px 12px;opacity:0.6;">Node.js (for n8n)</td></tr>
  <tr><td style="padding:6px 12px;font-weight:500;">Storage</td><td style="padding:6px 12px;opacity:0.6;">Workflows saved to <code>workflows/</code> directory as n8n JSON</td></tr>
</table>

---

## Example: Daily Report Email Workflow

Compose a scheduled automation that runs every morning:

```python
# Via MCP call (from orchestrated agent):
workflow = lan8n.compose_workflow(
    name="daily-sales-report",
    trigger_type="n8n-nodes-base.scheduleTrigger",
    nodes=[
        {"name": "Query DuckDB", "type": "n8n-nodes-base.executeQuery",
         "parameters": {"query": "SELECT * FROM gold_sales WHERE date = $NOW"}},
        {"name": "Format HTML", "type": "n8n-nodes-base.html",
         "parameters": {"template": "report-template.html"}},
        {"name": "Send Email", "type": "n8n-nodes-base.emailSend",
         "parameters": {"to": "team@example.com", "subject": "Daily Sales Report"}}
    ],
    error_path=True  # +error notify node
)

# Validate:
lan8n.validate_workflow(json_path="workflows/daily-sales-report.json")

# Export:
lan8n.export_workflow_json(workflow=workflow)
# → "workflows/daily-sales-report.json"
```

---

## Workflow Templates

LAN8N provides pre-built templates for common automation patterns:

| Template | Trigger | Description |
|----------|---------|-------------|
| Daily Report | Schedule (cron) | Query → format → email |
| Webhook Receiver | Webhook | Receive → validate → store |
| Data Sync | Schedule | Pull → transform → load |
| Alert Monitor | Polling | Check condition → notify |
| API Bridge | Webhook | Transform → forward → log |

Browse available templates via `lan8n.list_workflow_templates()`.

---

## Contributing

| Scope | Path |
|-------|------|
| **New workflow template** | LACOUNCIL proposal → Conselho majority → add to templates/ |
| **Bug / improvement** | Open an [issue](https://github.com/laurentaf/lan8n/issues) |
| **Quality gate rule** | PR to `spec/quality-gates/` with test cases |

See the [LAOS governance model](https://github.com/laurentaf/laos) for full details.

---

## License

<div style="margin:16px 0;">

**MIT** — see [`LICENSE`](https://github.com/laurentaf/lan8n/blob/main/LICENSE) for the full text.

Workflows, not scripts. Automation, not glue.

</div>

---

<div align="center" style="margin:36px 0;opacity:0.25;font-size:0.8em;">
<svg width="28" height="28" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-bottom:4px;">
  <rect x="4" y="4" width="56" height="56" rx="12" stroke="#00b894" stroke-width="1.5" fill="none" opacity="0.15"/>
  <circle cx="14" cy="32" r="4" stroke="#00b894" stroke-width="1.5" fill="none" opacity="0.5"/>
  <circle cx="32" cy="16" r="4" stroke="#00b894" stroke-width="1.5" fill="none" opacity="0.5"/>
  <circle cx="50" cy="32" r="4" stroke="#00b894" stroke-width="1.5" fill="none" opacity="0.5"/>
  <circle cx="32" cy="48" r="4" stroke="#00b894" stroke-width="1.5" fill="none" opacity="0.3"/>
</svg>
<br/>
LAN8N — part of the <a href="https://github.com/laurentaf/laos" style="text-decoration:none;">LAOS</a> ecosystem
</div>
