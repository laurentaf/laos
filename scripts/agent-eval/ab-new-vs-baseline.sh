#!/usr/bin/env bash
# scripts/agent-eval/ab-new-vs-baseline.sh
# Compara DUAS VERSOES do mesmo fluxo (não com vs sem)
# Adaptação de: colbymchenry/codegraph/scripts/agent-eval/ab-new-vs-baseline.sh
#
# Uso: MODEL=sonnet EFFORT=high RUNS=4 bash scripts/agent-eval/ab-new-vs-baseline.sh \
#       <repo-path> "<task-prompt>" [baseline-ref]
#
# baseline-ref: tag/commit da versão baseline (default: HEAD~1)
#
# Pass criteria (mediana de n>=2 runs):
#   - Arm B (new) usa menos tool calls que Arm A (baseline)
#   - Arm B Read/Grep <= Arm A (ideal: 0)
#   - Arm B wall-clock <= Arm A wall-clock
#   - Sem regressão em repo de controle

set -euo pipefail

REPO_PATH="${1:-}"
PROMPT="${2:-}"
BASELINE_REF="${3:-HEAD~1}"
MODEL="${MODEL:-sonnet}"
EFFORT="${EFFORT:-high}"
RUNS="${RUNS:-2}"

if [[ -z "$REPO_PATH" || -z "$PROMPT" ]]; then
  echo "Usage: $0 <repo-path> \"<task-prompt>\" [baseline-ref]"
  exit 1
fi

REPO_NAME=$(basename "$REPO_PATH")
OUT_DIR="artifacts/reviews"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p "$OUT_DIR"

echo "=== ab-new-vs-baseline.sh — LAOS Version Compare ==="
echo "  Repo:         $REPO_NAME"
echo "  Baseline:     $BASELINE_REF"
echo "  Model:        $MODEL / $EFFORT"
echo "  Runs:         $RUNS per arm"
echo "  Prompt:       ${PROMPT:0:60}..."
echo ""

# ── Pre-warm: garantir que daemon está rodando antes do eval ─────────────────
# (do CodeGraph: "pre-warm a persistent daemon to skip re-exec on cold start")
echo "Pre-warming LAOS MCP daemon..."
claude --info > /dev/null 2>&1 &
sleep 2
echo "  Daemon warmed."

# ── Arm A: Baseline (old version) ───────────────────────────────────────────
echo ""
echo "─── Arm A: Baseline ($BASELINE_REF) ───"
cd "$REPO_PATH"
git checkout "$BASELINE_REF" --quiet 2>/dev/null || true

for i in $(seq 1 "$RUNS"); do
  RUN_ID="run_${TIMESTAMP}_A_${i}"
  echo "  Run $i/$RUNS (ID: $RUN_ID)"

  START=$(date +%s.%N)
  RESULT=$(claude -p "$PROMPT" \
    --model "$MODEL" \
    --max-turns 50 \
    --output-format json 2>/dev/null || echo "{}")
  END=$(date +%s.%N)
  DURATION=$(echo "$END - $START" | bc)

  echo "{\"run_id\":\"$RUN_ID\",\"arm\":\"A\",\"duration\":$DURATION,\"result\":$RESULT}" \
    > "$OUT_DIR/${RUN_ID}.json"
  echo "    → ${DURATION}s"
done

# ── Arm B: New (current version) ─────────────────────────────────────────────
echo ""
echo "─── Arm B: New (current) ───"
git checkout HEAD --quiet

for i in $(seq 1 "$RUNS"); do
  RUN_ID="run_${TIMESTAMP}_B_${i}"
  echo "  Run $i/$RUNS (ID: $RUN_ID)"

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

# ── Aggregate ────────────────────────────────────────────────────────────────
echo ""
echo "─── Results ───"
node scripts/agent-eval/parse-run.mjs "$OUT_DIR" "$TIMESTAMP" "$RUNS"

echo ""
echo "=== Done ==="