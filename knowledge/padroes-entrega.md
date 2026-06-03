# Padrões de entrega

Checklist único que toda entrega de qualquer workflow precisa passar
antes de ser considerada feita. `delivery-reviewer` valida contra este
arquivo.

## P0 - bloqueia entrega

- [ ] `project.yaml` existe, é válido e declara `needs` + `deliverables`.
- [ ] Todos os `deliverables` listados existem em `artifacts/`.
- [ ] Nenhum segredo (API key, token, senha, connection string completa)
      aparece em arquivos versionados. `.env` está em `.gitignore`.
- [ ] Para cada artefato de dados: existe spec do modelo em `artifacts/data/`
      e ao menos uma regra de qualidade documentada.
- [ ] Para cada artefato de dados: o pipeline tem **guards para DataFrame vazio**
      em todas as etapas que accedem índices ou agregam (`.iloc[0]`, `.mean()`,
      `.min()`, `.max()`, `groupby()`, `to_csv()`). Dados vazios devem produzir
      mensagem amigável, não `IndexError` nem `ValueError`.
- [ ] Para cada artefato visual: o DESIGN.md utilizado está referenciado
      em `artifacts/design/source.md`.
- [ ] Para cada automação: o trigger e o SLA estão documentados.
- [ ] Não há código de implementação dentro de LAOS (apenas specs).
      Verificação: `Get-ChildItem projects -Recurse -Include *.sql,*.dax,*.pbix`
      retorna vazio.

## P1 - bloqueia se a entrega for para cliente externo

- [ ] README do projeto explica como reproduzir a entrega do zero.
- [ ] Snapshots de dados estão datados e identificados (não "dados.xlsx").
- [ ] Decks e dashboards passam por revisão de acessibilidade básica
      (contraste, ordem de leitura).
- [ ] Toda decisão técnica não óbvia está em `artifacts/decisions/`
      no formato ADR (Architecture Decision Record).

## P2 - qualidade desejável

- [ ] Comentários do agente foram revisados e os mais úteis viraram
      knowledge transversal ou foram movidos para a capability repo correta.
- [ ] Workflow usado foi atualizado se algum padrão novo emergiu.
- [ ] Capacidade nova descoberta foi catalogada em `registry/capabilities.yaml`.

## Política de "não fazer"

- Não copiar prompts entre projetos. Se precisa reusar, vai para uma
  Skill no repositório da capacidade correspondente.
- Não criar utilitários em LAOS. LAOS é orquestrador; utilitários vão
  para a capacidade que mais os usa.
- Não bypassar MCP. Se um subagente precisa chamar uma capacidade,
  é via MCP, não via `bash` no repo da capacidade.
- Não inventar capacidades. Se a necessidade não está em
  `registry/needs-to-capabilities.yaml`, atualize o registro antes
  de prosseguir.
