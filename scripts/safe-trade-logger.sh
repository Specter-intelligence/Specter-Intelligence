#!/bin/bash
# Safe trade logger - no external calls, local only

ACTION=$1
TOKEN=$2
AMOUNT_USD=$3
PRICE=$4
REASON=$5
TX=$6

TRADES_FILE="/home/ubuntu/.openclaw/workspace/data/trades.json"
mkdir -p "$(dirname "$TRADES_FILE")"

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Validate inputs
if [[ ! "$ACTION" =~ ^(BUY|SELL)$ ]]; then
  echo "Error: Action must be BUY or SELL"
  exit 1
fi

if [[ ! "$TX" =~ ^0x[0-9a-fA-F]{64}$ ]] && [[ "$TX" != "SIMULATED" ]]; then
  echo "Error: TX must be 0x... hash or SIMULATED"
  exit 1
fi

# Create trade entry
TRADE_JSON=$(cat <<EOF
{
  "timestamp": "$TIMESTAMP",
  "action": "$ACTION",
  "token": "$TOKEN",
  "amount_usd": "$AMOUNT_USD",
  "price": "$PRICE",
  "reason": "$REASON",
  "tx": "$TX",
  "verified": false,
  "sandboxed": true
}
EOF
)

# Append safely
if [ -f "$TRADES_FILE" ]; then
  if command -v jq >/dev/null 2>&1; then
    jq ". += [$TRADE_JSON]" "$TRADES_FILE" > "${TRADES_FILE}.tmp" && mv "${TRADES_FILE}.tmp" "$TRADES_FILE"
  else
    # Fallback without jq
    echo "$TRADE_JSON" >> "$TRADES_FILE"
  fi
else
  echo "[$TRADE_JSON]" > "$TRADES_FILE"
fi

echo "SAFE LOGGED: $ACTION $TOKEN \$$AMOUNT_USD (sandboxed)"
echo "Note: Trade not executed. Manual approval required for real trades."