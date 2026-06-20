# ADR-001: Adoção do Padrão LAOS inline HTML/CSS para READMEs

**Data:** 2026-06-19
**Status:** Aceito
**Autor:** LAOS orchestrator (via _meta/readme-improvement)
**Projeto:** _meta/readme-improvement

## Contexto

O portfólio de repositórios `laurentaf` no GitHub continha 15 READMEs com qualidade e formato inconsistentes (nota média 11.5/20). Alguns tinham apenas título e link, outros estavam desatualizados ou sem badges, seções de contribuição ou licença. Não existia um padrão visual ou estrutural compartilhado entre os repositórios.

O README do repositório `github.com/laurentaf/laos` (20/20) servia como exemplar não oficial — usava SVG inline para emblemas, badges `shields.io`, tabelas HTML com `border-collapse` e CSS inline para hierarquia visual.

## Decisão

Adotar o **padrão LAOS inline HTML/CSS** como template obrigatório para todo README do portfólio laurentaf. O padrão consiste em:

1. **SVG Emblem (72×72)** — único por repositório, derivado do domínio, com cor de destaque consistente
2. **Badges shields.io** — stack, status, licença, ecosystem LAOS
3. **Bilingual header** (EN + PT) para repositórios em português
4. **Tabelas HTML inline** para estrutura de arquivos e schemas (`border-collapse:separate`)
5. **Mermaid diagrams** para pipelines e arquitetura
6. **Inline HTML cards** para arquitetura visual
7. **Seções obrigatórias:** Contributing + Licença
8. **Footer** com SVG reduzido e link

## Alternativas Consideradas

1. **Manter sem padrão** — Rejeitado: não resolve a inconsistência do portfólio.
2. **Template GitHub Markdown puro** — Rejeitado: limitações de formatação (sem SVG, badges com aparência inferior, sem tabelas com bordas controladas).
3. **Template em framework externo (Jekyll, GitHub Pages)** — Rejeitado: overhead de manutenção para repositórios que são primordialmente de dados/código.
4. **Gerador automatizado de README** — Rejeitado: os READMEs precisam ser editáveis manualmente e adaptados ao contexto de cada repositório.

## Consequências

- **Positivas:** Consistência visual em 14/15 repositórios; nota média do portfólio elevada de 11.5/20 para ~14.5/20; padrão documentado em `knowledge/readme-templates.md` para reuso futuro
- **Negativas:** READMEs ficaram maiores (9-12KB cada); manutenção manual ainda necessária
- **Riscos:** Se um subagente não seguir o template em futuras edições, a consistência se perde — mitigado pelo delivery-reviewer que valida conformidade via `knowledge/readme-templates.md`
