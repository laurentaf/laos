# README Template — LAOS Portfolio Pattern

> **Proveniência:** Projeto `_meta/readme-improvement` (2026-06-19). Padrão validado em 11 READMEs do portfólio laurentaf. Nota média do portfólio: 11.5/20 → ~14.5/20 após aplicação.

## Princípio

Cada README deve funcionar como **landing page do repositório** — não um dump de informações. O leitor entende o que é o projeto, por que importa e como usar em ≤ 10 segundos.

## Estrutura canônica (seções na ordem)

### 1. SVG Emblem + Título
- SVG inline (72×72) com cantos arredondados (`rx="12"`)
- Único por repositório, derivado do domínio do projeto
- Cor de destaque consistente com o tema do repositório

### 2. Badges (`shields.io`)
- Stack principal (linguagem, framework, DB)
- Status (STABLE `#00b894`, BASIC `#fdcb6e`, COMPLETE `#00b894`)
- Licença
- Ecosystem LAOS (`#6c5ce7`) com link para `github.com/laurentaf/laos`
- Formato: `style=flat`, `logoColor=fff`

### 3. Bilingual Header / Resumo
- Repositórios em português: EN summary + PT resumo lado a lado
- Repositórios de capacidade (capability repos): inglês apenas
- 2-3 linhas: o que é, para quem, diferencial

### 4. Tabela de arquivos / estrutura
- `border-collapse:separate; border-spacing:0`
- Cabeçalho com opacidade reduzida (`opacity:0.5`)
- Linhas alternadas com opacidade no conteúdo (`opacity:0.7`)

### 5. Pipeline / Arquitetura (se aplicável)
- **Mermaid diagrams** para fluxos (ETL, dados, CI/CD)
- Diagramas ASCII/bloco para automações (n8n)
- **Inline HTML cards** para arquitetura visual (`border`, `border-radius`, `padding`, `margin`)

### 6. Dataset / Schema (se aplicável)
- Tabela de colunas com tipo e descrição
- Amostra de dados (primeiras 3-5 linhas em formato visual)

### 7. Setup / Como usar
- Bloco de código com `bash` para clonagem e comandos básicos
- Subseções para soluções alternativas (Docker, Python, etc)

### 8. Contributing
- Tabela bilíngue EN/PT (para repositórios em português)
- Ou parágrafo único em inglês

### 9. Licença
- Nome da licença com link para o arquivo LICENSE
- Nota sobre atribuição de dados / propósito do projeto

### 10. Footer
- SVG emblem reduzido ou link para o repositório
- Opacidade reduzida (`opacity:0.25`)

## Paleta de cores por repositório (exemplos)

| Repo | Cor | Emblema |
|------|-----|---------|
| laos | `#6c5ce7` (roxo) | Escudo LAOS |
| laecon | `#a29bfe` (lavanda) | Gráfico de regressão |
| ladesign | `#fdcb6e` (dourado) | Pincel + grid |
| lan8n | `#00cec9` (teal) | Nó de workflow |
| laengine | `#d63031` (vermelho) | Escudo de jogo |
| latade | `#6c5ce7` (roxo) | Medallion pipeline |
| pizzarias-sp | `#e17055` (coral) | Pizza + mapa |
| hospital-viana | `#0984e3` (azul) | Hospital cross |
| logistica-me | `#00b894` (verde) | Caminhão |
| emanuella | `#fdcb6e` (dourado) | Diamante/joia |
| semana-ai | `#d63031` (vermelho) | Cérebro/IA |
| giovanna | `#e84393` (rosa) | Gráfico de barras |
| abandono-academico | `#e17055` (laranja) | Capelo + seta |
| laurentaf (profile) | `#6c5ce7` (roxo) | Monograma LA |

## SVG Emblem — template genérico

```svg
<svg width="72" height="72" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-bottom:4px;">
  <rect x="4" y="4" width="56" height="56" rx="12" stroke="{{COLOR}}" stroke-width="1.5" fill="none" opacity="0.3"/>
  <!-- Shape específico do repositório -->
  <path d="..." stroke="{{COLOR}}" stroke-width="2" fill="none" stroke-linejoin="round" opacity="0.4"/>
</svg>
```

## Badge row — template

```html
<p style="margin:12px 0;">
  <img src="https://img.shields.io/badge/{{LABEL}}-{{VALUE}}-{{COLOR}}?style=flat&logo={{LOGO}}&logoColor=fff" alt="{{LABEL}}"/>
  &nbsp;
  <a href="https://github.com/laurentaf/laos"><img src="https://img.shields.io/badge/Ecosystem-LAOS-6c5ce7?style=flat" alt="LAOS Ecosystem"/></a>
</p>
```

## Quando usar

- Todo repositório no portfólio **deve** seguir este template (P1 para repositórios públicos)
- Capacidades LAOS (laecon, latade, ladesign, lan8n, laengine, etc) têm prioridade P0
- O `delivery-reviewer` valida conformidade com este template como parte do P0-20 (suficiência de output)
- README de perfil GitHub (`laurentaf/laurentaf`) segue variante resumida: emblema, badges, projetos em destaque, stats widget

## Anti-patterns

| Anti-pattern | Correção |
|-------------|----------|
| README só com título e link | Aplicar template completo |
| Badges sem ecosystem link | Adicionar LAOS ecosystem badge |
| Mermaid renderizado como texto | Usar blocos ```mermaid``` |
| Sem contribuição / licença | Adicionar ambas as seções |
| Português sem EN header | Adicionar resumo em inglês |
| Wall of text sem tabelas/quebras | Usar tabelas inline, cards, ou diagramas |
