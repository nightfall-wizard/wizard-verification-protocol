#!/usr/bin/env bash
set -Eeuo pipefail

echo "=== WVP SELF RELEASE SIGNATURE CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

REPO="${GH_REPO:-nightfall-wizard/wizard-verification-protocol}"
TAG="${WVP_RELEASE_TAG:-v0.2.0}"
ASSET="wvp-release-check-termux-android-aarch64"
CHECKSUM_ASSET="$ASSET.sha256"
SIG_ASSET="$ASSET.sig"
PUB="keys/release/wvp-release-signing-public.pem"

fail() {
  echo "RESULT: FAIL"
  echo "Stage: ${1:-unknown}"
  echo "Reason: ${2:-unknown}"
  exit 1
}

need() {
  command -v "$1" >/dev/null 2>&1 || fail "tool-check" "missing command: $1"
}

need gh
need openssl
need sha256sum
need find
need sort
need awk

[ -s "$PUB" ] || fail "public-key-check" "missing public verification key: $PUB"

echo "Repo: $REPO"
echo "Tag: $TAG"
echo "Asset: $ASSET"
echo "Checksum asset: $CHECKSUM_ASSET"
echo "Signature asset: $SIG_ASSET"
echo "Public key: $PUB"

echo "Tool versions:"
gh --version | head -n 1 || true
openssl version || true

PUB_SHA256="$(sha256sum "$PUB" | awk '{print $1}')"
PUB_FP="$(openssl pkey -pubin -in "$PUB" -outform DER 2>/dev/null | sha256sum | awk '{print $1}')"

echo "Public key file sha256: $PUB_SHA256"
echo "Public key DER fingerprint sha256: $PUB_FP"

DL_DIR="target/wvp-self-release-signature-$TAG-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$DL_DIR"
echo "Download dir: $DL_DIR"

download_one() {
  local pattern="$1"
  echo "Downloading: $pattern"
  gh release download "$TAG" \
    --repo "$REPO" \
    --pattern "$pattern" \
    --dir "$DL_DIR" \
    --clobber \
    || fail "download" "gh release download failed for pattern: $pattern"
}

download_one "$ASSET"
download_one "$CHECKSUM_ASSET"
download_one "$SIG_ASSET"

echo "Downloaded files:"
find "$DL_DIR" -maxdepth 1 -type f -print | sort

[ -s "$DL_DIR/$ASSET" ] || fail "asset-presence" "missing asset: $ASSET"
[ -s "$DL_DIR/$CHECKSUM_ASSET" ] || fail "checksum-presence" "missing checksum asset: $CHECKSUM_ASSET"
[ -s "$DL_DIR/$SIG_ASSET" ] || fail "signature-presence" "missing signature asset: $SIG_ASSET"

echo "Downloaded sha256:"
sha256sum "$DL_DIR/$ASSET" "$DL_DIR/$CHECKSUM_ASSET" "$DL_DIR/$SIG_ASSET"

echo "Checksum file content:"
cat "$DL_DIR/$CHECKSUM_ASSET"

echo "Running checksum verification..."
(
  cd "$DL_DIR"
  sha256sum -c "$CHECKSUM_ASSET"
) || fail "checksum-verification" "sha256sum -c failed"

echo "Running detached signature verification..."
VERIFY_OUTPUT="$(
  openssl dgst -sha256 \
    -verify "$PUB" \
    -signature "$DL_DIR/$SIG_ASSET" \
    "$DL_DIR/$ASSET" 2>&1
)" || {
  echo "$VERIFY_OUTPUT"
  fail "signature-verification" "openssl detached signature verification failed"
}

echo "$VERIFY_OUTPUT"

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "RESULT: PASS"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
