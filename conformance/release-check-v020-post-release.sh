#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP v0.2.0 POST-RELEASE CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

TAG="v0.2.0"
TARGET_REPO="${WVP_TARGET_REPO:-nightfall-wizard/wizard-verification-protocol}"
PUBLIC_KEY="keys/release/wvp-release-signing-public.pem"
ASSET_NAME="wvp-release-check-termux-android-aarch64"
DOC="docs/release/WVP-v0.2.0-POST-RELEASE-VERIFICATION.md"

test -s "$DOC"
test -s "$PUBLIC_KEY"

grep -Fq "WVP v0.2.0 has been released." "$DOC"
grep -Fq '"latest_release_tag": "v0.2.0"' "$DOC"
grep -Fq '"signature_verification_passed": true' "$DOC"
grep -Fq "This is not an audit." "$DOC"

gh release view "$TAG" --repo "$TARGET_REPO" >/dev/null

ASSET_COUNT="$(gh release view "$TAG" --repo "$TARGET_REPO" --json assets --jq '.assets | length')"
echo "Asset count: $ASSET_COUNT"

if [ "$ASSET_COUNT" -ne 3 ]; then
  echo "FAIL: expected exactly 3 assets"
  exit 1
fi

gh release view "$TAG" --repo "$TARGET_REPO" --json assets --jq '.assets[].name' | sort

TMP_DIR="target/wvp-v020-post-release-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$TMP_DIR"

gh release download "$TAG" \
  --repo "$TARGET_REPO" \
  --dir "$TMP_DIR" \
  --pattern "$ASSET_NAME*"

(
  cd "$TMP_DIR"
  sha256sum -c "$ASSET_NAME.sha256"
)

openssl dgst -sha256 \
  -verify "$PUBLIC_KEY" \
  -signature "$TMP_DIR/$ASSET_NAME.sig" \
  "$TMP_DIR/$ASSET_NAME"

cargo build --release --manifest-path reference/rust/wvp-release-check/Cargo.toml

JSON_OUT="$TMP_DIR/wvp-self-check.json"
target/release/wvp-release-check \
  --target "$TARGET_REPO" \
  --json \
  --live | tee "$JSON_OUT"

grep -Fq '"version": "0.4.0"' "$JSON_OUT"
# WVP-V020-HISTORICAL-PLUS-CURRENT-V040
# Historical v0.2 checks above remain strict.
LATEST="$(gh api "repos/$TARGET_REPO/releases?per_page=1" --jq '.[0].tag_name')"
META="$(gh release view "$LATEST" -R "$TARGET_REPO" --json assets,body)"
COUNT="$(printf '%s' "$META" | jq '.assets | length')"

if [ "$COUNT" -eq 0 ]; then
  printf '%s' "$META" | jq -e '.body | contains("Source-only release:")' >/dev/null
  jq -e '
    .status == "WARN" and
    .github.checksum_asset_count == 0 and
    .github.signature_asset_count == 0 and
    .github.signature_verification_attempted == false
  ' "$JSON_OUT" >/dev/null
else
  jq -e '
    .status == "INFO" and
    .github.checksum_verification_passed == true and
    .github.signature_verification_passed == true and
    .github.signature_verification_error == null
  ' "$JSON_OUT" >/dev/null
fi

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "RESULT: PASS"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
