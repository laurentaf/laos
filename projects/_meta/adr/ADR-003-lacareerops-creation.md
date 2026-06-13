# ADR-003: Criação da capability LACAREEROPS (job search optimization)

**Status:** accepted
**Date:** 2026-06-13
**Decisor:** LACOUNCIL (supermaioria, 3/4 SIM + 1 ABSTENCAO)
**Proposal:** 2f1ccd2d-7d0a-44fc-8382-24c3e16ebd0c

---

## Contexto

LAOS não tinha capability para gestão de carreira/busca de emprego. O ecossistema precisava de forma estruturada de:
1. Avaliar ofertas (salary vs. market, equity, benefits, remote)
2. Gerar CVs ATS-optimized em PDF
3. Escanear portais de emprego (LinkedIn, Indeed, Glassdoor, G2)
4. Processar múltiplas vagas em batch
5. Rastrear pipeline de candidaturas

O career-ops (santifer/career-ops, 740+ ofertas avaliadas, 100+ CVs gerados) já provou o conceito em produção com integração OpenCode nativa (.opencode/skills/ + commands/). A criação de uma capability formal permite governança, registry, e evolução estruturada.

A decisão de repo **PRIVADO** é devida a dados sensíveis (CV, salary history, career trajectory, target companies). O Conselho votou que isso é uma decisão correta de segurança (SC-1, SC-2, SC-3).

**Resultado da votação:**
- dashboard-designer: SIM
- automation-engineer: SIM
- delivery-reviewer: SIM
- data-architect: ABSTENCAO (incerteza sobre pipeline compatibility com LATADE)

A abstenção do data-architect não bloqueou — a compatibilidade com LATADE não é requisito para BASIC (lacareerops usa career-ops CLI Node.js, não DuckDB).

---

## Decisão

Criar a capability **LACAREEROPS** como **7ª capability domain** do LAOS, repo privado github.com/laurentaf/lacareerops.

### Stack
- **career-ops CLI (Node.js)** como engine — thin wrapper MCP em Python
- **Python stdlib** + `mcp` + `PyYAML` para o server wrapper
- **Playwright** (opcional, via career-ops) para PDF ATS-optimized
- Sem dependências pesadas — stdlib preferred

### Naming: `lacareerops`
- ✅ Claro: LAOS + career + ops
- ✅ Diferencia de automação genérica (lan8n) — propósito específico
- ✅ Não conflita com capabilities existentes

### Domínio
- `automation` (career job-search optimization) — adjacente a lan8n
- Não é `data` — não produz dados para LATADE por padrão
- Não é `design` — não produz dashboards por padrão

### Privacy by Design
- Repo é **PRIVADO** (dados sensíveis: CV, salary, career history)
- Cada usuário configura seus próprios `config/cv.md` e `profile.yml`
- Sem external API calls transmitindo dados do usuário
- `.gitignore` cobre `.env`, `config/*.yml`, `config/*.md`

### MCP Tools (7, todas operacionais em BASIC)

| Tool | Input | Output |
|------|-------|--------|
| `health` | — | `{status, version}` |
| `list_supported_operations` | — | `[{id, name, description}]` |
| `career_ops_evaluate` | `job_description: str` | evaluation JSON |
| `career_ops_generate_pdf` | `cv_text: str, job_description?: str` | PDF path |
| `career_ops_scan_portals` | `companies: str[]` | job openings list |
| `career_ops_batch_process` | `urls: str[]` | batch results |
| `career_ops_tracker_list` | — | pipeline JSON |

---

## Alternativas Consideradas

1. **Estender lan8n com career tools** — Rejeitado. lan8n é automação genérica de workflows; career-ops é domínio específico. Separar permite evolution independente e Constitution específica.

2. **Tornar repo público** — Rejeitado. CV, salary history, e career trajectory são dados sensíveis. Privacidade é hard requirement (delivery-reviewer concordou: HR #11 alignment).

3. **Usar LATADE como engine** — Rejeitado. career-ops é Node.js, não Python/DuckDB. A compatibilidade com LATADE é N/A para o escopo BASIC — lacareerops outputs são PDFs e JSON structs, não gold tables.

4. **Recusar (out-of-scope)** — Rejeitado. career-ops CLI já tem 740+ ofertas avaliadas e 100+ CVs gerados. O valor foi provado. Criar uma capability formal é o próximo passo natural.

5. **Usar LangChain/crewAI** — Rejeitado. career-ops usa regras deterministic, não LLMs. A proposta menciona explicitamente: "modelo de skill/command-based, não MCP-native".

---

## Consequências

### Positivas
- LAOS passa a ter 7 capabilities domain (6 STABLE + 1 BASIC)
- Usuários podem avaliar ofertas estruturadamente (salary vs. market, equity, benefits)
- CVs ATS-optimized gerados automaticamente
- Portal scanning integrated com o orchestrator
- Repo privado protege dados sensíveis

### Custos e responsabilidades
- Manutenção do MCP wrapper (mesmo se career-ops CLI mudar)
- Automation-engineer como domain specialist reviewer (G3)
- 30 dias para STABLE (deadline 2026-07-13)
- KB Handoff Boundaries deve ser mantido quando capabilities evoluem

### Riscos
- **Risco 1:** career-ops CLI muda API e quebra o wrapper. Mitigação: subprocess timeout + error handling + guidance on failure.
- **Risco 2:** Usuário commita `config/profile.yml` ou `config/cv.md`. Mitigação: `.gitignore` já cobre; revisar no preflight.
- **Risco 3:** Data architect continua preocupado com LATADE compatibility. Mitigação: ADR documenta que compatibility é N/A para BASIC; extensão future é possível.

---

## Implementação

### Entregue (2026-06-13)
- `github.com/laurentaf/lacareerops` (repo privado, auto-init)
- `mcp/server.py` com 7 tools (todas operacionais)
- `config/profile.example.yml` + `config/cv.example.md`
- `pyproject.toml` + `requirements.txt` + `.gitignore`
- `README.md` (reproduzível, ≥700 chars)
- `projects/_meta/lacareerops/` (meta-projeto completo)
- `registry/capabilities.yaml` (entry lacareerops, status=BASIC)
- `registry/needs-to-capabilities.yaml` (routing)
- `.opencode/opencode.jsonc` (MCP config)
- `knowledge/handoff-lacareerops.md` (G2 Handoff Boundaries)
- `projects/_meta/capability-evolution/lacareerops.md`
- Este ADR (G8)

### Próximos passos
- **G4** (2026-06-20): delivery-reviewer BASIC sign-off
- **G7** (2026-07-13): delivery-reviewer STABLE sign-off + status → STABLE
- **M2** (2026-08-13): Interview tracker + auto-submission

---

## Referências

- Proposta LACOUNCIL: `2f1ccd2d-7d0a-44fc-8382-24c3e16ebd0c`
- career-ops CLI: https://github.com/santifer/career-ops
- Governança de capabilities: `e9cd6dd8-b1e4-4e5f-8216-5cd69a095d4f`
- ADR-001 (formato): `projects/_meta/adr/ADR-001-capability-governance.md`
- ADR-002 (LAECON, precedente): `projects/_meta/adr/ADR-002-laecon-creation.md`