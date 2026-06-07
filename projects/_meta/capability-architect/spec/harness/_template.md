# HARNESS-NNN: {Name}

## Status
RASCUNHO

## Objective
Prove scaffold produces correct structure.

## Levels
| Level | Metric | Tolerance | Frequency |
|------:|--------|----------:|-----------|
| 1 | boot_check exit | 0 | every dispatch |
| 2 | file existence | 100% | every dispatch |
| 3 | content size | >= min chars | weekly |

## Treatment
| Status | Action |
|--------|--------|
| OK | Proceed |
| ALERT | Investigate |
| CRITICAL | Block |
