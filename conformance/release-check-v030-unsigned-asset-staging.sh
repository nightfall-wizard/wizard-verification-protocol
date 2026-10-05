#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP v0.3.0 UNSIGNED ASSET STAGING CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

STAGE_SCRIPT="scripts/release/stage-v030-unsigned-asset.sh"
STAGE_DOC="docs/release/WVP-V0.3-UNSIGNED-ASSET-STAGING.md"
STAGE_DIR="target/wvp-release-v0.3.0-unsigned"
ASSET_NAME="wvp-release-check-v0.3.0-termux-android-aarch64"

echo "=== VERIFY FILES EXIST ==="
test -s "$STAGE_SCRIPT"
test -s "$STAGE_DOC"
chmod +x "$STAGE_SCRIPT"
bash -n "$STAGE_SCRIPT"
echo "Required files exist."
echo

echo "=== RUN STAGING SCRIPT ==="
"$STAGE_SCRIPT"
echo

echo "=== VERIFY STAGED FILES ==="
test -x "$STAGE_DIR/$ASSET_NAME"
test -s "$STAGE_DIR/$ASSET_NAME.sha256"
test -s "$STAGE_DIR/STAGING-MANIFEST.json"

if [ -e "$STAGE_DIR/$ASSET_NAME.sig" ]; then
  echo "FAIL: signature exists during unsigned staging."
  exit 1
fi

echo "Staged files OK."
echo

echo "=== VERIFY CHECKSUM ==="
(
  cd "$STAGE_DIR"
  sha256sum -c "$ASSET_NAME.sha256"
)
echo "Checksum OK."
echo

echo "=== VERIFY MANIFEST TERMS ==="
grep -q '"package_version": "0.3.0"' "$STAGE_DIR/STAGING-MANIFEST.json"
grep -q '"planned_tag": "v0.3.0"' "$STAGE_DIR/STAGING-MANIFEST.json"
grep -q '"asset_name": "wvp-release-check-v0.3.0-termux-android-aarch64"' "$STAGE_DIR/STAGING-MANIFEST.json"
grep -q '"checksum_asset_name": "wvp-release-check-v0.3.0-termux-android-aarch64.sha256"' "$STAGE_DIR/STAGING-MANIFEST.json"
grep -q '"signature_asset_name": "wvp-release-check-v0.3.0-termux-android-aarch64.sig"' "$STAGE_DIR/STAGING-MANIFEST.json"
grep -q '"staging_only": true' "$STAGE_DIR/STAGING-MANIFEST.json"
grep -q '"tag_created": false' "$STAGE_DIR/STAGING-MANIFEST.json"
grep -q '"github_release_created": false' "$STAGE_DIR/STAGING-MANIFEST.json"
grep -q '"signature_created": false' "$STAGE_DIR/STAGING-MANIFEST.json"
grep -q '"source_to_release_proof": false' "$STAGE_DIR/STAGING-MANIFEST.json"
grep -q '"reproducible_build_claim": false' "$STAGE_DIR/STAGING-MANIFEST.json"
grep -q '"binary_safety_claim": false' "$STAGE_DIR/STAGING-MANIFEST.json"
grep -q '"audit_claim": false' "$STAGE_DIR/STAGING-MANIFEST.json"
echo "Manifest terms OK."
echo

echo "=== VERIFY DOC TERMS ==="
grep -q "This is not a published release" "$STAGE_DOC"
grep -q "This is not a tag" "$STAGE_DOC"
grep -q "This is not a signature event" "$STAGE_DOC"
grep -q "This is not a source-to-release proof" "$STAGE_DOC"
grep -q "This is not a reproducible-build proof" "$STAGE_DOC"
grep -q "This is not a binary-safety proof" "$STAGE_DOC"
grep -q "This is not an audit" "$STAGE_DOC"
grep -q "No v0.3.0 tag is created by this document" "$STAGE_DOC"
grep -q "No GitHub release is created by this document" "$STAGE_DOC"
grep -q "No signature is created by this document" "$STAGE_DOC"
echo "Doc terms OK."
echo

echo "=== VERIFY NO LOCAL v0.3.0 TAG CREATED ==="
if git tag --list | grep -qx "v0.3.0"; then
  echo "FAIL: v0.3.0 tag exists. Unsigned staging must not create a tag."
  exit 1
fi
echo "No local v0.3.0 tag found."
echo

echo "=== VERIFY NO FALSE 100 PERCENT CLAIM ==="
if grep -nE '100%|100 percent|fully complete|complete project' "$STAGE_DOC" "$STAGE_DIR/STAGING-MANIFEST.json"; then
  echo "FAIL: suspicious 100%/complete claim found."
  exit 1
fi
echo "No false 100% claim found."
echo

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "=== WVP v0.3.0 UNSIGNED ASSET STAGING CONFORMANCE RESULT ==="
echo "RESULT: PASS"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
