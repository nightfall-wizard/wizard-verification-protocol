#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP SELF RELEASE CHECKSUM CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

REPO="nightfall-wizard/wizard-verification-protocol"
TAG="$(gh release list --repo "$REPO" --limit 1 --json tagName --jq '.[0].tagName')"

if [ -z "$TAG" ] || [ "$TAG" = "null" ]; then
  echo "FAIL: no GitHub release tag found"
  false
fi

DL_DIR="$ROOT/target/wvp-self-release-checksum-$TAG-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$DL_DIR"

echo "Repo: $REPO"
echo "Tag: $TAG"
echo "Download dir: $DL_DIR"

gh release download "$TAG" --repo "$REPO" --dir "$DL_DIR" --clobber

echo "Downloaded files:"
find "$DL_DIR" -maxdepth 1 -type f -print | sort

SHA_FILE="$(find "$DL_DIR" -maxdepth 1 -type f -name '*.sha256' | head -n 1)"

if [ -z "$SHA_FILE" ]; then
  echo "FAIL: no checksum asset found"
  false
fi

echo "Checksum file:"
cat "$SHA_FILE"

(
  cd "$DL_DIR"
  sha256sum -c "$(basename "$SHA_FILE")"
)

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "RESULT: PASS"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
