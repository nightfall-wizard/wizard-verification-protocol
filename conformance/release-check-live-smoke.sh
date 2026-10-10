#!/usr/bin/env bash
set -euo pipefail
# WVP-LIVE-RELEASE-POLICY-V040

cd "$(dirname "${BASH_SOURCE[0]}")/.."

TARGET="${WVP_TARGET:-nightfall-wizard/wizard-verification-protocol}"

TAG="$(gh api "repos/$TARGET/releases?per_page=1" --jq '.[0].tag_name')"

[ -n "$TAG" ] || {
  echo 'FAIL: No latest release'
  exit 1
}

META="$(gh release view "$TAG" -R "$TARGET" --json assets,body)"
COUNT="$(printf '%s' "$META" | jq '.assets | length')"

OUT="$(cargo run --quiet --manifest-path reference/rust/wvp-release-check/Cargo.toml -- --target "$TARGET" --json --live)"

printf '%s\n' "$OUT"

printf '%s' "$OUT" | jq -e --arg tag "$TAG" --argjson n "$COUNT" '
  .live_inspection == true and
  .github.repository_found == true and
  .github.latest_release_found == true and
  .github.latest_release_tag == $tag and
  .github.latest_release_asset_count == $n and
  (.limitations | index("not an audit") != null)
' >/dev/null

if [ "$COUNT" -eq 0 ]; then
  printf '%s' "$META" | jq -e '.body | contains("Source-only release:")' >/dev/null

  printf '%s' "$OUT" | jq -e '
    .status == "WARN" and
    .github.checksum_asset_count == 0 and
    .github.signature_asset_count == 0 and
    .github.checksum_verification_attempted == false and
    .github.signature_verification_attempted == false
  ' >/dev/null

  echo 'PASS (BOUNDED): Source-only; NO binary integrity or signature proof'
else
  printf '%s' "$OUT" | jq -e '
    .status == "INFO" and
    .github.checksum_asset_count == 1 and
    .github.signature_asset_count == 1 and
    .github.checksum_verification_attempted == true and
    .github.checksum_verification_passed == true and
    .github.signature_verification_attempted == true and
    .github.signature_verification_passed == true and
    .github.signature_verification_error == null
  ' >/dev/null

  echo 'PASS: Published binary checksum and signature verified'
fi
