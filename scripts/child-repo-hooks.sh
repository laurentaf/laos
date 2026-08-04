#!/usr/bin/env bash
# child-repo-hooks.sh — LAOS child repo git hooks
# Provenance: Oracle 2Care §Hooks (adapted, Laurent)
# LACOUNCIL 3473c12b (aprovada 4/4 SIM, 2026-06-12)
# Escopo: open/synthetic data (sem LGPD, sem catalog auto-fix)

set -euo pipefail

HOOKS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR=".laos/hooks/logs"
TIMESTAMP="$(date -u +%Y-%m-%dT%H%M%S)"

# ─── Logging ────────────────────────────────────────────────────
log() {
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $1"
}

log_error() {
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ERROR: $1" >&2
}

ensure_log_dir() {
  mkdir -p "$LOG_DIR"
}

# ─── pre-commit ──────────────────────────────────────────────────
run_pre_commit() {
  ensure_log_dir
  local log_file="${LOG_DIR}/pre-commit-${TIMESTAMP}.log"
  exec > "$log_file" 2>&1

  log "pre-commit hook started"
  log "Checking staged files for secrets..."

  # 1. Verificar .env em stage (nunca commitar .env)
  local env_staged
  env_staged=$(git diff --cached --name-only | grep -E '^\.env' || true)
  if [[ -n "$env_staged" ]]; then
    log_error ".env file staged for commit — blocked."
    log_error "Staged .env files: $env_staged"
    log_error "Move .env to .gitignore or use environment variables."
    echo ""
    echo "ABORT: .env in staging area."
    exit 1
  fi

  # 2. Verificar segredos básicos em arquivos staged (pattern simples)
  # Isso é um guarda-low; para scanning real use github_run_secret_scanning
  local suspicious
  suspicious=$(git diff --cached -U2 | grep -iE '(password|secret|api_key|token|aws_secret|private_key)\s*=\s*['\''"]?[A-Za-z0-9+/]{20,}' || true)
  if [[ -n "$suspicious" ]]; then
    log_error "Potential secret detected in staged diff — blocked."
    log_error "Review the diff and remove secrets before committing."
    echo ""
    echo "ABORT: Suspicious pattern in staged files."
    exit 1
  fi

  # 3. Verificar se há arquivos muito grandes ( > 50MB — GitHub limit)
  local large_files
  large_files=$(git diff --cached --name-only | while read -r f; do
    [[ -f "$f" ]] && [[ "$(git ls-files -s "$f" | awk '{print $4}')" -gt 52428800 ]] && echo "$f"
  done || true)
  if [[ -n "$large_files" ]]; then
    log_error "Large files detected (>50MB): $large_files"
    echo ""
    echo "ABORT: Large files in staging area."
    exit 1
  fi

  log "pre-commit check passed — clean."
  echo ""
  echo "OK: pre-commit passed."
  exit 0
}

# ─── post-commit ─────────────────────────────────────────────────
run_post_commit() {
  ensure_log_dir
  local log_file="${LOG_DIR}/post-commit-${TIMESTAMP}.log"
  exec > "$log_file" 2>&1

  log "post-commit hook started"

  # Verificar se já fizemos push nesta sessão (evitar double-push)
  local pushed_marker=".laos/hooks/.pushed_this_session"
  if [[ -f "$pushed_marker" ]]; then
    log "Already pushed this session — skipping."
    exit 0
  fi

  log "Running git push origin HEAD..."

  # Tentar push com retry
  local attempt=0
  local max_attempts=2
  local push_success=0

  while [[ $attempt -lt $max_attempts ]]; do
    attempt=$((attempt + 1))
    log "Push attempt $attempt/$max_attempts"

    if git push origin HEAD 2>&1; then
      log "Push successful."
      touch "$pushed_marker"
      push_success=1
      break
    else
      log_error "Push attempt $attempt failed."
      if [[ $attempt -lt $max_attempts ]]; then
        log "Retrying in 2 seconds..."
        sleep 2
      fi
    fi
  done

  if [[ $push_success -eq 0 ]]; then
    log_error "Push failed after $max_attempts attempts."
    echo ""
    echo "WARNING: Push failed. Run 'git push origin HEAD' manually."
    exit 1
  fi

  echo ""
  echo "OK: pushed to origin."
  exit 0
}

# ─── session-end ────────────────────────────────────────────────
run_session_end() {
  local status
  status=$(git status --porcelain 2>/dev/null || echo "")

  if [[ -z "$status" ]]; then
    exit 0
  fi

  echo ""
  echo "WARNING: Uncommitted changes found at session end."
  echo "Files not yet committed:"
  echo "$status"
  echo ""
  echo "To commit: git add . && git commit -m 'message'"
  echo "To discard: git checkout -- ."

  # Log regardless
  ensure_log_dir
  local log_file="${LOG_DIR}/session-end-${TIMESTAMP}.log"
  echo "Uncommitted changes at session end:" > "$log_file"
  echo "$status" >> "$log_file"
  echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$log_file"

  exit 1
}

# ─── Main ────────────────────────────────────────────────────────
case "${1:-}" in
  pre-commit)
    run_pre_commit
    ;;
  post-commit)
    run_post_commit
    ;;
  session-end)
    run_session_end
    ;;
  *)
    echo "Usage: $0 {pre-commit|post-commit|session-end}"
    exit 1
    ;;
esac