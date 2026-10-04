#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP BUILD PROVENANCE COMPARISON FORMAT CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

DOC="docs/release/LINUX-VS-ANDROID-BUILD-EVIDENCE-COMPARISON-FORMAT.md"
GEN_SCRIPT="scripts/release/generate-ci-build-provenance-artifact.sh"
COMPARE_SCRIPT="scripts/release/compare-build-provenance-artifacts.sh"
WORKFLOW=".github/workflows/ci.yml"

test -s "$DOC"
test -x "$GEN_SCRIPT"
test -x "$COMPARE_SCRIPT"
test -s "$WORKFLOW"

grep -Fq "This is not a reproducible-build proof." "$DOC"
grep -Fq "build-provenance-artifact-comparison" "$DOC"
grep -Fq "reproducible_build_claim: false" "$DOC"
grep -Fq "A Linux x86_64 native binary and an Android aarch64 native binary are not expected to be byte-identical." "$DOC"

grep -Fq "WVP build provenance comparison format conformance" "$WORKFLOW"

LEFT_DIR="target/wvp-comparison-left"
RIGHT_DIR="target/wvp-comparison-right"
OUT_DIR="target/wvp-comparison-format-output"

rm -rf "$LEFT_DIR" "$RIGHT_DIR" "$OUT_DIR"

LEFT_LOG="target/wvp-comparison-left.log"
RIGHT_LOG="target/wvp-comparison-right.log"
mkdir -p target

"$GEN_SCRIPT" --allow-dirty > "$LEFT_LOG"
cp -a target/wvp-ci-build-provenance "$LEFT_DIR"

"$GEN_SCRIPT" --allow-dirty > "$RIGHT_LOG"
cp -a target/wvp-ci-build-provenance "$RIGHT_DIR"

test -s "$LEFT_LOG"
test -s "$RIGHT_LOG"

"$COMPARE_SCRIPT" "$LEFT_DIR" "$RIGHT_DIR" "$OUT_DIR"

JSON="$OUT_DIR/BUILD-PROVENANCE-COMPARISON.json"

test -s "$JSON"

grep -Fq '"evidence_type": "build-provenance-artifact-comparison"' "$JSON"
grep -Fq '"reproducible_build_claim": false' "$JSON"
grep -Fq '"not_a_reproducible_build_proof": true' "$JSON"
grep -Fq '"source_to_release_proof": false' "$JSON"
grep -Fq '"binary_safety_proof": false' "$JSON"
grep -Fq '"format_checks_passed": true' "$JSON"
grep -Fq '"can_claim_reproducible_build": false' "$JSON"
grep -Fq '"binary_sha256_match": true' "$JSON"
grep -Fq '"package_version_match": true' "$JSON"
grep -Fq '"cargo_lock_hash_match": true' "$JSON"

python3 - "$JSON" <<'PY'
import json
import sys

with open(sys.argv[1], "r", encoding="utf-8") as f:
    data = json.load(f)

assert data["evidence_type"] == "build-provenance-artifact-comparison"
assert data["reproducible_build_claim"] is False
assert data["not_a_reproducible_build_proof"] is True
assert data["source_to_release_proof"] is False
assert data["binary_safety_proof"] is False
assert data["comparison"]["format_checks_passed"] is True
assert data["interpretation"]["can_claim_reproducible_build"] is False
assert data["left"]["environment_class"] in {
    "android-termux-aarch64",
    "github-actions-linux-x86_64",
    "linux-aarch64",
    "linux-x86_64",
    "unknown",
}
assert data["right"]["environment_class"] in {
    "android-termux-aarch64",
    "github-actions-linux-x86_64",
    "linux-aarch64",
    "linux-x86_64",
    "unknown",
}
assert data["left"]["binary_sha256"]
assert data["right"]["binary_sha256"]
assert data["left"]["binary_size_bytes"] > 0
assert data["right"]["binary_size_bytes"] > 0
PY

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "RESULT: PASS"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
