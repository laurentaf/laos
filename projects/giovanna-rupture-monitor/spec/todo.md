# TODO — Current Tasks

---

## Missão 0 — SDD Scaffold

- [x] Criar spec/constitution.md (Princípios, Scope, Non-goals)
- [x] Criar spec/todo.md (este arquivo)
- [x] Criar spec/adr/_template.md + spec/adr/README.md
- [x] Criar spec/harness/_template.md
- [x] Criar spec/specs/000-bootstrap/spec.md
- [x] Criar contract.md
- [x] Criar README.md
- [x] SDD boot-check passou (6ª dimensão)

---

## Fase 1 — Pipeline + Docker

- [x] Reescrever main.py para ler ShadowTraffic JSON (colunas: regiao, produto, categoria, estoque_atual, giro_diario, cobertura_dias, irc, risco, critico)
- [x] Agregação por região com 9 colunas no CSV de saída
- [x] Empty DataFrame guards em todos os estágios
- [x] Dockerfile + entrypoint.sh + docker-compose.yml
- [x] Dashboard HTML (fetch genérico de CSV)
- [x] Teste Docker end-to-end: `docker run -p 8000:8000 giovanna-rupture` → dashboard funcional

---

## Fase 2 — Revisão de entrega

- [x] delivery-reviewer validou contra padroes-entrega.md
- [x] Corrigir findings do reviewer (quality_rules.md, .env.example, requirements.txt, ADR index)

---

## Fase 3 — Validação final

- [ ] Re-dispatch delivery-reviewer para sign-off final
- [ ] Resolver findings do reviewer (se houver)
- [ ] Marcar projeto como delivered
