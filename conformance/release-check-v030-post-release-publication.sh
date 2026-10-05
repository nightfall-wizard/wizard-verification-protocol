#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP v0.3.0 POST-RELEASE PUBLICATION CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

TARGET_REPO="nightfall-wizard/wizard-verification-protocol"
TAG="v0.3.0"
EXPECTED_HEAD="538460a967936b70792e4d275d50ee3b2a0b90c4"
EXPECTED_ASSET_SHA256="e77aee158c8a3997c17d45dc51f9192839103b9eef0bf59cc3abb312b963e1fb"

ASSET_NAME="wvp-release-check-v0.3.0-termux-android-aarch64"
CHECKSUM_NAME="$ASSET_NAME.sha256"
SIGNATURE_NAME="$ASSET_NAME.sig"
PUBLIC_KEY_NAME="wvp-release-signing-public-rsa3072.pem"

WORK_DIR="target/wvp-v0.3.0-post-release-conformance"
DOWNLOAD_DIR="$WORK_DIR/downloaded"
RELEASE_JSON="$WORK_DIR/release.json"

mkdir -p "$WORK_DIR" "$DOWNLOAD_DIR"

echo "=== VERIFY GITHUB CLI ==="
command -v gh >/dev/null
echo "GitHub CLI exists."

echo "=== VERIFY RELEASE EXISTS ==="
gh release view "$TAG" --repo "$TARGET_REPO" --json assets,tagName,name,isDraft,isPrerelease,url,targetCommitish > "$RELEASE_JSON"
cat "$RELEASE_JSON"

echo "=== VERIFY RELEASE JSON TERMS ==="
python3 - "$RELEASE_JSON" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))

required = sorted([
    "wvp-release-check-v0.3.0-termux-android-aarch64",
    "wvp-release-check-v0.3.0-termux-android-aarch64.sha256",
    "wvp-release-check-v0.3.0-termux-android-aarch64.sig",
    "wvp-release-signing-public-rsa3072.pem",
])

names = sorted(asset["name"] for asset in data["assets"])
print("Release assets:")
for name in names:
    print("-", name)

missing = [name for name in required if name not in names]
if missing:
    raise SystemExit(f"missing required release assets: {missing}")

if data.get("tagName") != "v0.3.0":
    raise SystemExit("wrong tagName")

if data.get("isDraft") is not False:
    raise SystemExit("release is draft")

print("Release JSON terms OK.")
PY

echo "=== DOWNLOAD RELEASE ASSETS ==="
mkdir -p "$DOWNLOAD_DIR"
rm -f \
  "$DOWNLOAD_DIR/$ASSET_NAME" \
  "$DOWNLOAD_DIR/$CHECKSUM_NAME" \
  "$DOWNLOAD_DIR/$SIGNATURE_NAME" \
  "$DOWNLOAD_DIR/$PUBLIC_KEY_NAME"

gh release download "$TAG" --repo "$TARGET_REPO" --dir "$DOWNLOAD_DIR" --pattern "$ASSET_NAME"
gh release download "$TAG" --repo "$TARGET_REPO" --dir "$DOWNLOAD_DIR" --pattern "$CHECKSUM_NAME"
gh release download "$TAG" --repo "$TARGET_REPO" --dir "$DOWNLOAD_DIR" --pattern "$SIGNATURE_NAME"
gh release download "$TAG" --repo "$TARGET_REPO" --dir "$DOWNLOAD_DIR" --pattern "$PUBLIC_KEY_NAME"

test -s "$DOWNLOAD_DIR/$ASSET_NAME"
test -s "$DOWNLOAD_DIR/$CHECKSUM_NAME"
test -s "$DOWNLOAD_DIR/$SIGNATURE_NAME"
test -s "$DOWNLOAD_DIR/$PUBLIC_KEY_NAME"

echo "=== VERIFY ASSET HASH ==="
ACTUAL_ASSET_SHA256="$(sha256sum "$DOWNLOAD_DIR/$ASSET_NAME" | awk '{print $1}')"
echo "Asset SHA256: $ACTUAL_ASSET_SHA256"

if [ "$ACTUAL_ASSET_SHA256" != "$EXPECTED_ASSET_SHA256" ]; then
  echo "FAIL: asset SHA256 mismatch."
  exit 1
fi

echo "=== VERIFY PUBLIC KEY IS NOT PRIVATE MATERIAL ==="
PRIVATE_MARKER_RE='BEGIN (PGP |OPENSSH |RSA |EC |DSA )?PR''IVATE KEY|AGE-SE''CRET-KEY-'
if grep -qE "$PRIVATE_MARKER_RE" "$DOWNLOAD_DIR/$PUBLIC_KEY_NAME"; then
  echo "FAIL: public key asset contains private-key-like material."
  exit 1
fi
grep -qE 'BEGIN PUBLIC KEY' "$DOWNLOAD_DIR/$PUBLIC_KEY_NAME"

echo "=== VERIFY CHECKSUM ==="
(
  cd "$DOWNLOAD_DIR"
  sha256sum -c "$CHECKSUM_NAME"
)

echo "=== VERIFY DETACHED SIGNATURE ==="
openssl dgst -sha256 \
  -verify "$DOWNLOAD_DIR/$PUBLIC_KEY_NAME" \
  -signature "$DOWNLOAD_DIR/$SIGNATURE_NAME" \
  "$DOWNLOAD_DIR/$ASSET_NAME"

echo "=== VERIFY REMOTE TAG EXISTS ==="
if ! git ls-remote --tags origin "refs/tags/$TAG" | grep -q "$TAG"; then
  echo "FAIL: remote tag missing."
  exit 1
fi

echo "=== VERIFY NON-CLAIM BOUNDARY ==="
DOC="docs/release/WVP-V0.3-POST-RELEASE-VERIFICATION.md"
test -s "$DOC"
grep -q "not prove" "$DOC"
grep -q "reproducible build" "$DOC"
grep -q "source-to-release" "$DOC"
grep -q "binary safety" "$DOC"
grep -q "audit" "$DOC"

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo
echo "=== WVP v0.3.0 POST-RELEASE PUBLICATION CONFORMANCE RESULT ==="
echo "RESULT: PASS"
echo "Release exists."
echo "Remote tag exists."
echo "Required assets exist."
echo "Checksum verifies."
echo "Detached signature verifies."
echo "Public verification key is published."
echo "No reproducible-build/source-to-release/binary-safety/audit claim is made."
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
