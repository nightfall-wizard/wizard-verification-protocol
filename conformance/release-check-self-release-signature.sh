#!/usr/bin/env bash
set -euo pipefail

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

test -s "$PUB"

DL_DIR="target/wvp-self-release-signature-$TAG-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$DL_DIR"

echo "Repo: $REPO"
echo "Tag: $TAG"
echo "Download dir: $DL_DIR"

gh release download "$TAG" --repo "$REPO" --pattern "$ASSET" --dir "$DL_DIR"
gh release download "$TAG" --repo "$REPO" --pattern "$CHECKSUM_ASSET" --dir "$DL_DIR"
gh release download "$TAG" --repo "$REPO" --pattern "$SIG_ASSET" --dir "$DL_DIR"

echo "Downloaded files:"
find "$DL_DIR" -maxdepth 1 -type f -print | sort

(
  cd "$DL_DIR"
  sha256sum -c "$CHECKSUM_ASSET"
)

openssl dgst -sha256 \
  -verify "$PUB" \
  -signature "$DL_DIR/$SIG_ASSET" \
  "$DL_DIR/$ASSET"

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "RESULT: PASS"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
