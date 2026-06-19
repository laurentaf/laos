# Spec 000: README Portfolio Improvement

## Contexto

The `github.com/laurentaf` portfolio has 15 public repositories. An audit on 2026-06-19 revealed a bimodal distribution: LAOS ecosystem repos score 16-20/20 while capability repos (laecon, ladesign, lan8n) score 5/20. The average is 11.5/20. Four repos are CRITICAL (score < 8). The capability repos are the public face of the LAOS ecosystem but read like afterthoughts, undermining credibility.

## Decisão Inicial

Rewrite and improve all 15 READMEs in a tiered approach (CRITICAL → HIGH → MEDIUM → LOW), using the `laos` README as the gold standard. Each rewrite follows a consistent template adapted from the LAOS patterns. Cross-cutting improvements (badge system, Mermaid diagrams, bilingual headers) are applied portfolio-wide.

## Critérios de Pronto

- [ ] All 4 CRITICAL repos (laecon, ladesign, lan8n, laos-brand) have READMEs scoring ≥ 7/10 on both curriculum and design
- [ ] All HIGH repos (laengine, pizzarias, hospital-viana) have READMEs scoring ≥ 7/10
- [ ] All MEDIUM repos have badges, Mermaid diagrams, and bilingual headers where applicable
- [ ] All LOW repos have minor polish applied (screenshots, contributing sections)
- [ ] A reusable README template exists in `knowledge/readme-templates.md`
- [ ] Portfolio average rises from 11.5 to ≥ 14.5/20

## Alcance

### In-scope
- 15 public repositories from `github.com/laurentaf`
- README.md files only (no code changes, no repo structure changes)
- Badge system, visual hierarchy, content completeness, bilingual headers

### Fora do escopo
- Private repos (emprestisa, career-ops, lacareerops, previsao-concursos, brasfoot-poc, template-base, lopes-melo-telecom, personal)
- Code implementation or feature changes
- Repository structure reorganization
- CI/CD pipeline changes

## Capacidades Utilizadas

| Capability | Role |
|-----------|------|
| LADESIGN | Dashboard-designer subagent rewrites READMEs with visual polish |
| LATADE | Data-architect subagent handles data-heavy READMEs (latade, logistica-me) |
| LACOUNCIL | Record project, detect patterns for future portfolio improvements |

## Dependências

- Audit report: `artifacts/review/readme-audit-2026-06-19.md`
- LAOS README patterns (inline HTML/CSS, SVG emblem, badge system)
- Industry examples: Supabase, Tailwind CSS, shadcn/ui, Raycast, Vue.js, React
