<!--
  LAOS Brand — Brand identity, narrative architecture, and launch materials
  README.md  |  github.com/laurentaf/laos-brand
  Brand: "A 3,000-year inversion made visible."
  Tone: Monumental, clear, refined — Stripe docs × Linear clarity.
  This file uses inline HTML/CSS for visual polish.
-->

<div align="center" style="margin-top:48px;margin-bottom:24px;">

<!-- Crown emblem — dissolved crown / distributed dots -->
<svg width="80" height="80" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-bottom:8px;">
  <rect x="4" y="4" width="56" height="56" rx="14" stroke="#3B1F5E" stroke-width="1.5" fill="none" opacity="0.25"/>
  <!-- Crown laurel arcs -->
  <path d="M16 44 Q22 28 32 24 Q42 28 48 44" stroke="#3B1F5E" stroke-width="1.8" fill="none" opacity="0.6"/>
  <path d="M20 44 Q26 32 32 28 Q38 32 44 44" stroke="#C8A951" stroke-width="1.5" fill="none" opacity="0.4"/>
  <!-- Dissolving dots (the laós) -->
  <circle cx="20" cy="40" r="2" fill="#3B1F5E" opacity="0.5"/>
  <circle cx="28" cy="34" r="2.5" fill="#3B1F5E" opacity="0.7"/>
  <circle cx="36" cy="34" r="2.5" fill="#3B1F5E" opacity="0.7"/>
  <circle cx="44" cy="40" r="2" fill="#3B1F5E" opacity="0.5"/>
  <circle cx="24" cy="28" r="1.5" fill="#C8A951" opacity="0.6"/>
  <circle cx="32" cy="22" r="2" fill="#C8A951" opacity="0.8"/>
  <circle cx="40" cy="28" r="1.5" fill="#C8A951" opacity="0.6"/>
</svg>

<br/>

# LAOS Brand
### Identity &bull; Narrative &bull; Design System &bull; Assets

<p style="margin:12px 0;">
  <img src="https://img.shields.io/badge/Status-ACTIVE-3B1F5E?style=flat" alt="Status: ACTIVE"/>
  &nbsp;
  <img src="https://img.shields.io/badge/License-MIT-31c754?style=flat" alt="License: MIT"/>
  &nbsp;
  <a href="https://github.com/laurentaf/laos"><img src="https://img.shields.io/badge/Ecosystem-LAOS-6c5ce7?style=flat" alt="LAOS Ecosystem"/></a>
</p>

<hr style="width:48px;margin:24px auto;border:none;border-top:2px solid #3B1F5E;opacity:0.3;"/>

</div>

> **A 3,000-year inversion made visible.**  
> The imperial laurel → the sovereign laós. LAOS dissolves the crown and distributes sovereignty to every operator. This repository is the source of truth for that identity — its design system, narrative architecture, brand assets, and usage guidelines.

---

## The Brand in 30 Seconds

| Concept | Expression |
|---------|-----------|
| **Core metaphor** | The emperor's laurel → the people's intelligence |
| **Brand spine** | "The laurel was exclusive. The intelligence doesn't have to be." |
| **Tone** | Monumental but clear. Stripe docs × Linear clarity. No hype, no dry. |
| **Visual tension** | Authority (purple, gold, structured grids, editorial serifs) vs Access (warm paper, open space, human scale, clean sans) |
| **Audience** | Data architects, ML engineers, analytics engineers, technical leaders |

The full story spine, manifesto, voice guidelines, and taglines are in [`narrative/`](./narrative/).

---

## Color Palette

<div align="center">

