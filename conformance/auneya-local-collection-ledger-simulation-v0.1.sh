#!/usr/bin/env bash
set -euo pipefail

echo "=== AUNEYA Local Collection Ledger Simulation v0.1 Conformance ==="

TMP_DIR=".tmp/auneya-local-collection-ledger-test"
LEDGER="$TMP_DIR/local-collection-ledger.json"
RECORD_ONE="$TMP_DIR/record-one.txt"
RECORD_TWO="$TMP_DIR/record-two.txt"
SHOW_OUT="$TMP_DIR/show.txt"
RESET_OUT="$TMP_DIR/reset.txt"
INVALID_OUT="$TMP_DIR/invalid.txt"

rm -rf "$TMP_DIR"
mkdir -p "$TMP_DIR"

test -x tools/auneya/auneya_local_collection_ledger.py
test -f docs/auneya/AUNEYA-LOCAL-COLLECTION-LEDGER-SIMULATION-V0.1.md

echo "=== Reset prüfen ==="
python3 tools/auneya/auneya_local_collection_ledger.py \
  --ledger "$LEDGER" \
  --reset > "$RESET_OUT"

test -f "$LEDGER"
grep -q "reset ledger" "$RESET_OUT"
grep -q "Token created: false" "$RESET_OUT"
grep -q "AUNEYA created: false" "$RESET_OUT"
grep -q "neya created: false" "$RESET_OUT"

echo "=== Ersten lokalen Simulationseintrag zählen ==="
python3 tools/auneya/auneya_local_collection_ledger.py \
  --ledger "$LEDGER" \
  --record \
  --claim-key release-reality \
  --out-dir "$TMP_DIR/out-one" \
  --witness-id witness_android_termux_local_001 \
  --start-time 2026-10-06T00:14:00Z > "$RECORD_ONE"

grep -q "AUNEYA LOCAL COLLECTION LEDGER SIMULATION v0.1" "$RECORD_ONE"
grep -q "Recorded local non-value entry" "$RECORD_ONE"
grep -q "claim_key: release-reality" "$RECORD_ONE"
grep -q "simulated_amount:" "$RECORD_ONE"
grep -q "total_simulated_entries: 1" "$RECORD_ONE"
grep -q "Token created: false" "$RECORD_ONE"
grep -q "AUNEYA created: false" "$RECORD_ONE"
grep -q "neya created: false" "$RECORD_ONE"
grep -q "Market value claimed: false" "$RECORD_ONE"
grep -q "Transferable: false" "$RECORD_ONE"
grep -q "Mainnet: not active" "$RECORD_ONE"

echo "=== Zweiten lokalen Simulationseintrag zählen ==="
python3 tools/auneya/auneya_local_collection_ledger.py \
  --ledger "$LEDGER" \
  --record \
  --claim-key download-integrity \
  --out-dir "$TMP_DIR/out-two" \
  --witness-id witness_android_termux_local_001 \
  --start-time 2026-10-06T00:15:00Z > "$RECORD_TWO"

grep -q "claim_key: download-integrity" "$RECORD_TWO"
grep -q "total_simulated_entries: 2" "$RECORD_TWO"

echo "=== Ledger anzeigen ==="
python3 tools/auneya/auneya_local_collection_ledger.py \
  --ledger "$LEDGER" \
  --show > "$SHOW_OUT"

grep -q "AUNEYA LOCAL COLLECTION LEDGER SIMULATION v0.1" "$SHOW_OUT"
grep -q "total_simulated_entries: 2" "$SHOW_OUT"
grep -q "unit: simulated_neya" "$SHOW_OUT"
grep -q "Token created: false" "$SHOW_OUT"
grep -q "AUNEYA created: false" "$SHOW_OUT"
grep -q "neya created: false" "$SHOW_OUT"
grep -q "Market value claimed: false" "$SHOW_OUT"
grep -q "Transferable: false" "$SHOW_OUT"
grep -q "Mainnet: not active" "$SHOW_OUT"
grep -q "release-reality" "$SHOW_OUT"
grep -q "download-integrity" "$SHOW_OUT"

echo "=== Ledger JSON prüfen ==="
python3 - <<'PY'
import json
import sys
from pathlib import Path

path = Path(".tmp/auneya-local-collection-ledger-test/local-collection-ledger.json")
obj = json.loads(path.read_text())

def fail(msg):
    print(f"FAIL {path}: {msg}")
    sys.exit(1)

if obj["schema_version"] != "auneya-local-collection-ledger-v0.1":
    fail("wrong schema_version")

if obj["ledger_type"] != "local_non_value_collection_simulation":
    fail("wrong ledger_type")

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

if obj["unit"] != "simulated_neya":
    fail("unit must be simulated_neya")

if obj["total_simulated_entries"] != 2:
    fail("expected two simulated entries")

if len(obj["entries"]) != 2:
    fail("entries array must have length two")

if obj["total_simulated_neya_counted"] <= 0:
    fail("total simulated count must be positive")

claim_keys = [entry["claim_key"] for entry in obj["entries"]]

if claim_keys != ["release-reality", "download-integrity"]:
    fail("claim key order mismatch")

for index, entry in enumerate(obj["entries"], start=1):
    if entry["entry_sequence"] != index:
        fail("entry sequence mismatch")

    if entry["entry_type"] != "local_non_value_collection_simulation":
        fail("wrong entry type")

    if entry["simulated_unit"] != "simulated_neya":
        fail("wrong simulated unit")

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

    if not str(entry.get("entry_hash", "")).startswith("sha256:"):
        fail("entry hash missing")

print("PASS local collection ledger JSON validation")
PY

echo "=== Ungültiger Claim-Key muss scheitern ==="
set +e
python3 tools/auneya/auneya_local_collection_ledger.py \
  --ledger "$LEDGER" \
  --record \
  --claim-key invalid-private-data \
  --out-dir "$TMP_DIR/out-invalid" > "$INVALID_OUT" 2>&1
STATUS=$?
set -e

if [ "$STATUS" -eq 0 ]; then
  echo "FAIL: invalid claim key was accepted"
  exit 1
fi

grep -q "FAIL:" "$INVALID_OUT"

echo "PASS AUNEYA Local Collection Ledger Simulation v0.1 conformance"
