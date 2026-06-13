# Capability Evolution — laecon

**Status:** IN_PROGRESS
**Created:** 2026-06-04
**Proposal:** cbe2d8ef-f65c-4d0e-8960-ea99527ab39f (LACOUNCIL, supermaioria, aprovada 2026-06-04 — 4/4 SIM, 100%)
**Deadline:** 2026-07-04 (+30 dias da primeira dispatch)
**Owner:** ../laecon (repo) + projects/_meta/laecon-capability/project.yaml (meta-projeto)

---

## Capability Info

| Field | Value |
|-------|-------|
| Name | laecon |
| Status atual | BASIC (scaffold entregue 2026-06-04) |
| Status target | STABLE |
| Domínio | data (extension of modeling concern) |
| Capability repo | github.com/laurentaf/laecon (a ser criado) |
| Local path | ../laecon/ |
| Tracking issue | this file + lacouncil proposal `cbe2d8ef-...` |
| Meta-projeto | projects/_meta/laecon-capability/project.yaml |
| ADR | projects/_meta/adr/ADR-002-laecon-creation.md |

---

## why

LAOS não tinha capability para modelagem preditiva/ML/econometria interpretável.
- `latade` cobre data engineering (SQL, DuckDB, medallion bronze→silver→gold)
  mas seu `data.modeling` é restrito a SQL de agregação, não modelagem
  estatística/ML.
- `ladesign` cobre dashboards e visual.
- `lan8n` cobre automação.
- Nenhuma cobre: regressão OLS com inferência completa, GLM, ordered/grouped
  logit, validação de pressupostos (Gujarati staples), efeitos marginais,
  cross-validation, árvores com interpretação, ensemble, simulation de drivers.

Necessidade disparada por:
1. Usuário (economista Unicamp) declarou que precisa evoluir em ML/data
   science.
2. Forneceu Gujarati & Porter (Basic Econometrics 5th ed, 2009) como base
   teórica — sugere que a capability deve ser econometrics-first, não ML-first.
3. Forneceu artigo da Quirk's (modeling NPS drivers) — reforça:
   likelihood explícita > black box; ordered/grouped logit > MNL/OLS para
   outcome ordinal; simulação de drivers > coeficientes soltos.

Decisão de naming: **laecon** (LA-ECON, econometria + ML). Não `laml` (genérico),
não `lacausal` (escopo restrito demais), não `lamod` (já conflita com latade.modeling).

---

## Escopo (consolidado pós-Conselho)

### Dentro do escopo
- **Regressão linear:** OLS, GLS, WLS, robust SE (Huber-White, HAC).
- **GLM:** logit, probit, poisson, negative binomial, gamma, inverse gaussian.
- **Ordered models:** ordered logit/probit (essencial para NPS).
- **Grouped models:** grouped logit (essencial para NPS agregado por região).
- **Validação de pressupostos:** heterocedasticidade (Breusch-Pagan, White),
  autocorrelação (Durbin-Watson, Breusch-Godfrey), multicolinearidade (VIF),
  normalidade dos resíduos (Jarque-Bera, Shapiro-Wilk).
- **Interpretação:** coeficientes, SE, t/z-stats, p-values, IC 95%, efeitos
  marginais (AME/MER), odds ratios com IC, elasticidades.
- **Avaliação:** R², adj-R², AIC, BIC, log-likelihood, RMSE, MAE, log-loss,
  AUC, confusion matrix, classification report.
- **Predição:** in-sample, out-of-sample com IC.
- **Simulação:** what-if de drivers (NPS driver simulator do artigo).
- **Cross-validation:** k-fold, stratified k-fold, leave-one-out.
- **ML interpretável (complemento, SÓ COM SHAP):** decision tree, random
  forest com feature importance, gradient boosting (XGBoost/LightGBM)
  com SHAP values. **Tree models entram no MESMO release que `compute_shap`**
  (condição vinculante do data-architect — anti-black-box desde o dia 1).
- **Convenção `_commomdata`** (E:\projects\_commomdata\) documentada como
  fonte de dados cross-project.

### Fora do escopo (BÁSICO)
- Deep learning (PyTorch, TensorFlow) — pós-STABLE se houver demanda.
- NLP/LLM, computer vision — fora do escopo LAOS.
- Big data distribuído (Spark, Dask) — DuckDB é suficiente.
- Causal inference avançada (DiD, RDD, IV, PSM) — extensão pós-STABLE,
  **com roadmap explícito** (ver M3 abaixo) — condição vinculante
  do data-architect.

---

