# Handoff de entrega — limpeza-casa

## onde_esta [OK]
  F:\projects\LAOS\projects\limpeza-casa
  ! contrato vive em LAOS; artefatos em artifacts/ (mirror)

## organizacao [OK]
  - artifacts
  - artifacts\limpeza
  - artifacts\limpeza\fase1-necessidades.html
  - artifacts\limpeza\fase2-produtos.html
  - artifacts\limpeza\fase3-dashboard.html
  - artifacts\limpeza\index.html
  - HANDOFF.md
  - project.yaml
  - README.md
  - spec
  - spec\spec.md
  ! estrutura do mirror LAOS (contract + artifacts)

## workflow [OK]
  laos run (pipeline de fases com auto-resume) -> laos verify

## como_utilizar [OK]
  - cd F:\projects\LAOS
  - uv run python -c "from laos.cli import main; main(['run','limpeza-casa','--force-new'])"
  - uv run python -c "from laos.cli import main; main(['verify','limpeza-casa'])"
  - python scripts/server.py start   # painel :7331

## banco [OK]
  F:\projects\LAOS\.laos\laos.duckdb
  ! DuckDB single-file; tabelas de projeto em runs/phases/deliverables

## site [OK]
  - http://127.0.0.1:7331 (painel LAOS)
  - http://localhost:3000 (Langfuse)

## garantir_rodando [OK]
  python scripts/limpeza_verify.py ou laos verify (botao verify no painel)

## ferramentas [OK]
  - runtime: Python 3.11 + uv
  - deps: fastapi, uvicorn, duckdb, jinja2, pyyaml, litellm
  - observabilidade: Langfuse :3000 + LiteLLM :4000 (OpenCode Go)
  - painel: FastAPI + HTMX (laos/web)

## clonavel [OK]
  rastreado no repo LAOS (5 arquivos); sem repo proprio (repo: vazio no project.yaml)
  ! para entregar: criar repo proprio + push dos artifacts

## health [OK]
  - painel_7331: True
  - langfuse_3000: True
  - litellm_4000: True

## dependencias [OK]
  Python >=3.11, uv, Docker (para Langfuse/LiteLLM)

## portas [OK]
  - painel: 7331
  - langfuse: 3000
  - litellm: 4000

## como_testar [OK]
  uv run python -m pytest tests/  (46/47 baseline)

## secrets [OK]
  chave OpenCode Go em ~/.local/share/opencode/auth.json (nunca commitada); .env gitignored

## clonar_instalar [OK]
  git clone github.com/laurentaf/laos && uv sync && python scripts/infra_helper.py up

## dev_prod [OK]
  hoje: tudo local (painel + observabilidade em localhost). Producao: deploy dos artifacts HTML em qualquer static host (os 4 arquivos sao autossuficientes, zero backend)

## estado [OK]
  - runs: [{'status': 'completed', 'count': 1, 'cost': 0.0044833600000000005, 'errors': 1}]
  - fases_total: 4
  - custo_total_usd: 0.0044833600000000005
  - tokens_total: 16512

## historico [OK]
  - 199a400 teste real: limpeza-casa executado de ponta a ponta com LLM

## autor [OK]
  - autor: Laurent
  - github: laurentaf
  - licenca: nao declarada no project.yaml

## readme_spec [OK]
  - README.md: True
  - spec/: True
  ! OK

## RESULTADO
  itens faltando: nenhum
  pronto para cliente: True