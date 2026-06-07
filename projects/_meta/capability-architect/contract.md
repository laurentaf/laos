# Contract — capability-architect meta-project

**Project:** capability-architect
**Type:** meta-projeto
**Status:** BASIC → evolving to STABLE by 2026-07-04
**Proposal:** LACOUNCIL `2f42afe6-71d5-4ef8-a88a-1339d72ec501` (supermaioria, 4/4 SIM)

## Brief

Adicionar um subagente `capability-architect` à topologia do LAOS, com escopo estrito: implementar mudanças estruturais APROVADAS pelo Conselho via LACOUNCIL (novas capabilities, novas entradas de registry, novos workflows, novos knowledge entries, novos meta-projetos). NÃO propõe mudanças (papel do orchestrator+LACOUNCIL), NÃO faz trabalho de projeto (papel dos especialistas de domínio), NÃO vota no Conselho (separation of duties).

## Needs

- improvement
- governance
- investigation

## Capabilities used

- lacouncil (primary)
- context7 (library docs)
- exa (research)
- github (repo ops)

## Deliverables

1. Agent file `.opencode/agent/capability-architect.md` (R1–R5 + G1–G9)
2. Meta-artifacts (project.yaml, binding-conditions.md, capability-evolution.md, ADR-003)
3. Structural changes to LAOS (AGENTS.md, orchestrator.md)

## Repo

Self (meta-project lives in `projects/_meta/capability-architect/` within LAOS repo)

## Binding conditions

R1–R5 (structural restrictions) + G1–G9 (quality gates) = 14 conditions.
See `binding-conditions.md` for full details.
