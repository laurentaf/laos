# LAOS — Agent Operating System

**LAOS** é um runtime de orquestração de agentes + control plane de
entrega. Não é um framework de prompts — é um sistema que executa
projetos de ponta a ponta, audita custo real, verifica entregáveis e
expõe um painel para operar tudo.

> Este é o **LAOS canônico** (2.0). O antecessor — o LAOS de governança
> com Conselho/LACOUNCIL/WDL — foi congelado como legado.

## O que faz

| Capacidade | Onde |
|---|---|
| **Pipeline com auto-resume** | `laos run <proj>` — executa fases em ordem, kill mid-run continua do último step |
| **Custo real por fase** | cada fase reporta tokens/custo reais (via LiteLLM → OpenCode Go) |
| **Verifier (check garantido)** | `laos verify <proj>` — existe? carrega? passa teste? bate com spec? |
| **Observabilidade** | Langfuse (:3000) — traces LLM, custo, scores de verificação |
| **Painel portfolio** | `laos server` → http://127.0.0.1:7331 (board, dashboard executivo, detalhe) |
| **Console LLM-aware** | `/projects/<x>/console` — conversa com a LLM que conhece o estado real do projeto |
| **Handoff de entrega** | `laos handoff <proj>` — 20 itens que um dev cobra antes de entregar a cliente |

## Como rodar

```bash
uv sync
uv run python -c "from laos.cli import main; main(['doctor'])"   # saúde
uv run python -c "from laos.cli import main; main(['run','limpeza-casa'])"  # executa um projeto
uv run python -c "from laos.cli import main; main(['verify','limpeza-casa'])"  # verifica
uv run python -m pytest tests/     # suite do runtime (37 testes)
python scripts/server.py start     # painel :7331
```

## Observabilidade (stack Docker)

```bash
python scripts/infra_helper.py up     # Langfuse :3000 + LiteLLM :4000
python scripts/infra_helper.py health # probe dos serviços
```

Chave do LLM: lida de `~/.local/share/opencode/auth.json` (OpenCode Go)
— nunca commitada.

## Estrutura

```
laos/          package runtime (pipeline, verify, chat, web, check)
infra/         observability (Langfuse + LiteLLM)
registry/      capability catalog (routing de needs → capabilities)
projects/      deliverables (cada projeto = contrato + artifacts)
tests/         suite do runtime (37 testes)
scripts/       helpers (server, infra_helper)
```

## Prova de vida

Projeto "Gestão de Produtos de Limpeza" (4 fases, app HTML de 3 abas)
executado de ponta a ponta: **US$ 0,0045** de custo real, 4 artefatos,
verificação 4/4 OK, handoff 20/20 pronto para cliente.
