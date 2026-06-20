# ADR-013: Lacareerops submodule architecture + career_ops_sync tool

**Status:** accepted
**Date:** 2026-06-19
**Decisor:** LACOUNCIL (supermaioria, 4/4 SIM)
**Proposal:** `ba9a9bd7-3686-4d6e-9f1b-3efc46f37a8c`
**Predecessor ADR:** `ADR-003-lacareerops-creation.md` (LACOUNCIL `2f1ccd2d`)

---

## Contexto

When `lacareerops` was created on 2026-06-13 (ADR-003), the chosen architecture
was **fork-and-wrap**: a private LAOS-controlled fork of `santifer/career-ops`
that mirrored upstream without any LAOS-owned commits. Six days later:

- **Zero local commits** had been made to the fork — it was purely a mirror.
- **Drift was inevitable**: upstream `career-ops` is active (recent commit
  `9d1404f` on 2026-06-18 = "feat(dashboard): customizable columns with
  column picker"). Without an explicit sync protocol, the fork would
  silently diverge.
- **Operational cost doubled**: every maintenance task implied updating two
  repositories instead of one.
- **No rollback path**: if a sync broke the wrapper, there was no machine-
  checkable way to detect or reverse it.

LACOUNCIL triggered an investigation (5 Whys + Fishbone), which surfaced
"fork-for-stability when upstream is active and wrapper consumes upstream
as a subprocess" as an architectural anti-pattern.

---

## Decisão

Replace the fork mirror with a **git submodule** architecture and add a
new MCP tool (`career_ops_sync`) that automates the pin advance with a
smoke-test gate and an automatic rollback.

### Components

1. **Hub repo** `laurentaf/lacareerops-hub` (PRIVATE) — replaces
   `laurentaf/career-ops`. Contains only LAOS-owned artifacts:
   - `mcp/server.py` (the wrapper; now version `1.1.0`)
   - `config/profile.example.yml`, `config/cv.example.md` (templates)
   - `pyproject.toml`, `LICENSE`, `.gitignore`, `README.md`
   - `docs/adr/` (mirrors of LAOS-side ADRs)
   - `SUBMODULE_SHA.txt` (last-known-good SHA, mutated only on smoke pass)
   - `.gitmodules`
   - `upstream/` (submodule — NOT a manual copy)

2. **Submodule** pointing at `https://github.com/santifer/career-ops.git`
   pinned to `9d1404f32022b552e2dea1d773e0a10a22e2c004` (HEAD as of
   2026-06-19). The pin is recorded in `SUBMODULE_SHA.txt` at the
   hub root.

3. **New MCP tool** `career_ops_sync` (idempotent, smoke-gated):
   ```
   await career_ops_sync()                          # advance to upstream HEAD
   await career_ops_sync(target_sha="<40-hex>")     # pin explicitly
   await career_ops_sync(dry_run=True)              # report only, no mutation
   ```
   Returns `{status, current_sha, requested_sha, source, smoke_results,
   smoke_passed, persisted?}`.

4. **Wrapper resolution semantics**: the tool tries
   `npm exec --prefix upstream -- @santifer/career-ops` first (so the
   pinned SHA is the actual source of truth) and falls back to
   `npx -y @santifer/career-ops@<pinned-sha>` if the submodule is not
   initialized. The pinned SHA always closes the loop, even on fallback.

### Quality guard rails

- Smoke test battery (4 checks) executed before every pin advance:
  - `upstream/package.json` parses as JSON.
  - `health()` self-call returns ok.
  - `list_supported_operations()` returns all 8 tools (sync included).
  - `node` binary is on PATH (career-ops CLI requirement).
- **Auto-rollback** if any smoke check fails: `git submodule update
  --init upstream` and `status: rolled_back` in the response.
- `SUBMODULE_SHA.txt` mutates **only** when smoke passes AND the new
  SHA differs from the previous one.

### Privacy invariants (preserved from ADR-003)

- `.gitignore` covers `config/profile.yml`, `config/cv.md`,
  `config/SNAPSHOT_*`, and excludes the submodule pointer `/upstream/`.
- Hub is **PRIVATE** on GitHub. Real user data never crosses a network.
- Sync tool only mutates the pinned SHA — it never reads `config/*.yml`
  or `config/cv.md`.

### Numbering note

This is ADR-013 (not ADR-004) because `projects/_meta/adr/ADR-004-charter-autonomy.md`
already exists with a different topic. ADRs are added in chronological
order; the next free number at the time of writing is `013`.

---

## Alternativas Consideradas

1. **Manter fork + manual sync protocol.** Rejected. Drift é inevitável
   sem tooling; mesmo com CI/cron, rollback fica manual e propenso a
   erro humano. Custo operacional de manter dois repos é o mesmo argumento
   desta proposta como *anti-feature*.

2. **Hub LAOS only-zero-config (zip distribution).** Rejected. Zip é
   snapshot estático; perde-se a janela para acompanhar upstream ativo.
   Adequado para distribuições versionadas, não para capability em
   evolução.

3. **Aguardar upstream tornar-se MCP-native.** Rejected. Upstream pode
   nunca oferecer MCP; LAOS perde a janela BASIC→STABLE (deadline
   2026-07-13). Wrapper-via-subprocess é o caminho mais próximo do
   contrato MCP sem esperar upstream.

4. **Substituir lacareerops por skill-only (drop MCP).** Rejected.
   Quebra integração MCP wall; `automation-engineer` perde acesso
   roteado via `registry/needs-to-capabilities.yaml`. Skill não tem
   o lifecycle de capability.

5. **Renomear lacareerops → outro slug.** Rejected. Rename + migrate
   tem custo comparável ao root cause fix; prefere-se resolver a
   arquitetura em vez de migrar todos os call-sites.

---

## Consequências

### Positivas

- **Single source of truth** para o engine: submodule pin determina
  exatamente qual versão de `career-ops` é consumida em toda checkout.
- **Sync repetível**: `career_ops_sync` substitui coordenação manual.
- **Rollback safety**: smoke test embutido detecta quebras antes do
  pin avançar; rollback automático se algo falhar.
- **Custo operacional** cai de 2 repo → 1 + sync tool.
- **Privacy preservada** sem mudança funcional.
- **Compatibilidade MCP wall**: 7 tools existentes preservadas + 1 nova.
  `registry/capabilities.yaml.owns` permanece "career.*".
- **Hub + LAOS verificáveis**: ambos os lados declaram a outra ponta
  via `repo:` + MCP config; refresh = 1 commit em cada lado.

### Custos e responsabilidades

- `capability-architect` implementa (esta proposta).
- `delivery-reviewer` valida G4 BASIC sign-off e G8 STABLE.
- `automation-engineer` continua sendo `G3` domain-specialist reviewer
  (KB + contracts) — confirmado via voto na proposta.
- Manutenção do submodule + sync tool (baixa quando upstream está
  estável; maior quando upstream acelera releases).
- Backup `config/` local durante migração (snapshot em
  `config/SNAPSHOT_2026-06-19/`).

### Riscos

- **Risco 1** — Submodule SHA errado quebra execução. Mitigação:
  `SUBMODULE_SHA.txt` + smoke test gate + auto-rollback.
- **Risco 2** — Vazamento acidental de dados via `config/` no commit.
  Mitigação: `.gitignore` continua cobrindo `config/profile.yml`,
  `config/cv.md`, `config/SNAPSHOT_*/`.
- **Risco 3** — Upstream muda CLI e quebra wrapper. Mitigação: smoke
  test + rollback embutidos; em M+30, adicionar `career-ops doctor`
  ao smoke battery.
- **Risco 4** — Lacareerops BASIC passa em STABLE pós-refactor, e os
  testes anteriores ficam stale. Mitigação: smoke suite é o novo
  baseline; STABLE eval usa o mesmo suite via `career_ops_sync`.

---

## Implementation plan executado (2026-06-19)

1. ✅ Backup snapshot de `config/profile.yml` + `config/cv.md` →
   `config/SNAPSHOT_2026-06-19/` (local only).
2. ✅ Criação de `laurentaf/lacareerops-hub` (PRIVATE) via
   `github_create_repository` (já existia por dispatch anterior).
3. ✅ `.gitmodules` + `SUBMODULE_SHA.txt` (pin = `9d1404f3...`) commitados
   no hub (`9fc6f03`).
4. ✅ Wrapper migration: `mcp/server.py` (v1.1.0, 8 tools incl.
   `career_ops_sync`), `.gitignore`, `config/profile.example.yml`,
   `config/cv.example.md` (já no hub em commits 1-2), `pyproject.toml`
   atualizado (já no hub), `LICENSE` adicionado (commit `9357af3`).
5. ✅ Tool `career_ops_sync` adicionado ao wrapper com smoke battery
   (4 checks) + auto-rollback (commit `9357af3`).
6. ✅ Atualizar LAOS-side structural files (este ADR, registro, KB,
   capability-evolution, meta-projeto `lacareerops-refactor/`).
7. ⏳ Validation:
   - Smoke test do `health` retorna `architecture: "submodule"`.
   - Smoke test do `list_supported_operations` retorna 8 ids incluindo `career_ops_sync`.
   - `career_ops_sync(dry_run=True)` retorna `{status: ok, smoke_passed: <bool>, ...}`.
   - `health_check: smoke_test_pending_first_session` — N/A real CV in LAOS repo.
   - Push ao GitHub (Regime A gated por delivery-reviewer BASIC sign-off).

---

## Implementação — atualizado 2026-06-19 (este dispatch)

LACOUNCIL `ba9a9bd7` aprovada 4/4 (supermaioria). capability-architect
implementa em dispatch. Commits na hub:

| SHA      | Conteúdo |
|----------|----------|
| `68d229c` | Initial commit (repo skeleton) |
| `9fc6f03` | `feat(v1.1.0): scaffold lacareerops-hub (submodule mode)` — `.gitmodules`, `SUBMODULE_SHA.txt`, `.gitignore`, `README.md`, config templates, `pyproject.toml` |
| `9357af3` | `feat(v1.1.0): add mcp/server.py with career_ops_sync + LICENSE + hub-side ADR-013` |
| `c92d61c` | `docs: fix ADR numbering reference in README (004-hoc-lacareerops-submodule -> ADR-013)` |

LACOUNCIL `lacouncil.record_project(lacareerops_refactor)` chamado após
validação do delivery-reviewer (Regime A gated).

---

## Referências

- LACOUNCIL proposal: `ba9a9bd7-3686-4d6e-9f1b-3efc46f37a8c`
- Predecessor ADR: `ADR-003-lacareerops-creation.md`
- Investigation: `lacouncil.investigate(...)` (5 Whys + Fishbone, 2026-06-19)
- WDL verdict: `artifacts/wdl/lacareerops-refactor-001/verdict.yaml`
- Capability evolution: `projects/_meta/capability-evolution/lacareerops.md`
- Refactor meta-project: `projects/_meta/lacareerops-refactor/project.yaml`
- Hub repository: `https://github.com/laurentaf/lacareerops-hub`
- Hub-side ADR mirror: `https://github.com/laurentaf/lacareerops-hub/blob/main/docs/adr/ADR-013-lacareerops-submodule.md`
- Upstream: `https://github.com/santifer/career-ops` (submodule)
- ADR format: `projects/_meta/adr/ADR-001-capability-governance.md`
