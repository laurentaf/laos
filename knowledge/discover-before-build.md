# Discover before build

Regra transversal: antes de **planejar** ou **executar** qualquer
coisa, **verifique o que já existe** no workspace e no sistema.

> **Anti-pattern 1 (planning):** agente sugere Java para um counter
> quando Python já está configurado com venv e dependências — ignora
> o toolchain existente.
>
> **Anti-pattern 2 (execution):** subagente que `pip install docker`
> quando Docker já está no PATH; que cria `.venv` novo quando o repo
> já tem um sincronizado; que baixa uma CLI que já está instalada.

---

## Fase 1 — Planning: descobrir o toolchain antes de sugerir stack

Antes de propor arquitetura, linguagem, ou framework, o agente
**inventaria o que já está disponível** no workspace e usa isso
como base para a sugestão.

### 1.1 Inventário obrigatório (checklist de planning)

**Este inventário não é opcional.** O orchestrator roda
`uv run python scripts/toolchain_inventory.py` no início de cada
ciclo de projeto. O output JSON é incluído no dispatch brief de
todo subagente. Subagentes que ignoram o inventário violam a regra.

O inventário mecanizado cobre estas verificações:

| # | O que inventariar | Como | O que revela |
|---|-------------------|------|-------------|
| 1 | **Runtimes no PATH** | `Get-Command python,java,node,go,rustc,cpp` (PS) | Quais linguagens já instaladas |
| 2 | **Gerenciadores de pacote** | `Get-Command uv,pip,npm,cargo,go` (PS) | Como instalar dependências |
| 3 | **Venvs existentes** | `Get-ChildItem E:\projects\*\\.venv -Directory` | Projetos Python já configurados |
| 4 | **Containers rodando** | `docker ps --format "{{.Names}}"` | Serviços já ativos (n8n, DBs) |
| 5 | **pyproject.toml / package.json** | `Get-ChildItem E:\projects\*\pyproject.toml` | Projetos com deps declaradas |
| 6 | **Repo do projeto** | `Get-ChildItem <project-dir>` | Se já tem código, libs, ou toolchain |

### 1.2 Regra de prioridade na sugestão

O agente segue esta hierarquia ao sugerir stack:

```
1. Já existe no projeto?       → USAR (não sugerir outra coisa)
2. Já existe no workspace?    → PREFERIR (evitar nova instalação)
3. Já existe no PATH?         → PREFERIR (evitar setup)
4. Nada existe?               → SUGERIR o mais simples (Python > Java > C++)
```

**Exemplo concreto:**

```
Usuário: "Quero fazer um counter app"
Agente inventaria:
  - python no PATH ✅
  - uv no PATH ✅
  - venv do projeto já existe ✅
  - Nenhum JDK encontrado ❌
  - Nenhum Rust/Cargo ❌

Decisão: Python (já configurado, zero setup novo)
Não sugerir: Java, C++, Go (requerem instalação nova)
```

### 1.3 Quando sugerir algo DIFERENTE do que já existe

Só é justificado sugerir um runtime novo quando:

1. **O existente não atende o requisito técnico** — ex: precisa de
   performance de sistema e Python é lento demais para o caso.
2. **O usuário pediu explicitamente** — ex: "quero aprender Rust".
3. **A dependência só existe em outro ecossistema** — ex: precisa de
   uma lib Java sem equivalente Python.

Nesses casos, o agente:
- Documenta **por que** o toolchain existente não serve
- Sugere a alternativa com justificativa técnica
- Oferece o caminho de menor resistência (ex: `winget install`)

### 1.4 Anti-patterns de planning

| Anti-pattern | Por que é ruim | Correção |
|-------------|----------------|----------|
| Sugerir Java para app simples quando Python já está no PATH | Setup desnecessário, conflito de ecossistemas | Inventariar runtimes primeiro |
| Sugerir "vamos usar Node" sem checar se Node já existe | Pode não estar instalado, vai precisar de setup | `Get-Command node` antes |
| Ignorar venv existente e propor criar novo | Duplica ambientes, confunde dependências | Checar `.venv` no projeto primeiro |
| Sugerir C++ para protótipo rápido | Overkill, tempo de compilação desnecessário | Preferir linguagem interpretada disponível |
| Não checar containers antes de sugerir "vamos subir um DB" | DB pode já estar rodando via Docker | `docker ps` antes |

---

## Fase 2 — Execution: não construir o que já existe

Antes de criar, instalar ou configurar qualquer coisa em runtime,
**verifique se já existe** no workspace ou no sistema.

---

## 1. Hierarquia de descoberta (ordem obrigatória)

Antes de qualquer ação de setup, o agente segue esta cascata:

