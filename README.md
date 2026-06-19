<!--
  LAOS — Laurent Agent Operating System
  README.md  |  github.com/laurentaf/laos

  Brand spine: "The laurel was exclusive. The intelligence doesn't have to be."
  Brand tone: Monumental but clear. Stripe docs × Linear clarity. No hype, no dry.

  This file uses inline HTML + CSS for visual polish.
  GitHub strips external CSS/JS. All styling is inline or <style> scoped.
-->

<div align="center" style="margin-top:48px;margin-bottom:48px;">

<!-- Crown emblem — 3-bar OS-style mark -->
<svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="4" y="4" width="56" height="56" rx="12" stroke="currentColor" stroke-width="1.5" fill="none" opacity="0.15"/>
  <line x1="14" y1="20" x2="14" y2="46" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="24" y1="20" x2="24" y2="46" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="34" y1="14" x2="34" y2="46" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="44" y1="20" x2="44" y2="46" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="54" y1="26" x2="54" y2="46" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
</svg>

<br/>

# LAOS
### Laurent Agent Operating System

<hr style="width:48px;margin:24px auto;border:none;border-top:2px solid currentColor;opacity:0.3;"/>

</div>

> <span style="font-size:1.15em;line-height:1.6;">**The laurel was exclusive. The intelligence doesn't have to be.**</span>

For 3,000 years, the laurel cinged one head — the emperor's. Intelligence was centralized, privileged, gated. LAOS dissolves the crown and distributes sovereignty to every operator: **the laós**.

**Not a framework. Not a platform.** An operating system for composable AI — 7 specialized capabilities, 1 orchestrator, zero implementation in the orchestration layer.

<p align="center" style="margin:40px 0;">
  <a href="#ecosystem-architecture" style="text-decoration:none;border:1px solid currentColor;border-radius:100px;padding:8px 28px;font-weight:500;opacity:0.8;">Explore the system&nbsp;→</a>
  &nbsp;&nbsp;
  <a href="#about-the-architect" style="text-decoration:none;border-bottom:1px solid currentColor;opacity:0.5;padding-bottom:2px;">About the architect</a>
</p>

---

## The Inversion

<div align="center">

<table style="width:100%;max-width:680px;border-collapse:separate;border-spacing:0;font-size:0.9em;line-height:1.5;">
  <tr style="border-bottom:1px solid currentColor;">
    <th align="left" style="padding:12px 16px;font-weight:600;opacity:0.4;">Old World</th>
    <th align="left" style="padding:12px 16px;font-weight:600;opacity:0.9;">LAOS</th>
  </tr>
  <tr>
    <td style="padding:10px 16px;opacity:0.5;">Data team owns the pipeline</td>
    <td style="padding:10px 16px;">Every operator runs their own data</td>
  </tr>
  <tr>
    <td style="padding:10px 16px;opacity:0.5;">AI lab hoards the models</td>
    <td style="padding:10px 16px;">Capabilities are composed, not siloed</td>
  </tr>
  <tr>
    <td style="padding:10px 16px;opacity:0.5;">Tickets and dashboards for the rest</td>
    <td style="padding:10px 16px;">MCP-native tool access for every agent</td>
  </tr>
  <tr>
    <td style="padding:10px 16px;opacity:0.5;">Emperor decides</td>
    <td style="padding:10px 16px;">Conselho deliberates (proposals, voting, trust)</td>
  </tr>
</table>

</div>

---

## Ecosystem Architecture

<div align="center">

