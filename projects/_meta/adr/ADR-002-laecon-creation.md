# ADR-002: Criação da capability LAECON (econometria + ML interpretável)

**Status:** accepted
**Date:** 2026-06-04
**Decisor:** LACOUNCIL (supermaioria, 4/4 SIM, 100%)
**Proposal:** cbe2d8ef-f65c-4d0e-8960-ea99527ab39f

---

## Contexto

LAOS (orquestrador) não tinha capability para modelagem preditiva/ML/econometria interpretável. As 5 capabilities existentes cobriam:
- `latade` (STABLE) — data engineering, SQL, DuckDB, medallion pipeline. `data.modeling` é restrito a SQL de agregação, não modelagem estatística/ML.
- `ladesign` (STABLE) — dashboards, visual, design systems.
- `lan8n` (STABLE) — automação N8N, workflows, integrações.
- `lacouncil` (STABLE) — LACOUNCIL, investigação, proposals, memory.
- `laengine` (BASIC) — game development, sports simulation.

Necessidade disparada por:
1. Usuário declarou explicitamente: "preciso melhorar minhas capacidades de machine learning e data science".
2. Usuário é economista formado na Unicamp, com background em estatística, matrizes e econometria.
3. Forneceu duas fontes de grounding:
   - Gujarati & Porter, *Basic Econometrics 5th ed* (2009), 946 pp., em `E:\projects\_commomdata\`. Cobre OLS, GLS, heterocedasticidade, autocorrelação, multicolinearidade, dummies, séries temporais, painéis.
   - Larson & Goungetas, *"Modeling the drivers of Net Promoter Score"* (Quirk's, 2013). Econometristas da AT&T defendendo ordered/grouped logit com likelihood function explícita (anti-black-box), simulação de drivers como deliverable final.

DIAGNÓSTICO DE ROUTING:
- Needs `ml`, `data-science`, `econometrics`, `nps-driver-analysis`, `causal-inference`, `predictive-modeling` NÃO existiam em `registry/needs-to-capabilities.yaml`.
- `modeling` mapeava para `latade` mas o `data.modeling` de latade é restrito a SQL.
- Capability nova, com knowledge próprio, com tools concretos via MCP. Atende os 3 critérios cumulativos para nova capability do regime `e9cd6dd8`.

---

## Decisão

Criar a capability **LAECON** (LA-ECON, econometria + ML interpretável) como **6ª capability domain** do LAOS, seguindo o regime de governança aprovado em `e9cd6dd8` (G1-G8 quality gates).

### Posicionamento
- **Econometria é a espinha, ML é o músculo.** Diferencia de ML genérico.
- **Likelihood explícita, não black box.** Alinhado com a tradição econométrica que o usuário domina e com o artigo da Quirk's.
- **Interpretabilidade antes de acurácia.** Coeficientes com SE e p-values, efeitos marginais, odds ratios, antes de métricas de scoring.
- **Local-first, DuckDB como engine.** Reusa o runtime de latade. Suficiente para o escopo.

### Naming: `laecon`
- ✅ Claro: "LA-ECON" = LAOS + Econometria.
- ✅ Diferencia de `laml` (ML genérico), `lacausal` (escopo restrito demais), `lamod` (conflita com latade.modeling).
- ✅ Aproveita o background do usuário como diferencial.

### Domínio
- `data` (extension of modeling concern, paralelamente a latade).
- Sub-domínios próprios: econometrics, ml.interpretable, data.causal-inference, ml.timeseries (FUTURO).

### Localização
- Repo: `../laecon/` (sibling de latade, lan8n, ladesign, lacouncil, laengine).
- GitHub: `github.com/laurentaf/laecon` (a ser criado via `gh repo create`).
- venv isolado: `../laecon/.venv/` gerenciado por `uv sync`.

### Status e evolução
- **Status inicial:** BASIC (paralelo a laengine).
- **Deadline de evolução:** 2026-07-04 (+30 dias) para STABLE.
- **Tracking:** `projects/_meta/capability-evolution/laecon.md`.
- **Meta-projeto:** `projects/_meta/laecon-capability/project.yaml`.

### Convenção transversal nova
- **`_commomdata` (`E:\projects\_commomdata\`)** — diretório compartilhado cross-project para fontes de grounding (livros, papers, datasets públicos). Documentada em `knowledge/data-conventions.md`.

---

## Escopo

### Dentro
- Regressão: OLS, GLS, WLS, robust SE (Huber-White, HAC).
- GLM: logit, probit, poisson, negative binomial, gamma, inverse gaussian.
- Ordered models: ordered logit/probit (essencial para NPS).
- Grouped models: grouped logit (essencial para NPS agregado por região).
- Validação de pressupostos: heterocedasticidade (Breusch-Pagan, White), autocorrelação (Durbin-Watson, Breusch-Godfrey), multicolinearidade (VIF), normalidade (Jarque-Bera, Shapiro-Wilk).
- Interpretação: coeficientes, SE, t/z-stats, p-values, IC 95%, efeitos marginais (AME/MER), odds ratios com IC, elasticidades.
- Avaliação: R², adj-R², AIC, BIC, log-likelihood, RMSE, MAE, log-loss, AUC, confusion matrix, classification report.
- Predição: in-sample, out-of-sample com IC.
- Simulação: what-if de drivers (NPS driver simulator do artigo).
- Cross-validation: k-fold, stratified k-fold, leave-one-out.
- ML interpretável (M2, com SHAP): decision tree, random forest, gradient boosting (XGBoost/LightGBM) com SHAP values.
- Convenção `_commomdata` como fonte de dados cross-project.

### Fora
- Deep learning (PyTorch, TensorFlow) — pós-STABLE se houver demanda.
- NLP/LLM, computer vision — fora do escopo LAOS.
- Big data distribuído (Spark, Dask) — DuckDB é suficiente.
- Causal inference avançada (DiD, RDD, IV, PSM) — M3, pós-STABLE.

### MCP Tools (9 BASIC, com roadmap M1-M3)
Ver `projects/_meta/capability-evolution/laecon.md` para lista completa e roadmap.

---

## Condições vinculantes (17 acordadas com o Conselho)

### Do data-architect (3)
- **DA-1:** Painel, time series, IV/2SLS com roadmap de datas explícitas (M2 painel, M3 time series, M3 IV/2SLS).
- **DA-2:** XGBoost/LightGBM SÓ entram no MESMO release que `compute_shap` (anti-black-box).
- **DA-3:** Handoff latade↔laecon vira artigo(s) da Constitution (Art. 4 sobre input/output contracts).

### Do dashboard-designer (3)
- **DD-1:** Handoff laecon→ladesign com artefatos estruturados (JSON/YAML) consumíveis por dashboards.
- **DD-2:** Plots do `export_diagnostic_report` incluem SHAP summary, partial dependence, calibration, probability curves por outcome level (NPS).
- **DD-3:** Pós-STABLE, `export_dashboard_payload` (executive-facing).

### Do automation-engineer (4)
- **AE-1:** `model_id` reutilizável (model registry + versionamento) — Constitution Art. 6.
- **AE-2:** Workflow N8N de referência (trigger + SLA + error path + alert routing) — G2/G3.
- **AE-3:** Output path determinístico para `export_diagnostic_report` — G1/G2.
- **AE-4:** Credenciais e contratos de I/O na Constitution Art. 4.

### Do delivery-reviewer (5 P0, bloqueiam G7 sign-off)
- **DR-1:** DataFrame empty guards nos MCP tools (P0 `padroes-entrega.md`).
- **DR-2:** Spec de modelo de dados em `artifacts/data/` com ≥1 regra de qualidade.
- **DR-3:** DESIGN.md referenciado em `artifacts/design/source.md` SE plots.
- **DR-4:** Segredos + `.env` em `.gitignore`.
- **DR-5:** ADR-002 (este documento) segue formato ADR-001.

Detalhamento e onde cada condição é endereçada: `projects/_meta/capability-evolution/laecon.md`.

---

## Alternativas Consideradas

1. **Estender latade com módulo de ML** — Rejeitado. latade já é focado em SQL/DuckDB/medallion; misturar ML no mesmo repo viola single-responsibility e prejudica o Constitution de latade (9 artigos consolidados).

2. **Criar capability genérica `laml`** — Rejeitado. Genérico demais, perde o posicionamento econométrico que o background do usuário habilita e que as fontes de grounding sustentam. ML puro tende a black-box (XGBoost sem SHAP, deep learning), o que contradiz a tradição econométrica e o artigo da Quirk's.

3. **Criar `lacausal`** — Rejeitado. Escopo restrito demais. Causal inference é uma sub-área, não o todo. Pode virar sub-domínio (`data.causal-inference`) na evolução pós-STABLE.

4. **Criar `lamod`** — Rejeitado. "mod" conflita com latade's `data.modeling`. Confunde registry.

5. **Recusar (out-of-scope)** — Rejeitado. Há demanda concreta (usuário declarou), grounding teórico (Gujarati), caso de uso (NPS), e tools concretos (likelihood-based ML). Atende os 3 critérios cumulativos de nova capability do regime `e9cd6dd8`.

6. **Criar `laquant` (quantitative methods)** — Considerado. Seria mais amplo que econometria, cobrindo estatística geral, séries temporais, etc. Rejeitado por ser genérico demais e diluir o posicionamento econométrico que o background do usuário e a fonte Gujarati habilitam. Mantido como fallback se o Conselho preferir.

---

## Consequências

### Positivas
- LAOS passa a ter 6 capabilities domain (5 STABLE + 1 BASIC = 4 stable antigos + laengine basic + laecon basic).
- `_commomdata` vira convenção transversal, não específica de laecon. Outros projetos futuros podem usar.
- Knowledge econométrico (likelihood explícita, validação de pressupostos, efeitos marginais) vira referência quando o usuário pedir dashboards preditivos ou interpretação causal em outros projetos.
- LATADE permanece responsável por data engineering; laecon consome seus outputs (gold tables) como input para modelagem.
- Caso de uso NPS driver analysis fica como primeiro pattern canônico (G6).
- Usuário consegue fazer econometria aplicada (não black-box) diretamente em LAOS, com grounding em Gujarati + interpretação Quirk's-style.

### Custos e responsabilidades
- 17 condições vinculantes do Conselho a serem entregues nos milestones (G4-M3).
- `delivery-reviewer` valida 17 condições em G7 antes de promover a STABLE.
- Risco de scope creep em M2/M3 (tree+SHAP, painel, time series, causal) — mitigado por roadmap com datas explícitas.
- Manutenção de Constitution (G4), SDD templates (G5), KB domain (G6) — paralelos à evolução de laengine.

### Riscos
- **Risco 1:** Capability fica BASIC indefinidamente se Constitution (G4) não for entregue em 10 dias. Mitigação: tracking com deadline explícito + enforcement de `delivery-reviewer`.
- **Risco 2:** Tree models sem SHAP (violação do DA-2). Mitigação: DA-2 está em M2, junto com `compute_shap`. Tree training tool só entra com explainer.
- **Risco 3:** Handoff latade↔laecon operacional confuso. Mitigação: DA-3 vira Art. 4 da Constitution.
- **Risco 4:** Model registry/versionamento ausente quebra automação (AE-1). Mitigação: Constitution Art. 6 + workflow N8N de referência (AE-2).

---

## Implementação

### Já entregue (2026-06-04)
- `../laecon/` scaffold (pyproject, README, .gitignore, CONSTITUTION skeleton, kb/, skills/).
- `../laecon/mcp/server.py` com 9 tools (health + list_supported_operations funcionais, 7 stubs com `not_implemented_yet`).
- `registry/capabilities.yaml` com entry `laecon` (status=BASIC).
- `registry/needs-to-capabilities.yaml` com 6 novas rotas.
- `projects/_meta/capability-evolution/laecon.md` com tracking + 17 condições + roadmap M1-M3.
- `projects/_meta/laecon-capability/project.yaml` com meta-projeto + conditions mapping.
- `knowledge/data-conventions.md` com convenção `_commomdata`.
- Este ADR-002 (G8).

### Próximos passos
- **G4** (2026-06-14, +10d): Constitution.md completo (9 artigos).
- **G5** (2026-06-24, +20d): SDD templates (BRAINSTORM, DEFINE, PLAN, TASKS).
- **G6** (2026-07-04, +30d): KB domain mínimo (index + 1 pattern NPS driver analysis).
- **G7** (2026-07-04, +30d): `delivery-reviewer` valida 17 condições + `padroes-entrega.md` + promove a STABLE.
- **M2** (2026-08-04, +60d): Tree models com SHAP, cross-validation, painel FE/RE, model registry operacional.
- **M3** (2026-09-04, +90d): Time series (ARIMA, VAR), causal inference (PSM, IV, DiD).

---

## Referências

- Proposta LACOUNCIL: `cbe2d8ef-f65c-4d0e-8960-ea99527ab39f`
- Governança de capabilities: `e9cd6dd8-b1e4-4e5f-8216-5cd69a095d4f` (aprovada 2026-06-04, 100% SIM)
- ADR-001 (precedente de formato): `projects/_meta/adr/ADR-001-capability-governance.md`
- Tracking BASIC: `projects/_meta/capability-evolution/laecon.md`
- Meta-projeto: `projects/_meta/laecon-capability/project.yaml`
- Fontes de grounding:
  - Gujarati & Porter, *Basic Econometrics 5th ed* (2009), `E:\projects\_commomdata\`
  - Larson & Goungetas, *"Modeling the drivers of Net Promoter Score"* (Quirk's, 2013)
  - J. Scott Long, *Regression Models for Categorical and Limited Dependent Variables*
- Convenção `_commomdata`: `knowledge/data-conventions.md`
- Padrões de entrega: `knowledge/padroes-entrega.md`
