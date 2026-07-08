# Contract — lacareerops-selfeval

## Brief

**Project:** Avaliação estratégica do posicionamento de Laurent Ferreira
para o mercado de AI Data Engineer / Data Specialist em 2026.

**Brief:** Em single-shot, o usuário pediu 5 eixos de análise: (1) gaps
de ferramentas vs mercado, (2) gaps do portfolio GitHub projeto-a-projeto,
(3) curriculum gaps cruzando 1 × 2, (4) estratégia LinkedIn (avaliar
ideia original + gerar 30 posts + âncora de autoridade), (5) wage bands
para negociação em entrevistas. Input: o CV fornecido pelo usuário
em `user_input_data/`.

## Needs

**Needs declaradas:**
- `career-evaluation` → roteia para `lacareerops` (primary)
- `research` → roteia para `exa` (primary) + `context7` (optional)
- `design` → roteia para `ladesign` (primary)
- `documentation-lookup` → `context7`
- `repo-operations` → `github`

## Deliverables

**Deliverables (paths relativos a `projects/lacareerops-selfeval/`):**
- `artifacts/cv/parsed-cv.md` — texto extraído do docx em seções
- `artifacts/market/tools-gaps.md` — ferramentas/skills do mercado, cobertura
- `artifacts/portfolio/github-audit.md` — auditoria projeto-a-projeto
- `artifacts/cv/curriculum-gaps.md` — matriz 3 zonas
- `artifacts/strategy/strategy-evaluation.md` — avaliação da ideia do usuário
- `artifacts/strategy/30-posts-backlog.md` — 30 posts estruturados
- `artifacts/strategy/visuals-deck.html` — visuals dos 30 conceitos
- `artifacts/market/wage-bands.md` — faixas salariais 3 markets
- `artifacts/review/checklist.md` — output do delivery-reviewer

## Capabilities

**Capabilities usadas:** LACOUNCIL (workflow-decomposer preflight),
LACAREEROPS (CV parsing + career_ops_evaluate), LADESIGN (visuals-deck
via dashboard-designer), LATADE (parsers estruturados auxiliares),
GITHUB MCP (audit dos repos `laurentaf`), EXA (research de JDs + wage),
CONTEXT7 (docs de libs/frameworks).

## Repo

**Repo:** `null` — projeto ad-hoc. Sem child repo. Outputs ficam em
`projects/lacareerops-selfeval/artifacts/`.

**Status:** SDD scaffold criado 2026-06-21. Próximo passo: WDL preflight
gate via `workflow-decomposer`.
