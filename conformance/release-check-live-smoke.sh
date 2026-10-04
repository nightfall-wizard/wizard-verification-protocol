#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP RELEASE CHECK LIVE CONFORMANCE SMOKE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

TARGET="nightfall-wizard/wizard-verification-protocol"
echo "Target: $TARGET"

OUT="$(cargo run --quiet --manifest-path reference/rust/wvp-release-check/Cargo.toml -- --target "$TARGET" --json --live)"
echo "$OUT"

echo "$OUT" | grep -q '"tool": "wvp-release-check"'
echo "$OUT" | grep -q '"target": "nightfall-wizard/wizard-verification-protocol"'
echo "$OUT" | grep -q '"live_inspection": true'
echo "$OUT" | grep -q '"repository_found": true'
echo "$OUT" | grep -q '"release_count":'
echo "$OUT" | grep -q '"tag_count":'
echo "$OUT" | grep -q '"latest_release_found":'
echo "$OUT" | grep -q '"latest_release_tag":'
echo "$OUT" | grep -q '"latest_release_asset_count":'
echo "$OUT" | grep -q '"checksum_asset_count":'
echo "$OUT" | grep -q '"signature_asset_count":'
echo "$OUT" | grep -q '"errors":'
echo "$OUT" | grep -q '"release metadata is not security proof"'
echo "$OUT" | grep -q '"asset name discovery is not checksum verification"'
echo "$OUT" | grep -q '"signature asset discovery is not signature verification"'

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "RESULT: PASS"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