| # | O que verificar | Como | Exemplo |
|---|----------------|------|---------|
| 1 | **Tool já está no PATH** | `Get-Command <tool>` (PS) ou `which <tool>` (unix) | `Get-Command docker` → já instalado, usar direto |
| 2 | **Tool já está no sistema** | Checar paths conhecidos: `C:\Program Files\`, `E:\tools\`, `E:\projects\**\.venv\` | Docker Desktop em `C:\Program Files\Docker\` |
| 3 | **Venv já existe no repo** | `Test-Path <repo>\.venv` ou `ls <repo>/.venv/bin/python` | `E:\projects\latade\.venv` já sincronizado |
| 4 | **Container já rodando** | `docker ps --format "{{.Names}}"` | n8n já rodando como container |
| 5 | **Dependência já instalada** | `pip list \| findstr <pkg>` dentro do venv existente | scikit-learn já no venv do laecon |
| 6 | **Só então: instalar/criar** | Comando apropriado | `uv sync` ou `pip install` |

**Nunca pular direto para o passo 6.** A cascata é obrigatória.

---

## 2. Regras por categoria de tool

### Runtime / venv

- **Nunca criar `.venv` manualmente** se `uv` está disponível.
  `uv sync` detecta `.venv` existente e só re-sincroniza.
- **Se o repo já tem `.venv`**, usar `uv run python` (herda o venv
  automaticamente). Não criar novo.
- **Se múltiplos venvs existem** no workspace, o boot check já
  valida quais estão sincronizados. Confiar no boot check.

### Container / Docker

- **Checar `docker ps`** antes de `docker run`. Se o container
  já existe (parado ou rodando), reutilizar.
- **Checar `docker images`** antes de `docker pull`. Se a imagem
  já existe, não baixar novamente.
- **Preferir `docker compose`** quando o projeto tem
  `docker-compose.yaml` — não orquestrar containers manualmente.

### CLI tools

- **Checar PATH primeiro**: `Get-Command <tool>` (PowerShell).
  Se retorna resultado, usar direto.
- **Checar versão**: `<tool> --version` para confirmar que a
  versão é compatível com o necessário.
- **Se não existe**: instalar via método canônico do tool
  (`uv`, `npm -g`, `pip install`, `winget install`).

### Dados / arquivos

- **Checar se arquivo já existe** antes de gerar/baixar:
  `Test-Path <path>`.
- **Se existe e está completo**: não regenerar.
- **Se existe mas está desatualizado**: atualizar (diff primeiro).
- **Se não existe**: criar/baixar.

---

## 4. Onde se aplica

| Agente | Planning (Fase 1) | Execution (Fase 2) |
|--------|-------------------|---------------------|
| `orchestrator` | Inventariar runtimes antes de sugerir arquitetura de projeto | Verificar MCP server já rodando antes de spawn; checar scaffold antes de Missão 0 |
| `data-architect` | Verificar se Python/scikit-learn já disponível antes de propor stack ML | Verificar se `.venv` do latade existe antes de `uv sync`; checar se DuckDB já tem tabela |
| `dashboard-designer` | Verificar se Node/pnpm já disponíveis antes de propor framework | Verificar se LADESIGN daemon já rodando; checar se DESIGN.md já existe |
| `automation-engineer` | Verificar se n8n já disponível (Docker ou local) antes de propor automação | Verificar se container já rodando; checar se workflow já existe |
| `capability-architect` | Verificar se capability repo já existe antes de propor nova capability | Verificar se registry entry já existe antes de adicionar |
| `delivery-reviewer` | (read-only — sempre descobre primeiro, nunca propõe) | (read-only — sempre descobre primeiro, nunca cria) |

---

## 4. Integração com boot check

O `subagent_boot_check.py` já valida a dimensão 1 (venv) e 2
(daemon). Esta convenção **extende** o princípio para além do
boot check — cobre tools, CLIs, containers, e arquivos que o
boot check não monitora.

**Fluxo completo:**

```
orchestrator roda boot check
  → venv OK? daemon OK? MCP OK? paths OK? env OK?
    → dispatch subagente
      → subagente: "preciso de Docker"
        → Checa: Get-Command docker
          → Existe? → USA (passo 1 da cascata)
          → Não existe? → Reporta ao orchestrator
```

---

## 6. Anti-patterns conhecidos

### Planning (Fase 1)

| Anti-pattern | Por que é ruim | Correção |
|-------------|----------------|----------|
| Sugerir Java para app simples quando Python já está no PATH | Setup desnecessário, conflito de ecossistemas | Inventariar runtimes primeiro |
| Sugerir "vamos usar Node" sem checar se Node já existe | Pode não estar instalado, vai precisar de setup | `Get-Command node` antes |
| Ignorar venv existente e propor criar novo | Duplica ambientes, confunde dependências | Checar `.venv` no projeto primeiro |
| Sugerir C++ para protótipo rápido | Overkill, tempo de compilação desnecessário | Preferir linguagem interpretada disponível |
| Não checar containers antes de sugerir "vamos subir um DB" | DB pode já estar rodando via Docker | `docker ps` antes |

### Execution (Fase 2)

| Anti-pattern | Por que é ruim | Correção |
|-------------|----------------|----------|
| `pip install X` sem checar se X já está no venv | Duplo install, possível conflito de versão | `pip list \| findstr X` primeiro |
| `docker pull` sem checar `docker images` | Download desnecessário, gasta bandwidth | `docker images \| findstr X` primeiro |
| Criar `.venv` com `python -m venv` quando `uv` gerencia | Dois systems de venv, confusão | Sempre `uv sync` |
| `docker run` sem checar `docker ps` | Container duplicado, porta em conflito | `docker ps \| findstr X` primeiro |
| Gerar arquivo que já existe em `artifacts/` | Overwrite de trabalho válido | `Test-Path` antes de escrever |
| Instalar CLI globalmente quando `npx -y` resolve | Polui o PATH global | `npx -y <tool>` para uso pontual |

---

## 7. Exceções (quando NÃO aplicar)

- **Testes**: um teste pode querer criar um ambiente isolado
  de propósito (fixtures, setUp). Isso é diferente de "esqueceu
  que já existia".
- **CI/CD**: pipelines frequentemente começam do zero
  (clean room). Esta regra é para dev local e subagentes.
- **Explicitamente solicitado**: o usuário pede "crie um venv
  novo" ou "quero usar Rust" — aí faz. A regra é sobre o agente
  decidir por conta própria, não sobre contrariar ordem direta.
- **Performance crítica**: quando o caso de uso exige um runtime
  específico por razão técnica (ex: C++ para game engine,
  Rust para sistema), independentemente do que já está disponível.
