#!/usr/bin/env bash
set -euo pipefail

CLAIM_KEY="${1:-${AUNEYA_CLAIM_KEY:-release-reality}}"
LEDGER="${AUNEYA_LEDGER:-.auneya/local-collection-ledger.json}"
OUT_ROOT="${AUNEYA_COLLECT_OUT_ROOT:-.tmp/auneya-local-collect}"
WITNESS_ID="${AUNEYA_WITNESS_ID:-witness_android_termux_local_001}"
START_TIME="${AUNEYA_START_TIME:-$(date -u +"%Y-%m-%dT%H:%M:%SZ")}"
RUN_DIR="$OUT_ROOT/latest"

mkdir -p "$OUT_ROOT"

echo "AUNEYA LOCAL COLLECT COMMAND v0.1"
echo "Mode: local non-value simulation"
echo "Claim key: $CLAIM_KEY"
echo "Ledger: $LEDGER"
echo "Network: none"
echo "Mainnet: not active"
echo "Token created: false"
echo "AUNEYA created: false"
echo "neya created: false"
echo "Real reward created: false"
echo "Market value claimed: false"
echo "Transferable: false"
echo

python3 tools/auneya/auneya_local_collection_ledger.py \
  --ledger "$LEDGER" \
  --record \
  --claim-key "$CLAIM_KEY" \
  --out-dir "$RUN_DIR" \
  --witness-id "$WITNESS_ID" \
  --start-time "$START_TIME"

echo
echo "=== LOCAL COLLECTION STATUS ==="
python3 tools/auneya/auneya_local_collection_status.py \
  --ledger "$LEDGER"

echo
echo "AUNEYA local collect completed"
echo "ledger=$LEDGER"
echo "claim_key=$CLAIM_KEY"
echo "non_value_simulation=true"
echo "token_created=false"
echo "auneya_created=false"
echo "neya_created=false"
echo "real_reward_created=false"
echo "market_value_claimed=false"
echo "transferable=false"
echo "mainnet_active=false"
