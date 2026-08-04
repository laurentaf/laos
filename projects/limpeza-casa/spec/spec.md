# Especificação — Gestão de Produtos de Limpeza

## Objetivo
App HTML autossuficiente para gestão doméstica de produtos de limpeza:
registrar necessidades, cadastrar produtos com estoque, e obter
dashboard de gastos + sugestão de compra.

## Requisitos funcionais

### Fase 1 — Necessidades (aba 1)
- RF1.1 Usuário adiciona necessidades à vontade (texto livre)
- RF1.2 Lista necessidades com remoção individual
- RF1.3 Persistência em localStorage

### Fase 2 — Produtos (aba 2)
- RF2.1 Cadastro de produto: nome, capacidade (ml), preço pago
- RF2.2 Checkboxes das necessidades que o produto cobre
- RF2.3 Nível de estoque 100/80/60/40/20/0% (slider)
- RF2.4 Lista com edição/remoção

### Fase 3 — Dashboard (aba 3)
- RF3.1 Estoque atual por produto (barras coloridas)
- RF3.2 Alerta de necessidades sem nenhum produto associado
- RF3.3 Gasto médio do mês
- RF3.4 Sugestão de compra: estoque ≤ 30% → "repor X ml"

### Fase 4 — App completo
- RF4.1 3 abas navegáveis num único arquivo
- RF4.2 Dados compartilhados entre abas via localStorage

## Requisitos não funcionais
- RNF1 HTML único autossuficiente (zero dependência externa)
- RNF2 Zero backend (localStorage)
- RNF3 Português, interface limpa

## Critérios de aceite (verifier)
- Artefato existe, carrega (parse), contém form + localStorage + botões
- Batem com o spec declarado no project.yaml

## Dados
- Sem dados externos; dados do usuário em localStorage
- `data_policy: allow_synthetic: true` (POC — sem dados reais)
