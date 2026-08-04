#!/usr/bin/env bash
# scripts/agent-eval/run-all.sh
# A/B eval: WITH vs WITHOUT uma mudança estrutural em LAOS
# Adaptação de: colbymchenry/codegraph/scripts/agent-eval/run-all.sh
#
# Usage: bash scripts/agent-eval/run-all.sh <repo-path> "<task-prompt>" [model] [effort] [runs]
# Example: MODEL=sonnet EFFORT=high RUNS=4 bash scripts/agent-eval/run-all.sh \
#           E:/projects/meu-projeto "Quero criar um dashboard" sonnet high 4
#
# Output: artifacts/reviews/<run-id>.md por run
#   run-id format: run_<timestamp>_<arm>_<n>
#
# Pass criteria (mediana de n>=2 runs):
#   - Arm B (with) usa menos tool calls que Arm A (without)
#   - Arm B Read/Grep <= Arm A Read/Grep
#   - Arm B wall-clock <= Arm A wall-clock

set -euo pipefail

# ── Defaults ──────────────────────────────────────────────────────────────
REPO_PATH="${1:-}"
PROMPT="${2:-}"
MODEL="${MODEL:-sonnet}"
EFFORT="${EFFORT:-high}"
RUNS="${RUNS:-2}"

if [[ -z "$REPO_PATH" || -z "$PROMPT" ]]; then
  echo "Usage: $0 <repo-path> \"<task-prompt>\" [model] [effort] [runs]"
  echo "  model  (default: sonnet)"
  echo "  effort (default: high)"
  echo "  runs   (default: 2)"
  exit 1
fi

REPO_NAME=$(basename "$REPO_PATH")
OUT_DIR="artifacts/reviews"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p "$OUT_DIR"

echo "=== run-all.sh — LAOS Structural Eval ==="
echo "  Repo:     $REPO_NAME"
echo "  Model:    $MODEL / $EFFORT"
echo "  Runs:     $RUNS per arm"
echo "  Prompt:   ${PROMPT:0:60}..."
echo ""

# ── Arm A: WITHOUT (baseline) ───────────────────────────────────────────────
echo "─── Arm A: WITHOUT (baseline) ───"
ARM_A_RUNS=()
for i in $(seq 1 "$RUNS"); do
  RUN_ID="run_${TIMESTAMP}_A_${i}"
  echo "  Run $i/$RUNS (ID: $RUN_ID)"

  # Desabilita capability sendo testada via env var (mudar conforme capability)
  # Exemplo: CODEGRAPH_ENABLED=0 para testar sem codegraph
  # Para eval de WDL: WDL_ENABLED=0
  START=$(date +%s.%N)

  # Executa o eval via orchestrator (claude headless ou similar)
  # Substituir pela chamada real do eval harness de LAOS
  # Formato output: JSON com {duration, tool_calls, read_count, grep_count, tokens}
  RESULT=$(claude -p "$PROMPT" \
    --model "$MODEL" \
    --max-turns 50 \
    --output-format json 2>/dev/null || echo "{}")

  END=$(date +%s.%N)
  DURATION=$(echo "$END - $START" | bc)

  # Parse do resultado (simplificado — adaptar para formato real)
  echo "{\"run_id\":\"$RUN_ID\",\"arm\":\"A\",\"duration\":$DURATION,\"result\":$RESULT}" \
    > "$OUT_DIR/${RUN_ID}.json"

  echo "    → ${DURATION}s"
done

# ── Arm B: WITH (new) ────────────────────────────────────────────────────────
echo ""
echo "─── Arm B: WITH (change applied) ───"
ARM_B_RUNS=()
for i in $(seq 1 "$RUNS"); do
  RUN_ID="run_${TIMESTAMP}_B_${i}"
  echo "  Run $i/$RUNS (ID: $RUN_ID)"

  # Habilita capability (WDL, novo registry, etc.)
  # Exemplo: CODEGRAPH_ENABLED=1
  START=$(date +%s.%N)

  RESULT=$(claude -p "$PROMPT" \
    --model "$MODEL" \
    --max-turns 50 \
    --output-format json 2>/dev/null || echo "{}")

  END=$(date +%s.%N)
  DURATION=$(echo "$END - $START" | bc)

  echo "{\"run_id\":\"$RUN_ID\",\"arm\":\"B\",\"duration\":$DURATION,\"result\":$RESULT}" \
    > "$OUT_DIR/${RUN_ID}.json"

  echo "    → ${DURATION}s"
done

# ── Aggregate + compare ──────────────────────────────────────────────────────
echo ""
echo "─── Results ───"
node scripts/agent-eval/parse-run.mjs "$OUT_DIR" "$TIMESTAMP" "$RUNS"

echo ""
echo "=== Done. Results in $OUT_DIR/ ==="
echo "Review each run: ls $OUT_DIR/run_${TIMESTAMP}_*.json"