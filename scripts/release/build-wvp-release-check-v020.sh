#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP v0.2.0 LOCAL RELEASE BUILD ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

EXPECTED_VERSION="0.2.0"
CRATE_MANIFEST="reference/rust/wvp-release-check/Cargo.toml"
PRIVATE_KEY="${WVP_RELEASE_PRIVATE_KEY:-$HOME/.wvp-release-signing/wvp-release-signing-private-rsa3072.pem}"
PUBLIC_KEY="keys/release/wvp-release-signing-public.pem"
ASSET_NAME="wvp-release-check-termux-android-aarch64"
TARGET_REPO="${WVP_RELEASE_TARGET_REPO:-nightfall-wizard/wizard-verification-protocol}"

echo "Expected version: $EXPECTED_VERSION"
echo "Target repo for self-check: $TARGET_REPO"

if ! grep -Fq 'version = "0.2.0"' "$CRATE_MANIFEST"; then
  echo "FAIL: Cargo.toml is not at version 0.2.0"
  exit 1
fi

if [ ! -s "$PRIVATE_KEY" ]; then
  echo "FAIL: private signing key missing outside repo"
  exit 1
fi

REPO_ROOT="$(git rev-parse --show-toplevel)"
case "$PRIVATE_KEY" in
  "$REPO_ROOT"/*)
    echo "FAIL: private signing key is inside repository"
    exit 1
    ;;
esac

if [ ! -s "$PUBLIC_KEY" ]; then
  echo "FAIL: public verification key missing"
  exit 1
fi

OUT_DIR="target/wvp-release-build-v${EXPECTED_VERSION}-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUT_DIR"

echo "=== BUILD RELEASE BINARY ==="
cargo build --release --manifest-path "$CRATE_MANIFEST"

SRC_BIN="target/release/wvp-release-check"
ASSET="$OUT_DIR/$ASSET_NAME"
CHECKSUM="$OUT_DIR/$ASSET_NAME.sha256"
SIGNATURE="$OUT_DIR/$ASSET_NAME.sig"

if [ ! -x "$SRC_BIN" ]; then
  echo "FAIL: release binary missing: $SRC_BIN"
  exit 1
fi

cp -p "$SRC_BIN" "$ASSET"
chmod 0755 "$ASSET"

echo "=== VERIFY BINARY VERSION ==="
VERSION_JSON="$("$ASSET" --target "$TARGET_REPO" --json)"
echo "$VERSION_JSON" | grep -Fq '"version": "0.2.0"'

echo "=== CREATE CHECKSUM ==="
(
  cd "$OUT_DIR"
  sha256sum "$ASSET_NAME" > "$ASSET_NAME.sha256"
  sha256sum -c "$ASSET_NAME.sha256"
)

echo "=== CREATE DETACHED SIGNATURE ==="
openssl dgst -sha256 -sign "$PRIVATE_KEY" -out "$SIGNATURE" "$ASSET"

echo "=== VERIFY DETACHED SIGNATURE ==="
openssl dgst -sha256 -verify "$PUBLIC_KEY" -signature "$SIGNATURE" "$ASSET"

echo "=== RELEASE BUILD ARTIFACTS ==="
ls -l "$OUT_DIR"

echo "Artifact directory: $OUT_DIR"

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "RESULT: PASS"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
echo "No tag created."
echo "No GitHub release created."
echo "No assets uploaded."
