# Padrões de entrega

Checklist único que toda entrega de qualquer workflow precisa passar
antes de ser considerada feita. `delivery-reviewer` valida contra este
arquivo.

> **Origem do regime SDD:** Proposta LACOUNCIL `f9b636fc-5ca9-4860-94ca-3a6b43c6862c`
> (unanimidade 4/4, 2026-06-05). Missão 0 — SDD Scaffold — é obrigatória
> em todo projeto LAOS. Detalhes operacionais e cross-references em
> `knowledge/sdd-principles.md`.

## P0 - bloqueia entrega

### Estrutura do projeto (SDD scaffold — Missão 0)

- [ ] **SDD scaffold existe.** O projeto tem `spec/constitution.md`,
      `spec/todo.md`, `spec/adr/{_template.md,README.md}`,
      `spec/harness/_template.md`, `spec/specs/000-bootstrap/spec.md`,
      `contract.md`, `README.md` na raiz do child repo, e
      `spec/design-direction.md` (este último **só** se `needs:` contém
      `dashboard` ou `design`). Cada arquivo atende o tamanho mínimo
      da matriz per-file em `knowledge/sdd-principles.md` §2.
- [ ] **`spec/todo.md` populado desde Stage 0.** A 1ª task do tracker
      é a própria Missão 0 (SDD scaffold). Stages seguintes adicionam
      tasks, mas a estrutura existe desde o kickoff.
- [ ] **`contract.md` existe** e espelha `project.yaml` em prosa
      (brief, needs, deliverables, capabilities_used, repo). ≥ 250 chars.

### Validação obrigatória

- [ ] `delivery-reviewer` validou contra critérios de aceitação específicos do projeto antes do push. Nenhum push para avaliação externa sem aprovação.
- [ ] `project.yaml` existe, é válido e declara `needs` + `deliverables`.
- [ ] Todos os `deliverables` listados existem em `artifacts/`.
- [ ] Nenhum segredo (API key, token, senha, connection string completa)
      aparece em arquivos versionados. `.env` está em `.gitignore`.

### Artefatos por subclasse

- [ ] Para cada artefato de dados: existe spec do modelo em `artifacts/data/`
      e ao menos uma regra de qualidade documentada.
- [ ] Para cada artefato de dados: o pipeline tem **guards para DataFrame vazio**
      em todas as etapas que accedem índices ou agregam (`.iloc[0]`, `.mean()`,
      `.min()`, `.max()`, `groupby()`, `to_csv()`). Dados vazios devem produzir
      mensagem amigável, não `IndexError` nem `ValueError`.
- [ ] Para cada artefato visual: o DESIGN.md utilizado está referenciado
      em `artifacts/design/source.md`.
- [ ] Para cada automação: o trigger e o SLA estão documentados.

### Decisões (ADRs)

- [ ] **ADR-mínimo-1 com gatilho temporal.** Após o **primeiro estágio
      que produza decisão** (data-model, design ou build, o que vier
      primeiro), o projeto deve ter **≥ 1 ADR real** em `spec/adr/`
      (numerado a partir de `001-*.md`), além do `_template.md` e
      `README.md`. Antes desse estágio, só `_template.md` + `README.md`
      (índice vazio) são aceitos. Isso destrava POCs que param em
      discovery. Verificado pela 6ª dimensão do
      `subagent_boot_check.py` (sub-check `first-real-adr`).
- [ ] **Path único de ADRs:** `spec/adr/NNN-<slug>.md` (numerado a
      partir de 001). O diretório `artifacts/decisions/` é **morto**
      e não deve ser usado. Os 3 agent files que escrevem ADRs hoje
      (`data-architect.md`, `dashboard-designer.md`,
      `automation-engineer.md`) foram atualizados pelo
      `capability-architect` para apontar o novo path.

### Reprodução e legibilidade

- [ ] **README do child repo** (≥ 400 chars) explica como reproduzir
      a entrega do zero. Seções mínimas: "O que é", "Como rodar",
      "Onde está o quê". Promovido de P1 → P0 nesta revisão.
- [ ] **Não há código de implementação dentro de LAOS** (apenas specs).
      Verificação: `Get-ChildItem projects -Recurse -Include *.sql,*.dax,*.pbix`
      retorna vazio.

### Calibração e pré-flight

- [ ] **PR-1 (Princípio de Calibração 20/10 vs 50/1):** O nível de rigor
      aplicado à entrega é **Level-A (padrão global)**, não PhD (overkill)
      nem 4º-ano (insuficiente). Regra: se o investimento de tempo/esforço
      extra produzir +10% de qualidade por +20% de tempo, ADOTAR; se
      produzir +1% por +50% de tempo, REJEITAR (calcular
      `ratio = Δqualidade% / Δtempo%`; limiar ≥ 0.5). Verificável via:
      revisão por par (humano ou subagente) que o output seria aceito
      por 80% dos praticantes do campo para o mesmo problema.
      Implementação: Constitution laecon Art. 10 §7 (referência canônica),
      pré-flight mecânico em `scripts/preflight_check.py` (5 checks).
- [ ] **Preflight mecânico (Stage 0 do delivery-reviewer) passou.**
      O orchestrator deve rodar `uv run python scripts/preflight_check.py
      projects/<name>` antes de dispatchar o `delivery-reviewer`. Se
      exit ≠ 0, corrigir antes de prosseguir. Cobre 5 checks mecânicos:
      YAML+arithmetic, path existence, secret scan, cross-reference
      integrity, no implementation code in LAOS.
- [ ] **Boot check 6ª dimensão passou (`child-repo-skeleton`).**
      O orchestrator deve rodar `uv run python scripts/subagent_boot_check.py
      <subagent> --project-name <name>` antes de cada dispatch. O
      sub-check `skeleton` (sempre ativo) valida a matriz per-file
      da Missão 0; o sub-check `first-real-adr` (gated) valida o
      ADR-mínimo-1 só após o 1º estágio decisório. Se exit ≠ 0,
      corrigir antes de prosseguir.

## P1 - bloqueia se a entrega for para cliente externo

- [ ] Snapshots de dados estão datados e identificados (não "dados.xlsx").
- [ ] Decks e dashboards passam por revisão de acessibilidade básica
      (contraste, ordem de leitura).
- [ ] Toda decisão técnica não óbvia está em `spec/adr/` no formato
      ADR (Architecture Decision Record) — numerada, datada, com
      Contexto, Decisão, Alternativas, Consequências.
- [ ] `artifacts/review/checklist.md` foi produzido pelo
      `delivery-reviewer` durante o sign-off (output do reviewer,
      não entregável do projeto). Ownership: clause explícita em
      `.opencode/agent/delivery-reviewer.md` §"Sign-off checklist".

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
- Não escrever ADRs em `artifacts/decisions/`. O único path canônico
  é `spec/adr/NNN-<slug>.md` (ver §"Decisões (ADRs)" acima).
- Não tratar `artifacts/review/checklist.md` como entregável do
  projeto. É output do `delivery-reviewer`.
- Não pular Missão 0 (SDD scaffold). É obrigatória em todo projeto
  LAOS novo. Para projetos existentes, retrofit passivo: o
  `delivery-reviewer` exige retrofit ao tocar o projeto em
  sign-off ou auditoria normal (sem varredura ativa de projetos
  parados).
