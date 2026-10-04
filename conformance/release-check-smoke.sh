#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP RELEASE CHECK CONFORMANCE SMOKE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

VECTOR="test-vectors/release-check/bootstrap-basic.json"

if [ ! -f "$VECTOR" ]; then
  echo "FAIL: missing vector: $VECTOR"
  exit 1
fi

echo "Vector: $VECTOR"

OUT="$(cargo run --quiet --manifest-path reference/rust/wvp-release-check/Cargo.toml -- --target nightfall-wizard/wizard-verification-protocol --json)"

echo "$OUT"

echo "$OUT" | grep -q '"tool": "wvp-release-check"'
echo "$OUT" | grep -q '"status": "WARN"'
echo "$OUT" | grep -q '"classification": "observed"'
echo "$OUT" | grep -q '"not an audit"'
echo "$OUT" | grep -q '"no signature verification yet"'
echo "$OUT" | grep -q '"no checksum verification yet"'
echo "$OUT" | grep -q '"no reproducible build verification yet"'

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "RESULT: PASS"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
