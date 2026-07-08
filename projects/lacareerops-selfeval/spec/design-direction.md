# Design Direction — lacareerops-selfeval

> **Por que este arquivo existe:** paddroes-entrega.md §SDD scaffold
> (Missão 0) exige `spec/design-direction.md` quando `needs:` contém
> `dashboard` ou `design`. Este projeto tem `design` (para os 30
> LinkedIn visuals), logo o arquivo é obrigatório.

---

## Brief visual

Audience: Laurent Ferreira **sozinho**, lendo no editor do navegador
para escolher 1 a 5 posts para começar imediatamente.

Contexto: cada post de LinkedIn tem 1 visual correspondente. O deck é
ferramenta de decisão, não entregável final — então deve priorizar
**scannability** sobre densidade.

## Tom

- **Front:** editorial engineering — sério mas não técnico-dry.
- **Back:** pragmático, focado em utilidade.
- Sem AI-slop (sem cantos arredondados supérfluos, sem gradient rainbow,
  sem emoji como motivo). Tipografia sustenta o tom sozinha.

## Tipografia

- Headlines: **Söhne Mono** (ou IBM Plex Mono fallback) — mistério
  editorial + clareza técnica. Caps em hooks curtos.
- Body: **Inter** (sans, humanist). Tracking apertado.
- Números: mono, alinhados à esquerda.

## Paleta (3 modos — escolher 1)

| Mode | Background | Foreground | Accent | Onde brilha |
|------|-----------|-----------|--------|------------|
| **Boardroom** | `#0E1116` warm-black | `#F7F5EE` warm-paper | `#C9A24B` muted-gold | Posts de mercado / autoridade |
| **Applied** | `#F5F4ED` warm-paper | `#1B1B1B` ink | `#3C6E47` pine-green | Posts técnico-aplicáveis |
| **Warstory** | `#1B1B1B` ink | `#F7F5EE` warm-paper | `#E07A5F` terracotta | Posts carreira / vulnerabilidade |

Comutação: alternar entre os 3 modos pelos 30 posts (≈10 cada), evita
monotonia visual sem cair em cauda-de-arco-íris.

## Grid & Layout

- Card base: 1080 × 1350 px (4:5 portrait) — formato LinkedIn canon.
- Grid: 12-col com gutters 24px; margem segura (safe-zone) 80px top
  e 64px sides para corte do feed.
- Hierarquia: numero da semana (pequeno, mono) → pilar (caps mono) →
  hook (headline até 18 palavras) → 3 linhas de body → CTA keyword
  (mono, em accent) → mini-logo "@laurentaf" canto inferior.

## Motion (no `visuals-deck.html`)

- Navegação: diag-arrow (← / →) + scroll-snap.
- Hover: lift mínimo (translate-y -2px, transition 200ms ease-out).
- Prefer-reduced-motion: mata o lift + snap, deixa só a navegação inline.

## Componentes

- **`<CardPost>`** — content-type wrapper para cada um dos 30.
- **`<PillarBadge>`** — pill 64×24 com texto em mono caps.
- **`<WeekStripe>`** — barra de progresso sequencial por semana (4 semanas).
- **`<MetaFooter>`** — data + mix-pilar em mono.

## Anti-patterns (bloqueios)

- Sem cards-inside-cards-inside-cards.
- Sem gradient-de-múltiplas-cores.
- Sem emoji isolado (só integrado em ≤ motivo).
- Sem stock image.
- Sem texto > 18 palavras em hook.
- Sem CTA que peça "Salve!", "Compartilhe!" — CTA concreto (link para
  repo, link para post anterior, etc.).

## Direção de copy (cross-reference com backlog)

- Tom: 1ª pessoa, dúvidas em vez de afirmações, específico > genérico.
- Ângulo por post vem do backlog em `artifacts/linkedin/30-posts-backlog.md`.
- CTA final de cada post: 1 link concreto OU 1 pergunta direta ao
  Laurent-ferreira.

## Production notes

- LADESIGN skill sugerido: `deck-swiss-international` (grid 16-col,
  accent saturado, 22 layouts lockados) — alta densidade, austero,
  cabe perfeitamente no Boardroom mode. Para Applied/Warstory, usar
  `docs/opencode-templates/design-system.md` como base e sair do grid.
- Output final: `artifacts/linkedin/visuals-deck.html` (single-file).
