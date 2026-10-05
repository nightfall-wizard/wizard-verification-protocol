#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP SIGNATURE VERIFIED POLICY CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

TARGET="${WVP_TARGET:-nightfall-wizard/wizard-verification-protocol}"
EXPECTED_TAG="${WVP_RELEASE_TAG:-v0.3.0}"

echo "Target: $TARGET"
echo "Expected latest tag: $EXPECTED_TAG"

OUT="$(
  cargo run --quiet --manifest-path reference/rust/wvp-release-check/Cargo.toml -- \
    --target "$TARGET" \
    --json \
    --live
)"

echo "$OUT"

check_contains() {
  needle="$1"
  if ! echo "$OUT" | grep -Fq "$needle"; then
    echo "FAIL: expected output to contain: $needle"
    false
  fi
}

check_contains '"status": "INFO"'
check_contains '"latest_release_tag": "'$EXPECTED_TAG'"'
check_contains '"checksum_asset_count": 1'
check_contains '"signature_asset_count": 1'
check_contains '"checksum_verification_attempted": true'
check_contains '"checksum_verification_passed": true'
check_contains '"signature_verification_attempted": true'
check_contains '"signature_verification_passed": true'
check_contains '"signature_verification_error": null'
check_contains '"signature asset discovery is not signature verification"'
check_contains '"signature verification depends on configured public key"'

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "RESULT: PASS"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