```
                         ┌─────────────────┐
                         │      LAOS        │
                         │   Orchestrator   │
                         │  (this repo)     │
                         └────────┬────────┘
                                  │
           ┌──────────────────────┼──────────────────────────┐
           │                      │                          │
     ┌─────┴─────┐         ┌──────┴──────┐         ┌───────┴──────┐
     │  LATADE   │         │  LADESIGN   │         │    LAN8N     │
     │    Data   │         │   Design    │         │  Automation  │
     │ sql·dbt·  │         │ dashboards· │         │  n8n · APIs  │
     │ DuckDB·BI │         │ decks · UI  │         │  workflows   │
     └───────────┘         └─────────────┘         └──────────────┘
     ┌────────────┐        ┌──────────────┐        ┌─────────────┐
     │ LACOUNCIL  │        │   LAECON     │        │  LAENGINE   │
     │ Governance │        │ Econometrics │        │    Game     │
     │ proposals· │        │ regressions· │        │ simulation· │
     │ voting·mem │        │ causal · ML  │        │ match ·squad│
     └────────────┘        └──────────────┘        └─────────────┘
     ┌──────────────┐
     │ LACAREEROPS  │
     │    Career    │
     │ job·CV·scan  │
     └──────────────┘
```

**7 capabilities · 7 MCP servers · 0 implementation in the orchestrator**

Each capability is its own repository, its own MCP server, its own lifecycle. LAOS composes them — it never owns them.

</div>

<div align="center" style="display:flex;flex-wrap:wrap;gap:32px;justify-content:center;margin:36px 0;">

<div style="text-align:center;min-width:110px;">
  <div style="font-weight:700;font-size:1.1em;opacity:0.5;letter-spacing:0.05em;">LATADE</div>
  <div style="font-size:0.8em;opacity:0.55;">sql · DuckDB · dbt · quality · docs</div>
</div>

<div style="text-align:center;min-width:110px;">
  <div style="font-weight:700;font-size:1.1em;opacity:0.5;letter-spacing:0.05em;">LADESIGN</div>
  <div style="font-size:0.8em;opacity:0.55;">dashboards · decks · wireframes · video</div>
</div>

<div style="text-align:center;min-width:110px;">
  <div style="font-weight:700;font-size:1.1em;opacity:0.5;letter-spacing:0.05em;">LAN8N</div>
  <div style="font-size:0.8em;opacity:0.55;">n8n · workflows · integrations · alerts</div>
</div>

<div style="text-align:center;min-width:110px;">
  <div style="font-weight:700;font-size:1.1em;opacity:0.5;letter-spacing:0.05em;">LACOUNCIL</div>
  <div style="font-size:0.8em;opacity:0.55;">proposals · voting · trust · memory</div>
</div>

<div style="text-align:center;min-width:110px;">
  <div style="font-weight:700;font-size:1.1em;opacity:0.5;letter-spacing:0.05em;">LAECON</div>
  <div style="font-size:0.8em;opacity:0.55;">econometrics · ML · causal · interpret</div>
</div>

<div style="text-align:center;min-width:110px;">
  <div style="font-weight:700;font-size:1.1em;opacity:0.5;letter-spacing:0.05em;">LAENGINE</div>
  <div style="font-size:0.8em;opacity:0.55;">simulation · match engine · squad mgmt</div>
</div>

<div style="text-align:center;min-width:110px;">
  <div style="font-weight:700;font-size:1.1em;opacity:0.5;letter-spacing:0.05em;">CAREEROPS</div>
  <div style="font-size:0.8em;opacity:0.55;">job search · CV · portal scan</div>
</div>

</div>

---

## How a Client Project Works

