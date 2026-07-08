# ADR-003: Wage Bands — Multi-Source Convergence Method

**Date:** 2026-06-21  
**Status:** Accepted  
**Author:** Laurent.io (orchestrator)

## Context

To position Laurent's salary expectations, we needed current wage data for AI Data Engineers. Three categories:

- BR CLT (with benefits)
- BR PJ (full remote)
- US/EU remote (hourly/contractor)

## Decision

Use **multi-source convergence** — collect from 5+ sources and triangulate rather than trusting any single source:

1. **Glassdoor** (R$8k-15k pleno) — self-reported salaries, biased toward lower end
2. **GeekHunter** (R$12k-22k pleno) — recruiter-reported, biased toward higher end  
3. **LinkedIn Salary** (R$10k-18k pleno) — mixed, moderate quality
4. **Levels.fyi** (US remote $70k-120k) — high quality for US
5. **Trampos + Indeed** — sanity check for BR market

Method: Take midpoint of overlapping ranges, add premium bracket for RAG/Agent/MLOps skills (based on market signal strength = more JDs requiring these skills at higher salary ranges).

## Alternatives considered

- Single source (Glassdoor-only) — known downward bias (respondents under-report)
- Blind survey of 20 contacts — small sample, not representative
- No salary data — leaves Laurent negotiating without anchor

## Consequences

- ✅ Anchored range for negotiations (R$15k-22k after 30d sprint)
- ✅ USD vs BRL conversion explicit for US remote comparisons
- ⚠️ BR premium bracket is inferred, not directly reported (newer role category)
- ⚠️ R$ exchange rate volatility affects US remote calculations
