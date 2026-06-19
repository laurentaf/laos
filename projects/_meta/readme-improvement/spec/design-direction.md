# Design Direction — README Portfolio Improvement

## Direction

Every README in the portfolio should feel like a **landing page for the project** — not a dump of information. The reader should understand what the project is, why it matters, and how to use it within 10 seconds of opening the page.

## Principles

### 1. Visual Hierarchy Is Non-Negotiable
Headers, spacing, and opacity create a reading rhythm. No wall of text. Every section has a clear visual boundary. Tables use `border-collapse:separate; border-spacing:0` for clean lines.

### 2. Badges Are Identity, Not Decoration
A consistent badge set (Python, License, Status, Ecosystem) across all repos creates portfolio-wide coherence. Colors follow the LAOS palette: Python blue `#3776AB`, MIT green `#31c754`, status colors (STABLE `#00b894`, BASIC `#fdcb6e`).

### 3. Show, Don't Tell
Screenshots, GIFs, Mermaid diagrams, and code output examples replace paragraphs of description. A single dashboard screenshot is worth 500 words of "what this project does."

### 4. The LAOS README Is the Template
The `laos` README (20/20) demonstrates: SVG emblem, inline CSS tables, numbered workflows, visual architecture with bordered cards. Other READMEs adapt these patterns to their domain — they don't copy them verbatim.

### 5. Bilingual Framing, Monolingual Content
Portuguese repos get English headers and summary at the top. The body stays in Portuguese. This maximizes international reach without erasing the original language.
