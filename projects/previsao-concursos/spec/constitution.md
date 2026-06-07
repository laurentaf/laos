# Constitution — previsao-concursos

**Version:** 1.0 | **Status:** Vigente (Missão 0, 2026-06-05)
**Origem:** cópia literal do template LATADE (`registry/spec-templates/spec/constitution.md`),
adaptada com Art. 0 do projeto e seções canônicas `Principles / Scope / Non-goals`
exigidas pelo gate `subagent_boot_check.py` 6ª dimensão.

---

## Article 0 — Missão 0 é obrigatória (projeto)

A Missão 0 (SDD scaffold) é obrigatória em qualquer projeto LAOS. O
`subagent_boot_check.py` 6ª dimensão (sub-check `skeleton`) valida esta
constituição + `spec/todo.md` + `spec/adr/` + `spec/harness/_template.md` +
`spec/specs/000-bootstrap/spec.md` + `contract.md` + `README.md` (e
`spec/design-direction.md` se `needs:` contém `dashboard` ou `design`).
Projeto sem scaffold **não passa em preflight** e não é despachado.

Retrofit passivo se aplica a projetos legados (sem varredura ativa).

---

## Principles

Cinco princípios macro governam este projeto (decorrem dos Artigos I–IX
do LATADE e dos rules de negócio em `project.yaml:107-111`):

1. **Probabilidades são empíricas, não causais.** Conta ocorrências no
   histórico, sem inferência causal nem extrapolação. Mede-se Brier
   score, NDCG@K e Top-K Recall — não "acerto da questão".
2. **LLM proibido no caminho de predição.** Tagging de sub_assunto é
   determinístico (hierarquia do edital + dicionário de sinônimos).
   LLM só pode aparecer em tooling auxiliar (análise exploratória,
   sumarização), nunca no scorer.
3. **Split temporal obrigatório.** Treino 2022-2024, validação 2025-2026.
   Janela móvel anual, sem leakage entre cadernos do mesmo concurso.
4. **Cada caderno vira `evento_id` próprio.** Manhã/Tarde e Tipos 1-4
   do mesmo edital são tratados como eventos independentes, porque a
   banca pode distribuir pesos diferentes.
5. **Reprodutibilidade por snapshot.** Toda agregação consome uma view
   gold congelada, não a tabela bronze raw. Decks e dashboards sempre
   referenciam a data do snapshot.

---

## Scope

**Dentro (POC):**

- Concursos das bancas FCC e FGV, cargo-alvo Auditor Fiscal (federal /
  estadual / municipal).
- Janela temporal 2022-2026, mínimo 20 concursos (alvo 25), 10-15 por
  banca.
- Probabilidade empírica por (banca, cargo, matéria, assunto, sub-assunto).
- Roteiro hierárquico Matéria > Assunto > Sub-assunto, ordenado do mais
  provável para o menos.
- Refresh mensal (capability `lan8n` para automação de ingestão).

**Adjacente (declarado, não construído no POC):**

- Outras bancas (VUNESP, CEBRASPE, AOCP, IBFC, FEPESE) — mesmo
  pipeline, dados não coletados.
- Outros cargos (Analista, Técnico, Policial) — modelo é o mesmo,
  matriz de cobrança difere.
- Inferência causal ("se cair X, aumenta chance de Y") — fora do
  escopo (regra §"Principles" #1).
- Auto-aplicação de questões pelo candidato — fora do escopo.

---

## Non-goals

1. **Não é coaching, não é cursinho.** Plataforma informa probabilidade;
   não substitui aula, não hierarquiza candidato, não emite opinião.
2. **Não é conselho jurídico sobre editais.** Probabilidade de cobrança
   não é garantia; o candidato consulta a fonte oficial (bancas FCC/FGV).
3. **Não comercializa dados pessoais.** POC 100% local, sem captura de
   usuário, sem telemetria, sem analytics externo. LGPD-safe by design.
4. **Não roda LLM em produção.** Inferência é pandas/scikit-learn/xgboost
   locais. LLM fica restrito a tooling offline de análise.
5. **Não replica provas com copyright.** PDFs de provas anteriores são
   cacheados localmente, com citação da fonte, sem republicação.

---

## Article I — Medallion as Structural Invariant
Every pipeline follows bronze → silver → gold.

## Article II — Mandatory Testability
Every component has pre-condition, post-condition, HARNESS level.

## Article III — Test-First Imperative
NO code before acceptance criteria and validations defined.

## Article IV — Idempotency
Every job executable N times without different results.

## Article V — Ubiquitous Language
Code names reflect GSD vocabulary.

## Article VI — No Cross-Layer Reads
Silver reads from silver. Gold reads from silver.

## Article VII — Simplicity
Max 3 medallion layers. No speculative features.

## Article VIII — Anti-Abstraction
Use tools directly. No unnecessary wrappers.

## Article IX — Integration Before Implementation
Contracts before code. HARNESS before production.