## Condições vinculantes do Conselho (17 itens consolidados)

Estas condições foram acordadas na votação LACOUNCIL. **Bloqueiam a promoção
a STABLE em G7** se não forem atendidas.

### Do data-architect (5 vinculantes)

| ID | Condição | Onde endereça |
|----|----------|---------------|
| **DA-1** | **Painel, time series, IV/2SLS** precisam de roadmap com datas explícitas (não menção vaga "pós-STABLE"). Sugestão: painel em +60d (M2), time series em +90d (M3). | Este arquivo, M2 e M3 |
| **DA-2** | **XGBoost/LightGBM só entram no MESMO release que `compute_shap`**. Caso contrário o princípio da capability é violado. | M2 |
| **DA-3** | **Handoff latade↔laecon underspec'd** — feature engineering (laecon), outputs preditivos (storage próprio? gold tables? DuckDB file?), `validate_assumptions` (DuckDB ou arquivo?). Vira artigo(s) da Constitution (provavelmente Art. 4 sobre input/output contracts). | Constitution G4 (Art. 4) |
| **DA-4** | **Detalhamento metodológico extremo** — toda decisão (algoritmo, hiperparâmetro, variável) tem justificativa explícita + ≥1 alternativa rejeitada + referência bibliográfica com valor numérico de referência. As 7 perguntas (hipótese, por-quê-este-algoritmo, por-quê-este-hiperparâmetro, por-quê-esta-variável, quão-bom-esperado, quão-ruim-aceitável, quando-retreinar) são obrigatórias em todo modelo. | **Constitution Art. 10 (BASIC, vinculante desde já, não espera G4)** + `train_*` tools retornam `model_card` + skill enforce em M1 |
| **DA-5** | **`export_diagnostic_report` tem seção obrigatória "Decisões Metodológicas"** com tabelas (algoritmo candidato, hiperparâmetros, variáveis, indicadores) + bibliografia citada. | **Vinculante desde BASIC (princípio); implementação em M1** — Constitution Art. 10 §4 |

### Do dashboard-designer (3 vinculantes)

| ID | Condição | Onde endereça |
|----|----------|---------------|
| **DD-1** | **Handoff laecon → ladesign explícito** — laecon deve emitir artefatos estruturados (JSON/YAML) que ladesign consuma para construir dashboards. | Constitution G4 (Art. 4) + M1 |
| **DD-2** | **Plots list do `export_diagnostic_report` está incompleta** — faltam SHAP summary, partial dependence, calibration, e **probability curves por outcome level** (essencial para o caso NPS). | M1 |
| **DD-3** | `export_diagnostic_report` é analyst-facing; **complementar pós-STABLE** com `export_dashboard_payload` (executive-facing). | M2 ou M3 |

### Do automation-engineer (4 vinculantes G1-G3)

| ID | Condição | Onde endereça |
|----|----------|---------------|
| **AE-1** | **Model registry/ID** — `predict` precisa de `model_id` para ser reutilizável; retraining sem versionamento quebra automação. | G1 + Constitution Art. 6 |
| **AE-2** | **Workflow N8N de referência** no escopo — trigger+SLA+error path+alert routing. | G2 ou G3 |
| **AE-3** | **`export_diagnostic_report` output path determinístico** — sem path determinístico, workflow downstream não sabe onde ler. | G1 ou G2 |
| **AE-4** | **Credenciais/fonte de dados (input/output contracts)** na Constitution. | Constitution Art. 4 |

### Do delivery-reviewer (5 P0, bloqueiam G7 sign-off)

| ID | Condição | Onde endereça |
|----|----------|---------------|
| **DR-1** | **DataFrame empty guards** nos MCP tools — `train_regression`, `train_classifier`, `predict`, `interpret_model`, `evaluate_model` operam sobre dados. `padroes-entrega.md` P0: `.iloc[0]`, `.mean()`, `predict` em DF vazio não podem explodir. | G1 (MCP server) |
| **DR-2** | **Spec de modelo de dados em `artifacts/data/` com ≥1 regra de qualidade** — toda artefato de dados exige. | G6 (KB) + M1 (primeiro pattern NPS) |
| **DR-3** | **DESIGN.md referenciado em `artifacts/design/source.md`** SE `export_diagnostic_report` incluir plots. | M1 |
| **DR-4** | **Segredos + `.env` em `.gitignore`** em `../laecon/`. | G1 (scaffold) |
| **DR-5** | **ADR-002 deve seguir formato ADR-001** — Contexto, Decisão, Alternativas Consideradas, Consequências, Status, Date, Decisor. | ADR-002 (neste meta-projeto) |

