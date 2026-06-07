# Design Direction — Giovanna Rupture Monitor

## Estilo visual

- **Paleta:** escura com acentos em vermelho/laranja para regiões críticas, verde para confortáveis
- **Tipografia:** sans-serif limpa (Inter ou equivalente) para legibilidade em dashboards
- **Densidade:** média — cards por região com KPIs visíveis, sem excesso de informação
- **Layout:** tabela principal com colunas alinhadas, header fixo, scroll vertical

## Anti-padrões

- Não usar gráficos de pizza para comparação entre regiões (preferir barras ou tabela)
- Não carregar dados dinâmicos por API — CSV local servido same-origin
- Não usar cores primárias para dados neutros (reservar para alertas)

## Componentes

- Dashboard HTML single-file com fetch genérico de CSV (header parsing automático)
- Sem framework CSS — vanilla + estilos inline para máxima portabilidade
- Responsivo mínimo (mobile-friendly table)

## Referência

Dashboard gerado via LADESIGN (Open Design) — preview URL servido no container Docker.
