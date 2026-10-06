#!/usr/bin/env bash
set -euo pipefail

echo "=== AUNEYA Local Witness CLI Display v0.1 Conformance ==="

TMP_DIR=".tmp/auneya-local-display"
FLOW_OUT="$TMP_DIR/local-flow.json"
DISPLAY_OUT="$TMP_DIR/display.txt"
COMPACT_OUT="$TMP_DIR/display-compact.txt"

rm -rf "$TMP_DIR"
mkdir -p "$TMP_DIR"

echo "=== Erzeuge lokalen Flow mit Runner ==="
python3 tools/auneya/auneya_local_witness_runner.py \
  --claim fixtures/auneya/claims/valid-release-reality.json \
  --out "$FLOW_OUT" \
  --witness-id witness_android_termux_local_001 \
  --start-time 2026-10-06T00:10:00Z

test -f "$FLOW_OUT"

echo "=== Erzeuge Display ==="
python3 tools/auneya/auneya_local_witness_display.py \
  --input "$FLOW_OUT" > "$DISPLAY_OUT"

test -f "$DISPLAY_OUT"

echo "=== Erzeuge Compact Display ==="
python3 tools/auneya/auneya_local_witness_display.py \
  --input "$FLOW_OUT" \
  --compact > "$COMPACT_OUT"

test -f "$COMPACT_OUT"

echo "=== Prüfe Display-Inhalt ==="
grep -q "AUNEYA LOCAL WITNESS" "$DISPLAY_OUT"
grep -q "local non-value simulation" "$DISPLAY_OUT"
grep -q "Token created:.*false" "$DISPLAY_OUT"
grep -q "Market value claimed:.*false" "$DISPLAY_OUT"
grep -q "Transferable:.*false" "$DISPLAY_OUT"
grep -q "Mainnet:.*not active" "$DISPLAY_OUT"
grep -q "Pulses:" "$DISPLAY_OUT"
grep -q "Micro-Proofs:" "$DISPLAY_OUT"
grep -q "Prooflet:" "$DISPLAY_OUT"
grep -q "Private data:.*not accessed" "$DISPLAY_OUT"
grep -q "Hacked data:.*not used" "$DISPLAY_OUT"
grep -q "Paywall bypass:.*not used" "$DISPLAY_OUT"
grep -q "Credentials:.*not used" "$DISPLAY_OUT"
grep -q "Surveillance:.*not performed" "$DISPLAY_OUT"
grep -q "No token, real reward, mainnet or market value is created" "$DISPLAY_OUT"

echo "=== Prüfe Compact-Inhalt ==="
grep -q "AUNEYA LOCAL WITNESS" "$COMPACT_OUT"
grep -q "transferable=false" "$COMPACT_OUT"
grep -q "market_value_claimed=false" "$COMPACT_OUT"
grep -q "mainnet=not_active" "$COMPACT_OUT"
grep -q "simulated_neya=" "$COMPACT_OUT"

echo "=== Display muss Value-Reward-Verstoß ablehnen ==="
set +e
python3 tools/auneya/auneya_local_witness_display.py \
  --input fixtures/auneya/pulse-flow/invalid-value-reward-flow.json > "$TMP_DIR/invalid-display.txt" 2>&1
STATUS=$?
set -e

if [ "$STATUS" -eq 0 ]; then
  echo "FAIL: invalid value reward flow was not rejected by display"
  exit 1
fi

grep -q "FAIL:" "$TMP_DIR/invalid-display.txt"

echo "PASS AUNEYA Local Witness CLI Display v0.1 conformance"
