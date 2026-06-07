# ADR-002: Guards para DataFrame vazio em todas as etapas do pipeline

## Status

Accepted

## Contexto

O Data Mission rejeitou a entrega (REJECTED) porque print_summary() assume que
existe pelo menos uma região e acessa top3.iloc[0] sem verificar se summary
está vazio. Quando a API não retorna registros (ou o arquivo JSON local está
vazio), isso gera IndexError e toda a execução trava.

O mesmo risco existe em todas as operações de agregação do pipeline:
.mean(), .min(), .max(), groupby(), to_csv().

## Decisão

Adicionar guards de DataFrame vazio em todas as etapas do pipeline:

| Função | Proteção |
|--------|----------|
| fetch_data() | Avisa se API retornar lista vazia |
| main() | early exit com mensagem clara se raw_data vazio |
| build_demand_forecast() | Retorna DF vazio com colunas corretas se input vazio |
| compute_rupture() | Retorna DF vazio com colunas se sem registros válidos |
| print_summary() | Mensagem amigável + return cedo se summary vazia |
| save_report() | Avisa se DataFrame vazio antes de salvar |

### Regra geral

Antes de qualquer operação de indexação ou agregação em DataFrame:
if df.empty: retorna mensagem amigável

Antes de acessar índices fixos (iloc[0]):
if top3.empty: retorna mensagem

## Alternativas

### A) Try/except genérico
Rejeitado porque mascara erros reais.

### B) Schema validation library (pandera, great_expectations)
Rejeitado por adicionar dependência pesada para um pipeline de 2 dependências.

## Consequências

+ Pipeline nunca trava por IndexError ou ValueError com dados vazios
+ Mensagens de erro claras indicam o problema exato
+ Comportamento consistente em todas as etapas
- Boilerplate adicional em cada função (~10 linhas extras)