---

## MCP Tools — Escopo Inicial (BASIC, 9 tools)

| # | Tool | Descrição | BASIC | M1 (STABLE) |
|---|------|-----------|-------|-------------|
| 1 | `health` | Liveness probe | ✅ implementado | ✅ |
| 2 | `list_supported_operations` | Catálogo de operações | ✅ implementado | ✅ |
| 3 | `train_regression` | OLS, GLS, WLS, robust SE com inferência completa | ⚠️ stub | ✅ |
| 4 | `train_classifier` | Logit, probit, ordered logit/probit, grouped logit | ⚠️ stub | ✅ |
| 5 | `validate_assumptions` | Heterocedasticidade, autocorrelação, multicolinearidade, normalidade | ⚠️ stub | ✅ |
| 6 | `interpret_model` | Efeitos marginais, odds ratios, partial dependence | ⚠️ stub | ✅ |
| 7 | `evaluate_model` | In-sample e out-of-sample metrics | ⚠️ stub | ✅ |
| 8 | `predict` | Predição pontual + IC, requer `model_id` (AE-1) | ⚠️ stub | ✅ |
| 9 | `export_diagnostic_report` | Relatório markdown/HTML com coefs + diagnostics + plots (DD-2) | ⚠️ stub | ✅ |

### Tools futuras (M2+)
- `cross_validate` (k-fold, stratified) — M2
- `train_tree_model` (decision tree, RF, gradient boosting) — **M2, JUNTO com `compute_shap`** (DA-2)
- `compute_shap` (SHAP values para interpretabilidade de ensembles) — M2 (junto com tree models)
- `simulate_drivers` (what-if de drivers — caso NPS do artigo) — M2 ou M3
- `export_dashboard_payload` (executive-facing, DD-3) — M2 ou M3
- `train_time_series` (ARIMA, VAR, ECM) — M3 (DA-1)
- `train_causal_model` (PSM, IV, DiD) — M3 (DA-1)
- `compare_models` (AIC/BIC/likelihood-ratio) — M1
- `train_panel_model` (FE/RE + Hausman) — M2 (DA-1)

---

## Quality Gates (G1-G8)

| Gate | Descrição | Status (2026-06-04) |
|------|-----------|---------|
| G1 | MCP server funcional (mesmo que stub) | ✅ scaffold entregue (health + list_supported_operations funcionais) |
| G2 | Entry em capabilities.yaml com status=BASIC | ✅ atualizado |
| G3 | Routing em needs-to-capabilities.yaml (6 rotas) | ✅ atualizado |
| G4 | Constitution.md com 9 artigos (conteúdo completo) | ✅ entregue (2026-06-13, 926 linhas, +464 linhas) |
| G5 | SDD workflow + templates (BRAINSTORM, DEFINE, PLAN, TASKS) | ⏳ pendente — 2026-06-24 |
| G6 | KB domain mínimo (index + 1 pattern NPS) | ⏳ pendente — 2026-07-04 |
| G7 | delivery-reviewer valida contra knowledge/ + condições acima | ⏳ pendente — após G1-G6 |
| G8 | ADR documentando rationale | ✅ ADR-002 publicado |

---

## Evolution Plan (com datas explícitas por DA-1)

| Milestone | Descrição | Deadline | Status |
|-----------|-----------|----------|--------|
| **M0** | Meta-projeto + LACOUNCIL proposal + scaffold BASIC | 2026-06-04 | ✅ entregue |
| G1 | MCP server stub funcional | 2026-06-04 | ✅ |
| G2 | Registry entry laecon BASIC | 2026-06-04 | ✅ |
| G3 | Routing needs-to-capabilities.yaml (6 rotas) | 2026-06-04 | ✅ |
| G8 | ADR-002 publicado | 2026-06-04 | ✅ |
| G4 | Constitution.md com 9 artigos completos | 2026-06-14 (+10d) | ✅ entregue 2026-06-13 (926 linhas, +464) |
| G5 | SDD templates (BRAINSTORM, DEFINE, PLAN, TASKS) | 2026-06-24 (+20d) | ⏳ pendente |
| G6 | KB domain mínimo (index + 1 pattern NPS) | 2026-07-04 (+30d) | ⏳ pendente |
| G7 | delivery-reviewer sign-off final (verifica 17 condições) | 2026-07-04 (+30d) | ⏳ pendente |
| **M1 (STABLE)** | Status promovido para STABLE | 2026-07-04 | ⏳ |
| **M2** | Tree-based models COM SHAP (DA-2), cross-validation, painel FE/RE (DA-1), model registry (AE-1) | 2026-08-04 (+60d) | ⏳ |
| **M3** | Time series (ARIMA, VAR, ECM) + causal inference (PSM, IV, DiD) (DA-1) | 2026-09-04 (+90d) | ⏳ |
| **M4+** | Deep learning sob demanda, NLP sob demanda, GARCH | sob demanda | ⏳ |

