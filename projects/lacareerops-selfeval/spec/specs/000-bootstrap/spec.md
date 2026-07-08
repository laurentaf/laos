# Spec 000: lacareerops-selfeval — Strategic Career Audit

## Contexto

Laurent Ferreira está se posicionando para AI Data Engineer / Data
Specialist em 2026. Tem 1 CV (`Laurent_Ferreira_Engenheiro_de_dados_para_Inteligencia_Artificial_2026.docx`)
e 15+ repos públicos no GitHub (`laurentaf`). Mas a distância entre
a narrativa que ele conta no LinkedIn, o que está no docx e o que o
mercado exige em 2026 não foi quantificada ainda.

O briefing do usuário de 2026-06-21 pediu 5 eixos de análise em
single-shot:
1. Gaps em tools para AI Data Engineer / Data Specialist / correlatos
2. Gaps no portfolio GitHub (qualidade, projeto-a-projeto, o que
   mostrar e o que falta)
3. Curriculum gaps (cruzando 1 × 2; matriz de 3 zonas)
4. Estratégia LinkedIn (avaliação da ideia original + 30 posts backlog)
5. Faixa salarial de negociação (BR + US remote + EU remote)

## Decisão Inicial

Tratar como projeto agentic-adhoc (não dashboard-completo nem
apresentação-executiva). Passa pelo WDL preflight gate (workflow-
decomposer) antes de dispatchar especialistas. Usa `lacareerops` como
primary para a parte de CV/curriculum, `ladesign` para os visuais dos
posts, `exa`/`context7` para a pesquisa de mercado + salários, `github`
MCP para a auditoria dos repos, e `lacouncil.investigate` se algum
estágio precisar de análise de causa-raiz.

## Critérios de Pronto

- [ ] `artifacts/cv/parsed-cv.md` extraído do docx com seções
      estruturadas (perfil, experiência, skills, formação, certificações).
- [ ] `artifacts/market/tools-gaps.md` lista ≥ 15 ferramentas/skills
      com prioridade de mercado, cobertura no CV e cobertura nos repos.
- [ ] `artifacts/portfolio/github-audit.md` audita ≥ 10 repos da
      `laurentaf` com score 0-10 e lista o que falta por projeto.
- [ ] `artifacts/portfolio/curriculum-gaps.md` produz matriz 3 zonas
      + plano 30d com 1 ação por gap Z2.
- [ ] `artifacts/linkedin/strategy-evaluation.md` avalia a ideia
      McDonald's com critérios objetivos + ≥ 2 alternativas de ângulo.
- [ ] `artifacts/linkedin/30-posts-backlog.md` lista 30 posts
      estruturados com hook / body / CTA / visual concept.
- [ ] `artifacts/linkedin/visuals-deck.html` apresenta cards visuais
      navegáveis para os 30 conceitos.
- [ ] `artifacts/market/wage-bands.md` lista wage bands em 3 markets
      (BR CLT, BR PJ, US remote) com faixas júnior / pleno / sênior
      e âncora de negociação sugerida.
- [ ] Pelo menos 1 ADR real em `spec/adr/` (produzido durante Stage 3
      ou Stage 6) — gate de ADR-mínimo-1.

## Alcance

### In-scope
- 1 CV (docx fornecido pelo usuário)
- Repos públicos `laurentaf` (≥10 auditados)
- Mercado AI Data Engineer / Data Specialist em 2026, BR + US + EU
- LinkedIn estratégia em PT-BR + EN

### Fora do escopo
- Reescrita do CV (gap analysis + plano, não o rewrite em si)
- Reescrita dos READMEs (o que falta, sim; refazer, não)
- Aplicação de mudanças em qualquer repo
- Posts reais publicados (apenas backlog estruturado)
- Negociação real com empregador (apenas âncora sugerida)

## Capacidades Utilizadas

| Capability | Role |
|-----------|------|
| LACOUNCIL | WDL preflight (workflow-decomposer), record_project no close |
| LACAREEROPS | CV parsing + career evaluation via career_ops_evaluate |
| LATADE | Helper para parsers estruturados se necessário |
| LADESIGN | `visuals-deck.html` (30 posts) via dashboard-designer |
| GITHUB | Audit dos repos `laurentaf` (github.list_repositories etc.) |
| EXA | Pesquisa de JDs reais + wage bands |
| CONTEXT7 | Documentação de tools (RAG, vector DB, Airflow, dbt…) |

## Dependências

- CV em `user_input_data/Laurent_Ferreira_*.docx`
- GitHub PAT disponível no OS env (`GITHUB_TOKEN`)
- Acesso aos tools MCP: `lacareerops.*`, `github.*`, `exa.*`, `context7.*`,
  `ladesign.*`, `lacouncil.*`

## Riscos & Mitigações

| Risco | Mitigação |
|-------|-----------|
| Docx não parseável por `lacareerops` | Fallback: data-architect lê o docx via python-docx no venv de LAOS |
| Repos privados GitHub bloqueiam audit | Restringe scope a repos públicos (público-first); sinaliza repos privados como "não-visíveis" |
| Wage data desatualizada | Cross-check 3 fontes distintas (Glassdoor, Levels.fyi, LinkedIn) |
| `<¨input_values>` ambiguos | perguntar ao usuário antes de começar cada fase de pesquisa |
