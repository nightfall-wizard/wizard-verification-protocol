#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP RELEASE CHECK CONFORMANCE SMOKE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"
echo "Vector: test-vectors/release-check/bootstrap-basic.json"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

OUT="$(cargo run --quiet --manifest-path reference/rust/wvp-release-check/Cargo.toml -- --target nightfall-wizard/wizard-verification-protocol --json)"
echo "$OUT"

check_contains() {
  needle="$1"
  printf '%s\n' "$OUT" | grep -Fq "$needle"
}

check_contains '"tool": "wvp-release-check"'
check_contains '"version": "0.3.0"'
check_contains '"target": "nightfall-wizard/wizard-verification-protocol"'
check_contains '"status": "WARN"'
check_contains '"classification": "observed"'
check_contains '"live_inspection": false'
check_contains '"summary": "GitHub release metadata, artifact discovery, checksum verification and signature verification baseline"'

check_contains '"repository_found": null'
check_contains '"release_count": null'
check_contains '"tag_count": null'
check_contains '"latest_release_found": null'
check_contains '"latest_release_tag": null'
check_contains '"latest_release_asset_count": null'
check_contains '"checksum_asset_count": null'
check_contains '"signature_asset_count": null'
check_contains '"signature_verification_attempted": null'
check_contains '"signature_verification_passed": null'
check_contains '"signature_verification_error": null'
check_contains '"checksum_verification_attempted": null'
check_contains '"checksum_verification_passed": null'
check_contains '"checksum_verification_error": null'
check_contains '"errors": ['

check_contains '"not an audit"'
check_contains '"release metadata is not security proof"'
check_contains '"asset name discovery is not checksum verification"'
check_contains '"checksum verification is integrity verification only"'
check_contains '"signature asset discovery is not signature verification"'
check_contains '"signature verification depends on configured public key"'
check_contains '"no reproducible build verification yet"'

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "RESULT: PASS"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