---

## Projetos que disparam evolução

| Projeto | Data primeira dispatch | Status | Nota |
|---------|----------------------|--------|------|
| laecon-capability (este) | 2026-06-04 | M0 entregue | Scaffold BASIC + ADR + registry + 17 condições catalogadas |

---

## Fontes de grounding

| Fonte | Tipo | Uso |
|-------|------|-----|
| Gujarati & Porter, Basic Econometrics 5th ed (2009) | Livro, 946 pp., `E:\projects\_commomdata\` | Base teórica (OLS, GLS, heterocedasticidade, autocorrelação, multicolinearidade, dummies, séries temporais, painéis) |
| Larson & Goungetas (Quirk's, 2013) — "Modeling the drivers of Net Promoter Score" | Artigo | Caso de uso canônico (ordered/grouped logit, likelihood explícita, simulação de drivers) |
| J. Scott Long, *Regression Models for Categorical and Limited Dependent Variables* | Livro (citado pelo artigo) | Referência para programação de likelihood de ordered/grouped logit |

---

## Propostas aprovadas (pós-BASIC)

| Proposta | Data | Estratégia | Resultado | Implementação |
|----------|------|-----------|-----------|---------------|
| `2505af1e` — Protocolo de Revisão Metodológica Obrigatório (Art. 10 §8) | 2026-06-13 | maioria (4/4 SIM) | APROVADA | G4 (Constitution completa) — adicionar §8 com 5 dimensões + auto-documentação |

---

## Progresso desta sessão (2026-06-13)

### Concluído

| Entrega | Status | Detalhes |
|---------|--------|----------|
| LACOUNCIL `2505af1e` — Art. 10 §8 | ✅ APROVADA (4/4 SIM) | Protocolo de Revisão Metodológica (5 dimensões) publicado na Constitution |
| Constitution Art. 10 §8 | ✅ Skeleton publicado | 5 dimensões, formato de output, implementação G4-G6-M1, auto-documentação |
| KB references — 8 arquivos | ✅ Criados (464 linhas) | gujarati-porter.md, hosmer-lemeshow.md, long-1997.md, breiman-2001-rf.md, friedman-2001-gbm.md, shap-lime.md, cross-validation.md, model-selection.md |
| KB README.md | ✅ Atualizado | Catálogo dos 8 arquivos com ✅ markers |
| Visual guide (HTML) | ✅ Criado | `laecon/guides/modeling-decision-guide.html` — 32.6KB, 10 seções, dark theme, sidebar nav, 7 Questions ref |
| **G4 — Constitution completa** | ✅ **Entregue (2026-06-13)** | Art. 4 (+55 linhas), 6 (+97), 7 (+92), 9 (+59) expandidos; Constitution vai de 462 → 926 linhas. Todos os skeleton markers removidos. |

### Pendente (próxima sessão)

| Entrega | Prioridade | Nota |
|---------|-----------|------|
| Learning material acquisition | MÉDIA | Baixar "Just Do OLS" PDF para `_commomdata/` + Fortmann-Roe essay |
| G5 — SDD templates (BRAINSTORM, DEFINE, PLAN, TASKS) | MÉDIA | Deadline 2026-06-24 |
| G6 — KB domain mínimo (index + 1 pattern NPS) | BAIXA | Deadline 2026-07-04 — mas pode avançar se houver tempo |

### Erros registrados (2026-06-13)

| # | Erro | Correção | Lição |
|---|------|----------|-------|
| 1 | **Shell calls excessivas** — orchestrator rodou `subagent_boot_check.py` + `head` (PowerShell não tem `head`) + glob + read de project.yaml + read de 3 arquivos WDL antes de dispatchar. 5 tool calls desnecessários antes de agir. | Parar após boot check + WDL verdict. O resto é overhead. | "Read the room" — se já tem verdict READY + boot PASS, dispatch imediatamente. Não fazer inventory completo quando o planejamento já foi feito. |
| 2 | **Dispatch `general` em vez de `dashboard-designer`** — WDL verdict sugeriu `general` (rationale: "single-file HTML, no data/design work"). Orchestrator seguiu cegamente o WDL. Mas HTML visual guide é trabalho de design, não de agente genérico. | Usar `dashboard-designer` para qualquer artefato visual/HTML que tenha design concerns (estilo, hierarquia visual, navegação). | WDL é advisory, não mandatório. Orchestrator tem juízo final sobre qual agente despachar. HTML com design system, dark theme, e flowcharts VISUAIS é trabalho de design. |
| 3 | **Documentar erros SÓ quando usuário pede** — erros anteriores (WDL path resolution, bypass manifests) foram notados mas não documentados proativamente no tracking file. | Documentar todo erro assim que detectado, não esperar que usuário peça. | Seção "Erros registrados" deve ser updated em tempo real durante a sessão. |
| 4 | **WDL gate não encontra verdict.yaml** — arquivo existe em `artifacts/wdl/<plan-id>/verdict.yaml` com estado READY, mas plugin `laos-wdl-gate.ts` não consegue ler via `findVerdictFromFile()`. Possível causa: `directory` param não aponta para workspace root, ou `require("fs")` falha no runtime OpenCode. Bypass via bypass-manifest.yaml registrado. | Usar LADESIGN MCP tools diretamente (agentic, bypassa WDL) ou `general` agent para trabalho não-especializado. | WDL gate é advisory para simple tasks — se exemption aplica, bypass é legítimo. |
| 5 | **LADESIGN auth failed** — `ladesign_start_run` retornou `AGENT_AUTH_REQUIRED`. Claude Code não autenticado. | Usar `general` agent como fallback para criação de HTML. | Ter fallback sempre disponível; não depender de um único MCP para deliverables críticos. |

### Notas técnicas

- WDL gate plugin corrigido nesta sessão — path resolution funcionando.
- Dispatch type para HTML visual guides: `dashboard-designer` (não `general`). WDL advisory aceito com override justificado.
- **WDL gate file-read issue:** verdict.yaml existe com estado READY mas plugin não encontra. Bypass legítimo para simple tasks.
- **LADESIGN auth:** Claude Code precisa de `/login` antes de usar `ladesign_start_run`. Fallback via `general` agent funciona.
- **Python venv policy:** `uv run python` sempre, nunca `python` direto (Hard Rule #9).

---

## Bloqueadores

- Nenhum no momento (M0 entregue).

---

## Notas

- Decisão de scope (econometrics-first) alinhada com background do usuário
  e com as fontes. ML preditivo é complemento, não centro.
- Decisão de naming (`laecon`) diferencia de ML genérico e aproveita o
  background do usuário como vantagem competitiva da capability.
- **17 condições vinculantes** do Conselho estão catalogadas acima e
  devem ser entregues nos milestones correspondentes. `delivery-reviewer`
  vai verificar todas em G7. DA-4 e DA-5 (Detalhamento Metodológico) são
  **vinculantes desde o BASIC** — Constitution Art. 10 já publicado;
  o enforcement nas tools e skill vem em M1, mas o princípio já rege
  qualquer uso da capability.
- Convenção `_commomdata` é transversal, não específica de laecon —
  documentada em `knowledge/data-conventions.md`.
- **Anti-black-box desde o dia 1:** tree-based models só entram com SHAP.
  Princípio fundador da capability.
- **Bibliotecas Python instaladas (2026-06-04, pós-solicitação do usuário):**
  pyproject.toml expandido com 26 deps no `[main]` (numpy 2.x, pandas 3.x,
  scipy 1.x, statsmodels 0.14, linearmodels 7.0, scikit-learn 1.6, xgboost
  3.2, lightgbm 4.6, catboost 1.2, shap 0.48, lime 0.2, optuna 4.9,
  matplotlib 3.10, seaborn 0.13 + utilities) e 13 grupos de extras
  (dev, notebooks, causal, timeseries, viz, feature_eng, nlp, validation,
  dl, bayesian, symbolic, graphs, full). `uv sync --extra full` validado
  exit 0 (200+ pacotes instalados).
  - **Importante:** libs instaladas ≠ tools expostos. Constitution não
    muda quando libs ficam disponíveis. Tools seguem M1/M2/M3 timeline.
  - **Pacotes deferidos para M3+** (conflito de pin com pydantic 2.x /
    altair 5.x já em `[main]`): neuralprophet (pydantic 1.x), great-
    expectations (pina altair<5), causalimpact (redundante).
  - Detalhes em `laecon/README.md` seção "Bibliotecas Python instaladas".
