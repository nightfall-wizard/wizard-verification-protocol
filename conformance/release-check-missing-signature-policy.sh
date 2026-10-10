#!/usr/bin/env bash
set -euo pipefail
# WVP-SIGNATURE-POLICY-V040

cd "$(dirname "${BASH_SOURCE[0]}")/.."

TARGET="${WVP_TARGET:-nightfall-wizard/wizard-verification-protocol}"
TAG="$(gh api "repos/$TARGET/releases?per_page=1" --jq '.[0].tag_name')"
META="$(gh release view "$TAG" -R "$TARGET" --json assets,body)"
COUNT="$(printf '%s' "$META" | jq '.assets | length')"

OUT="$(cargo run --quiet --manifest-path reference/rust/wvp-release-check/Cargo.toml -- --target "$TARGET" --json --live)"

if [ "$COUNT" -eq 0 ]; then
  printf '%s' "$META" | jq -e '.body | contains("Source-only release:")' >/dev/null
  printf '%s' "$OUT" | jq -e '
    .status == "WARN" and
    .github.signature_asset_count == 0 and
    .github.signature_verification_attempted == false and
    .github.signature_verification_passed == null
  ' >/dev/null
  echo 'PASS: Source-only release is WARN, never VERIFIED'
else
  printf '%s' "$OUT" | jq -e '
    .status == "INFO" and
    .github.signature_asset_count == 1 and
    .github.signature_verification_attempted == true and
    .github.signature_verification_passed == true
  ' >/dev/null
  echo 'PASS: Binary signature verified'
fi
