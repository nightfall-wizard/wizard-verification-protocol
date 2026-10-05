#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP v0.3.0 DETACHED SIGNATURE PROCEDURE ==="

START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

MODE="${1:---dry-run}"

VERSION="0.3.0"
TAG="v0.3.0"
STAGE_DIR="target/wvp-release-v0.3.0-unsigned"
ASSET_NAME="wvp-release-check-v0.3.0-termux-android-aarch64"
ASSET="$STAGE_DIR/$ASSET_NAME"
CHECKSUM="$STAGE_DIR/$ASSET_NAME.sha256"
SIGNATURE="$STAGE_DIR/$ASSET_NAME.sig"
MANIFEST_JSON="$STAGE_DIR/STAGING-MANIFEST.json"

case "$MODE" in
  --dry-run|--sign)
    ;;
  *)
    echo "FAIL: unsupported mode: $MODE"
    echo "Usage:"
    echo "  $0 --dry-run"
    echo "  WVP_SIGNING_PRIVATE_KEY=/path/outside/repo/key.pem WVP_VERIFY_PUBLIC_KEY=/path/public.pem $0 --sign"
    exit 1
    ;;
esac

echo "Mode: $MODE"
echo

echo "=== VERIFY STAGED INPUTS ==="
test -x "$ASSET"
test -s "$CHECKSUM"
test -s "$MANIFEST_JSON"

if [ "$MODE" = "--dry-run" ] && [ -e "$SIGNATURE" ]; then
  echo "FAIL: signature file already exists during dry-run."
  exit 1
fi

echo "Asset: $ASSET"
echo "Checksum: $CHECKSUM"
echo "Manifest: $MANIFEST_JSON"
echo "Signature path: $SIGNATURE"
echo

echo "=== VERIFY CHECKSUM ==="
(
  cd "$STAGE_DIR"
  sha256sum -c "$ASSET_NAME.sha256"
)
echo

echo "=== VERIFY NO TAG OR RELEASE EXECUTION ==="
if git tag --list | grep -qx "$TAG"; then
  echo "FAIL: local $TAG tag already exists. This signing procedure must not create a tag."
  exit 1
fi
echo "No local $TAG tag found."
echo

echo "=== VERIFY MANIFEST BOUNDARY ==="
grep -q '"staging_only": true' "$MANIFEST_JSON"
grep -q '"tag_created": false' "$MANIFEST_JSON"
grep -q '"github_release_created": false' "$MANIFEST_JSON"
grep -q '"source_to_release_proof": false' "$MANIFEST_JSON"
grep -q '"reproducible_build_claim": false' "$MANIFEST_JSON"
grep -q '"binary_safety_claim": false' "$MANIFEST_JSON"
grep -q '"audit_claim": false' "$MANIFEST_JSON"
echo "Manifest boundary OK."
echo

if [ "$MODE" = "--dry-run" ]; then
  echo "=== DRY RUN ONLY ==="
  echo "No private signing key is required in dry-run."
  echo "No detached signature is created in dry-run."
  echo "No tag is created."
  echo "No GitHub release is created."
  echo

  END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
  END_EPOCH="$(date +%s)"
  DURATION="$((END_EPOCH - START_EPOCH))"

  echo "=== WVP v0.3.0 DETACHED SIGNATURE PROCEDURE RESULT ==="
  echo "RESULT: PASS"
  echo "Mode: dry-run"
  echo "Signature: not created"
  echo "Tag: not created"
  echo "GitHub release: not created"
  echo "Endzeit: $END_TS"
  echo "Dauer Sekunden: $DURATION"
  exit 0
fi

echo "=== SIGN MODE SAFETY CHECKS ==="

if [ -z "${WVP_SIGNING_PRIVATE_KEY:-}" ]; then
  echo "FAIL: WVP_SIGNING_PRIVATE_KEY is not set."
  echo "The private signing key path must be supplied through the environment and must live outside the repository."
  exit 1
fi

if [ -z "${WVP_VERIFY_PUBLIC_KEY:-}" ]; then
  echo "FAIL: WVP_VERIFY_PUBLIC_KEY is not set."
  echo "The public verification key path must be supplied so the detached signature can be verified immediately."
  exit 1
fi

PRIVATE_KEY_FILE="$WVP_SIGNING_PRIVATE_KEY"
PUBLIC_KEY_FILE="$WVP_VERIFY_PUBLIC_KEY"

REPO_ROOT="$(git rev-parse --show-toplevel)"

PRIVATE_KEY_REAL="$(python3 - "$PRIVATE_KEY_FILE" <<'PY'
from pathlib import Path
import sys
print(Path(sys.argv[1]).expanduser().resolve())
PY
)"

PUBLIC_KEY_REAL="$(python3 - "$PUBLIC_KEY_FILE" <<'PY'
from pathlib import Path
import sys
print(Path(sys.argv[1]).expanduser().resolve())
PY
)"

REPO_ROOT_REAL="$(python3 - "$REPO_ROOT" <<'PY'
from pathlib import Path
import sys
print(Path(sys.argv[1]).resolve())
PY
)"

python3 - "$PRIVATE_KEY_REAL" "$REPO_ROOT_REAL" <<'PY'
from pathlib import Path
import sys

key = Path(sys.argv[1])
repo = Path(sys.argv[2])

try:
    key.relative_to(repo)
    raise SystemExit("FAIL: private signing key is inside the repository.")
except ValueError:
    pass

print("Private signing key path is outside the repository.")
PY

test -s "$PRIVATE_KEY_REAL"
test -s "$PUBLIC_KEY_REAL"

if [ -e "$SIGNATURE" ] && [ "${WVP_OVERWRITE_SIGNATURE:-0}" != "1" ]; then
  echo "FAIL: signature already exists. Set WVP_OVERWRITE_SIGNATURE=1 to overwrite intentionally."
  exit 1
fi

echo "=== CREATE DETACHED SIGNATURE ==="
openssl dgst -sha256 -sign "$PRIVATE_KEY_REAL" -out "$SIGNATURE" "$ASSET"
test -s "$SIGNATURE"
echo "Signature created: $SIGNATURE"
echo

echo "=== VERIFY DETACHED SIGNATURE ==="
openssl dgst -sha256 -verify "$PUBLIC_KEY_REAL" -signature "$SIGNATURE" "$ASSET"
echo "Detached signature verification OK."
echo

echo "=== SIGNATURE FILE ==="
ls -la "$SIGNATURE"
echo

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "=== WVP v0.3.0 DETACHED SIGNATURE PROCEDURE RESULT ==="
echo "RESULT: PASS"
echo "Mode: sign"
echo "Signature: created and verified"
echo "Tag: not created"
echo "GitHub release: not created"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
