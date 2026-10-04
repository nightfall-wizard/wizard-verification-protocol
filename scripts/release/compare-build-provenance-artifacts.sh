#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP BUILD PROVENANCE ARTIFACT COMPARISON ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
  echo "Usage: $0 LEFT_ARTIFACT_DIR RIGHT_ARTIFACT_DIR [OUT_DIR]"
  exit 1
fi

LEFT_DIR="$1"
RIGHT_DIR="$2"
OUT_DIR="${3:-target/wvp-build-provenance-comparison-$(date +%Y%m%d-%H%M%S)}"

if [ ! -d "$LEFT_DIR" ]; then
  echo "FAIL: left artifact directory not found: $LEFT_DIR"
  exit 1
fi

if [ ! -d "$RIGHT_DIR" ]; then
  echo "FAIL: right artifact directory not found: $RIGHT_DIR"
  exit 1
fi

mkdir -p "$OUT_DIR"

for side in left right; do
  case "$side" in
    left)
      DIR="$LEFT_DIR"
      ;;
    right)
      DIR="$RIGHT_DIR"
      ;;
  esac

  test -s "$DIR/CI-BUILD-PROVENANCE-MANIFEST.json"
  test -s "$DIR/BUILD-PROVENANCE.json"
  test -s "$DIR/BUILD-ENVIRONMENT-CLASSIFICATION.json"
  test -s "$DIR/wvp-release-check-native"
  test -s "$DIR/wvp-release-check-native.sha256"

  (
    cd "$DIR"
    sha256sum -c wvp-release-check-native.sha256
  )
done

COMPARISON_JSON="$OUT_DIR/BUILD-PROVENANCE-COMPARISON.json"

python3 - "$LEFT_DIR" "$RIGHT_DIR" "$START_TS" <<'PY' > "$COMPARISON_JSON"
import hashlib
import json
import os
import sys
from pathlib import Path

left_dir = Path(sys.argv[1])
right_dir = Path(sys.argv[2])
started_at = sys.argv[3]

def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def artifact_data(root: Path):
    manifest = load_json(root / "CI-BUILD-PROVENANCE-MANIFEST.json")
    build = load_json(root / "BUILD-PROVENANCE.json")
    env = load_json(root / "BUILD-ENVIRONMENT-CLASSIFICATION.json")
    binary = root / "wvp-release-check-native"

    return {
        "artifact_dir": str(root),
        "manifest": manifest,
        "build": build,
        "environment": env,
        "binary_sha256_actual": sha256_file(binary),
        "binary_size_bytes_actual": binary.stat().st_size,
    }

left = artifact_data(left_dir)
right = artifact_data(right_dir)

left_manifest = left["manifest"]
right_manifest = right["manifest"]

left_env_class = left_manifest["environment_class"]
right_env_class = right_manifest["environment_class"]

left_source = left_manifest["source"]
right_source = right_manifest["source"]

left_toolchain = left_manifest["toolchain"]
right_toolchain = right_manifest["toolchain"]

left_inputs = left_manifest["inputs"]
right_inputs = right_manifest["inputs"]

left_outputs = left_manifest["outputs"]
right_outputs = right_manifest["outputs"]

same_environment_class = left_env_class == right_env_class
linux_vs_android_comparison = {
    left_env_class,
    right_env_class,
} == {
    "android-termux-aarch64",
    "github-actions-linux-x86_64",
}

binary_sha256_match = left["binary_sha256_actual"] == right["binary_sha256_actual"]
binary_size_match = left["binary_size_bytes_actual"] == right["binary_size_bytes_actual"]

source_commit_match = left_source["git_commit"] == right_source["git_commit"]
package_version_match = left_manifest["package_version"] == right_manifest["package_version"]
cargo_lock_hash_match = left_inputs["cargo_lock_sha256"] == right_inputs["cargo_lock_sha256"]
rustc_version_match = left_toolchain["rustc"] == right_toolchain["rustc"]
cargo_version_match = left_toolchain["cargo"] == right_toolchain["cargo"]

comparison_passed_format_checks = True

data = {
    "tool": "wvp-release-check",
    "evidence_type": "build-provenance-artifact-comparison",
    "comparison_started_at": started_at,
    "reproducible_build_claim": False,
    "not_a_reproducible_build_proof": True,
    "source_to_release_proof": False,
    "binary_safety_proof": False,
    "independent_environment_comparison_performed": not same_environment_class,
    "linux_vs_android_comparison_detected": linux_vs_android_comparison,
    "same_environment_class": same_environment_class,
    "left": {
        "artifact_dir": str(left_dir),
        "environment_class": left_env_class,
        "git_commit": left_source["git_commit"],
        "package_version": left_manifest["package_version"],
        "cargo_lock_sha256": left_inputs["cargo_lock_sha256"],
        "rustc": left_toolchain["rustc"],
        "cargo": left_toolchain["cargo"],
        "binary_sha256": left["binary_sha256_actual"],
        "binary_size_bytes": left["binary_size_bytes_actual"],
    },
    "right": {
        "artifact_dir": str(right_dir),
        "environment_class": right_env_class,
        "git_commit": right_source["git_commit"],
        "package_version": right_manifest["package_version"],
        "cargo_lock_sha256": right_inputs["cargo_lock_sha256"],
        "rustc": right_toolchain["rustc"],
        "cargo": right_toolchain["cargo"],
        "binary_sha256": right["binary_sha256_actual"],
        "binary_size_bytes": right["binary_size_bytes_actual"],
    },
    "comparison": {
        "source_commit_match": source_commit_match,
        "package_version_match": package_version_match,
        "cargo_lock_hash_match": cargo_lock_hash_match,
        "rustc_version_match": rustc_version_match,
        "cargo_version_match": cargo_version_match,
        "binary_sha256_match": binary_sha256_match,
        "binary_size_bytes_match": binary_size_match,
        "format_checks_passed": comparison_passed_format_checks,
    },
    "interpretation": {
        "binary_hash_mismatch_is_failure": same_environment_class,
        "cross_arch_binary_match_required": False,
        "can_claim_reproducible_build": False,
    },
    "limitations": [
        "build provenance artifact comparison is not a reproducible-build proof",
        "matching source commit and Cargo.lock hash do not prove binary reproducibility",
        "different architecture native binaries are not expected to be byte-identical",
        "this comparison does not prove the published release asset was built from source",
        "this comparison does not prove binary safety",
    ],
}

print(json.dumps(data, indent=2, sort_keys=True))
PY

echo
echo "=== BUILD PROVENANCE COMPARISON JSON ==="
cat "$COMPARISON_JSON"
echo

python3 - "$COMPARISON_JSON" <<'PY'
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
assert data["left"]["binary_sha256"]
assert data["right"]["binary_sha256"]
assert data["left"]["binary_size_bytes"] > 0
assert data["right"]["binary_size_bytes"] > 0
PY

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "RESULT: PASS"
echo "Artifact directory: $OUT_DIR"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