<table style="width:100%;border-collapse:collapse;">
  <tr>
    <td style="vertical-align:top;width:36px;padding-right:16px;padding-bottom:16px;"><span style="display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:28px;border:1px solid currentColor;font-size:0.75em;font-weight:600;opacity:0.4;">1</span></td>
    <td style="padding-bottom:16px;"><strong>Brief → contract</strong><br/><span style="opacity:0.45;font-size:0.9em;">A project is born as its own repository. LAOS holds the contract (<code>project.yaml</code>) — the routing table, the delivery checklist — nothing else.</span></td>
  </tr>
  <tr>
    <td style="vertical-align:top;width:36px;padding-right:16px;padding-bottom:16px;"><span style="display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:28px;border:1px solid currentColor;font-size:0.75em;font-weight:600;opacity:0.4;">2</span></td>
    <td style="padding-bottom:16px;"><strong>Needs → capabilities</strong><br/><span style="opacity:0.45;font-size:0.9em;">The orchestrator resolves declared needs via the registry. Deterministic. No guessing.</span></td>
  </tr>
  <tr>
    <td style="vertical-align:top;width:36px;padding-right:16px;padding-bottom:16px;"><span style="display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:28px;border:1px solid currentColor;font-size:0.75em;font-weight:600;opacity:0.4;">3</span></td>
    <td style="padding-bottom:16px;"><strong>WDL preflight</strong><br/><span style="opacity:0.45;font-size:0.9em;">The workflow-decomposer validates the plan before any specialist is dispatched. No bypass without manifest + penalty.</span></td>
  </tr>
  <tr>
    <td style="vertical-align:top;width:36px;padding-right:16px;padding-bottom:16px;"><span style="display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:28px;border:1px solid currentColor;font-size:0.75em;font-weight:600;opacity:0.4;">4</span></td>
    <td style="padding-bottom:16px;"><strong>Specialist dispatch via MCP</strong><br/><span style="opacity:0.45;font-size:0.9em;">Data-architect, dashboard-designer, automation-engineer — each talks only to its capability MCP. Siloed by design.</span></td>
  </tr>
  <tr>
    <td style="vertical-align:top;width:36px;padding-right:16px;padding-bottom:16px;"><span style="display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:28px;border:1px solid currentColor;font-size:0.75em;font-weight:600;opacity:0.4;">5</span></td>
    <td style="padding-bottom:16px;"><strong>Delivery review</strong><br/><span style="opacity:0.45;font-size:0.9em;">The delivery-reviewer validates every artifact against the P0-P2 checklist. No push without sign-off.</span></td>
  </tr>
  <tr>
    <td style="vertical-align:top;width:36px;padding-right:16px;"><span style="display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:28px;border:1px solid currentColor;font-size:0.75em;font-weight:600;opacity:0.4;">6</span></td>
    <td><strong>Artifacts land in the child repo</strong><br/><span style="opacity:0.45;font-size:0.9em;">LAOS never stores implementation. Every project is self-contained, independently forkable.</span></td>
  </tr>
</table>

---

## Delivered Projects

<div align="center">

