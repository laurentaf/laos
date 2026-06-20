# Contract — lacareerops-refactor

## What (brief)

Refatorar a capability `lacareerops` substituindo o fork mirror
(`laurentaf/career-ops`) por uma **hub privada** (`laurentaf/lacareerops-hub`)
que consome o upstream `santifer/career-ops` via **git submodule**. Inclui
um novo MCP tool `career_ops_sync` que automatiza o avanço de pin com
**smoke battery de 4 checks + auto-rollback** embutido, preservando os
invariantes de privacidade SC-1/SC-2/SC-3 do predecessor
`ADR-003-lacareerops-creation.md`.

## Why (problem)

- O fork `laurentaf/career-ops` não recebeu **nenhuma** commit local em 6 dias
  — era puro mirror, custando manter **dois** repos sem benefício.
- Upstream `santifer/career-ops` é ativo (commit `9d1404f` em 2026-06-18 =
  "feat(dashboard): customizable columns with column picker"). Sem protocolo
  explícito de sync, o fork diverge silenciosamente.
- Sem `career_ops_sync`, qualquer roll-forward requer git commands manuais,
  sem smoke test e sem rollback. Quebras são descobertas no call-site (late),
  não no advance (pre).
- Cada manutenção implica custo operacional de 2 repos: o fork LAOS-owned
  + o upstream santifer-owned. Submodule + hub elimina o primeiro.

## How (deliverables)

**Hub (`laurentaf/lacareerops-hub`, PRIVATE):**
- `mcp/server.py` — Python FastMCP wrapper, v1.1.0, 8 tools (7 preservados + 1 novo).
- `career_ops_sync` — refresh do pin + smoke battery + auto-rollback.
- `.gitmodules` apontando para `santifer/career-ops`.
- `SUBMODULE_SHA.txt` — pin atual `9d1404f32022b552e2dea1d773e0a10a22e2c004`.
- `.gitignore` — `config/*` excluido (apenas `*.example.*` rastreado), `SNAPSHOT_*`,
  `/upstream/`.
- Templates: `config/profile.example.yml`, `config/cv.example.md`.
- `pyproject.toml`, `LICENSE` (MIT), `README.md`.
- `docs/adr/ADR-013-lacareerops-submodule.md` (mirror).

**LAOS (este repo):**
- `projects/_meta/lacareerops-refactor/` — meta-projeto (este arquivo).
- `projects/_meta/adr/ADR-013-lacareerops-submodule.md` — LAOS-side canonical ADR.
- `registry/capabilities.yaml` — `lacareerops.repo` apontando para o novo hub.
- `knowledge/handoff-lacareerops.md` — seção "Submodule architecture (v1.1.0)" adicionada.
- `projects/_meta/capability-evolution/lacareerops.md` — loop 1 entry adicionada.

## Capabilities used

- **Primary:** `lacouncil` — proposal lifecycle + investigation + `record_project`
  após delivery-reviewer sign-off.
- **Optional:** `github` (repo create + push), `context7` (FastMCP docs se
  necessário).

## Repo / local paths

- **Hub (remote):** `https://github.com/laurentaf/lacareerops-hub` (PRIVATE).
- **Hub (cabin scratch):** `E:/projects/_architect-scratch/lacareerops-hub`.
- **Legacy fork:** `E:/projects/career-ops` (preservado como histórico local).
- **Snapshot:** `E:/projects/career-ops/config/SNAPSHOT_2026-06-19/`
  (`profile.yml`, `cv.md`, `README.md`) — única fonte de local truth para
  dados pessoais durante a migração.

## Governance

- **Proposal:** `ba9a9bd7-3686-4d6e-9f1b-3efc46f37a8c` (LACOUNCIL,
  supermaioria 4/4 SIM, 2026-06-19).
- **Flow:** LACOUNCIL proposal → Conselho vota → capability-architect
  implementa → delivery-reviewer valida → orchestrator commit+pushed Regra A.
- **Votes:** 4/4 (data-architect, dashboard-designer, automation-engineer,
  delivery-reviewer).
- **Regime A:** mudança estrutural aprovada pelo Conselho e validada pelo
  reviewer deve ser commitada e pushada dentro da mesma sessão. Para o hub
  isso já aconteceu. Para LAOS, o push ocorre após G4 BASIC sign-off
  (pré-regra Regra A + `padroes-entrega.md`).
