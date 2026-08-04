# WDL Gate Test Prompt

Use this prompt to test the WDL gate enforcement.

## Test 1: Agent dispatch (should be ALLOWED)

```
Dispatch a data-architect to create a simple SQL model for a test table.
```

**Expected:** WDL gate allows this (agent dispatch is always allowed)

## Test 2: MCP tool call (should be ALLOWED)

```
Use latade_execute_sql to run a SELECT * FROM test_table query.
```

**Expected:** WDL gate allows this (MCP tools are agentic use)

## Test 3: Shell call (should be BLOCKED)

```
Run this SQL directly: SELECT * FROM test_table
```

**Expected:** WDL gate blocks this (shell calls are non-agent)

## Test 4: Direct file write (should be BLOCKED)

```
Write a SQL file to artifacts/data/model.sql with a simple SELECT query.
```

**Expected:** WDL gate blocks this (direct file writes are non-agent)

## Test 5: Agent dispatch with WDL verdict (should be ALLOWED)

```
Dispatch a dashboard-designer to create a simple wireframe.
```

**Expected:** WDL gate allows this (agent dispatch is always allowed)

## Test 6: MCP tool for design (should be ALLOWED)

```
Use ladesign_create_project to create a new project called "test-project".
```

**Expected:** WDL gate allows this (MCP tools are agentic use)

## Test 7: Shell for git operations (should be BLOCKED)

```
Run git status to check the repository state.
```

**Expected:** WDL gate blocks this (shell calls are non-agent)

## Test 8: Agent for git operations (should be ALLOWED)

```
Dispatch a general agent to check git status.
```

**Expected:** WDL gate allows this (agent dispatch is always allowed)

## How to run

1. Copy one of the test prompts above
2. Paste it into OpenCode
3. Check the console output for WDL gate messages
4. Verify the behavior matches expectations

## Expected console output

For ALLOWED actions:
```
[LAOS WDL Gate] ALLOWED: <tool> is agentic use
```

For BLOCKED actions:
```
[LAOS WDL Gate] BLOCKED: <tool> bypasses agent system
```
