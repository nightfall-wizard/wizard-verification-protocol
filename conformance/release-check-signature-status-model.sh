#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP SIGNATURE STATUS MODEL CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

DOC="docs/release/SIGNATURE-STATUS-MODEL.md"
MODEL="reference/rust/wvp-release-check/src/model.rs"
CLASSIFY="reference/rust/wvp-release-check/src/classify.rs"

test -s "$DOC"
test -s "$MODEL"
test -s "$CLASSIFY"

grep -Fq "A discovered signature asset is not the same as a verified signature" "$DOC"
grep -Fq 'signature_verification_attempted' "$DOC"
grep -Fq 'signature_verification_passed' "$DOC"
grep -Fq 'signature verification attempted and failed: `FAIL`' "$DOC"
grep -Fq 'checksum passed and signature passed: eligible for `INFO`' "$DOC"

grep -Fq 'signature_verification_attempted: Option<bool>' "$MODEL"
grep -Fq 'signature_verification_passed: Option<bool>' "$MODEL"
grep -Fq 'signature_verification_error: Option<String>' "$MODEL"
grep -Fq 'status_warns_when_signature_asset_exists_but_not_verified' "$CLASSIFY"
grep -Fq 'status_fails_when_signature_verification_fails' "$CLASSIFY"
grep -Fq 'status_info_when_checksum_and_signature_verification_pass' "$CLASSIFY"

cargo test --workspace --locked signature

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "RESULT: PASS"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
