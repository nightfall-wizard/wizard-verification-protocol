#!/usr/bin/env bash
set -euo pipefail

echo "=== AUNEYA Local Collection Status Display v0.1 Conformance ==="

TMP_DIR=".tmp/auneya-local-collection-status-test"
LEDGER="$TMP_DIR/local-collection-ledger.json"
STATUS_OUT="$TMP_DIR/status.txt"
COMPACT_OUT="$TMP_DIR/status-compact.txt"
EMPTY_OUT="$TMP_DIR/status-empty.txt"
BAD_LEDGER="$TMP_DIR/bad-ledger.json"
BAD_OUT="$TMP_DIR/bad-status.txt"

rm -rf "$TMP_DIR"
mkdir -p "$TMP_DIR"

test -x tools/auneya/auneya_local_collection_ledger.py
test -x tools/auneya/auneya_local_collection_status.py
test -f docs/auneya/AUNEYA-LOCAL-COLLECTION-STATUS-DISPLAY-V0.1.md

echo "=== Leeren Status ohne Ledger prüfen ==="
python3 tools/auneya/auneya_local_collection_status.py \
  --ledger "$TMP_DIR/missing-ledger.json" > "$EMPTY_OUT"

grep -q "AUNEYA LOCAL COLLECTION STATUS" "$EMPTY_OUT"
grep -q "Ledger exists:.*false" "$EMPTY_OUT"
grep -q "Total simulated entries:.*0" "$EMPTY_OUT"
grep -q "Total simulated_neya:.*0" "$EMPTY_OUT"
grep -q "Token created:.*false" "$EMPTY_OUT"
grep -q "AUNEYA created:.*false" "$EMPTY_OUT"
grep -q "neya created:.*false" "$EMPTY_OUT"
grep -q "Transferable:.*false" "$EMPTY_OUT"

echo "=== Ledger mit zwei Simulationseinträgen erzeugen ==="
python3 tools/auneya/auneya_local_collection_ledger.py \
  --ledger "$LEDGER" \
  --reset > "$TMP_DIR/reset.txt"

python3 tools/auneya/auneya_local_collection_ledger.py \
  --ledger "$LEDGER" \
  --record \
  --claim-key release-reality \
  --out-dir "$TMP_DIR/out-one" \
  --witness-id witness_android_termux_local_001 \
  --start-time 2026-10-06T00:16:00Z > "$TMP_DIR/record-one.txt"

python3 tools/auneya/auneya_local_collection_ledger.py \
  --ledger "$LEDGER" \
  --record \
  --claim-key website-claim-reality \
  --out-dir "$TMP_DIR/out-two" \
  --witness-id witness_android_termux_local_001 \
  --start-time 2026-10-06T00:17:00Z > "$TMP_DIR/record-two.txt"

echo "=== Status Display prüfen ==="
python3 tools/auneya/auneya_local_collection_status.py \
  --ledger "$LEDGER" > "$STATUS_OUT"

grep -q "AUNEYA LOCAL COLLECTION STATUS" "$STATUS_OUT"
grep -q "Mode:.*local non-value simulation" "$STATUS_OUT"
grep -q "Ledger exists:.*true" "$STATUS_OUT"
grep -q "Network:.*none" "$STATUS_OUT"
grep -q "Mainnet:.*not active" "$STATUS_OUT"
grep -q "Token created:.*false" "$STATUS_OUT"
grep -q "AUNEYA created:.*false" "$STATUS_OUT"
grep -q "neya created:.*false" "$STATUS_OUT"
grep -q "Real reward created:.*false" "$STATUS_OUT"
grep -q "Market value claimed:.*false" "$STATUS_OUT"
grep -q "Transferable:.*false" "$STATUS_OUT"
grep -q "Total simulated entries:.*2" "$STATUS_OUT"
grep -q "Total simulated_neya:" "$STATUS_OUT"
grep -q "Unit:.*simulated_neya" "$STATUS_OUT"
grep -q "LATEST ENTRY" "$STATUS_OUT"
grep -q "website-claim-reality" "$STATUS_OUT"
grep -q "release-reality" "$STATUS_OUT"
grep -q "No token, AUNEYA, neya, real reward, mainnet or market value is created" "$STATUS_OUT"
grep -q "Nothing shown here is transferable" "$STATUS_OUT"

echo "=== Compact Status prüfen ==="
python3 tools/auneya/auneya_local_collection_status.py \
  --ledger "$LEDGER" \
  --compact > "$COMPACT_OUT"

grep -q "AUNEYA LOCAL COLLECTION STATUS" "$COMPACT_OUT"
grep -q "ledger_exists=true" "$COMPACT_OUT"
grep -q "total_entries=2" "$COMPACT_OUT"
grep -q "total_simulated_neya=" "$COMPACT_OUT"
grep -q "unit=simulated_neya" "$COMPACT_OUT"
grep -q "token_created=false" "$COMPACT_OUT"
grep -q "auneya_created=false" "$COMPACT_OUT"
grep -q "neya_created=false" "$COMPACT_OUT"
grep -q "real_reward_created=false" "$COMPACT_OUT"
grep -q "market_value_claimed=false" "$COMPACT_OUT"
grep -q "transferable=false" "$COMPACT_OUT"
grep -q "mainnet=not_active" "$COMPACT_OUT"

echo "=== Boundary-Verstoß muss abgelehnt werden ==="
python3 - <<'PY'
import json
from pathlib import Path

src = Path(".tmp/auneya-local-collection-status-test/local-collection-ledger.json")
dst = Path(".tmp/auneya-local-collection-status-test/bad-ledger.json")

obj = json.loads(src.read_text())
obj["transferable"] = True
dst.write_text(json.dumps(obj, indent=2) + "\n")
PY

set +e
python3 tools/auneya/auneya_local_collection_status.py \
  --ledger "$BAD_LEDGER" > "$BAD_OUT" 2>&1
STATUS=$?
set -e

if [ "$STATUS" -eq 0 ]; then
  echo "FAIL: bad ledger boundary was accepted"
  exit 1
fi

grep -q "FAIL:" "$BAD_OUT"

echo "PASS AUNEYA Local Collection Status Display v0.1 conformance"
