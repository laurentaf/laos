# LACAREEROPS — Constitution

**Status:** BASIC
**Date:** 2026-06-13
**Owner:** github.com/laurentaf/lacareerops (repo privado)

---

## Art. 1 — Purpose

LACAREEROPS é a capability do LAOS para job search optimization. Oferece:
- Avaliação estruturada de ofertas (salary, remote, equity, benefits)
- Geração de CVs ATS-optimized em PDF
- Escaneamento de portais de emprego
- Processamento em batch
- Tracking de candidaturas

A capability é thin-wrapper: o engine real é o career-ops CLI (Node.js). O MCP server apenas expõe ferramentas para o LAOS orquestrar.

---

## Art. 2 — Privacy by Design

LACAREEROPS é **PRIVADO** por design. Dados de carreira (CV, salary history, target companies, career trajectory) são sensíveis.

- O repo github.com/laurentaf/lacareerops é **PRIVADO**
- Cada usuário configura seus próprios `config/cv.md` e `config/profile.yml`
- Não há external API calls que transmitam dados do usuário
- `.gitignore` cobre `.env`, `*.log`, `__pycache__`, `.venv`, credenciais

---

## Art. 3 — MCP Tools Contract

### G1 Observability (mandatory from day 1)

| Tool | Signature | Description |
|------|-----------|-------------|
| `health` | `() → {status, version}` | Liveness probe |
| `list_supported_operations` | `() → [{id, name, description}]` | Typed catalog |
| `career_ops_evaluate` | `(job_description: str) → EvaluationReport` | Avalia oferta |
| `career_ops_generate_pdf` | `(cv_text: str, job_description: str) → PDFPath` | Gera CV PDF |
| `career_ops_scan_portals` | `(companies: str[]) → JobOpening[]` | Escaneia portais |
| `career_ops_batch_process` | `(urls: str[]) → BatchResult[]` | Batch processing |
| `career_ops_tracker_list` | `() → TrackerPipeline` | Lista pipeline |

### Error Handling (P0-21)

Condições esperadas/recuperáveis (arquivo não encontrado, perfil não configurado) retornam `{status: ok, guidance: ...}` — **não** `isError: true`. `isError` é reservado para "pare de tentar" (recusa de segurança, malfuncionamento genuíno).

---

## Art. 4 — Dependencies

| Dependency | Version | Use |
|------------|---------|-----|
| Node.js | ≥18 | career-ops CLI runtime |
| career-ops | latest | Core engine (npm install -g career-ops) |
| Python | ≥3.11 | MCP server wrapper |
| mcp | latest | MCP protocol |
| PyYAML | ≥6.0 | config/profile parsing |

---

## Art. 5 — Inputs

- `config/profile.yml` — experience, skills, target_roles, salary_expectation
- `config/cv.md` — CV markdown (ATS-optimized structure)
- `job_description` — free text job description (passed per-call)

**Segurança:** Nenhum dado é hardcoded. Inputs vêm do usuário ou de parâmetros de chamada.

---

## Art. 6 — Outputs

| Tool | Output |
|------|--------|
| `career_ops_evaluate` | JSON: {score, breakdown: {salary, remote, equity, benefits}, market_benchmark, recommendation} |
| `career_ops_generate_pdf` | Path string (local filesystem) |
| `career_ops_scan_portals` | JSON array of {company, role, url, posted_date, match_score} |
| `career_ops_batch_process` | JSON array of results |
| `career_ops_tracker_list` | JSON: {total, applied, interviewing, offered, rejected} |

---

## Art. 7 — Non-Goals

- Auto-submission de candidaturas (semanal.STABLE)
- Integração com ATS externos (Workday, Greenhouse) — extensão futura
- Armazenamento centralizado — repo é local por design
- ML/IA generativa — career-ops usa regras, não LLMs

---

## Art. 8 — Handoff Boundaries

### Quando usar lacareerops
- "avaliar uma oferta de emprego"
- "gerar um CV ATS-optimized para esta vaga"
- "escanear vagas no LinkedIn/Indeed para empresa X"
- "processar em batch 20 URLs de vagas"
- "ver meu pipeline de candidaturas atual"

### Quando NÃO usar lacareerops
- "criar um dashboard de analytics de carreira" → **ladesign** (visualização)
- "armazenar histórico de avaliações no DuckDB" → **latade** (data engineering)
- "automatizar envio semanal de alertas" → **lan8n** (workflow automation)

### Sinais de subutilização
- Usuário manualmente avaliando ofertas quando `career_ops_evaluate` existir
- CV em Word quando `career_ops_generate_pdf` pode gerar ATS-optimized

### Sinais de sobrecarga
- `career_ops_*` tools lentas demais → career-ops CLI desatualizado
- PDF gerado com formatação quebrada → Playwright desatualizado

---

(End of file — 95 lines)