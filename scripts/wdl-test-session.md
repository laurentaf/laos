# WDL Gate Test — New Session Prompt

Copy this entire prompt into a new OpenCode session:

---

## Test the WDL gate

Run these 3 tests in order:

### Test 1: Agent dispatch (should work)
Dispatch a general agent to run `git status` and report the repository state.

### Test 2: MCP tool call (should work)
Use `latade_health` to check if the LATADE MCP server is running.

### Test 3: Shell call (should be blocked)
Run `echo "hello"` via bash.

Report what happened for each test. Did the WDL gate block or allow each one?
