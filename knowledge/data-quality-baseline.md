# Baseline DQ checks — universal data quality checks for every LAOS data project

**Status:** vigente (origem: proposta LACOUNCIL `d6c79133-51c1-4948-ab8a-60589b0a5883`,
maioria 4/4, 2026-06-09)

**Cross-references:**
- `knowledge/padroes-entrega.md` — P1 item que operacionaliza esta página
- `knowledge/data-fabrication-policy.md` — proveniência de dados (complementar, não substitui)
- `knowledge/data-conventions.md` — paths e formatos compartilhados

---

## 1. Princípio

> **Todo projeto de dados LAOS implementa 6 checks de DQ no primeiro estágio que toca dados.**
> Não é necessário que o briefing os mencione explicitamente — são checks que qualquer
> practitioner de dados faz por padrão, como guardar contra DataFrame vazio (que já é P0).

O episódio que originou esta regra: no projeto `abandono-academico-casa-grande`,
4 desses checks foram documentados como TODOs desde a Fase 1 (DQ-02 a DQ-05 em
`artifacts/dq/checks.md`). Na Fase 3, a DataMission exigiu preprocessamento que
limpa colunas nulas — exatamente o que DQ-05 cobria. Se tivessem sido implementados
desde o início, a Fase 3 seria incremental em vez de corretiva.

**Anti-pattern fechado:** "Defer DQ checks como TODO; implementar depois."
Depois nunca chega. O próximo estágio sempre depende do check que foi adiado.

---

## 2. Os 6 checks baseline

| # | Check | O que faz | Sem ele | Severidade default |
|---|-------|-----------|---------|-------------------|
| 1 | **Null profiling** | Contar e reportar nulls por coluna ANTES de qualquer transformação | Downstream quebra silenciosamente (mean de NaN, groupby drop) | MEDIUM |
| 2 | **Column existence** | Verificar que todas as colunas esperadas estão presentes (assert explícito, não KeyError implícito) | Schema drift invisível até a pipeline falhar em produção | MEDIUM |
| 3 | **Type validation** | Checar dtypes das colunas contra o schema declarado em `artifacts/data/model.md` | Pipeline falha tarde (LabelEncoder em int, sklearn em string) | MEDIUM |
| 4 | **Duplicate detection** | Contar duplicatas na grain key (PK declarada em model.md) | Grain errado, agregações infladas, KPIs dobrados | MEDIUM |
| 5 | **Target balance** | Logar distribuição do target antes do treino (`value_counts` + proporção) | Treinar em 90/10 sem saber; class_weight compensa, mas não informa | MEDIUM |
| 6 | **Range/bounds check** | Validar que colunas numéricas estão dentro do range esperado (ex: GPA 0-4, taxa 0-100) | Dados impossíveis propagam (GPA 999, idade negativa) | MEDIUM |

---

## 3. Severidade: MEDIUM default → HIGH quando dependente

Cada check é **MEDIUM** por default — não bloqueia a entrega, mas deve ser
implementado (ou explicitamente justificado como N/A).

Um check é promovido para **HIGH** quando o estágio seguinte depende daquele
check. Exemplos:

| Check | Quando vira HIGH | Exemplo |
|-------|-------------------|---------|
| Null profiling | Próximo estágio faz limpeza de nulls | DataMission Fase 3 exige "limpa colunas nulas" |
| Target balance | Próximo estágio treina modelo | Qualquer projeto com `ml` ou `predictive-modeling` em needs |
| Column existence | Próximo estágio seleciona features | Pipeline que filtra colunas por lista |
| Range/bounds | Próximo estágio normaliza ou clipa | Feature engineering com StandardScaler |

**Enforcement:** o delivery-reviewer verifica que os 6 checks estão implementados
(ou justificados N/A). Se um check é HIGH e não está implementado → P0 violation.
Se é MEDIUM e não está → advisory (P2).

---

## 4. Implementação

### 4.1. Formato

Não é framework pesado. Cada check é uma função simples em `main.py` ou helper:

