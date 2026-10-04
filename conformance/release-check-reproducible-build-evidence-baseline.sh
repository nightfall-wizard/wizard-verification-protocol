#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP REPRODUCIBLE-BUILD EVIDENCE BASELINE CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

DOC="docs/release/REPRODUCIBLE-BUILD-EVIDENCE-MODEL.md"
PLAN="docs/release/WVP-v0.3-REPRODUCIBLE-BUILD-EVIDENCE-PLAN.md"
SCRIPT="scripts/release/build-wvp-release-check-provenance.sh"
ASSET_NAME="wvp-release-check-termux-android-aarch64"

test -s "$DOC"
test -s "$PLAN"
test -x "$SCRIPT"

grep -Fq "This is not a reproducible-build proof." "$DOC"
grep -Fq "single-environment-build-provenance" "$DOC"
grep -Fq "reproducible_build_claim: false" "$DOC"
grep -Fq "Disallowed wording until proven" "$PLAN"

LOG="target/wvp-repro-evidence-baseline-$(date +%Y%m%d-%H%M%S).log"

"$SCRIPT" --allow-dirty | tee "$LOG"

OUT_DIR="$(grep -F 'Artifact directory:' "$LOG" | tail -n 1 | sed 's/^Artifact directory: //')"

if [ -z "$OUT_DIR" ] || [ ! -d "$OUT_DIR" ]; then
  echo "FAIL: artifact directory not found"
  exit 1
fi

test -s "$OUT_DIR/$ASSET_NAME"
test -s "$OUT_DIR/$ASSET_NAME.sha256"
test -s "$OUT_DIR/BUILD-PROVENANCE.json"

(
  cd "$OUT_DIR"
  sha256sum -c "$ASSET_NAME.sha256"
)

grep -Fq '"evidence_type": "single-environment-build-provenance"' "$OUT_DIR/BUILD-PROVENANCE.json"
grep -Fq '"not_a_reproducible_build_proof": true' "$OUT_DIR/BUILD-PROVENANCE.json"
grep -Fq '"reproducible_build_claim": false' "$OUT_DIR/BUILD-PROVENANCE.json"
grep -Fq '"binary_sha256":' "$OUT_DIR/BUILD-PROVENANCE.json"
grep -Fq '"cargo_lock_sha256":' "$OUT_DIR/BUILD-PROVENANCE.json"
grep -Fq '"git_commit":' "$OUT_DIR/BUILD-PROVENANCE.json"
grep -Fq '"rustc":' "$OUT_DIR/BUILD-PROVENANCE.json"
grep -Fq '"cargo":' "$OUT_DIR/BUILD-PROVENANCE.json"

OUT="$("$OUT_DIR/$ASSET_NAME" --target nightfall-wizard/wizard-verification-protocol --json)"
echo "$OUT"
echo "$OUT" | grep -Fq '"version": "0.2.0"'

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "RESULT: PASS"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