<table style="width:100%;max-width:720px;border-collapse:separate;border-spacing:0;font-size:0.9em;">
  <tr style="border-bottom:1px solid currentColor;">
    <th align="left" style="padding:10px 14px;font-weight:600;opacity:0.5;">Project</th>
    <th align="left" style="padding:10px 14px;font-weight:600;opacity:0.5;">Domain</th>
    <th align="right" style="padding:10px 14px;font-weight:600;opacity:0.5;">Impact</th>
  </tr>
  <tr>
    <td style="padding:8px 14px;font-weight:500;"><a href="https://github.com/laurentaf/abandono-academico" style="text-decoration:none;">abandono-academico</a></td>
    <td style="padding:8px 14px;opacity:0.6;">ML — Dropout prediction</td>
    <td style="padding:8px 14px;text-align:right;font-variant-numeric:tabular-nums;"><strong>87.5%</strong> accuracy · <strong>93.7%</strong> recall · 32k students</td>
  </tr>
  <tr>
    <td style="padding:8px 14px;font-weight:500;"><a href="https://github.com/laurentaf/hospital-viana-claims" style="text-decoration:none;">hospital-viana-claims</a></td>
    <td style="padding:8px 14px;opacity:0.6;">Healthcare ETL</td>
    <td style="padding:8px 14px;text-align:right;font-variant-numeric:tabular-nums;">6 DQ checks · IFRS17-ready · daily GH Actions</td>
  </tr>
  <tr>
    <td style="padding:8px 14px;font-weight:500;"><a href="https://github.com/laurentaf/giovanna-rupture-monitor" style="text-decoration:none;">giovanna-rupture-monitor</a></td>
    <td style="padding:8px 14px;opacity:0.6;">Retail analytics</td>
    <td style="padding:8px 14px;text-align:right;font-variant-numeric:tabular-nums;">4,150 regions analyzed · 33% stock-out detection</td>
  </tr>
  <tr>
    <td style="padding:8px 14px;font-weight:500;"><a href="https://github.com/laurentaf/emanuella-stock-ingestion" style="text-decoration:none;">emanuella-stock-ingestion</a></td>
    <td style="padding:8px 14px;opacity:0.6;">Retail ETL</td>
    <td style="padding:8px 14px;text-align:right;font-variant-numeric:tabular-nums;">dbt-ready · 3-stage medallion · SLA &lt; 5 min</td>
  </tr>
  <tr>
    <td style="padding:8px 14px;font-weight:500;"><a href="https://github.com/laurentaf/previsao-concursos" style="text-decoration:none;">previsao-concursos</a></td>
    <td style="padding:8px 14px;opacity:0.6;">NLP — Education</td>
    <td style="padding:8px 14px;text-align:right;font-variant-numeric:tabular-nums;">1,236 questions · 27 contests · Laplace smoothing</td>
  </tr>
  <tr style="border-top:1px solid currentColor;border-bottom:1px solid currentColor;">
    <td style="padding:8px 14px;font-weight:500;"><a href="https://github.com/laurentaf/laengine" style="text-decoration:none;">brasfoot-poc → laengine</a></td>
    <td style="padding:8px 14px;opacity:0.6;">Game dev capability</td>
    <td style="padding:8px 14px;text-align:right;font-variant-numeric:tabular-nums;">10-team simulation · round-robin · MCP tools</td>
  </tr>
  <tr>
    <td colspan="3" style="padding:10px 14px;opacity:0.35;font-size:0.85em;text-align:center;">Every project is its own repository. Contract in LAOS; everything else in the child repo.</td>
  </tr>
</table>

</div>

---

## What This Proves

<div align="center">

<table style="width:100%;max-width:720px;border-collapse:separate;border-spacing:0;font-size:0.9em;">
  <tr style="border-bottom:1px solid currentColor;">
    <th align="left" style="padding:10px 14px;font-weight:600;opacity:0.5;width:36%;">Skill</th>
    <th align="left" style="padding:10px 14px;font-weight:600;opacity:0.5;">Evidence</th>
  </tr>
  <tr>
    <td style="padding:8px 14px;"><strong>System architecture</strong></td>
    <td style="padding:8px 14px;opacity:0.7;">Designed a meta-system orchestrating 7 independent capabilities across 4 domains</td>
  </tr>
  <tr>
    <td style="padding:8px 14px;"><strong>MCP protocol</strong></td>
    <td style="padding:8px 14px;opacity:0.7;">Wired 7 MCP servers — data, design, automation, governance, econometrics, game, career</td>
  </tr>
  <tr>
    <td style="padding:8px 14px;"><strong>Declarative contracts</strong></td>
    <td style="padding:8px 14px;opacity:0.7;"><code>project.yaml</code> as single source of truth → deterministic need-to-capability routing</td>
  </tr>
  <tr>
    <td style="padding:8px 14px;"><strong>Governance engineering</strong></td>
    <td style="padding:8px 14px;opacity:0.7;">LACOUNCIL: proposals, Conselho voting (unanimity / supermajority / majority), trust scores, DuckDB memory</td>
  </tr>
  <tr>
    <td style="padding:8px 14px;"><strong>Multi-agent orchestration</strong></td>
    <td style="padding:8px 14px;opacity:0.7;">9 subagent types, WDL preflight gate, sequential / parallel / consensus dispatch modes</td>
  </tr>
  <tr>
    <td style="padding:8px 14px;"><strong>Quality automation</strong></td>
    <td style="padding:8px 14px;opacity:0.7;">12 OpenCode plugins enforce hard rules mechanically (not by prompt). Delivery-reviewer validates every project</td>
  </tr>
  <tr>
    <td style="padding:8px 14px;"><strong>SDD methodology</strong></td>
    <td style="padding:8px 14px;opacity:0.7;">Every project produces 8+ SDD artifacts before any implementation code</td>
  </tr>
  <tr>
    <td style="padding:8px 14px;"><strong>CI/CD for AI systems</strong></td>
    <td style="padding:8px 14px;opacity:0.7;">GitHub Actions, preflight checks, boot validation per dispatch</td>
  </tr>
