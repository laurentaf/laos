<!--
  LADESIGN — Design capability for LAOS
  README.md  |  github.com/laurentaf/ladesign
  Brand: "A design tool must look good."
  Tone: Refined, confident, visually expressive.
  Adapted from the LAOS README (20/20) inline-HTML pattern.
-->

<div align="center" style="margin-top:48px;margin-bottom:24px;">

<!-- Emblem: diamond / golden ratio mark -->
<svg width="72" height="72" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-bottom:4px;">
  <rect x="4" y="4" width="56" height="56" rx="12" stroke="#C8A951" stroke-width="1.5" fill="none" opacity="0.3"/>
  <path d="M32 8 L48 32 L32 56 L16 32 Z" stroke="#3B1F5E" stroke-width="2" fill="none" opacity="0.5"/>
  <circle cx="32" cy="32" r="6" fill="#C8A951" opacity="0.25"/>
  <circle cx="32" cy="32" r="3" fill="#C8A951" opacity="0.6"/>
  <line x1="16" y1="32" x2="48" y2="32" stroke="#3B1F5E" stroke-width="1" opacity="0.2"/>
  <line x1="32" y1="8" x2="32" y2="56" stroke="#3B1F5E" stroke-width="1" opacity="0.2"/>
</svg>

<br/>

# LADESIGN
### Dashboards &bull; Decks &bull; Wireframes &bull; Design Systems &bull; Video

<p style="margin:12px 0;">
  <img src="https://img.shields.io/badge/Python-%E2%89%A53.11-3776AB?style=flat&logo=python&logoColor=fff" alt="Python 3.11+"/>
  &nbsp;
  <img src="https://img.shields.io/badge/Status-STABLE-00b894?style=flat" alt="Status: STABLE"/>
  &nbsp;
  <img src="https://img.shields.io/badge/License-MIT-31c754?style=flat" alt="License: MIT"/>
  &nbsp;
  <img src="https://img.shields.io/badge/Skills-50%2B-ff7675?style=flat" alt="50+ skills"/>
  &nbsp;
  <a href="https://github.com/laurentaf/laos"><img src="https://img.shields.io/badge/Ecosystem-LAOS-6c5ce7?style=flat" alt="LAOS Ecosystem"/></a>
</p>

<hr style="width:48px;margin:24px auto;border:none;border-top:2px solid #C8A951;opacity:0.3;"/>

</div>

> **A design capability must feel designed.**  
> LADESIGN is the LAOS ecosystem's visual layer — producing dashboards, executive decks, wireframes, brand guidelines, design systems, and HyperFrames (HTML-to-video motion) from structured briefs. 50+ design skills, 5 core MCP tools, one consistent visual language.

---

## What LADESIGN Is

LADESIGN transforms structured specs into visual artifacts. It does not edit pixels — it *composes* them from design contracts (DESIGN.md), data models, and presentation outlines. Every artifact is deterministic, reproducible, and self-contained.

**Why LADESIGN exists:** Dashboards and decks are the public face of data work. LADESIGN ensures that face is always consistent — same brand, same tokens, same layout discipline — whether the output is an executive deck, a data dashboard, or a video animation.

**Provenance:** LAOS ecosystem design capability. Produces artifacts under `artifacts/design/`, `artifacts/deck/`, and `artifacts/hyperframes/`.

---

## Architecture

<div align="center" style="margin:24px 0;">

