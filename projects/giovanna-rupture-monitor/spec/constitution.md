# Constitution – Giovanna Rupture Monitor

This file defines the mandatory SDD scaffold for the project. All sections are required by the Missão 0.

## Princípios

1. **Reprodutibilidade acima de tudo.** O pipeline usa dados sintéticos (ShadowTraffic) e roda em modo `--local` sem dependência de API externa. Um `docker run` deve produzir o dashboard completo.
2. **Determinismo.** Os mesmos dados de entrada produzem sempre o mesmo CSV de saída. Sem aleatoriedade não controlada no pipeline.
3. **Guards explícitos para dados vazios.** Toda operação de agregação ou indexação de DataFrame verifica vazio antes de prosseguir (conforme P0 de `padroes-entrega.md`).
4. **Separação de estágios.** Ingestão → Transformação → Relatório. Cada estágio é uma função isolada, testável independentemente.

## Scope

- Monitoramento de ruptura de estoque por região nas lojas Giovanna.
- Pipeline ETL: ingestão de dados ShadowTraffic → transformação (agregação por região, cálculo de IRC médio, % crítico) → relatório CSV agregado por região.
- Dashboard HTML servido via Docker container, consumindo o CSV gerado.
- Dados determinísticos e reprodutíveis (sem dependência de API externa em modo `--local`).

## Non-goals

- Previsão de demanda ou reposição automática (somente diagnóstico de ruptura atual).
- Integração com ERP ou sistemas de gestão da Giovanna (escopo futuro, não neste ciclo).
- Dashboard real-time ou streaming (o pipeline é batch, rodado sob demanda).
- Análise por loja individual (granularidade é por região).
