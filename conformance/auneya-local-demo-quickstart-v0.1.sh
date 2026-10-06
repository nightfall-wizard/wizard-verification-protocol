#!/usr/bin/env bash
set -euo pipefail

echo "=== AUNEYA Local Demo Quickstart v0.1 Conformance ==="

DOC="docs/auneya/AUNEYA-LOCAL-DEMO-QUICKSTART-V0.1.md"
TMP_DIR=".tmp/auneya-quickstart-test"
LOG_OUT="$TMP_DIR/quickstart-demo.log"

test -f "$DOC"
test -x tools/auneya/auneya_one_command_local_demo.sh
test -x tools/auneya/auneya_local_witness_runner.py
test -x tools/auneya/auneya_local_witness_display.py

grep -q "AUNEYA Local Demo Quickstart v0.1" "$DOC"
grep -q "./tools/auneya/auneya_one_command_local_demo.sh" "$DOC"
grep -q "Token created: false" "$DOC"
grep -q "Market value claimed: false" "$DOC"
grep -q "Transferable: false" "$DOC"
grep -q "Mainnet: not active" "$DOC"
grep -q "This does not create AUNEYA" "$DOC"
grep -q "This does not create neya" "$DOC"
grep -q "This does not create a real reward" "$DOC"
grep -q "Legal review is required" "$DOC"

rm -rf "$TMP_DIR"
mkdir -p "$TMP_DIR"

AUNEYA_DEMO_OUT_DIR="$TMP_DIR/out" \
AUNEYA_WITNESS_ID="witness_android_termux_local_001" \
AUNEYA_START_TIME="2026-10-06T00:12:00Z" \
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

python3 - <<'PY'
import json
import sys
from pathlib import Path

path = Path(".tmp/auneya-quickstart-test/out/local-flow.json")
obj = json.loads(path.read_text())

def fail(msg):
    print(f"FAIL {path}: {msg}")
    sys.exit(1)

if obj["schema_version"] != "auneya-pulse-flow-v0.1":
    fail("wrong schema_version")

if obj["flow_type"] != "phone_witness_loop":
    fail("wrong flow_type")

if obj["claim_ref"]["claim_id"] != "auneya_claim_release_reality_001":
    fail("wrong claim_id")

if len(obj["pulses"]) != 4:
    fail("expected four pulses")

if len(obj["micro_proofs"]) != 2:
    fail("expected two micro proofs")

reward = obj["simulated_reward_entry"]

if reward["entry_type"] != "non_value_simulation":
    fail("wrong reward entry type")

if reward["unit"] != "simulated_neya":
    fail("wrong simulated unit")

if reward["transferable"] is not False:
    fail("simulated entry must be non-transferable")

if reward["market_value_claimed"] is not False:
    fail("simulated entry must not claim market value")

print("PASS quickstart output validation")
PY

echo "=== Quickstart private-data rejection check ==="
set +e
AUNEYA_DEMO_OUT_DIR="$TMP_DIR/private-out" \
./tools/auneya/auneya_one_command_local_demo.sh \
  fixtures/auneya/claims/invalid-private-data-claim.json > "$TMP_DIR/private.log" 2>&1
STATUS=$?
set -e

if [ "$STATUS" -eq 0 ]; then
  echo "FAIL: quickstart demo accepted private-data claim"
  exit 1
fi

grep -q "FAIL:" "$TMP_DIR/private.log"

echo "PASS AUNEYA Local Demo Quickstart v0.1 conformance"
