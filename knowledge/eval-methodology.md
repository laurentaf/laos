# Eval Methodology

**Source:** CodeGraph (`colbymchenry/codegraph`), `docs/benchmarks/call-sequence-analysis.md` + `docs/benchmarks/codegraph-ab-matrix.md` + `docs/design/agent-codegraph-adoption.md`. Adaptado para LAOS em 2026-06-12.

**Purpose:** Formalizar como LAOS valida mudanças estruturais — WDL, registry, workflow templates, knowledge entries — com evidência quantitativa, não opinião.

---

## 1. Métricas — Hierarquia

Quando uma mudança é "melhor", a ordem de prioridade é:

| Prioridade | Métrica | Por que |
|---|---|---|
| 1 | **Wall-clock time** | O que importa para o usuário final |
| 2 | **Tool-call count** | Custo direto de tokens e turns |
| 3 | **Read/Grep = 0** | Agent não precisou ler arquivo para confirmar |
| 4 | **Token total** | Resultado, não target — segue naturalmente |

**Regra:** nunca otimizar para token cost sozinho. Se wall-clock e tool-calls melhoram, token cost segue. Se apenas token cost melhora mas wall-clock piora, a mudança é regressão.

**Como medir token total:** somar `usage` por turn, **não** o `result.usage` da última resposta (que é só do último turn). Em Claude Code headless: cada turn tem `usage` no JSON de resposta.

---

## 2. Model Floor Policy

Para qualquer eval de mudança estrutural, **sempre usar Sonnet como floor**.

```bash
MODEL=sonnet EFFORT=high bash scripts/agent-eval/run-all.sh <repo> "<task>"
```

**Nunca Opus, nunca Fable.** Por que (CodeGraph validated):

1. Sonnet não queima tokens — resultados são mais limpos, sem o modelo "pensando demais"
2. Sonnet é o modelo real dos usuários (Cursor Composer, Gemini, etc.)
3. Opus/Fable cobrem problemas de saliência/suficiência que Sonnet expõe
4. Um affordance que funciona em Sonnet **generaliza para cima**; um que só funciona em Opus **não generalize para baixo**

Se você validar em Opus e aprovar, pode estar aprovando algo que não funciona para seus usuários reais.

---

## 3. Regra de n≥2 — Variance é real

**Nunca conclua de n=1.** Run-to-run variance é grande. Uma mudança que parece 30% melhor em n=1 pode ser 5% pior na mediana de n=4.

```bash
# Correto: 4 runs por arm, mediana como resultado
bash scripts/agent-eval/run-all.sh <repo> "<task>"  # 2 runs/arm mínimo, 4 preferido
```

Se você está fazendo uma mudança e o resultado de n=1 parece muito bom, **rode mais** antes de aprovar.

---

## 4. Estrutura A/B

### Arm A — Baseline

Mudança **não aplicada**. Reprodiz o comportamento atual.

### Arm B — New

Mudança **aplicada**. Comportamento novo.

Ambas correm no mesmo repo, mesma task, mesmo model, mesmo effort. A única diferença é a mudança sendo testada.

### Para mudanças em LAOS itself

Diferente de CodeGraph (que testa duas builds do mesmo tool), aqui testamos duas versões do mesmo fluxo:

- **WDL v0 vs WDL v1** (mesmo repo, fluxos diferentes)
- **registry existente vs registry com nova entry** (mesma task, rotas diferentes)
- **workflow existente vs workflow novo** (mesma necessidade, capacidades diferentes)

---

## 5. Harness — run-all.sh

`run-all.sh` compara WITH vs WITHOUT a mudança.

```bash
bash scripts/agent-eval/run-all.sh <repo-path> "<task-prompt>" [model] [effort]
```

**Uso típico:**
```bash
# Testar WDL v1 vs baseline (sem WDL gate)
MODEL=sonnet EFFORT=high bash scripts/agent-eval/run-all.sh \
  E:/projects/meu-projeto \
  "Quero criar um dashboard de vendas. Me guie pelos steps."
```

**Output:** `artifacts/reviews/<run-id>.md` com:
- Duração total (wall-clock)
- Tool calls por tipo (`Read`, `Grep`, `mcp__lacouncil__*`, `mcp__latade__*`, etc.)
- Read/Grep counts
- Total tokens (soma por turn)
- Custo estimado (se model tiver pricing)

---

## 6. Harness — ab-new-vs-baseline.sh

`ab-new-vs-baseline.sh` compara **duas versões do mesmo fluxo** no mesmo repo.

```bash
bash scripts/agent-eval/ab-new-vs-baseline.sh <repo-path> "<task-prompt>" [baseline-ref]
```