<table style="border-collapse:separate;border-spacing:0;min-width:560px;">
  <tr>
    <td colspan="3" align="center" style="padding:0 0 8px 0;">
      <div style="display:inline-block;border:1.5px solid #3B1F5E;border-radius:8px;padding:12px 24px;text-align:center;">
        <div style="font-weight:700;font-size:1em;letter-spacing:0.04em;color:#3B1F5E;">LADESIGN MCP Server</div>
        <div style="font-size:0.8em;opacity:0.5;">Python orchestrator · 50+ design skills</div>
      </div>
    </td>
  </tr>
  <tr><td colspan="3" align="center" style="padding:0;"><div style="width:1.5px;height:14px;background:#3B1F5E;opacity:0.2;margin:0 auto;"></div></td></tr>
  <tr>
    <td align="center" style="padding:0 8px;width:33%;">
      <div style="border:1px solid #3B1F5E;border-radius:6px;padding:8px 14px;text-align:center;">
        <div style="font-weight:600;font-size:0.85em;letter-spacing:0.02em;">Dashboards &amp; UI</div>
        <div style="font-size:0.7em;opacity:0.5;">Wireframes · Specs ·<br/>Visual hierarchy</div>
      </div>
    </td>
    <td align="center" style="padding:0 8px;width:33%;">
      <div style="border:1px solid #C8A951;border-radius:6px;padding:8px 14px;text-align:center;">
        <div style="font-weight:600;font-size:0.85em;letter-spacing:0.02em;">Decks &amp; Presentations</div>
        <div style="font-size:0.7em;opacity:0.5;">HTML → PPTX · Executive<br/>briefs · Video decks</div>
      </div>
    </td>
    <td align="center" style="padding:0 8px;width:33%;">
      <div style="border:1px solid #3B1F5E;border-radius:6px;padding:8px 14px;text-align:center;">
        <div style="font-weight:600;font-size:0.85em;letter-spacing:0.02em;">Design Systems</div>
        <div style="font-size:0.7em;opacity:0.5;">Tokens · Brand ·<br/>DESIGN.md contracts</div>
      </div>
    </td>
  </tr>
</table>

</div>

---

## MCP Tools

<table style="width:100%;border-collapse:separate;border-spacing:0;font-size:0.9em;">
  <tr style="border-bottom:1px solid #C8A951;opacity:0.4;">
    <th align="left" style="padding:10px 14px;font-weight:600;opacity:0.5;width:25%;">Tool</th>
    <th align="left" style="padding:10px 14px;font-weight:600;opacity:0.5;">Description</th>
  </tr>
  <tr><td style="padding:8px 14px;font-weight:500;"><code>generate_dashboard</code></td><td style="padding:8px 14px;opacity:0.7;">Dashboard spec from data model → self-contained HTML</td></tr>
  <tr><td style="padding:8px 14px;font-weight:500;"><code>generate_deck</code></td><td style="padding:8px 14px;opacity:0.7;">Presentation deck from outline → HTML + PPTX export</td></tr>
  <tr><td style="padding:8px 14px;font-weight:500;"><code>generate_wireframe</code></td><td style="padding:8px 14px;opacity:0.7;">Wireframe spec with layout hierarchy, density, rhythm</td></tr>
  <tr><td style="padding:8px 14px;font-weight:500;"><code>health</code></td><td style="padding:8px 14px;opacity:0.7;">Server liveness probe</td></tr>
  <tr><td style="padding:8px 14px;font-weight:500;"><code>list_supported_operations</code></td><td style="padding:8px 14px;opacity:0.7;">Full capability catalog + skills index</td></tr>
</table>

---

## Skills Library

LADESIGN ships **50+ design skills** — specialized templates and workflows that produce production-grade artifacts. Notable skills include:

<div align="center">

<table style="width:100%;max-width:640px;border-collapse:separate;border-spacing:0;font-size:0.85em;">
  <tr style="border-bottom:1px solid currentColor;opacity:0.3;">
    <th align="left" style="padding:8px 12px;font-weight:600;opacity:0.5;">Category</th>
    <th align="left" style="padding:8px 12px;font-weight:600;opacity:0.5;">Skills</th>
  </tr>
  <tr><td style="padding:6px 12px;font-weight:500;">Deck templates</td><td style="padding:6px 12px;opacity:0.7;">Swiss International, Editorial Burgundy, Digits Fintech, Retro Quarterly Review, After Hours Editorial</td></tr>
  <tr><td style="padding:6px 12px;font-weight:500;">HyperFrames video</td><td style="padding:6px 12px;opacity:0.7;">8-bit Orbit, WeRead Year-in-Review, Field Notes Editorial, Swiss User Research</td></tr>
  <tr><td style="padding:6px 12px;font-weight:500;">Design systems</td><td style="padding:6px 12px;opacity:0.7;">Design MD, Brand Kit, Brand Guidelines, Reference Design Contract, Design Taste Frontend</td></tr>
  <tr><td style="padding:6px 12px;font-weight:500;">Visual &amp; motion</td><td style="padding:6px 12px;opacity:0.7;">GSAP Core + Timeline + ScrollTrigger + React, Three.js, Shader Dev, D3 Visualization</td></tr>
  <tr><td style="padding:6px 12px;font-weight:500;">Image &amp; media</td><td style="padding:6px 12px;opacity:0.7;">Imagegen (Web + Mobile), Fal.ai suite (generate, edit, video, 3D, lip-sync), Sora, Replicate</td></tr>
  <tr><td style="padding:6px 12px;font-weight:500;">Research &amp; copy</td><td style="padding:6px 12px;opacity:0.7;">Research Decision Room, Brainstorming, Copywriting, Marketing Psychology, Ad Creative</td></tr>
  <tr><td style="padding:6px 12px;font-weight:500;">Platform design</td><td style="padding:6px 12px;opacity:0.7;">Apple HIG, WCAG 2.2, Material 3, Figma Generate + Implement, shadcn/ui</td></tr>
  <tr><td style="padding:6px 12px;font-weight:500;">Utility</td><td style="padding:6px 12px;opacity:0.7;">Theme Factory, Export/Download Debugging, Full Page Screenshot, Hand-drawn Diagrams</td></tr>
