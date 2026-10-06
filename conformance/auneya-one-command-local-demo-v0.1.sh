#!/usr/bin/env bash
set -euo pipefail

echo "=== AUNEYA One-Command Local Demo v0.1 Conformance ==="

TMP_DIR=".tmp/auneya-one-command-demo-test"
LOG_OUT="$TMP_DIR/demo.log"

rm -rf "$TMP_DIR"
mkdir -p "$TMP_DIR"

echo "=== Demo muss gültigen lokalen Flow erzeugen ==="
AUNEYA_DEMO_OUT_DIR="$TMP_DIR/out" \
AUNEYA_WITNESS_ID="witness_android_termux_local_001" \
AUNEYA_START_TIME="2026-10-06T00:11:00Z" \
./tools/auneya/auneya_one_command_local_demo.sh \
  fixtures/auneya/claims/valid-release-reality.json > "$LOG_OUT"

test -f "$TMP_DIR/out/local-flow.json"
test -f "$TMP_DIR/out/local-display.txt"
test -f "$TMP_DIR/out/local-display-compact.txt"

grep -q "AUNEYA ONE-COMMAND LOCAL DEMO v0.1" "$LOG_OUT"
grep -q "AUNEYA LOCAL WITNESS" "$LOG_OUT"
grep -q "Token created: false" "$LOG_OUT"
grep -q "Market value claimed: false" "$LOG_OUT"
grep -q "Transferable: false" "$LOG_OUT"
grep -q "Mainnet: not active" "$LOG_OUT"
grep -q "No token, real reward, mainnet or market value is created" "$LOG_OUT"

grep -q "transferable=false" "$TMP_DIR/out/local-display-compact.txt"
grep -q "market_value_claimed=false" "$TMP_DIR/out/local-display-compact.txt"
grep -q "mainnet=not_active" "$TMP_DIR/out/local-display-compact.txt"
grep -q "simulated_neya=" "$TMP_DIR/out/local-display-compact.txt"

python3 - <<'PY'
import json
import sys
from pathlib import Path

path = Path(".tmp/auneya-one-command-demo-test/out/local-flow.json")
obj = json.loads(path.read_text())

def fail(msg):
    print(f"FAIL {path}: {msg}")
    sys.exit(1)

if obj["schema_version"] != "auneya-pulse-flow-v0.1":
    fail("wrong schema_version")

if obj["flow_type"] != "phone_witness_loop":
    fail("wrong flow_type")

if len(obj["pulses"]) != 4:
    fail("expected four pulses")

if len(obj["micro_proofs"]) != 2:
    fail("expected two micro proofs")

if obj["simulated_reward_entry"]["transferable"] is not False:
    fail("simulated entry must be non-transferable")

if obj["simulated_reward_entry"]["market_value_claimed"] is not False:
    fail("simulated entry must not claim market value")

if obj["witness"]["device_class"] != "android_termux":
    fail("expected android_termux device class")

print("PASS one-command demo output validation")
PY

echo "=== Demo muss private Claim ablehnen ==="
set +e
AUNEYA_DEMO_OUT_DIR="$TMP_DIR/private-out" \
./tools/auneya/auneya_one_command_local_demo.sh \
  fixtures/auneya/claims/invalid-private-data-claim.json > "$TMP_DIR/private.log" 2>&1
STATUS=$?
set -e

if [ "$STATUS" -eq 0 ]; then
  echo "FAIL: private-data claim was not rejected by one-command demo"
  exit 1
fi

grep -q "FAIL:" "$TMP_DIR/private.log"

echo "PASS AUNEYA One-Command Local Demo v0.1 conformance"
