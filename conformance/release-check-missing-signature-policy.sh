#!/usr/bin/env bash
set -euo pipefail
# WVP-SIGNATURE-POLICY-V040

cd "$(dirname "${BASH_SOURCE[0]}")/.."

TARGET="${WVP_TARGET:-nightfall-wizard/wizard-verification-protocol}"
TAG="$(gh api "repos/$TARGET/releases?per_page=1" --jq '.[0].tag_name')"
META="$(gh release view "$TAG" -R "$TARGET" --json assets,body)"
COUNT="$(printf '%s' "$META" | jq '.assets | length')"

echo "Target: $TARGET"
echo "Expected selected WVP release tag: $EXPECTED_TAG"

OUT="$(
  WVP_RELEASE_TAG="$EXPECTED_TAG" cargo run --quiet --manifest-path reference/rust/wvp-release-check/Cargo.toml -- \
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
