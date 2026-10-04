#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP SAME-ENVIRONMENT REPEAT-BUILD COMPARISON ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

ALLOW_DIRTY=0

for arg in "$@"; do
  case "$arg" in
    --allow-dirty)
      ALLOW_DIRTY=1
      ;;
    --require-clean)
      ALLOW_DIRTY=0
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

MANIFEST="reference/rust/wvp-release-check/Cargo.toml"
BINARY_NAME="wvp-release-check"

test -s "$MANIFEST"
test -s "Cargo.lock"

DIRTY_STATE="false"
if [ -n "$(git status --porcelain)" ]; then
  DIRTY_STATE="true"
fi

if [ "$DIRTY_STATE" = "true" ] && [ "$ALLOW_DIRTY" -ne 1 ]; then
  echo "FAIL: source tree is dirty."
  echo "Use --allow-dirty only for development/conformance evidence."
  exit 1
fi

VERSION="$(grep -m1 '^version = ' "$MANIFEST" | sed -E 's/version = "([^"]+)"/\1/')"
COMMIT_SHA="$(git rev-parse HEAD)"
BRANCH_NAME="$(git rev-parse --abbrev-ref HEAD)"
CARGO_LOCK_SHA256="$(sha256sum Cargo.lock | awk '{print $1}')"
RUSTC_VERSION="$(rustc --version)"
CARGO_VERSION="$(cargo --version)"
UNAME_VALUE="$(uname -a)"
BUILD_COMMAND="cargo build --release --locked --manifest-path $MANIFEST"

OUT_DIR="target/wvp-repeat-build-${VERSION}-$(date +%Y%m%d-%H%M%S)"
TARGET_A="$OUT_DIR/target-a"
TARGET_B="$OUT_DIR/target-b"
BUILD_A_DIR="$OUT_DIR/build-a"
BUILD_B_DIR="$OUT_DIR/build-b"

mkdir -p "$TARGET_A" "$TARGET_B" "$BUILD_A_DIR" "$BUILD_B_DIR"

echo "Version: $VERSION"
echo "Commit: $COMMIT_SHA"
echo "Branch: $BRANCH_NAME"
echo "Dirty source tree: $DIRTY_STATE"
echo "Output directory: $OUT_DIR"
echo

echo "=== BUILD A ==="
CARGO_TARGET_DIR="$TARGET_A" cargo build --release --locked --manifest-path "$MANIFEST"

BIN_A="$TARGET_A/release/$BINARY_NAME"
if [ ! -x "$BIN_A" ]; then
  echo "FAIL: build A binary missing: $BIN_A"
  exit 1
fi

cp -p "$BIN_A" "$BUILD_A_DIR/$BINARY_NAME"
chmod 0755 "$BUILD_A_DIR/$BINARY_NAME"

SHA_A="$(sha256sum "$BUILD_A_DIR/$BINARY_NAME" | awk '{print $1}')"
SIZE_A="$(wc -c < "$BUILD_A_DIR/$BINARY_NAME" | tr -d ' ')"

echo "Build A SHA256: $SHA_A"
echo "Build A size:   $SIZE_A"
echo

echo "=== BUILD B ==="
CARGO_TARGET_DIR="$TARGET_B" cargo build --release --locked --manifest-path "$MANIFEST"

BIN_B="$TARGET_B/release/$BINARY_NAME"
if [ ! -x "$BIN_B" ]; then
  echo "FAIL: build B binary missing: $BIN_B"
  exit 1
fi

cp -p "$BIN_B" "$BUILD_B_DIR/$BINARY_NAME"
chmod 0755 "$BUILD_B_DIR/$BINARY_NAME"

SHA_B="$(sha256sum "$BUILD_B_DIR/$BINARY_NAME" | awk '{print $1}')"
SIZE_B="$(wc -c < "$BUILD_B_DIR/$BINARY_NAME" | tr -d ' ')"

echo "Build B SHA256: $SHA_B"
echo "Build B size:   $SIZE_B"
echo

HASH_MATCH="false"
SIZE_MATCH="false"

if [ "$SHA_A" = "$SHA_B" ]; then
  HASH_MATCH="true"
fi

if [ "$SIZE_A" = "$SIZE_B" ]; then
  SIZE_MATCH="true"
fi

PROVENANCE="$OUT_DIR/SAME-ENVIRONMENT-REPEAT-BUILD.json"

export WVP_REPEAT_TOOL="wvp-release-check"
export WVP_REPEAT_VERSION="$VERSION"
export WVP_REPEAT_COMMIT="$COMMIT_SHA"
export WVP_REPEAT_BRANCH="$BRANCH_NAME"
export WVP_REPEAT_DIRTY="$DIRTY_STATE"
export WVP_REPEAT_RUSTC="$RUSTC_VERSION"
export WVP_REPEAT_CARGO="$CARGO_VERSION"
export WVP_REPEAT_UNAME="$UNAME_VALUE"
export WVP_REPEAT_CARGO_LOCK_SHA256="$CARGO_LOCK_SHA256"
export WVP_REPEAT_BUILD_COMMAND="$BUILD_COMMAND"
export WVP_REPEAT_STARTED_AT="$START_TS"
export WVP_REPEAT_SHA_A="$SHA_A"
export WVP_REPEAT_SHA_B="$SHA_B"
export WVP_REPEAT_SIZE_A="$SIZE_A"
export WVP_REPEAT_SIZE_B="$SIZE_B"
export WVP_REPEAT_HASH_MATCH="$HASH_MATCH"
export WVP_REPEAT_SIZE_MATCH="$SIZE_MATCH"

python3 <<'PY' > "$PROVENANCE"
import json
import os

dirty = os.environ["WVP_REPEAT_DIRTY"] == "true"
hash_match = os.environ["WVP_REPEAT_HASH_MATCH"] == "true"
size_match = os.environ["WVP_REPEAT_SIZE_MATCH"] == "true"

data = {
    "tool": os.environ["WVP_REPEAT_TOOL"],
    "package_version": os.environ["WVP_REPEAT_VERSION"],
    "evidence_type": "same-environment-repeat-build-comparison",
    "reproducible_build_claim": False,
    "not_a_reproducible_build_proof": True,
    "independent_environment_evidence": False,
    "source": {
        "git_commit": os.environ["WVP_REPEAT_COMMIT"],
        "git_branch": os.environ["WVP_REPEAT_BRANCH"],
        "dirty": dirty,
    },
    "toolchain": {
        "rustc": os.environ["WVP_REPEAT_RUSTC"],
        "cargo": os.environ["WVP_REPEAT_CARGO"],
    },
    "environment": {
        "uname": os.environ["WVP_REPEAT_UNAME"],
    },
    "inputs": {
        "cargo_lock_sha256": os.environ["WVP_REPEAT_CARGO_LOCK_SHA256"],
        "manifest": "reference/rust/wvp-release-check/Cargo.toml",
    },
    "build": {
        "command": os.environ["WVP_REPEAT_BUILD_COMMAND"],
        "started_at": os.environ["WVP_REPEAT_STARTED_AT"],
        "build_count": 2,
    },
    "builds": [
        {
            "id": "build-a",
            "binary_name": "wvp-release-check",
            "binary_sha256": os.environ["WVP_REPEAT_SHA_A"],
            "binary_size_bytes": int(os.environ["WVP_REPEAT_SIZE_A"]),
        },
        {
            "id": "build-b",
            "binary_name": "wvp-release-check",
            "binary_sha256": os.environ["WVP_REPEAT_SHA_B"],
            "binary_size_bytes": int(os.environ["WVP_REPEAT_SIZE_B"]),
        },
    ],
    "comparison": {
        "binary_sha256_match": hash_match,
        "binary_size_bytes_match": size_match,
        "same_environment": True,
        "same_source_commit": True,
    },
    "limitations": [
        "same-environment repeat-build comparison is not an independent reproducible-build proof",
        "matching hashes in one environment do not prove another environment can reproduce the binary",
        "this does not prove the published release binary was built from source",
        "independent-environment matching builds are still required before stronger reproducibility claims",
    ],
}

print(json.dumps(data, indent=2, sort_keys=True))
PY

echo "=== REPEAT-BUILD COMPARISON JSON ==="
cat "$PROVENANCE"
echo

if [ "$HASH_MATCH" != "true" ]; then
  echo "RESULT: FAIL"
  echo "Binary SHA256 mismatch between same-environment builds."
  echo "Artifact directory: $OUT_DIR"
  exit 1
fi

if [ "$SIZE_MATCH" != "true" ]; then
  echo "RESULT: FAIL"
  echo "Binary size mismatch between same-environment builds."
  echo "Artifact directory: $OUT_DIR"
  exit 1
fi

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "RESULT: PASS"
echo "Artifact directory: $OUT_DIR"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