</table>

</div>

---

## Quick Start

```bash
# Install dependencies
uv sync

# Start the MCP server (daemon)
uv run ladesign-server
```

### Requirements

<table style="font-size:0.85em;border-collapse:separate;border-spacing:0;">
  <tr><td style="padding:6px 12px;font-weight:500;">Python</td><td style="padding:6px 12px;opacity:0.6;">≥ 3.11</td></tr>
  <tr><td style="padding:6px 12px;font-weight:500;">Runtime</td><td style="padding:6px 12px;opacity:0.6;">Node.js (for daemon mode, pnpm managed)</td></tr>
  <tr><td style="padding:6px 12px;font-weight:500;">Infrastructure</td><td style="padding:6px 12px;opacity:0.6;">LAOS orchestrator with OpenCode CLI</td></tr>
</table>

---

## Example: Dashboard from Data Model

A data-architect delivers a gold-aggregated table. LADESIGN turns it into a visual dashboard:

```
→ Input:   DuckDB table "sales_summary" with columns [region, product, revenue, qty]
→ Tool:    generate_dashboard(data_model=sales_summary, layout="executive")
→ Output:  artifacts/design/sales-dashboard.html
             — KPI cards (total revenue, units, YoY change)
             — Bar chart (revenue by region)
             — Heatmap (product × region performance)
             — Data table with sort/filter
             — Responsive, self-contained, single-file HTML
```

---

## Example: Deck from Outline

```
→ Input:   Markdown outline (5 slides: intro, data, model, results, next steps)
→ Tool:    generate_deck(outline=deck.md, template="swiss-international")
→ Output:  artifacts/deck/project-review.html
             — HTML with keyboard-navigation
             — Exportable to PPTX via python-pptx
             — 16-column Swiss grid, consistent typography
```

---

## Contributing

| Scope | Path |
|-------|------|
| **New design skill** | LACOUNCIL proposal → Conselho majority → add to skills/ directory |
| **Bug / improvement** | Open an [issue](https://github.com/laurentaf/ladesign/issues) |
| **Template contribution** | PR with standalone HTML + source.md reference |

See the [LAOS governance model](https://github.com/laurentaf/laos) for full details.

---

## License

<div style="margin:16px 0;">

**MIT** — see [`LICENSE`](https://github.com/laurentaf/ladesign/blob/main/LICENSE) for the full text.

Design is deterministic. The visual hierarchy is the argument.

</div>

---

<div align="center" style="margin:36px 0;opacity:0.25;font-size:0.8em;">
<svg width="28" height="28" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-bottom:4px;">
  <rect x="4" y="4" width="56" height="56" rx="12" stroke="#C8A951" stroke-width="1.5" fill="none" opacity="0.15"/>
  <path d="M32 8 L48 32 L32 56 L16 32 Z" stroke="#3B1F5E" stroke-width="2" fill="none" opacity="0.3"/>
  <circle cx="32" cy="32" r="3" fill="#C8A951" opacity="0.5"/>
</svg>
<br/>
LADESIGN — part of the <a href="https://github.com/laurentaf/laos" style="text-decoration:none;">LAOS</a> ecosystem
</div>
