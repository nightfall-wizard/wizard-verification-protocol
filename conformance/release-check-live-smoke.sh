#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP RELEASE CHECK LIVE CONFORMANCE SMOKE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

TARGET="${WVP_TARGET:-nightfall-wizard/wizard-verification-protocol}"

echo "Target: $TARGET"

OUT="$(
  cargo run --quiet --manifest-path reference/rust/wvp-release-check/Cargo.toml -- \
    --target "$TARGET" \
    --json \
    --live
)"

echo "$OUT"

echo "$OUT" | grep -q '"live_inspection": true'
echo "$OUT" | grep -q '"repository_found": true'
echo "$OUT" | grep -q '"latest_release_found": true'
echo "$OUT" | grep -q '"latest_release_tag": "v0.1.1"'
echo "$OUT" | grep -q '"checksum_asset_count": 1'
echo "$OUT" | grep -Eq '"signature_asset_count": [1-9][0-9]*'
echo "$OUT" | grep -q '"checksum_verification_attempted": true'
echo "$OUT" | grep -q '"checksum_verification_passed": true'
echo "$OUT" | grep -q '"signature_verification_attempted": false'
echo "$OUT" | grep -q '"signature_verification_passed": null'
echo "$OUT" | grep -q '"signature_verification_error": "signature asset discovered but signature verification is not implemented yet"'
echo "$OUT" | grep -q '"status": "WARN"'
echo "$OUT" | grep -q '"no signature verification yet"'

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "RESULT: PASS"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
