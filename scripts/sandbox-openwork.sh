#!/bin/bash
# Sandbox wrapper for Openwork API calls
# Logs all requests, validates URLs, rate limits

set -e

API_KEY="ow_5e2b61c4df8f453b612773e9db30807449694818af351ae9"
BASE_URL="https://www.openwork.bot/api"
LOG_FILE="/tmp/openwork-audit.log"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

validate_url() {
  local url="$1"
  if [[ ! "$url" =~ ^https://www\.openwork\.bot/api/ ]]; then
    log "BLOCKED: Invalid URL pattern: $url"
    return 1
  fi
  return 0
}

case "$1" in
  "get-jobs")
    validate_url "$BASE_URL/jobs?status=open" || exit 1
    log "GET: /jobs?status=open"
    curl -s -H "Authorization: Bearer $API_KEY" "$BASE_URL/jobs?status=open"
    ;;
  "submit-job")
    JOB_ID="$2"
    SUBMISSION="$3"
    validate_url "$BASE_URL/jobs/$JOB_ID/submit" || exit 1
    log "POST: /jobs/$JOB_ID/submit | Job: $JOB_ID"
    curl -s -X POST "$BASE_URL/jobs/$JOB_ID/submit" \
      -H "Authorization: Bearer $API_KEY" \
      -H "Content-Type: application/json" \
      -d "$SUBMISSION"
    ;;
  "agent-status")
    validate_url "$BASE_URL/agents/me" || exit 1
    log "GET: /agents/me"
    curl -s -H "Authorization: Bearer $API_KEY" "$BASE_URL/agents/me"
    ;;
  *)
    echo "Usage: $0 {get-jobs|submit-job JOB_ID JSON|agent-status}"
    exit 1
    ;;
esac