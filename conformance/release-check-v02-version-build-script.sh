#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP v0.2 VERSION AND BUILD SCRIPT CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

MANIFEST="reference/rust/wvp-release-check/Cargo.toml"
LOCKFILE="Cargo.lock"
SCRIPT="scripts/release/build-wvp-release-check-v020.sh"

test -s "$MANIFEST"
test -s "$LOCKFILE"
test -x "$SCRIPT"

grep -Fq 'version = "0.3.0"' "$MANIFEST"
grep -Fq 'name = "wvp-release-check"' "$LOCKFILE"
grep -Fq 'version = "0.3.0"' "$LOCKFILE"

grep -Fq 'EXPECTED_VERSION="0.2.0"' "$SCRIPT"
grep -Fq 'cargo build --release' "$SCRIPT"
grep -Fq 'sha256sum -c' "$SCRIPT"
grep -Fq 'openssl dgst -sha256 -sign' "$SCRIPT"
grep -Fq 'openssl dgst -sha256 -verify' "$SCRIPT"
grep -Fq 'No GitHub release created.' "$SCRIPT"
grep -Fq 'No assets uploaded.' "$SCRIPT"

if grep -Eq 'gh release (create|upload)|git tag|git push' "$SCRIPT"; then
  echo "FAIL: build script must not create tags, releases, uploads or pushes"
  exit 1
fi

cargo build --release --manifest-path "$MANIFEST"

BIN="target/release/wvp-release-check"
test -x "$BIN"

OUT="$("$BIN" --target nightfall-wizard/wizard-verification-protocol --json)"
echo "$OUT"
echo "$OUT" | grep -Fq '"version": "0.3.0"'

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "RESULT: PASS"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