<table style="width:100%;max-width:520px;border-collapse:separate;border-spacing:0;font-size:0.9em;">
  <tr style="border-bottom:1px solid currentColor;opacity:0.3;">
    <th align="left" style="padding:10px 14px;font-weight:600;opacity:0.5;">Color</th>
    <th align="center" style="padding:10px 14px;font-weight:600;opacity:0.5;">Swatch</th>
    <th align="left" style="padding:10px 14px;font-weight:600;opacity:0.5;">Token</th>
    <th align="left" style="padding:10px 14px;font-weight:600;opacity:0.5;">Usage</th>
  </tr>
  <tr>
    <td style="padding:8px 14px;font-weight:500;">Laurel Purple</td>
    <td align="center" style="padding:8px 14px;"><span style="display:inline-block;width:24px;height:24px;border-radius:4px;background:#3B1F5E;border:1px solid rgba(0,0,0,0.1);vertical-align:middle;"></span></td>
    <td style="padding:8px 14px;font-family:monospace;font-size:0.85em;">#3B1F5E</td>
    <td style="padding:8px 14px;opacity:0.7;">Primary accent, CTAs, brand mark</td>
  </tr>
  <tr>
    <td style="padding:8px 14px;font-weight:500;">Antique Gold</td>
    <td align="center" style="padding:8px 14px;"><span style="display:inline-block;width:24px;height:24px;border-radius:4px;background:#C8A951;border:1px solid rgba(0,0,0,0.1);vertical-align:middle;"></span></td>
    <td style="padding:8px 14px;font-family:monospace;font-size:0.85em;">#C8A951</td>
    <td style="padding:8px 14px;opacity:0.7;">Secondary accent, data highlights, decorative</td>
  </tr>
  <tr>
    <td style="padding:8px 14px;font-weight:500;">Near-Black</td>
    <td align="center" style="padding:8px 14px;"><span style="display:inline-block;width:24px;height:24px;border-radius:4px;background:#0A0A0A;border:1px solid rgba(0,0,0,0.1);vertical-align:middle;"></span></td>
    <td style="padding:8px 14px;font-family:monospace;font-size:0.85em;">#0A0A0A</td>
    <td style="padding:8px 14px;opacity:0.7;">Body text, dark mode surfaces</td>
  </tr>
  <tr>
    <td style="padding:8px 14px;font-weight:500;">Warm Cream</td>
    <td align="center" style="padding:8px 14px;"><span style="display:inline-block;width:24px;height:24px;border-radius:4px;background:#F7F5EE;border:1px solid rgba(0,0,0,0.1);vertical-align:middle;"></span></td>
    <td style="padding:8px 14px;font-family:monospace;font-size:0.85em;">#F7F5EE</td>
    <td style="padding:8px 14px;opacity:0.7;">Light mode backgrounds, card surfaces</td>
  </tr>
</table>

</div>