</table>

</div>

---

## Key Files

<table style="width:100%;max-width:640px;border-collapse:separate;border-spacing:0;font-size:0.9em;">
  <tr style="border-bottom:1px solid currentColor;">
    <th align="left" style="padding:8px 12px;font-weight:600;opacity:0.5;">File</th>
    <th align="left" style="padding:8px 12px;font-weight:600;opacity:0.5;">Purpose</th>
  </tr>
  <tr>
    <td style="padding:6px 12px;font-family:monospace;font-size:0.85em;"><code>AGENTS.md</code></td>
    <td style="padding:6px 12px;opacity:0.7;">Hard rules + agent topology + 12-plugin architecture</td>
  </tr>
  <tr>
    <td style="padding:6px 12px;font-family:monospace;font-size:0.85em;"><code>registry/needs-to-capabilities.yaml</code></td>
    <td style="padding:6px 12px;opacity:0.7;">Deterministic routing — 20+ needs → capabilities</td>
  </tr>
  <tr>
    <td style="padding:6px 12px;font-family:monospace;font-size:0.85em;"><code>registry/capabilities.yaml</code></td>
    <td style="padding:6px 12px;opacity:0.7;">Full capability catalog (7 domain + platform MCPs)</td>
  </tr>
  <tr>
    <td style="padding:6px 12px;font-family:monospace;font-size:0.85em;"><code>knowledge/padroes-entrega.md</code></td>
    <td style="padding:6px 12px;opacity:0.7;">P0-P2 delivery checklist — 13+ checks, SDD scaffold enforcement</td>
  </tr>
  <tr>
    <td style="padding:6px 12px;font-family:monospace;font-size:0.85em;"><code>knowledge/sdd-principles.md</code></td>
    <td style="padding:6px 12px;opacity:0.7;">Spec-Driven Development — 9-file scaffold matrix</td>
  </tr>
  <tr>
    <td style="padding:6px 12px;font-family:monospace;font-size:0.85em;"><code>workflows/</code></td>
    <td style="padding:6px 12px;opacity:0.7;">Project archetype templates (etl, dashboard, presentation)</td>
  </tr>
  <tr>
    <td style="padding:6px 12px;font-family:monospace;font-size:0.85em;"><code>projects/&lt;name&gt;/project.yaml</code></td>
    <td style="padding:6px 12px;opacity:0.7;">Contract for every client project</td>
  </tr>
  <tr>
    <td style="padding:6px 12px;font-family:monospace;font-size:0.85em;"><code>scripts/subagent_boot_check.py</code></td>
    <td style="padding:6px 12px;opacity:0.7;">6-dimension validation before every specialist dispatch</td>
  </tr>
</table>

---

## Quick Start

<div style="background:rgba(128,128,128,0.06);border-radius:12px;padding:16px 24px;font-family:monospace;font-size:0.85em;overflow-x:auto;max-width:600px;">

<pre style="margin:0;line-height:1.7;">
<span style="opacity:0.35;"># Install dependencies</span>
uv sync

<span style="opacity:0.35;"># Health check</span>
uv run python scripts/preflight_check.py .

<span style="opacity:0.35;"># Launch the orchestrator</span>
opencode .
</pre>

</div>

---

## Architecture Rules

<ol style="padding-left:20px;line-height:1.7;">

