# ADR-001: Tools Gaps Methodology — Frequency Extraction from Job Descriptions

**Date:** 2026-06-21  
**Status:** Accepted  
**Author:** Laurent.io (orchestrator)

## Context

As part of the career audit, we needed to identify which tools and skills Laurent is missing compared to the AI Data Engineer market. Two approaches were considered:

- **A. Subjective gap analysis** — author looks at CV and "feels" what's missing
- **B. Frequency extraction** — sample real job descriptions, extract required skills, score by frequency, cross-reference with CV

## Decision

Adopt **B. Frequency extraction** using:

1. **10+ real job descriptions** sourced from jobdescription.org, decipheru.com, dev.to, linkedin.com
2. **Simple frequency counter** — if a skill appears in ≥ 2 JDs, it's included
3. **3-zone classification:** Covered / Partial / Absent
4. **Priority scoring** = Market Frequency × Gap Severity factor

## Alternatives considered

- Using LinkedIn Talent Insights (paid, not available)
- ML-based skills gap analysis (overkill for single audit; would require labeled training data)
- Hiring a recruiter to review (expensive, not reproducible)

## Consequences

- ✅ **Reproducible** — anyone could run the same method on the same JDs
- ✅ **Actionable** — each gap has a "30d action" column
- ⚠️ **Sample bias** — JDs are a convenience sample, not randomized
- ⚠️ **JD ≠ real hire** — some JDs are "wish lists," not actual requirements
