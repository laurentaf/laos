# Child Repo Hooks

> **Proveniência:** Oracle 2Care §Hooks (mesmo autor, Laurent).
> Adaptado de produção healthcare para contexto LAOS open/synthetic data.
> LACOUNCIL proposal `3473c12b` (aprovada 4/4 SIM, 2026-06-12).

## Modelo de Hooks

O child repo (projeto-filho, ex: `laurentaf/<project-name>`) segue um modelo
de 3 hooks que automatizam o ciclo git e garantem segurança:

| Hook | Responsabilidade | Quando roda |
|------|-----------------|-------------|
| **pre-commit** | Secret scan, sanity check, readiness audit | `git commit` (antes do commit) |
| **post-commit** | Auto-push para origin | `git commit` (depois do commit) |
| **session-end** | Safety net para changes não commitados | Fim da sessão do agent |

## Hooks Implementados

### pre-commit

```
scripts/child-repo-hooks.sh pre-commit
```

**O que faz:**
1. Verifica se há `.env` ou segredos em stage (`git diff --cached`)
2. Roda `github_run_secret_scanning` nos arquivos em stage
3. Loga resultado em `.laos/hooks/logs/pre-commit-<timestamp>.log`
4. Se secret encontrado → aborta commit com mensagem acionável
5. Se limpo → permite commit prosseguir

**Não faz (LAOS vs Oracle 2Care):**
- ❌ Catalog auto-fix (LAOS não tem catalog como Oracle 2Care)
- ❌ Governance audit (Regime A/B cobre isso via delivery-reviewer)
- ❌ LGPD scan (fora de escopo — LAOS usa open/synthetic data)

**Exit codes:**
- `0` — limpo, commit permitido
- `1` — segredo detectado, commit bloqueado
- `2` — erro no scanner, commit bloqueado (fail-safe)

### post-commit

```
scripts/child-repo-hooks.sh post-commit
```

**O que faz:**
1. Verifica se `git push` já foi feito nesta sessão (evita double-push)
2. Executa `git push origin HEAD`
3. Loga em `.laos/hooks/logs/post-commit-<timestamp>.log`
4. Se push falha → tenta retry uma vez após 2s
5. Se retry falha → avisa o agent para push manual

**Exit codes:**
- `0` — push OK
- `1` — push falhou após retry, agent precisa resolver manualmente

### session-end

```
scripts/child-repo-hooks.sh session-end
```

**O que faz:**
1. Verifica `git status --porcelain` para changes não commitados
2. Se changes pendentes → imprime lista de arquivos + `git diff --stat`
3. Se nada pendente → silent exit
4. Não modifica nada (read-only safety net)

**Exit codes:**
- `0` — sem pending changes
- `1` — pending changes encontrados (aviso, não erro)

## Integração com Regime A/B (AGENTS.md §Git sync regime)

| Regime | Trigger | Hook usado | Quem roda |
|--------|---------|-----------|-----------|
| **Regime A** | Mudança estrutural aprovada + validada | post-commit auto-push | automático |
| **Regime B** | Artefatos de domínio validados + confirmação usuário | post-commit (após confirmação) | após delivery-reviewer G4 |

Hooks são agnósticos de regime — o Regime A/B controla *quando* o commit acontece;
os hooks controlam *o que* acontece em torno do commit.

## Instalação

O `scripts/child-repo-hooks.sh` deve ser linkado como git hooks no child repo:

```bash
# No child repo (ex: laurentaf/meu-projeto)
cp E:/projects/LAOS/scripts/child-repo-hooks.sh .git/hooks/pre-commit
cp E:/projects/LAOS/scripts/child-repo-hooks.sh .git/hooks/post-commit
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/post-commit
```

Ou via setup script do projeto (SDD Stage 0).

## Logs

Logs dos hooks vivem em `.laos/hooks/logs/` no child repo (gitignored).
Estrutura:
```
.laos/hooks/logs/
├── pre-commit-2026-06-12T143022.log
├── post-commit-2026-06-12T143025.log
└── session-end-2026-06-12T160000.log
```

## Diferença de Oracle 2Care

| Aspecto | Oracle 2Care | LAOS (este arquivo) |
|---------|-------------|---------------------|
| Escopo | Produção healthcare (LGPD) | Open/synthetic data |
| compliance-gatekeeper | Sim (LGPD audit) | Não (fora de escopo) |
| catalog auto-fix | Sim | Não (sem catalog) |
| Pre-commit secret scan | Sim | Sim |
| Post-commit auto-push | Sim | Sim |
| Session-end safety | Sim | Sim |

## pre-push (LAOS repo only)

```
.git/hooks/pre-push
```

**O que faz (auto-rebase on divergent remote):**
1. `git fetch` to update remote tracking refs
2. Check `git rev-list --count HEAD..origin/main` — if 0, proceed
3. If remote has new commits → `git pull --rebase origin main`
4. If rebase succeeds → exit 0, push proceeds
5. If conflicts → abort with actionable message

**Por que existe:**
Sem ele: 8 passos manuais para resolver divergent push (fetch → pull --rebase → resolve conflicts → add → rebase --continue → push).
Com ele: 1 passo (`git push`) se rebase succeeds, or 3 steps if conflicts.

**Exit codes:**
- `0` — up to date or rebase succeeded, push proceeds
- `1` — conflicts, abort with manual resolution instructions

**Instalação (LAOS repo):**
```bash
cp scripts/pre-push .git/hooks/pre-push
git config core.hooksPath .git/hooks
```

## Histórico

- 2026-06-12 — Criado via LACOUNCIL `3473c12b` (adção de 3 padrões Oracle 2Care)