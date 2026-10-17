#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP SAME-ENVIRONMENT REPEAT-BUILD CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

DOC="docs/release/SAME-ENVIRONMENT-REPEAT-BUILD-COMPARISON.md"
SCRIPT="scripts/release/compare-wvp-release-check-same-env.sh"
BINARY_NAME="wvp-release-check"

test -s "$DOC"
test -x "$SCRIPT"

grep -Fq "This is not a reproducible-build proof." "$DOC"
grep -Fq "same-environment-repeat-build-comparison" "$DOC"
grep -Fq "reproducible_build_claim: false" "$DOC"
grep -Fq "does not prove independent reproducibility" "$DOC"

LOG="target/wvp-same-env-repeat-build-$(date +%Y%m%d-%H%M%S).log"

"$SCRIPT" --allow-dirty | tee "$LOG"

OUT_DIR="$(grep -F 'Artifact directory:' "$LOG" | tail -n 1 | sed 's/^Artifact directory: //')"

if [ -z "$OUT_DIR" ] || [ ! -d "$OUT_DIR" ]; then
  echo "FAIL: artifact directory not found"
  exit 1
fi

JSON="$OUT_DIR/SAME-ENVIRONMENT-REPEAT-BUILD.json"

test -s "$JSON"
test -x "$OUT_DIR/build-a/$BINARY_NAME"
test -x "$OUT_DIR/build-b/$BINARY_NAME"

grep -Fq '"evidence_type": "same-environment-repeat-build-comparison"' "$JSON"
grep -Fq '"reproducible_build_claim": false' "$JSON"
grep -Fq '"not_a_reproducible_build_proof": true' "$JSON"
grep -Fq '"independent_environment_evidence": false' "$JSON"
grep -Fq '"binary_sha256_match": true' "$JSON"
grep -Fq '"binary_size_bytes_match": true' "$JSON"
grep -Fq '"build_count": 2' "$JSON"
grep -Fq '"git_commit":' "$JSON"
grep -Fq '"cargo_lock_sha256":' "$JSON"
grep -Fq '"rustc":' "$JSON"
grep -Fq '"cargo":' "$JSON"

SHA_A="$(sha256sum "$OUT_DIR/build-a/$BINARY_NAME" | awk '{print $1}')"
SHA_B="$(sha256sum "$OUT_DIR/build-b/$BINARY_NAME" | awk '{print $1}')"

echo "SHA_A=$SHA_A"
echo "SHA_B=$SHA_B"

if [ "$SHA_A" != "$SHA_B" ]; then
  echo "FAIL: same-environment build hashes differ"
  exit 1
fi

OUT_A="$("$OUT_DIR/build-a/$BINARY_NAME" --target nightfall-wizard/wizard-verification-protocol --json)"
OUT_B="$("$OUT_DIR/build-b/$BINARY_NAME" --target nightfall-wizard/wizard-verification-protocol --json)"

echo "$OUT_A"
echo "$OUT_B"

echo "$OUT_A" | grep -Fq '"version": "0.4.0"'
echo "$OUT_B" | grep -Fq '"version": "0.4.0"'

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "RESULT: PASS"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
