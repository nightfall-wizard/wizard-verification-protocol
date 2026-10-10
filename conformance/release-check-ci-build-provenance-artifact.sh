#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP CI BUILD PROVENANCE ARTIFACT CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

DOC="docs/release/CI-BUILD-PROVENANCE-ARTIFACTS.md"
SCRIPT="scripts/release/generate-ci-build-provenance-artifact.sh"
WORKFLOW=".github/workflows/ci.yml"

test -s "$DOC"
test -x "$SCRIPT"
test -s "$WORKFLOW"

grep -Fq "This is not a reproducible-build proof." "$DOC"
grep -Fq "ci-build-provenance-artifact-generation" "$DOC"
grep -Fq "reproducible_build_claim: false" "$DOC"
grep -Fq "CI artifact does not prove that a release asset was built from source" "$DOC"

grep -Fq "WVP CI build provenance artifact generation" "$WORKFLOW"
grep -Fq "actions/upload-artifact@v4" "$WORKFLOW"
grep -Fq "wvp-ci-build-provenance" "$WORKFLOW"
grep -Fq "if-no-files-found: error" "$WORKFLOW"

LOG="target/wvp-ci-build-provenance-artifact-$(date +%Y%m%d-%H%M%S).log"

"$SCRIPT" --allow-dirty | tee "$LOG"

OUT_DIR="$(grep -F 'Artifact directory:' "$LOG" | tail -n 1 | sed 's/^Artifact directory: //')"

if [ -z "$OUT_DIR" ] || [ ! -d "$OUT_DIR" ]; then
  echo "FAIL: CI build provenance artifact directory not found"
  exit 1
fi

test -s "$OUT_DIR/CI-BUILD-PROVENANCE-MANIFEST.json"
test -s "$OUT_DIR/BUILD-PROVENANCE.json"
test -s "$OUT_DIR/BUILD-ENVIRONMENT-CLASSIFICATION.json"
test -x "$OUT_DIR/wvp-release-check-native"
test -s "$OUT_DIR/wvp-release-check-native.sha256"
test -s "$OUT_DIR/build-provenance.log"
test -s "$OUT_DIR/environment-classification.log"

(
  cd "$OUT_DIR"
  sha256sum -c wvp-release-check-native.sha256
)

python3 - "$OUT_DIR/CI-BUILD-PROVENANCE-MANIFEST.json" <<'PY'
import json
import sys

with open(sys.argv[1], "r", encoding="utf-8") as f:
    data = json.load(f)

assert data["evidence_type"] == "ci-build-provenance-artifact-generation"
assert data["reproducible_build_claim"] is False
assert data["not_a_reproducible_build_proof"] is True
assert data["independent_environment_evidence"] is False
assert data["source_to_release_proof"] is False
assert data["artifact_ready_for_upload"] is True
assert data["environment_class"] in {
    "android-termux-aarch64",
    "github-actions-linux-x86_64",
    "linux-aarch64",
    "linux-x86_64",
    "unknown",
}
assert data["outputs"]["native_binary_name"] == "wvp-release-check-native"
assert data["outputs"]["native_binary_sha256"]
assert data["outputs"]["native_binary_size_bytes"] > 0
PY

OUT="$("$OUT_DIR/wvp-release-check-native" --target nightfall-wizard/wizard-verification-protocol --json)"
echo "$OUT"
echo "$OUT" | grep -Fq '"version": "0.4.0"'

if [ "${GITHUB_ACTIONS:-false}" = "true" ]; then
  python3 - "$OUT_DIR/CI-BUILD-PROVENANCE-MANIFEST.json" <<'PY'
import json
import sys
with open(sys.argv[1], "r", encoding="utf-8") as f:
    data = json.load(f)
assert data["environment_class"] == "github-actions-linux-x86_64", data["environment_class"]
PY
fi

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "RESULT: PASS"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
