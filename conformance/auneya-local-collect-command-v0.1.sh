#!/usr/bin/env bash
set -euo pipefail

echo "=== AUNEYA Local Collect Command v0.1 Conformance ==="

TMP_DIR=".tmp/auneya-local-collect-test"
LEDGER="$TMP_DIR/local-collection-ledger.json"
COLLECT_ONE="$TMP_DIR/collect-one.txt"
COLLECT_TWO="$TMP_DIR/collect-two.txt"
INVALID_OUT="$TMP_DIR/invalid.txt"

rm -rf "$TMP_DIR"
mkdir -p "$TMP_DIR"

test -x tools/auneya/auneya_local_collect.sh
test -x tools/auneya/auneya_local_collection_ledger.py
test -x tools/auneya/auneya_local_collection_status.py
test -f docs/auneya/AUNEYA-LOCAL-COLLECT-COMMAND-V0.1.md

echo "=== Ersten Collect ausführen ==="
AUNEYA_LEDGER="$LEDGER" \
AUNEYA_COLLECT_OUT_ROOT="$TMP_DIR/out-one" \
AUNEYA_WITNESS_ID="witness_android_termux_local_001" \
AUNEYA_START_TIME="2026-10-06T00:18:00Z" \
./tools/auneya/auneya_local_collect.sh release-reality > "$COLLECT_ONE"

test -f "$LEDGER"

grep -q "AUNEYA LOCAL COLLECT COMMAND v0.1" "$COLLECT_ONE"
grep -q "Claim key: release-reality" "$COLLECT_ONE"
grep -q "Recorded local non-value entry" "$COLLECT_ONE"
grep -q "AUNEYA LOCAL COLLECTION STATUS" "$COLLECT_ONE"
grep -q "Total simulated entries:.*1" "$COLLECT_ONE"
grep -q "Token created:.*false" "$COLLECT_ONE"
grep -q "AUNEYA created:.*false" "$COLLECT_ONE"
grep -q "neya created:.*false" "$COLLECT_ONE"
grep -q "Real reward created:.*false" "$COLLECT_ONE"
grep -q "Market value claimed:.*false" "$COLLECT_ONE"
grep -q "Transferable:.*false" "$COLLECT_ONE"
grep -q "Mainnet:.*not active" "$COLLECT_ONE"
grep -q "AUNEYA local collect completed" "$COLLECT_ONE"
grep -q "non_value_simulation=true" "$COLLECT_ONE"

echo "=== Zweiten Collect ausführen ==="
AUNEYA_LEDGER="$LEDGER" \
AUNEYA_COLLECT_OUT_ROOT="$TMP_DIR/out-two" \
AUNEYA_WITNESS_ID="witness_android_termux_local_001" \
AUNEYA_START_TIME="2026-10-06T00:19:00Z" \
./tools/auneya/auneya_local_collect.sh website-claim-reality > "$COLLECT_TWO"

grep -q "Claim key: website-claim-reality" "$COLLECT_TWO"
grep -q "Total simulated entries:.*2" "$COLLECT_TWO"
grep -q "website-claim-reality" "$COLLECT_TWO"
grep -q "release-reality" "$COLLECT_TWO"

echo "=== Ledger JSON prüfen ==="
python3 - <<'PY'
import json
import sys
from pathlib import Path

path = Path(".tmp/auneya-local-collect-test/local-collection-ledger.json")
obj = json.loads(path.read_text())

def fail(msg):
    print(f"FAIL {path}: {msg}")
    sys.exit(1)

if obj["schema_version"] != "auneya-local-collection-ledger-v0.1":
    fail("wrong schema_version")

if obj["ledger_type"] != "local_non_value_collection_simulation":
    fail("wrong ledger_type")

if obj["total_simulated_entries"] != 2:
    fail("expected two entries")

if len(obj["entries"]) != 2:
    fail("expected two ledger entries")

if obj["total_simulated_neya_counted"] <= 0:
    fail("expected positive simulated total")

for key in [
    "mainnet_active",
    "token_created",
    "auneya_created",
    "neya_created",
    "real_reward_created",
    "market_value_claimed",
    "transferable",
]:
    if obj.get(key) is not False:
        fail(f"{key} must be false")

claim_keys = [entry["claim_key"] for entry in obj["entries"]]

if claim_keys != ["release-reality", "website-claim-reality"]:
    fail("claim keys mismatch")

for index, entry in enumerate(obj["entries"], start=1):
    if entry["entry_sequence"] != index:
        fail("entry sequence mismatch")

    if entry["entry_type"] != "local_non_value_collection_simulation":
        fail("entry type mismatch")

    if entry["simulated_unit"] != "simulated_neya":
        fail("simulated unit mismatch")

    if entry["simulated_amount"] <= 0:
        fail("simulated amount must be positive")

    for key in [
        "transferable",
        "market_value_claimed",
        "token_created",
        "auneya_created",
        "neya_created",
        "real_reward_created",
        "mainnet_active",
    ]:
        if entry.get(key) is not False:
            fail(f"entry {key} must be false")

print("PASS local collect ledger validation")
PY

echo "=== Ungültiger Claim-Key muss scheitern ==="
set +e
AUNEYA_LEDGER="$LEDGER" \
AUNEYA_COLLECT_OUT_ROOT="$TMP_DIR/out-invalid" \
./tools/auneya/auneya_local_collect.sh invalid-private-data > "$INVALID_OUT" 2>&1
STATUS=$?
set -e

if [ "$STATUS" -eq 0 ]; then
  echo "FAIL: invalid collect claim key was accepted"
  exit 1
fi

grep -q "FAIL:" "$INVALID_OUT"

echo "PASS AUNEYA Local Collect Command v0.1 conformance"
