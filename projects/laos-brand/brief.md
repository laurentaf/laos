# LAOS Brand — Brief de Contratação

## Contexto

LAOS (Laurent Agentic Operational System) é um sistema operacional agêntico
local-first orquestrado por um agente primário que compõe capacidades de
dados (LATADE), automação (LAN8N) e design (LADESIGN) via MCP.

O projeto já tem:
- Direção estratégica de marca definida
- Manifesto, taglines, voz, anti-padrões (ver seção abaixo)
- Repositório filho criado: `laurentaf/laos-brand`

## Tese de Marca (aprovada)

> A inversão de uma hierarquia de três mil anos. O louro (Laurent) cingia
> uma cabeça; o laós (povo/massa) obedecia. LAOS dissolve a coroa e
> distribui a soberania para cada operador.

## Arquitetura de Produto

| Módulo | Função | Inspiração |
|---|---|---|
| Laurent Core | Núcleo de orquestração | O louro destilado |
| Laós Layer | Runtime dos agentes | O povo soberano |
| Talos Mesh | Camada guardiã (monitoring, integridade) | Primeiro autômato da história |
| The Oracle | Inteligência preditiva | O oráculo como serviço, não como tirano |
| The Forum | Superfície de colaboração humana | Ágora, assembleia |

## Storytelling — Os 3 Atos

**Ato I — A Velha Ordem.** Em Roma o louro era do imperador. Em Atenas
o oráculo falava com reis. O laós assistia.

**Ato II — A Fratura.** A IA moderna herdou a torre: dados com data team,
IA com lab, o resto da empresa com tickets e dashboards.

**Ato III — A Inversão.** O louro vira camada operacional sob cada operador.
Talos vira arquitetura. A coroa é dissolvida.

## Anti-padrões (NUNCA usar)

- ❌ "Emperor of AI" / "AI imperator"
- ❌ "Democratize AI" (gasto, vazio)
- ❌ "All-seeing AI" / "Skynet"
- ❌ Grego/latim jogado sem propósito
- ❌ "Revolutionary" / "game-changing" / "10x"
- ❌ Tratar usuário como consumidor passivo

## Taglines Aprovadas

**Spine universal:** "The laurel was exclusive. The intelligence doesn't have to be."

**Punchy:** "Crown the operator." / "From emperor's crown to operator's console."

**Técnico:** "Agents that operate. Systems that serve." / "Orchestration for the laós."

## Entregáveis

Todos os artefatos devem ser produzidos no repositório `laurentaf/laos-brand`
via github MCP. O commit deve ser feito pelo próprio subagente executor.

### 1. `narrative/manifesto.md`
Manifesto completo (~150-200 palavras), formato markdown. Tom épico mas direto.
Pronto para abrir keynote, site ou README do produto.

### 2. `narrative/taglines.md`
Tagline set completo organizado por superfície:
- Spine universal (1 linha, heads-down, usada em tudo)
- Hero / homepage
- Estratégico / investor
- Punchy / social
- Técnico / developer

### 3. `narrative/voice.md`
Guia de voz e tom (~300 palavras). Incluir:
- Personalidade (analogia com pessoa famosa ajuda)
- O que dizer e o que evitar
- Ritmo e estrutura de frase
- Exemplos de "certo" vs "errado"

### 4. `narrative/story-spine.md`
Os 3 atos em formato narrativo, prontos para:
- Deck de apresentação (1 slide por ato)
- Seção "About" do site
- Pitch de 60 segundos

### 5. `narrative/product-naming.md`
Justificativa de cada nome de módulo:
- Por que "Laurent Core" e não "Engine"
- Por que "Laós Layer" e não "Runtime"
- Por que "Talos Mesh" e não "Guard"
- Por que "The Oracle" e não "AI"
- Por que "The Forum" e não "Dashboard"
Incluir a referência mitológica e a função técnica de cada um.

### 6. `design/design-system.md`
DESIGN.md compatível com o padrão open-design. Incluir:
- Paleta de cores primária e secundária (com valores hex)
- Tipografia (headings, body, mono)
- Espaçamento e grid
- Token naming convention
- Modo escuro e claro
- Referência ao DESIGN.md (este arquivo) como "source.md"

### 7. `design/keynote.html`
Deck de abertura em HTML, navegação por teclado (← →), 5-7 slides:
1. Título: "The Crown is Dissolved"
2. Ato I — A Velha Ordem
3. Ato II — A Fratura
4. Ato III — A Inversão
5. Arquitetura (Laurent Core, Laós Layer, Talos Mesh, Oracle, Forum)
6. O que LAOS entrega (value prop)
7. CTA / encerramento

Usar skill de deck HTML (ex: `deck-swiss-international`, `frontend-slides`,
ou `ppt-keynote`) como template de partida.

### 8. `design/landing-page.html`
Landing page de herói, single-page, ~5 seções:
1. Hero (tagline + CTA)
2. O Problema (a velha ordem)
3. A Inversão (LAOS)
4. Arquitetura (módulos)
5. CTA final

Usar skill de frontend (ex: `frontend-design` ou `design-taste-frontend`).

### 9. `decisions/brand-architecture.md`
ADR (Architecture Decision Record) documentando:
- Contexto: por que fazer um brand project
- Decisão: inversão narrativa (laurel vs laós)
- Consequências: módulos nomeados, anti-padrões, voz
- Alternativas consideradas e por que foram rejeitadas

## Skills Disponíveis para Uso

As skills abaixo estão carregadas e podem ser invocadas com `skill` tool:

- **brandkit** — identidade visual premium
- **copywriting** — copy de marca e marketing
- **design-brief** — parser de brief em I-Lang
- **design-md** — criação de DESIGN.md
- **design-taste-frontend** — frontend anti-slop
- **frontend-design** — landing pages e UI
- **frontend-slides** — decks HTML animados
- **ppt-keynote** — slides qualidade Apple Keynote
- **deck-swiss-international** — grid de 16 colunas
- **reference-design-contract** — referências visuais
- **marketing-psychology** — princípios de persuasão

## Ferramentas Disponíveis

- **github MCP** (github_*): criar/atualizar arquivos, push, commits
- **write/edit/read**: operações de arquivo
- **context7 MCP**: consulta de documentação
- **exa MCP**: pesquisa web (se necessário)

## Restrições

- Todos os artefatos DEVEM ir para o repositório `laurentaf/laos-brand`
- Arquivos de design vão em `design/`, narrativa em `narrative/`, decisões em `decisions/`
- O DESIGN.md deve seguir o padrão open-design (pode carregar `design-md` skill)
- O deck e landing page devem ser HTML funcional, não mockup ou imagem
- Nenhum segredo (API key, token) deve aparecer nos arquivos
- Nenhum placeholder genérico ("Lorem ipsum", "TODO")

## Critérios de Aceite

- [ ] Todos os 9 deliverables existem no repo
- [ ] Manifesto tem tom consistente com a tese
- [ ] Taglines estão organizadas por superfície
- [ ] Voice & Tone tem exemplos concretos
- [ ] Story spine conta os 3 atos de forma coerente
- [ ] Product naming justifica cada módulo com mitologia + função
- [ ] DESIGN.md tem valores de tokens reais (hex, font names, spacing)
- [ ] Keynote tem navegação por teclado e 5-7 slides
- [ ] Landing page é single-page com ~5 seções
- [ ] ADR documenta contexto, decisão e alternativas rejeitadas
