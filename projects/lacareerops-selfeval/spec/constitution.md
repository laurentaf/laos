# Constitution — lacareerops-selfeval
**Version:** 1.0 | **Status:** Vigente | **Created:** 2026-06-21

---

## Article I — Avaliação honesta antes de otimização
Nenhuma alavanca de carreira funciona se o gap entre o que está no CV
e o que o mercado exige não for nomeado com precisão. Toda análise
deve ser defendável com fonte (job descriptions, repos auditados,
benchmarks salariais). Inferência sem evidência = anti-pattern.

## Article II — Currículo e portfolio são o mesmo ativo
O que está no `Laurent_Ferreira_*.docx` deve refletir 1:1 o que está
nos repos públicos `laurentaf/*`. Divergência entre CV e realidade é
o pior sinal que se pode mandar a recrutadores — corroi todo o
resto. Toda lacuna do CV deve ser MENCIONADA como gap e mapeada
para um projeto novo (ou refactor) que feche o loop.

## Article III — Mercado fala primeiro; projeto fala segundo
A análise começa pelo mercado (JDs, faixas salariais, skills pedidas)
e só depois consulta o CV/portfolio. A ordem inversa leva a confirmar
preconceito em vez de detectar gaps. Stack ranking de tools/skills é
output do mercado como ele está, não como Laurent gostaria que
estivesse.

## Article IV — LinkedIn é veículo, não destino
Posts devem puxar tráfego para o portfolio (repos + blog) e para
oportunidades concretas, não virar hobbies de marca pessoal. Cada post
termina em CTA mensurável (link, pergunta, salvos). Vanity metrics
sem profundidade = anti-pattern.

## Article V — Calibração 20/10 vs 50/1 (PR-1)
Rigor analítico no nível que 80% dos profissionais do campo aceitariam
para o mesmo problema. Excessivo (PhD) é overkill; insuficiente
(4º-ano) é ruído. `ratio = Δqualidade% / Δtempo% ≥ 0.5`.

## Article VI — Sintético é proibido sem flag explícita
Achados deste projeto vêm de **dados reais**: JDs reais, repos
reais, salario reais. Inferências são marcadas como `[inferência]
justificativa: <X>`. Nenhum dado sintético é gerado para preencher.
(Hard Rule #11 — AGENTS.md.)

## Article VII — Outputs são estruturados e auditáveis
Cada deliverável traz: scope, método, fontes, decisões antigas
sinalizadas, próximo passo concreto. Markdown estruturado; tabs/comparativos
em tabelas; nenhum parágrafo longo sem listas anteriores.

## Article VIII — 30 posts = 30 ângulos, não 30 variações
Cada post do backlog ataca um pilar diferente (mercado, técnico,
carreira, projeto, autoridade). Repete-se em profundidade, não em
superfície. Sequência de 4 semanas com papéis bem distribuídos
(awareness → trust → conversion).

## Article IX — Apresentação visual dos 30 posts é amostra, não coaching
O `visuals-deck.html` serve para Laurent escolher 1 a 5 posts para
produzir primeiro, não como obrigação de executar todos os 30. Foco
em vetores de maior alavancagem.

---

## Principles

9 princípios: avaliação honesta, currículo-espelho-do-portfolio, mercado
antes de portfolio, LinkedIn-como-meio, calibração 20/10 vs 50/1, zero
sintético sem flag, outputs auditáveis, 30 ângulos distintos, deck-como-amostra.
Aplicam-se a todos os eixos: tools gaps, portfolio audit, curriculum gaps,
LinkedIn strategy e wage bands.

---

## Scope

- 1 CV (docx) fornecido pelo usuário via `user_input_data/`.
- ~10-15 repos públicos da `laurentaf` no GitHub (auditar via `github` MCP).
- Mercado brasileiro + remoto US + remoto EU para wage bands.
- LinkedIn estratégia em PT-BR e EN (proposta bimodial).
- Período de referência: Q2-Q3 2026.

## Non-Goals

- Não produzir CV escrito (output é o **gap analysis**, não o rewrite).
- Não produzir blog posts (apenas backlog curto + 1 ideia-âncora).
- Não aplicar mudanças nos repos (apenas lista do que mudar).
- Não negociar em nome de Laurent (apenas fornecer faixa ancorada).
