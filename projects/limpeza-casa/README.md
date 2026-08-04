# Gestão de Produtos de Limpeza

App HTML autossuficiente (1 arquivo, 3 abas, localStorage) para gestão
doméstica de produtos de limpeza.

## O que é

- **Aba 1 — Necessidades:** registre o que precisa ser limpo (vidro,
  pia, piso, vaso sanitário — adicione à vontade).
- **Aba 2 — Produtos:** cadastre produtos comprados (nome, capacidade
  em ml, checkboxes das necessidades que o produto cobre, quanto pagou,
  nível de estoque 100%→0%).
- **Aba 3 — Dashboard:** estoque atual por produto (barras coloridas),
  alerta de necessidades sem produto, gasto médio do mês, e sugestão de
  compra do próximo mês (estoque ≤ 30% → "repor X ml").

Tudo persistido em `localStorage` — **zero backend, zero servidor**.

## Como rodar

Abra `artifacts/limpeza/index.html` em qualquer navegador. Nada a
instalar.

## Como foi gerado

Projeto executado pelo LAOS (orquestrador): 4 fases, cada uma gerada
por LLM (deepseek-v4-flash via LiteLLM) com custo real auditado,
verificada por `laos verify`. Custo total do projeto: **US$ 0,0045**
(16.512 tokens) — os 4 arquivos HTML.

## Onde está o quê

```
projects/limpeza-casa/
├── project.yaml                  contrato (fases + specs)
├── HANDOFF.md                    relatório de entrega (20 itens)
├── spec/                         especificação do projeto
└── artifacts/limpeza/
    ├── fase1-necessidades.html   aba 1 (standalone)
    ├── fase2-produtos.html       aba 2 (standalone)
    ├── fase3-dashboard.html      aba 3 (standalone)
    └── index.html                APP COMPLETO (3 abas num arquivo)
```

## Estado

- 4/4 fases completas, verificação 4/4 OK (existe + carrega + testa + spec)
- 0 erros em produção; 1 erro de retry na fase 4 (max_tokens) — resolvido
