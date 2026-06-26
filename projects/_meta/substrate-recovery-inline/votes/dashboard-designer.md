# Conselho vote — dashboard-designer (ADR-014)
**date:** 2026-06-24
**voting_member:** dashboard-designer
**vote:** SIM
**confidence:** HIGH
**rationale:** Edit #1 aligns `opencode.jsonc` with what `registry/capabilities.yaml` already declares (Python STABLE), restoring the canonical `ladesign` entry-point my charter was designed against; Edit #2 correctly moves `ladesign` back into `mcp_primary` (Python MCP has `health()` for boot Check 3) and drops the now-spurious `daemon: ["ladesign"]` row. Edit #4's lacareerops registry entry stays inside its own domain (career.evaluation / cv-pdf / portal-scan / batch / tracker / sync) and crosses no visual-design boundary — no dashboard, deck, wireframe, or design-system surface is touched, so the ladesign contract is unaffected. Downstream projects can now dispatch `dashboard-designer` against a substrate whose entry-point story, registry status, and boot-check semantics are mutually consistent.
**blockers:** none
