#!/usr/bin/env bash
set -euo pipefail

CLAIM_PATH="${1:-fixtures/auneya/claims/valid-release-reality.json}"
OUT_DIR="${AUNEYA_DEMO_OUT_DIR:-.tmp/auneya-one-command-demo}"
WITNESS_ID="${AUNEYA_WITNESS_ID:-witness_android_termux_local_001}"
START_TIME="${AUNEYA_START_TIME:-2026-10-06T00:11:00Z}"

FLOW_OUT="$OUT_DIR/local-flow.json"
DISPLAY_OUT="$OUT_DIR/local-display.txt"
COMPACT_OUT="$OUT_DIR/local-display-compact.txt"

mkdir -p "$OUT_DIR"

echo "AUNEYA ONE-COMMAND LOCAL DEMO v0.1"
echo "Mode: local non-value simulation"
echo "Network: none"
echo "Mainnet: not active"
echo "Token created: false"
echo "Market value claimed: false"
echo "Transferable: false"
echo

python3 tools/auneya/auneya_local_witness_runner.py \
  --claim "$CLAIM_PATH" \
  --out "$FLOW_OUT" \
  --witness-id "$WITNESS_ID" \
  --start-time "$START_TIME"

echo

python3 tools/auneya/auneya_local_witness_display.py \
  --input "$FLOW_OUT" | tee "$DISPLAY_OUT"

python3 tools/auneya/auneya_local_witness_display.py \
  --input "$FLOW_OUT" \
  --compact > "$COMPACT_OUT"

echo
echo "Artifacts:"
echo "- flow: $FLOW_OUT"
echo "- display: $DISPLAY_OUT"
echo "- compact: $COMPACT_OUT"
echo
echo "Boundary:"
echo "- no token"
echo "- no real reward"
echo "- no market value"
echo "- no mainnet"
echo "- local protocol research only"
