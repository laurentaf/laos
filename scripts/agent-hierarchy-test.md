# Agent Hierarchy Test — New Session Prompt

Copy this entire prompt into a new OpenCode session:

---

## Test agent routing

Run these 4 tests in order:

### Test 1: Data work (should route to data-architect)
Dispatch a data-architect to create a simple SQL model for a test table with columns: id, name, created_at.

### Test 2: Design work (should route to dashboard-designer)
Dispatch a dashboard-designer to create a simple wireframe for a dashboard with a title and a chart placeholder.

### Test 3: File ops (should be handled by orchestrator directly)
Read the file `knowledge/kitchen-hierarchy.md` and summarize the agent hierarchy section.

### Test 4: Research via MCP (should use context7 or exa)
Use context7 to look up how to create a simple DuckDB table.

Report what happened for each test. Which agent handled each task?
