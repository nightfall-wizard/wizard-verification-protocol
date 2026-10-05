#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP ANDROID VS CI BUILD PROVENANCE CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

TARGET_REPO="${WVP_TARGET_REPO:-nightfall-wizard/wizard-verification-protocol}"
COMMIT_SHA="${WVP_COMMIT_SHA:-$(git rev-parse HEAD)}"
SHORT_SHA="$(printf '%s' "$COMMIT_SHA" | cut -c1-7)"
ARTIFACT_NAME="wvp-ci-build-provenance-$COMMIT_SHA"

BASE_DIR="target/wvp-android-vs-ci-conformance-$SHORT_SHA-$(date +%Y%m%d-%H%M%S)"
ANDROID_DIR="$BASE_DIR/android"
CI_DIR="$BASE_DIR/ci"
OUT_DIR="$BASE_DIR/comparison"
COMPARISON_JSON="$OUT_DIR/BUILD-PROVENANCE-COMPARISON.json"

echo "Repo: $TARGET_REPO"
echo "Commit: $COMMIT_SHA"
echo "Expected CI artifact: $ARTIFACT_NAME"
echo "Output directory: $BASE_DIR"
echo

echo "=== PRECONDITION: CLEAN SOURCE TREE ==="
git status --short --branch
if [ -n "$(git status --porcelain)" ]; then
  echo "FAIL: source tree is dirty."
  echo "Reason: Android-vs-CI evidence must not be generated from an uncommitted tree."
  exit 1
fi
echo "Source tree clean."
echo

echo "=== PRECONDITION: COMMIT MATCHES LOCAL HEAD ==="
LOCAL_HEAD="$(git rev-parse HEAD)"
echo "Local HEAD: $LOCAL_HEAD"
if [ "$LOCAL_HEAD" != "$COMMIT_SHA" ]; then
  echo "FAIL: WVP_COMMIT_SHA does not match local HEAD."
  echo "This conformance command only compares the checked-out commit."
  exit 1
fi
echo "Commit matches local HEAD."
echo

echo "=== PRECONDITION: GH AUTH ==="
gh auth status
echo

echo "=== FIND SUCCESSFUL CI RUN ==="
if [ -n "${WVP_RUN_ID:-}" ]; then
  RUN_ID="$WVP_RUN_ID"
  echo "Using WVP_RUN_ID: $RUN_ID"
else
  RUN_ID="$(gh run list \
    --repo "$TARGET_REPO" \
    --limit 30 \
    --json databaseId,headSha,conclusion,status,event \
    --jq ".[] | select(.headSha == \"$COMMIT_SHA\" and .conclusion == \"success\") | .databaseId" \
    | head -n 1)"
fi

if [ -z "$RUN_ID" ]; then
  echo "FAIL: no successful GitHub Actions run found for commit."
  exit 1
fi

echo "Run id: $RUN_ID"
echo

echo "=== PREPARE DIRECTORIES ==="
mkdir -p "$ANDROID_DIR" "$CI_DIR" "$OUT_DIR"
echo "Android dir:    $ANDROID_DIR"
echo "CI dir:         $CI_DIR"
echo "Comparison dir: $OUT_DIR"
echo

echo "=== DOWNLOAD CI ARTIFACT ==="
DOWNLOAD_START="$(date '+%Y-%m-%d %H:%M:%S %Z')"
DOWNLOAD_START_EPOCH="$(date +%s)"
echo "Download Startzeit: $DOWNLOAD_START"

gh run download "$RUN_ID" \
  --repo "$TARGET_REPO" \
  --name "$ARTIFACT_NAME" \
  --dir "$CI_DIR"

DOWNLOAD_END="$(date '+%Y-%m-%d %H:%M:%S %Z')"
DOWNLOAD_END_EPOCH="$(date +%s)"
DOWNLOAD_DURATION="$((DOWNLOAD_END_EPOCH - DOWNLOAD_START_EPOCH))"

echo "Download Endzeit: $DOWNLOAD_END"
echo "Download Dauer Sekunden: $DOWNLOAD_DURATION"
echo

echo "=== GENERATE LOCAL ANDROID ARTIFACT ==="
ANDROID_START="$(date '+%Y-%m-%d %H:%M:%S %Z')"
ANDROID_START_EPOCH="$(date +%s)"
echo "Android Startzeit: $ANDROID_START"

./scripts/release/generate-ci-build-provenance-artifact.sh
cp -a target/wvp-ci-build-provenance/. "$ANDROID_DIR"/

ANDROID_END="$(date '+%Y-%m-%d %H:%M:%S %Z')"
ANDROID_END_EPOCH="$(date +%s)"
ANDROID_DURATION="$((ANDROID_END_EPOCH - ANDROID_START_EPOCH))"

echo "Android Endzeit: $ANDROID_END"
echo "Android Dauer Sekunden: $ANDROID_DURATION"
echo

echo "=== REQUIRED FILE CHECK ==="
for dir in "$ANDROID_DIR" "$CI_DIR"; do
  echo "--- $dir ---"
  test -s "$dir/CI-BUILD-PROVENANCE-MANIFEST.json"
  test -s "$dir/BUILD-PROVENANCE.json"
  test -s "$dir/BUILD-ENVIRONMENT-CLASSIFICATION.json"
  test -s "$dir/wvp-release-check-native"
  test -s "$dir/wvp-release-check-native.sha256"
  (
    cd "$dir"
    sha256sum -c wvp-release-check-native.sha256
  )
done
echo "Required files OK."
echo

echo "=== COMPARE ARTIFACTS ==="
./scripts/release/compare-build-provenance-artifacts.sh \
  "$ANDROID_DIR" \
  "$CI_DIR" \
  "$OUT_DIR"

echo
echo "=== VALIDATE ANDROID VS CI SEMANTICS ==="
python3 - "$COMPARISON_JSON" <<'PY'
import json
import sys

path = sys.argv[1]
with open(path, "r", encoding="utf-8") as f:
    d = json.load(f)

assert d["evidence_type"] == "build-provenance-artifact-comparison"
assert d["left"]["environment_class"] == "android-termux-aarch64"
assert d["right"]["environment_class"] == "github-actions-linux-x86_64"
assert d["same_environment_class"] is False
assert d["independent_environment_comparison_performed"] is True
assert d["linux_vs_android_comparison_detected"] is True
assert d["comparison"]["source_commit_match"] is True
assert d["comparison"]["package_version_match"] is True
assert d["comparison"]["cargo_lock_hash_match"] is True
assert d["interpretation"]["binary_hash_mismatch_is_failure"] is False
assert d["interpretation"]["can_claim_reproducible_build"] is False
assert d["not_a_reproducible_build_proof"] is True
assert d["reproducible_build_claim"] is False
assert d["source_to_release_proof"] is False
assert d["binary_safety_proof"] is False

print("left_environment_class=" + str(d["left"]["environment_class"]))
print("right_environment_class=" + str(d["right"]["environment_class"]))
print("source_commit_match=" + str(d["comparison"]["source_commit_match"]))
print("cargo_lock_hash_match=" + str(d["comparison"]["cargo_lock_hash_match"]))
print("binary_sha256_match=" + str(d["comparison"]["binary_sha256_match"]))
print("can_claim_reproducible_build=" + str(d["interpretation"]["can_claim_reproducible_build"]))
PY

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo
echo "=== WVP ANDROID VS CI BUILD PROVENANCE CONFORMANCE RESULT ==="
echo "RESULT: PASS"
echo "Comparison JSON: $COMPARISON_JSON"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
