#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP CI BUILD PROVENANCE ARTIFACT GENERATION ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

DIRTY_FLAG="--require-clean"

for arg in "$@"; do
  case "$arg" in
    --allow-dirty)
      DIRTY_FLAG="--allow-dirty"
      ;;
    --require-clean)
      DIRTY_FLAG="--require-clean"
      ;;
    -h|--help)
      echo "Usage: $0 [--allow-dirty|--require-clean]"
      echo "Default: --require-clean"
      exit 0
      ;;
    *)
      echo "FAIL: unknown argument: $arg"
      exit 1
      ;;
  esac
done

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

CLASSIFY_SCRIPT="scripts/release/classify-build-environment.sh"
BUILD_SCRIPT="scripts/release/build-wvp-release-check-provenance.sh"

test -x "$CLASSIFY_SCRIPT"
test -x "$BUILD_SCRIPT"

STABLE_DIR="target/wvp-ci-build-provenance"
rm -rf "$STABLE_DIR"
mkdir -p "$STABLE_DIR"

CLASSIFY_LOG="$STABLE_DIR/environment-classification.log"
BUILD_LOG="$STABLE_DIR/build-provenance.log"

echo "=== CLASSIFY BUILD ENVIRONMENT ==="
"$CLASSIFY_SCRIPT" | tee "$CLASSIFY_LOG"

CLASSIFY_DIR="$(grep -F 'Artifact directory:' "$CLASSIFY_LOG" | tail -n 1 | sed 's/^Artifact directory: //')"
if [ -z "$CLASSIFY_DIR" ] || [ ! -d "$CLASSIFY_DIR" ]; then
  echo "FAIL: environment classification artifact directory not found"
  exit 1
fi

CLASSIFY_JSON="$CLASSIFY_DIR/BUILD-ENVIRONMENT-CLASSIFICATION.json"
test -s "$CLASSIFY_JSON"

cp -p "$CLASSIFY_JSON" "$STABLE_DIR/BUILD-ENVIRONMENT-CLASSIFICATION.json"

echo
echo "=== GENERATE BUILD PROVENANCE ==="
"$BUILD_SCRIPT" "$DIRTY_FLAG" | tee "$BUILD_LOG"

BUILD_DIR="$(grep -F 'Artifact directory:' "$BUILD_LOG" | tail -n 1 | sed 's/^Artifact directory: //')"
if [ -z "$BUILD_DIR" ] || [ ! -d "$BUILD_DIR" ]; then
  echo "FAIL: build provenance artifact directory not found"
  exit 1
fi

BUILD_JSON="$BUILD_DIR/BUILD-PROVENANCE.json"
test -s "$BUILD_JSON"

SOURCE_BINARY="$(python3 - "$BUILD_JSON" "$BUILD_DIR" <<'PY'
import json
import sys
from pathlib import Path

json_path = Path(sys.argv[1])
build_dir = Path(sys.argv[2])

data = json.loads(json_path.read_text())
asset_name = data["outputs"]["asset_name"]
print(build_dir / asset_name)
PY
)"

test -s "$SOURCE_BINARY"

NATIVE_BINARY="$STABLE_DIR/wvp-release-check-native"
cp -p "$SOURCE_BINARY" "$NATIVE_BINARY"
chmod 0755 "$NATIVE_BINARY"

(
  cd "$STABLE_DIR"
  sha256sum wvp-release-check-native > wvp-release-check-native.sha256
  sha256sum -c wvp-release-check-native.sha256
)

cp -p "$BUILD_JSON" "$STABLE_DIR/BUILD-PROVENANCE.json"

MANIFEST="$STABLE_DIR/CI-BUILD-PROVENANCE-MANIFEST.json"

python3 - "$STABLE_DIR" <<'PY' > "$MANIFEST"
import json
import os
import subprocess
import sys
from pathlib import Path

stable_dir = Path(sys.argv[1])

env_data = json.loads((stable_dir / "BUILD-ENVIRONMENT-CLASSIFICATION.json").read_text())
build_data = json.loads((stable_dir / "BUILD-PROVENANCE.json").read_text())

binary_path = stable_dir / "wvp-release-check-native"
binary_sha256 = subprocess.check_output(["sha256sum", str(binary_path)], text=True).split()[0]
binary_size = binary_path.stat().st_size

data = {
    "tool": "wvp-release-check",
    "package_version": build_data["package_version"],
    "evidence_type": "ci-build-provenance-artifact-generation",
    "reproducible_build_claim": False,
    "not_a_reproducible_build_proof": True,
    "independent_environment_evidence": False,
    "source_to_release_proof": False,
    "artifact_ready_for_upload": True,
    "environment_class": env_data["environment_class"],
    "source": build_data["source"],
    "toolchain": build_data["toolchain"],
    "inputs": build_data["inputs"],
    "outputs": {
        "native_binary_name": "wvp-release-check-native",
        "native_binary_sha256": binary_sha256,
        "native_binary_size_bytes": binary_size,
        "build_provenance_json": "BUILD-PROVENANCE.json",
        "environment_classification_json": "BUILD-ENVIRONMENT-CLASSIFICATION.json",
    },
    "limitations": [
        "CI build provenance artifact generation is not a reproducible-build proof",
        "CI build provenance does not prove the release asset was built from source",
        "CI build provenance is one environment class only",
        "independent environment comparison is still required",
    ],
}

print(json.dumps(data, indent=2, sort_keys=True))
PY

echo
echo "=== CI BUILD PROVENANCE ARTIFACT CONTENTS ==="
find "$STABLE_DIR" -maxdepth 1 -type f -print | sort
echo

echo "=== CI BUILD PROVENANCE MANIFEST ==="
cat "$MANIFEST"
echo

python3 - "$MANIFEST" <<'PY'
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
assert data["outputs"]["native_binary_sha256"]
assert data["outputs"]["native_binary_size_bytes"] > 0
PY

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "RESULT: PASS"
echo "Artifact directory: $STABLE_DIR"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
