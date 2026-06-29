# CONSTITUTION — LACOUNCIL

> Princípios vinculantes da capability LACOUNCIL.
> Mirror parcial do regime da Constitution LAECON (precedent). Será ampliado
> na revis̃ao G3 (specialist review) + G4 (delivery-reviewer BASIC sign-off).

---

## Art. 1 — Princípio da Single Source of Truth

Toda proposta é persistida em `memoria/lacouncil.duckdb` (tabela `propostas`).
Nada vive em markdown paralelamente para fins de deliberação. A versão em
markdown (ADRs) é **derivada**, não autoritativa.

§1. Uma proposta aprovada recebe um `proposal_id` UUID v4 e é imutável após
encerramento da votação.

§2. Mudanças em fundamentals (AGENTS.md, esta Constitution) exigem proposta
com estratégia `unanimidade`. Mudanças em registry (capabilities.yaml,
needs-to-capabilities.yaml) exigem estratégia `supermaioria`. Mudanças em
`knowledge/`, `workflows/` exigem estratégia `maioria`.

---

## Art. 2 — Princípio da Separação de Poderes

| Função | Agente responsável | NÃO-pode |
|--------|--------------------|----------|
| Investigação | orchestrator (lacouncil.investigate) | aprovar a própria proposta |
| Proposta | orchestrator (lacouncil.create_proposal) | votar |
| Voto | Conselho (4 subagentes + orchestrator para tie-break) | propor |
| Implementação | capability-architect | propor, votar |
| Sign-off | delivery-reviewer | propor, votar, implementar |

§1. capability-architect **nunca** lê uma proposta sem antes verificar
`status == "aprovada"` (binding-condition.md R1).

§2. Subagentes de projeto (data-architect, dashboard-designer, automation-engineer)
NÃO operam registry, knowledge, workflows, ou esta Constitution — apenas
deliberam via `register_vote`.

---

## Art. 3 — Princípio do Voto Vinculante

Toda votação registrada é final imutável. Alterações posteriores a um
proposal accepted exigem NOVA proposta (cancelamento da antiga via
`implement_proposal` com nota, e abertura de nova).

§1. Voto é pessoal: cada membro do Conselho tem 1 voto por proposta; não há
voto por procuração.

§2. `ABSTENCAO` é contada como **ausência** para fins de quorum (não muda
numerador nem denominador). `ausente` (deliberação não-respondida) é o mesmo
que `ABSTENCAO`.

---

## Art. 4 — Princípio da Auditabilidade

Toda ação do LACOUNCIL é logada em DuckDB com timestamp, agente autor, e
hash canônico do payload. Reads são permitidos sem log; writes sempre geram
audit record.

§1. O signature de cada proposta usa `sha256-canonical-json` (Jason Kinsky
canonical JSON) sobre o dict da proposta serializada em ordem determinística.

§2. Investigação (`investigate`) produz `session_id` único e seus derivados
são linkados via `created_by_session` na proposta resultante.

---

## Art. 5 — Voto e deliberação

§1. Estratégias — codificadas em `core/voting.py`:

- `unanimidade`: aprovado se e somente se `SIM == total` (abstencoes = não).
- `supermaioria`: aprovado se `SIM / total >= 0.75` (default 0.75; configurável em casos raros via `k_supermaioria` no campo `parametros`).
- `maioria`: aprovado se `SIM / total > 0.50`.

§2. Em empates, orchestrator tem voto de Minerva (quebra); documentado em
`propostas.deliberation_notes`.

§3. Após `tally_votes`, status atualiza para `aprovada | rejeitada`. Propostas
rejeitadas NÃO podem ser reabertas — apenas sucedidas por nova proposta
(mecanismo de OBRR — open-by-record-replace).

---

## Art. 6 — Implementação rastreada

§1. `implement_proposal(proposal_id, applied_at, commit_sha?)` é a única
maneira de marcar uma proposta como implementada. `applied_at` é um
string ISO-8601 local.

§2. `commit_sha` é opcional; se ausente, o orchestrator registra NA delivery.

§3. `files_changed` é uma lista computed-on-implementation — não editável
manualmente (audit only).

---

## Art. 7 — Detecção de padrões

§1. `detect_patterns(min_occurrences=3, scope?)` itera sobre
`projects_registrados` e agrupa por string canônica do sumário.

§2. Padrões que cruzam 2+ capabilities OU atingem o threshold são retornados
com `confidence` ∈ [0, 1].

§3. Threshold default é 3 ocorrências (Hard Rule #7 — patterns 3+ trigger
action).

---

## Art. 8 — RBAC mínimo

§1. Reads são públicos para orchestrator + delivery-reviewer + Conselho.

§2. Writes (`create_proposal`, `register_vote`, `implement_proposal`,
`record_project`) **só** pelo:
- orchestrator (via exemption scope HR #8.4 — 9 tools allowed)
- capability-architect (em R1-gated fluxo)
- Conselho (voto via `register_vote` — MCP Wall whitelist)

§3. Subagentes data/dashboard/automation NÃO escrevem (apenas votam).

---

## Art. 9 — Privacidade

§1. Nada pessoal entra na tabela `propostas` ou `projetos_registrados` exceto
o que o usuário explicitamente autorizou no `project.yaml`.

§2. Textos que carregam PII (CV, salary history, address) devem ser
**hasheados** (sha256 + truncated) antes de ir pro DuckDB. Padrão: hash
prefix `sha256:` seguido de 16 hex chars.

---

## Art. 10 — Versionamento

§1. Esta Constitution segue `<major>.<minor>.<patch>`. Mudanças em Artigos
1–5 exigem unanimidade. Mudanças em Artigos 6–10 exigem supermaioria.

§2. Versão inicial: `0.1.0` (BASIC).

---

## Compliance tracks

Para promover para STABLE, os seguintes itens são requeridos:

- [ ] review pelo `dashboard-designer` (ART. 5 — UX da resposta tally)
- [ ] review pelo `automation-engineer` (ART. 6 — formato implement_proposal)
- [ ] review pelo `delivery-reviewer` (audit-log completeness)
- [ ] review pelo `data-architect` (DuckDB schema normalization — Art. 1)

Cada revisão produz um `compliance_acknowledged_at` no tracking file
`projects/_meta/capability-evolution/lacouncil.md`.
