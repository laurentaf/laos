# Glossário de negócio

Termos que aparecem em projetos e devem significar a mesma coisa em
todos eles. Capacidades de domínio podem ter glossários próprios; este
arquivo só lista o que é **transversal**.

## Conceitos de entrega

- **Brief**: parágrafo curto que descreve o problema, o público e o
  que conta como sucesso. Toda capacidade começa pelo brief.
- **Artefato**: qualquer arquivo entregável (modelo, dashboard, deck,
  fluxo). Sempre versionado em `projects/<nome>/artifacts/`.
- **Spec**: descrição declarativa de um artefato antes de existir
  (`project.yaml`, `model.md`, `outline.md`).
- **Snapshot**: dado congelado para reprodutibilidade. Decks executivos
  e relatórios pontuais consomem snapshots, não consultas ao vivo.

## Conceitos de dados (referência rápida)

Definições profundas vivem em `../latade/`. Aqui só os atalhos:

- **KPI**: número que reflete diretamente um objetivo de negócio.
  Não confundir com **métrica** (qualquer número mensurado).
- **Dimensão**: atributo pelo qual uma métrica pode ser fatiada.
- **Fato**: tabela com métricas agregáveis e chaves para dimensões.
- **Mart**: subconjunto modelado de dados para um caso de uso específico.

## Conceitos de design

Definições profundas em `../open-design/`. Atalhos:

- **DESIGN.md**: contrato de marca (paleta, tipografia, espaçamento,
  voz, anti-padrões). Toda saída visual lê o DESIGN.md ativo.
- **Wireframe**: estrutura, sem visual final. Decide hierarquia antes
  de decidir cor.
- **Storyboard**: sequência narrativa de uma apresentação ou dashboard.

## Conceitos de automação

- **Workflow** (n8n): grafo de nós que executa uma automação ponta a
  ponta. Vive em `../n8n/` ou é deployado via `n8n-community`.
- **Trigger**: evento que dispara um workflow (schedule, webhook, etc).
- **SLA**: prazo máximo aceitável entre disparo e conclusão.

## Como adicionar um termo aqui

Antes de adicionar: o termo é mesmo transversal a múltiplos domínios?
Se só vive em dados, vai para `../latade/`. Se só vive em design, vai
para `../open-design/docs/`. Se só vive em automação, vai para
`../n8n/`. Este arquivo é a exceção, não a regra.