**Uso típico:**
```bash
# Testar workflow-v2 vs workflow-v1 (mesma task)
bash scripts/agent-eval/ab-new-vs-baseline.sh \
  E:/projects/meu-projeto \
  "Quero criar um pipeline de ETL para orders" \
  v1
```

**Diferença de run-all.sh:** run-all.sh é with-vs-without (duas condições diferentes). ab-new-vs-baseline.sh é new-vs-baseline (mesma condição, duas versões).

**Pass criteria (ambos harnesses):**
- [ ] Arm B usa menos tool calls que Arm A (mediana, n≥2)
- [ ] Arm B Read/Grep ≤ Arm A Read/Grep (ideal: 0 dentro do budget)
- [ ] Arm B wall-clock ≤ Arm A wall-clock
- [ ] Sem regressão em repo de controle

---

## 7. Parse-run — interpretando resultados

`parse-run.mjs` quebra o output de cada run por tipo de tool:

```
codegraph tools exposed: 8        ← tools/list respondeu
codegraph tools used: 3          ← chamadas reais
Read calls: 0                    ← não precisou ler arquivos
Grep calls: 2                     ← só grep (às vezes ok)
mcp__lacouncil__get_proposal: 2  ← chamadas de capacidade
```

**O que procurar:**
- `codegraph tools used: 0` + `codegraph tools exposed: 0` → agent rodou **sem** a capability (problema de inicialização)
- `Read calls` alto → output da tool não foi suficiente, agent precisou confirmar
- `mcp__*` alto mas `Read` também alto → tool está sendo chamada mas não está substituindo reads

---

## 8. Quando usar cada harness

| Situação | Harness |
|---|---|
| Testar WDL v1 vs sem WDL | `run-all.sh` (with vs without) |
| Testar workflow v2 vs workflow v1 | `ab-new-vs-baseline.sh` |
| Testar mudança em registry/need routing | `ab-new-vs-baseline.sh` |
| Validar nova capability MCP (primeira vez) | `run-all.sh` com repo grande |
| Verificar regressão após mudança | `run-all.sh` vs repo de controle |

---

## 9. Eval de delivery-reviewer (G4 sign-off)

Para validar mudanças no `delivery-reviewer` (o que é uma validação de outputs, não de tool-use), usar o harness de **sufficiency check**:

```bash
# Dado um artifact path, verificar se o output do subagent
# é completo o suficiente para o orchestrator tomar decisão
python scripts/eval_sufficiency.py artifacts/reviews/<run-id>.md
```

Este script verifica:
- Receipt tem `summary` ≤ 2 linhas e acionável
- `details_path` aponta para arquivo existente
- `error_class` presente quando status = error
- Não há "Done", "Finished", "Working on it" no summary

---

## 10. arm-eval em contexto LAOS — o que é diferente de CodeGraph

CodeGraph valida builds do mesmo tool (mesma pergunta, duas versões). LAOS valida **fluxos orquestrais** (mesma pergunta, duas composições de capabilities).

Na prática:
- CodeGraph mede `codegraph_explore` ser suficiente para parar agent
- LAOS mede `delivery-reviewer` sign-off passar + orchestrator non-trivial dispatch count

**analogia:**
```codegraph
query: "how does X work?"    → 1 call, 0 Read  ✓
laos
query: "build me a pipeline" → dispatch data-architect → produce artifact → reviewer approves ✓
```

O que importa em LAOS eval não é 1 tool call, mas sim:
1. **Orquestrator dispatchou corretamente** (WDL verdict = READY)
2. **Subagent produziu artifact completo** (reviewer approved)
3. **Regime B respeitado** (push só após approval + user confirm)

---

## 11. Arm-eval checklist

Antes de rodar qualquer eval:

- [ ] Task é genuinamente nova (não já coberta por feature existente)
- [ ] Model fixo: sonnet, effort=high (nunca opus)
- [ ] Runs: ≥2 por arm, mediana como resultado
- [ ] Repo é o mesmo para ambas arms (mesmo estado inicial)
- [ ] Tool-call tracking habilitado (parse-run.mjs no output)
- [ ] Read/Grep = 0 como target (não apenas "menos que baseline")

---

## Referências

- CodeGraph `docs/benchmarks/call-sequence-analysis.md` — origem do metric hierarchy
- CodeGraph `docs/benchmarks/codegraph-ab-matrix.md` — estrutura do eval harness
- CodeGraph `docs/design/agent-codegraph-adoption.md` §"Validation methodology" — model floor policy
- Proposal LACOUNCIL: `dbc88097` (subagent result contract, onde esta methodology será usada)