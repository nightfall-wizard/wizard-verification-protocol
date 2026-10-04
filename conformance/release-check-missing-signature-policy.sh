#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP MISSING SIGNATURE POLICY CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

TARGET="nightfall-wizard/wizard-verification-protocol"
echo "Target: $TARGET"

OUT="$(cargo run --quiet --manifest-path reference/rust/wvp-release-check/Cargo.toml -- --target "$TARGET" --json --live)"
echo "$OUT"

check_contains() {
  needle="$1"
  printf '%s\n' "$OUT" | grep -Fq "$needle"
}

check_contains '"status": "WARN"'
check_contains '"latest_release_found": true'
check_contains '"latest_release_tag": "v0.1.0"'
check_contains '"checksum_asset_count": 1'
check_contains '"checksum_verification_attempted": true'
check_contains '"checksum_verification_passed": true'
check_contains '"checksum_verification_error": null'
check_contains '"signature_asset_count": 0'
check_contains '"signature asset discovery is not signature verification"'
check_contains '"no signature verification yet"'

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "RESULT: PASS"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
