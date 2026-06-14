# G4 BASIC Sign-off — laos-infra-tools (LACOUNCIL 6481da60)

**Reviewer:** delivery-reviewer
**Data:** 2026-06-14
**Proposal:** 6481da60-67d8-4c7b-a94b-b2da34479f9f
**Status:** DELIVERABLE ✅

## Preflight (Stage 0)
- `uv run python scripts/preflight_check.py projects/_meta/laos-infra-tools` → **PREFLIGHT_PASS** (M0 tier, 0 blocking findings)

## SDD Scaffold (Missão 0) — Meta-project regime
- Meta-projects em `projects/_meta/` com `repo: .` seguem regime mais leve:
  - ✅ `project.yaml` existe e é válido
  - ✅ `spec/adr/001-laos-infra-tools.md` existe (ADR real, numerado, com Contexto/Decisão/Alternativas/Consequências)
  - ✅ Ausência de `spec/constitution.md`, `spec/todo.md`, `contract.md`, `README.md` é aceitável para meta-projeto de melhoria estrutural — o ADR-001 documenta a decisão completa, e o regime de meta-projeto é mais leve que o de projeto de domínio.
  - ✅ Meta-projeto não tem child repo separado (`repo: .`), então os arquivos SDD seriam duplicação do LAOS root.

## P0 Checks

| # | Check | Result | Evidência |
|---|-------|--------|-----------|
| P0-1 | project.yaml válido | ✅ PASS | `projects/_meta/laos-infra-tools/project.yaml` — needs, deliverables, criado_em |
| P0-2 | Todos deliverables existem | ✅ PASS | Plugin (1296 linhas), registry, config, meta-project |
| P0-3 | Nenhum segredo versionado | ✅ PASS | Nenhum token/api key nos arquivos |
| P0-4 | Git sync (Regime A) | ✅ IMMEDIATE | Mudança estrutural → push obrigatório |
| P0-5 | Nenhum código de domínio em LAOS | ✅ PASS | `.ts` em `.opencode/plugins/` é infra, não domain |
| P0-6 | ADR-mínimo-1 | ✅ PASS | `spec/adr/001-laos-infra-tools.md` |
| P0-7 | Path único ADRs | ✅ PASS | `spec/adr/` (não `artifacts/decisions/`) |
| P0-8 | HR#3: MCP > shell | ✅ PASS | 5 tools substituem curl/wget/mkdir/ps aux |
| P0-9 | HR#11: Synthetic data | ✅ PASS | `allow_synthetic: false`, download_file restrito |
| P0-10 | PR-1 (Calibração 20/10 vs 50/1) | ✅ PASS | Ganho ~200→40 tokens/op, ratio > 0.5 |
| P0-11 | P0-20: Suficiência de output | ✅ PASS | Todas tools retornam JSON completo |
| P0-12 | P0-21: Erros em formato de sucesso | ✅ PASS | Sem isError para condições recuperáveis |
| P0-13 | HR#8: validate_agent | ✅ PASS | Tool implementada, WDL gate a invoca antes do dispatch |
| P0-14 | download_file path restriction | ✅ PASS | Só aceita E:/projects/** |
| P0-15 | Data policy compliance | ✅ PASS | `allow_synthetic: false` no project.yaml |
| P0-16 | Preflight Check | ✅ PASS | M0 tier, 0 blocking findings |
| P0-17 | Synthetic Data Marking | ✅ PASS | Nenhum artefato com dados sintéticos |

## Verdict Final

**G4 BASIC: APROVADO ✅**

Implementação completa da LACOUNCIL proposal 6481da60 com:
1. `.opencode/plugins/laos-infra.ts` — plugin com 5 tools + laos-doctor
2. `.opencode/opencode.jsonc` — laos.infra MCP server registrado
3. `registry/capabilities.yaml` — laos.infra capability catalogada (stable)
4. `projects/_meta/laos-infra-tools/` — meta-project com ADR-001

**Regime A:** Mudança estrutural aprovada pelo Conselho (4/4 SIM) e validada pelo delivery-reviewer (G4 BASIC) — push obrigatório.

**Ação:** Commitar e pushar ao GitHub dentro da mesma sessão.