```python
def check_nulls(df: pd.DataFrame) -> dict:
    """Check 1: Null profiling."""
    nulls = df.isnull().sum()
    nulls_pct = (nulls / len(df) * 100).round(2)
    result = nulls[nulls > 0].to_dict()
    if result:
        print(f"[DQ-01] Nulls encontrados: {result} ({nulls_pct[result.index].to_dict()}%)")
    else:
        print("[DQ-01] Nenhum null encontrado.")
    return result

def check_columns(df: pd.DataFrame, expected: list[str]) -> bool:
    """Check 2: Column existence."""
    missing = [c for c in expected if c not in df.columns]
    if missing:
        print(f"[DQ-02] Colunas ausentes: {missing}", file=sys.stderr)
        return False
    print(f"[DQ-02] Todas as {len(expected)} colunas presentes.")
    return True

def check_types(df: pd.DataFrame, schema: dict) -> list[str]:
    """Check 3: Type validation. schema = {col: expected_dtype}."""
    mismatches = []
    for col, expected_dtype in schema.items():
        if col in df.columns and str(df[col].dtype) != expected_dtype:
            mismatches.append(f"{col}: expected {expected_dtype}, got {df[col].dtype}")
    if mismatches:
        print(f"[DQ-03] Type mismatches: {mismatches}")
    else:
        print("[DQ-03] Todos os tipos conferem com o schema.")
    return mismatches

def check_duplicates(df: pd.DataFrame, key_cols: list[str]) -> int:
    """Check 4: Duplicate detection na grain key."""
    dupes = df.duplicated(subset=key_cols).sum()
    print(f"[DQ-04] Duplicatas na PK {key_cols}: {dupes}")
    return dupes

def check_target_balance(df: pd.DataFrame, target_col: str) -> dict:
    """Check 5: Target balance."""
    counts = df[target_col].value_counts()
    pct = (counts / len(df) * 100).round(2).to_dict()
    print(f"[DQ-05] Target balance: {counts.to_dict()} ({pct}%)")
    return {"counts": counts.to_dict(), "pct": pct}

def check_bounds(df: pd.DataFrame, bounds: dict) -> list[str]:
    """Check 6: Range/bounds. bounds = {col: (min, max)}."""
    violations = []
    for col, (lo, hi) in bounds.items():
        if col in df.columns:
            oob = ((df[col] < lo) | (df[col] > hi)).sum()
            if oob > 0:
                violations.append(f"{col}: {oob} valores fora de [{lo}, {hi}]")
    if violations:
        print(f"[DQ-06] Bounds violations: {violations}")
    else:
        print("[DQ-06] Todos os valores dentro dos bounds esperados.")
    return violations
```

### 4.2. Onde chamar

No pipeline principal, **após** `fetch_dataset` e **antes** de qualquer
transformação (preprocess_data, train_model):

```
fetch_dataset → [DQ checks] → preprocess_data → train_model
```

### 4.3. Quando N/A

Um check pode ser justificado como N/A no `artifacts/dq/checks.md`:

| Check | Quando N/A |
|-------|-----------|
| Target balance | Projeto não tem modelo preditivo (ex: dashboard-only) |
| Duplicate detection | Dataset não tem PK declarada (ex: event stream sem dedup) |
| Range/bounds | Colunas numéricas não têm range conhecido a priori |

A justificativa N/A é explícita no `checks.md` — não é omitida.

---

## 5. Relação com padroes-entrega.md

Estes checks são P1 em `padroes-entrega.md` (adicionado por esta proposta):

> **P1:** Para cada artefato de dados, os 6 DQ baseline checks (null profiling,
> column existence, type validation, duplicate detection, target balance,
> range/bounds) foram implementados ou justificados N/A em `artifacts/dq/checks.md`.
> Bloqueia se a entrega for para cliente externo.

Isso complementa o P0 existente ("guard para DataFrame vazio") — que é o
check de emergência. Os 6 checks baseline são a versão proativa.

---

## 6. Cross-references

- `knowledge/padroes-entrega.md` P1 — enforcement no delivery-reviewer
- `knowledge/data-fabrication-policy.md` — proveniência (complementar)
- `knowledge/data-conventions.md` — paths e formatos
- `artifacts/data/model.md` (por projeto) — schema e grain key usados pelos checks 2, 3, 4, 6
- `artifacts/dq/checks.md` (por projeto) — onde os checks são documentados

---

## 7. Histórico

| Data | Evento | Detalhe |
|------|--------|---------|
| 2026-06-09 | Proposta LACOUNCIL | `d6c79133` — maioria 4/4 SIM |
| 2026-06-09 | Implementação | Knowledge entry + padroes-entrega P1 addition |
