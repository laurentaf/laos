---
id: PROPOSTA-001
titulo: "Título claro e direto da melhoria"
autor: "orchestrator"
data: "2026-06-03"
status: "rascunho"
estrategia: "maioria"
---

## Resumo

Uma linha sobre o que está sendo proposto.

## Contexto

Por que essa mudança é necessária? Qual padrão recorrente foi detectado?
Quantas ocorrências? Em quais projetos?

## Mudança Proposta

O que exatamente muda?

- **Arquivo**: `registry/capabilities.yaml`
- **Tipo**: adição de nova capability
- **Diff esperado**: +5 linhas

```
  - id: nova-capability
    kind: domain
    mcp_server: ...
    status: stub
```

## Impacto

- **Projetos afetados**: nenhum (adição, não modificação)
- **Risco de regressão**: baixo
- **Rollback**: reverter o diff

## Alternativas Consideradas

1. Não fazer nada — padrão continuará sem solução
2. Criar skill em capability repo — não resolve o problema transversal
3. **Escolhida**: esta proposta — por X motivo

## Votos do Conselho

| Membro | Voto | Justificativa |
|--------|------|---------------|
| data-architect | — | — |
| dashboard-designer | — | — |
| automation-engineer | — | — |
| delivery-reviewer | — | — |

## Resultado

- **Status**: [aprovada / rejeitada / implementada]
- **Data**: —
- **Hash antes**: —
- **Hash depois**: —
