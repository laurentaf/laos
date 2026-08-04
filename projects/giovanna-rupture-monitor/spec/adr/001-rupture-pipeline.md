# ADR-001: Pipeline de Monitor de Ruptura em 3 Estágios

## Status

Accepted

## Contexto

Precisamos de um pipeline que consuma dados de pedidos de uma API e produza
um relatório de ruptura de estoque por região.

A API retorna dados de pedidos (order_id, timestamp, customer_id,
product_category, price, quantity, store_location), mas não contém
estoque_atual ou demanda_prevista.

## Decisão

Pipeline em 3 estágios:

1. **Ingestão**: fetch_data() → JSON bruto em disco
2. **Processamento**:
   - Deriva "região" de store_location
   - Deriva "estoque_atual" de quantity (cada pedido representa unidades)
   - Gera "demanda_prevista" com variação determinística (SHA256 do order_id)
     para simular uma projeção de demanda realista e reprodutível entre execuções
   - Calcula ruptura = (demanda - estoque) / demanda
   - Agrega por região com mean e max
3. **Relatório**: print_summary() + CSV final

## Alternativas

### A) DuckDB + SQL
Alternativa com DuckDB em vez de pandas. Rejeitada porque o pandas oferece
prototipação mais rápida e ecossistema maduro para CI/CD.

### B) Polars
Alternativa performática com Polars. Rejeitada por ser menos conhecida no
portfolio de engenharia de dados.

## Consequências

+ Pipeline auto-contido (não depende de dados externos de estoque)
+ Demanda prevista determinística (reprodutível)
+ Dados brutos preservados para auditoria
- Demanda prevista é simulada, não real
- Precisão da ruptura depende da qualidade da simulação