<li style="margin-bottom:6px;">
  <strong>No implementation in LAOS.</strong>
  <span style="display:block;opacity:0.5;font-size:0.9em;margin-left:4px;">SQL, dashboards, n8n flows live in capability repos — never here.</span>
</li>

<li style="margin-bottom:6px;">
  <strong>Reached only via MCP.</strong>
  <span style="display:block;opacity:0.5;font-size:0.9em;margin-left:4px;">Capability repos are never <code>cd</code>'d into directly. The MCP wall enforces this mechanically.</span>
</li>

<li style="margin-bottom:6px;">
  <strong>Structural changes require consensus.</strong>
  <span style="display:block;opacity:0.5;font-size:0.9em;margin-left:4px;">LACOUNCIL proposals → Conselho voting (4 subagents) → implementation. No bypass without supermajority.</span>
</li>

<li style="margin-bottom:6px;">
  <strong>Every project has two homes.</strong>
  <span style="display:block;opacity:0.5;font-size:0.9em;margin-left:4px;">Contract in LAOS; all artifacts live in the child repo. LAOS never stores implementation.</span>
</li>

<li style="margin-bottom:6px;">
  <strong>WDL preflight is mandatory.</strong>
  <span style="display:block;opacity:0.5;font-size:0.9em;margin-left:4px;">No specialist dispatch without a <code>READY</code> verdict from the workflow-decomposer. Bypass requires a manifest + trust-score penalty.</span>
</li>

<li style="margin-bottom:6px;">
  <strong>Patterns repeated 3+ times trigger investigation.</strong>
  <span style="display:block;opacity:0.5;font-size:0.9em;margin-left:4px;">LACOUNCIL detects them automatically and proposes structural improvements.</span>
</li>

</ol>

---

## The LAOS Difference

<blockquote style="border-left:3px solid currentColor;padding-left:20px;margin:24px 0;opacity:0.8;">

**LAOS is not a framework you import. It's a system you inhabit.**

- Frameworks give you functions. LAOS gives you **governance**.
- Platforms give you lock-in. LAOS gives you **MCP-native composability**.
- AI agents give you answers. LAOS gives you **a system that checks its own work**.

> <span style="opacity:0.6;">"Data architecture isn't about the tools — it's about whether the C-suite trusts what it sees on the dashboard."</span>

</blockquote>

---

## About the Architect

<div style="display:flex;align-items:flex-start;gap:24px;flex-wrap:wrap;max-width:600px;">

<div>

### Laurent
<span style="opacity:0.5;">Data Architect &amp; ML Engineer</span>

Built LAOS because he couldn't find a system that composably orchestrates data, design, automation, and governance without becoming the implementation itself.

<p style="margin-top:12px;">
  <a href="https://github.com/laurentaf" style="text-decoration:none;border:1px solid currentColor;border-radius:100px;padding:6px 20px;font-size:0.85em;">GitHub</a>
  &nbsp;
  <a href="https://linkedin.com/in/lauferreira" style="text-decoration:none;border:1px solid currentColor;border-radius:100px;padding:6px 20px;font-size:0.85em;">LinkedIn</a>
</p>

Campinas/SP · Remote-first

<span style="opacity:0.45;font-size:0.85em;">Open to: Data Architect, AI Data Engineer, Analytics Engineering</span>

</div>

</div>

---

<div align="center" style="margin:48px 0;opacity:0.25;font-size:0.8em;">

<svg width="32" height="32" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-bottom:8px;">
  <rect x="4" y="4" width="56" height="56" rx="12" stroke="currentColor" stroke-width="1.5" fill="none" opacity="0.15"/>
  <line x1="14" y1="20" x2="14" y2="46" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="24" y1="20" x2="24" y2="46" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="34" y1="14" x2="34" y2="46" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="44" y1="20" x2="44" y2="46" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="54" y1="26" x2="54" y2="46" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
</svg>

<br/>
LAOS — Laurent Agent Operating System
<br/>
<span style="opacity:0.5;">Crown the operator.</span>

</div>