> **Note:** Gold (#C8A951) has insufficient contrast on white for body text (2.8:1). Use it for decorative/display purposes only. Full accessibility specs in the [design system](./design/design-system.md).

---

## Typography

<table style="width:100%;max-width:520px;border-collapse:separate;border-spacing:0;font-size:0.9em;">
  <tr style="border-bottom:1px solid currentColor;opacity:0.3;">
    <th align="left" style="padding:8px 12px;font-weight:600;opacity:0.5;">Family</th>
    <th align="left" style="padding:8px 12px;font-weight:600;opacity:0.5;">Role</th>
    <th align="left" style="padding:8px 12px;font-weight:600;opacity:0.5;">Weights</th>
  </tr>
  <tr>
    <td style="padding:6px 12px;font-family:'Playfair Display',Georgia,serif;font-weight:700;font-size:1em;">Playfair Display</td>
    <td style="padding:6px 12px;opacity:0.7;">Heading (editorial)</td>
    <td style="padding:6px 12px;opacity:0.7;">400, 600, 700, 900</td>
  </tr>
  <tr>
    <td style="padding:6px 12px;font-family:Inter,system-ui,sans-serif;font-weight:500;font-size:0.95em;">Inter</td>
    <td style="padding:6px 12px;opacity:0.7;">Body (clean)</td>
    <td style="padding:6px 12px;opacity:0.7;">300, 400, 500, 600, 700</td>
  </tr>
  <tr>
    <td style="padding:6px 12px;font-family:'Inter Tight',Inter,sans-serif;font-weight:600;font-size:0.95em;">Inter Tight</td>
    <td style="padding:6px 12px;opacity:0.7;">Display (deck)</td>
    <td style="padding:6px 12px;opacity:0.7;">400, 500, 600, 700, 800, 900</td>
  </tr>
  <tr>
    <td style="padding:6px 12px;font-family:'JetBrains Mono',Consolas,monospace;font-weight:400;font-size:0.9em;">JetBrains Mono</td>
    <td style="padding:6px 12px;opacity:0.7;">Monospace / code</td>
    <td style="padding:6px 12px;opacity:0.7;">400, 500</td>
  </tr>
</table>

---

## Repository Contents

| Path | Description | Format |
|------|-------------|--------|
| [`design/design-system.md`](./design/design-system.md) | Full design system — tokens, spacing, grid, motion, components | Markdown |
| [`design/keynote.html`](./design/keynote.html) | LAOS keynote deck (brand launch presentation) | HTML |
| [`design/landing-page.html`](./design/landing-page.html) | LAOS brand landing page | HTML |
| [`narrative/manifesto.md`](./narrative/manifesto.md) | "The Crown is Dissolved" — brand manifesto | Markdown |
| [`narrative/product-naming.md`](./narrative/product-naming.md) | Naming rationale (Laurent Core, Laós Layer, Talos Mesh, The Oracle, The Forum) | Markdown |
| [`narrative/story-spine.md`](./narrative/story-spine.md) | Brand story structure and narrative architecture | Markdown |
| [`narrative/taglines.md`](./narrative/taglines.md) | Tagline variants and usage guidelines | Markdown |
| [`narrative/voice.md`](./narrative/voice.md) | Brand voice, tone, and language rules | Markdown |
| [`decisions/brand-architecture.md`](./decisions/brand-architecture.md) | Brand architecture decisions (ADR-style) | Markdown |

---

## Usage Guidelines

### Do
- Use **Laurel Purple** (#3B1F5E) as the primary accent — CTAs, links, brand marks, icons
- Use **Antique Gold** (#C8A951) sparingly — data highlights, emphasis, decorative accents
- Default to **Warm Cream** (#F7F5EE) for light mode backgrounds
- Keep the 8px rhythm — every margin, padding, and gap is a multiple of 8
- Use Playfair Display for dramatic headlines; Inter for all body text and UI

### Don't
- ❌ Never mix purple and gold equally — one must dominate
- ❌ Never use purple on purple (insufficient contrast)
- ❌ Never use generic blue SaaS gradients
- ❌ Never use lorem ipsum or placeholder copy in brand materials
- ❌ Never apply rounded corners to deck/presentation cards

### Spacing
The base unit is **8px**. All spacing tokens are multiples of 8:

| Token | Value | Token | Value |
|-------|-------|-------|-------|
| `--laos-space-2` | 8px | `--laos-space-6` | 32px |
| `--laos-space-3` | 12px | `--laos-space-7` | 48px |
| `--laos-space-4` | 16px | `--laos-space-8` | 64px |
| `--laos-space-5` | 24px | `--laos-space-9` | 96px |

Full token reference in [`design/design-system.md`](./design/design-system.md).

---

## Brand Architecture (Module Naming)

| Module | Inspiration | Rejected | Why |
|--------|-------------|----------|-----|
| **Laurent Core** | Laurel crown of the emperor | "Engine" | Engine is brute force; Core is center of gravity |
| **Laós Layer** | λαός — sovereign people | "Runtime" | Runtime is empty; Layer carries jurisdiction |
| **Talos Mesh** | First automaton (Greek myth) | "Guard" | Guard is perimeter; Mesh is distributed |
| **The Oracle** | Oracle of Delphi | "AI" | Oracle names the function and the position |
| **The Forum** | Roman forum | "Dashboard" | Dashboard is read-only; Forum is deliberative |

Full narrative in [`narrative/product-naming.md`](./narrative/product-naming.md).

---

## Quick Start for Designers

```bash
# Clone the repo
git clone https://github.com/laurentaf/laos-brand.git
cd laos-brand

# Open the brand design system
open design/design-system.md

# Preview the keynote
open design/keynote.html

# Preview the landing page
open design/landing-page.html
```

### Importing the Design System

For CSS projects, copy the token variables from `design/design-system.md` (Palette, Typography, Spacing sections) into your project's `:root` block. Tokens follow the naming convention `--laos-{category}-{property}-{variant}`.

---

## Contributing

| Scope | Path |
|-------|------|
| **New asset / variant** | Open an [issue](https://github.com/laurentaf/laos-brand/issues) with visual reference |
| **Design system update** | PR to `design/design-system.md` with rationale |
| **Narrative / copy** | PR to `narrative/` directory |

---

## License

<div style="margin:16px 0;">

**MIT** — see [`LICENSE`](https://github.com/laurentaf/laos-brand/blob/main/LICENSE) for the full text.

The laurel was exclusive. The intelligence doesn't have to be.

</div>

---

<div align="center" style="margin:36px 0;opacity:0.35;font-size:0.85em;">
<svg width="28" height="28" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-bottom:4px;">
  <rect x="4" y="4" width="56" height="56" rx="14" stroke="#3B1F5E" stroke-width="1.5" fill="none" opacity="0.15"/>
  <path d="M16 44 Q22 28 32 24 Q42 28 48 44" stroke="#3B1F5E" stroke-width="1.5" fill="none" opacity="0.4"/>
  <circle cx="20" cy="40" r="1.5" fill="#3B1F5E" opacity="0.4"/>
  <circle cx="28" cy="34" r="2" fill="#3B1F5E" opacity="0.6"/>
  <circle cx="36" cy="34" r="2" fill="#3B1F5E" opacity="0.6"/>
  <circle cx="44" cy="40" r="1.5" fill="#3B1F5E" opacity="0.4"/>
  <circle cx="32" cy="22" r="1.5" fill="#C8A951" opacity="0.7"/>
</svg>
<br/>
LAOS — <span style="opacity:0.6;">Crown the operator.</span>
</div>
