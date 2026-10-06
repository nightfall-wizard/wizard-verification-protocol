#!/usr/bin/env bash
set -euo pipefail

echo "=== AUNEYA Local Claim Selection v0.1 Conformance ==="

TMP_DIR=".tmp/auneya-claim-selection-test"
LIST_OUT="$TMP_DIR/list.txt"
SELECT_OUT="$TMP_DIR/select.txt"
PATH_OUT="$TMP_DIR/path.txt"
DEMO_OUT="$TMP_DIR/demo.txt"

rm -rf "$TMP_DIR"
mkdir -p "$TMP_DIR"

test -x tools/auneya/auneya_local_claim_select.py
test -f docs/auneya/AUNEYA-LOCAL-CLAIM-SELECTION-V0.1.md

echo "=== Liste unterstützter Claims prüfen ==="
python3 tools/auneya/auneya_local_claim_select.py --list > "$LIST_OUT"

grep -q "AUNEYA LOCAL CLAIM SELECTION v0.1" "$LIST_OUT"
grep -q "release-reality" "$LIST_OUT"
grep -q "download-integrity" "$LIST_OUT"
grep -q "website-claim-reality" "$LIST_OUT"
grep -q "Token created: false" "$LIST_OUT"
grep -q "Market value claimed: false" "$LIST_OUT"
grep -q "Transferable: false" "$LIST_OUT"
grep -q "Mainnet: not active" "$LIST_OUT"
grep -q "no AUNEYA" "$LIST_OUT"
grep -q "no neya" "$LIST_OUT"

echo "=== Einzelne Auswahl prüfen ==="
python3 tools/auneya/auneya_local_claim_select.py \
  --claim-key release-reality > "$SELECT_OUT"

grep -q "AUNEYA LOCAL CLAIM SELECTED" "$SELECT_OUT"
grep -q "key: release-reality" "$SELECT_OUT"
grep -q "auneya_claim_release_reality_001" "$SELECT_OUT"
grep -q "Token created: false" "$SELECT_OUT"
grep -q "Market value claimed: false" "$SELECT_OUT"

echo "=== Pfad-Ausgabe prüfen ==="
python3 tools/auneya/auneya_local_claim_select.py \
  --claim-key release-reality \
  --print-path > "$PATH_OUT"

grep -q "^fixtures/auneya/claims/valid-release-reality.json$" "$PATH_OUT"

echo "=== Alle unterstützten Claim-Keys müssen auswählbar sein ==="
for key in release-reality download-integrity website-claim-reality; do
  python3 tools/auneya/auneya_local_claim_select.py \
    --claim-key "$key" \
    --print-path > "$TMP_DIR/$key.path"

  test -f "$(cat "$TMP_DIR/$key.path")"
done

echo "=== Ungültiger Claim-Key muss scheitern ==="
set +e
python3 tools/auneya/auneya_local_claim_select.py \
  --claim-key invalid-private-data \
  --print-path > "$TMP_DIR/invalid-key.txt" 2>&1
STATUS=$?
set -e

if [ "$STATUS" -eq 0 ]; then
  echo "FAIL: invalid claim key was accepted"
  exit 1
fi

grep -q "FAIL:" "$TMP_DIR/invalid-key.txt"

echo "=== Demo mit ausgewähltem Claim ausführen ==="
python3 tools/auneya/auneya_local_claim_select.py \
  --claim-key release-reality \
  --run-demo \
  --out-dir "$TMP_DIR/out" \
  --witness-id witness_android_termux_local_001 \
  --start-time 2026-10-06T00:13:00Z > "$DEMO_OUT"

test -f "$TMP_DIR/out/local-flow.json"
test -f "$TMP_DIR/out/local-display.txt"
test -f "$TMP_DIR/out/local-display-compact.txt"

grep -q "Selected claim:" "$DEMO_OUT"
grep -q "key: release-reality" "$DEMO_OUT"
grep -q "AUNEYA ONE-COMMAND LOCAL DEMO v0.1" "$DEMO_OUT"
grep -q "AUNEYA LOCAL WITNESS" "$DEMO_OUT"
grep -q "Token created: false" "$DEMO_OUT"
grep -q "Market value claimed: false" "$DEMO_OUT"
grep -q "Transferable: false" "$DEMO_OUT"
grep -q "Mainnet: not active" "$DEMO_OUT"

python3 - <<'PY'
import json
import sys
from pathlib import Path

path = Path(".tmp/auneya-claim-selection-test/out/local-flow.json")
obj = json.loads(path.read_text())

def fail(msg):
    print(f"FAIL {path}: {msg}")
    sys.exit(1)

if obj["schema_version"] != "auneya-pulse-flow-v0.1":
    fail("wrong schema_version")

if obj["flow_type"] != "phone_witness_loop":
    fail("wrong flow_type")

if obj["claim_ref"]["claim_id"] != "auneya_claim_release_reality_001":
    fail("wrong selected claim_id")

reward = obj["simulated_reward_entry"]

if reward["entry_type"] != "non_value_simulation":
    fail("wrong reward entry type")

if reward["transferable"] is not False:
    fail("simulated entry must be non-transferable")

if reward["market_value_claimed"] is not False:
    fail("simulated entry must not claim market value")

print("PASS claim selection demo output validation")
PY

echo "PASS AUNEYA Local Claim Selection v0.1 conformance"
