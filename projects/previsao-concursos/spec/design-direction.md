# Design Direction — previsao-concursos

**Origem:** condicional da Missão 0 (proposta LACOUNCIL `f9b636fc`).
Este arquivo é gateado por `subagent_boot_check.py` 6ª dimensão
quando `needs:` contém `dashboard` ou `design` (que é o caso deste
projeto). Gate: ≥ 300 chars, sem header fixo.

---

## Direção macro (1 parágrafo + 3 princípios)

A plataforma é uma **ferramenta de estudo**, não de entretenimento.
A experiência visual precisa reforçar **confiança analítica** e
**densidade informacional** — o candidato está aqui para decidir
**onde gastar a próxima hora de estudo**, não para passear. O
roteiro hierárquico Matéria > Assunto > Sub-assunto é o produto;
tudo o mais (cards de KPI, sparklines, grafo de cobertura) é
suporte à decisão. Paleta sóbria (preto + 1 cor de destaque, papel
quente), tipografia editorial, e **probabilidade sempre visível**
em cada nó (p. ex., "Crase: 98% 1 questão, 2% nenhuma"). Sem
gradientes decorativos, sem animações gratuitas, sem mascotes.

### Princípio 1 — Probabilidade é protagonista, não decoração

Cada sub_assunto mostra sua probabilidade empírica de forma
numérica e visível. A hierarquia visual do roteiro é dada
**diretamente pela probabilidade** (topo = mais provável, base =
menos). Sem ícones que disputem atenção com o número. Formato
sugerido: `### {Sub-assunto} — {p}%  ({n_concursos} concursos,
{questoes_por_evento}±{dp})`.

### Princípio 2 — Hierarquia Matéria > Assunto > Sub-assunto é a coluna vertebral

A navegação principal reflete a hierarquia do edital. Drill-down
em 3 níveis, sem rotas alternativas. Filtros laterais por banca
(FCC / FGV) e por ano. Sem dashboard alternativo, sem "view
resumida" / "view detalhada" — a hierarquia já é a view.

### Princípio 3 — Confiança vem de proveniência, não de branding

Cada número exibido tem **link para a fonte** (qual prova, qual
edital, qual ano) e para o **HARNESS correspondente**. O candidato
pode auditar a probabilidade sem sair da plataforma. Citações
visíveis, não escondidas em tooltip.

## Anti-padrões (proibidos)

- Gradientes decorativos, glassmorphism, drop-shadows agressivos.
- Animações de scroll (parallax, fade-in em massa).
- Cards empilhados com hierarquia visual artificial (rankings
  com medalhas, badges de "top 1%" sem critério).
- "AI-powered" / "smart" / "intelligent" como label — sem LLM no
  scorer, a palavra é mentirosa.
- Cores saturadas em mais de 1 elemento por viewport.
- Ícones que substituem números (sub-assunto vira "📚" sem label).

## Tokens sugeridos (rascunho — refinar em Stage 3)

- Paleta: papel `#F5F4ED` (background), tinta `#1B1B1B` (texto),
  acento `#1B365D` (probabilidade / link), alerta `#B4453A` (alerta DQ).
- Tipografia: 1 serifa editorial para hierarquia (matérias) + 1
  sans-serif para números (sub-assuntos).
- Espaçamento: 8px base, rhythm 16/24/40/64.
- Densidade: alta. Cada viewport deve mostrar ≥ 8 sub-assuntos
  com probabilidade visível.

## Onde isso vai ser refinado

O `dashboard-designer` (Stage 3) consome este arquivo + o
`artifacts/data/model.md` (Stage 2) e produz:

- `artifacts/design/wireframe.md` — esqueleto de hierarquia.
- `artifacts/design/visual-spec.md` — tokens finais.
- `artifacts/design/component-breakdown.md` — lista de componentes
  com responsabilidade e estado.
- `artifacts/design/source.md` — referenciando este `design-direction.md`.

O DESIGN.md final (com tokens locked) será escrito em iteração
no Stage 4 (build), se necessário.
