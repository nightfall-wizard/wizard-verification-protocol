#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP BUILD PROVENANCE: wvp-release-check ==="
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
ASSET_NAME="wvp-release-check-termux-android-aarch64"
SRC_BIN="target/release/wvp-release-check"

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

OUT_DIR="target/wvp-build-provenance-${VERSION}-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUT_DIR"

echo "Version: $VERSION"
echo "Commit: $COMMIT_SHA"
echo "Branch: $BRANCH_NAME"
echo "Dirty source tree: $DIRTY_STATE"
echo "Output directory: $OUT_DIR"
echo

echo "=== BUILD RELEASE BINARY ==="
cargo build --release --locked --manifest-path "$MANIFEST"

if [ ! -x "$SRC_BIN" ]; then
  echo "FAIL: release binary missing: $SRC_BIN"
  exit 1
fi

ASSET="$OUT_DIR/$ASSET_NAME"
CHECKSUM="$OUT_DIR/$ASSET_NAME.sha256"
PROVENANCE="$OUT_DIR/BUILD-PROVENANCE.json"

cp -p "$SRC_BIN" "$ASSET"
chmod 0755 "$ASSET"

(
  cd "$OUT_DIR"
  sha256sum "$ASSET_NAME" > "$ASSET_NAME.sha256"
  sha256sum -c "$ASSET_NAME.sha256"
)

BINARY_SHA256="$(sha256sum "$ASSET" | awk '{print $1}')"
BINARY_SIZE_BYTES="$(wc -c < "$ASSET" | tr -d ' ')"

export WVP_PROVENANCE_TOOL="wvp-release-check"
export WVP_PROVENANCE_VERSION="$VERSION"
export WVP_PROVENANCE_COMMIT="$COMMIT_SHA"
export WVP_PROVENANCE_BRANCH="$BRANCH_NAME"
export WVP_PROVENANCE_DIRTY="$DIRTY_STATE"
export WVP_PROVENANCE_RUSTC="$RUSTC_VERSION"
export WVP_PROVENANCE_CARGO="$CARGO_VERSION"
export WVP_PROVENANCE_UNAME="$UNAME_VALUE"
export WVP_PROVENANCE_CARGO_LOCK_SHA256="$CARGO_LOCK_SHA256"
export WVP_PROVENANCE_BINARY_SHA256="$BINARY_SHA256"
export WVP_PROVENANCE_BINARY_SIZE_BYTES="$BINARY_SIZE_BYTES"
export WVP_PROVENANCE_BUILD_COMMAND="$BUILD_COMMAND"
export WVP_PROVENANCE_STARTED_AT="$START_TS"
export WVP_PROVENANCE_ASSET_NAME="$ASSET_NAME"

python3 <<'PY' > "$PROVENANCE"
import json
import os

dirty = os.environ["WVP_PROVENANCE_DIRTY"] == "true"

data = {
    "tool": os.environ["WVP_PROVENANCE_TOOL"],
    "package_version": os.environ["WVP_PROVENANCE_VERSION"],
    "evidence_type": "single-environment-build-provenance",
    "reproducible_build_claim": False,
    "not_a_reproducible_build_proof": True,
    "source": {
        "git_commit": os.environ["WVP_PROVENANCE_COMMIT"],
        "git_branch": os.environ["WVP_PROVENANCE_BRANCH"],
        "dirty": dirty,
    },
    "toolchain": {
        "rustc": os.environ["WVP_PROVENANCE_RUSTC"],
        "cargo": os.environ["WVP_PROVENANCE_CARGO"],
    },
    "environment": {
        "uname": os.environ["WVP_PROVENANCE_UNAME"],
    },
    "inputs": {
        "cargo_lock_sha256": os.environ["WVP_PROVENANCE_CARGO_LOCK_SHA256"],
        "manifest": "reference/rust/wvp-release-check/Cargo.toml",
    },
    "outputs": {
        "asset_name": os.environ["WVP_PROVENANCE_ASSET_NAME"],
        "binary_sha256": os.environ["WVP_PROVENANCE_BINARY_SHA256"],
        "binary_size_bytes": int(os.environ["WVP_PROVENANCE_BINARY_SIZE_BYTES"]),
    },
    "build": {
        "command": os.environ["WVP_PROVENANCE_BUILD_COMMAND"],
        "started_at": os.environ["WVP_PROVENANCE_STARTED_AT"],
    },
    "limitations": [
        "single-environment provenance is not a reproducible-build proof",
        "checksum verification does not prove source-build correspondence",
        "signature verification does not prove source-build correspondence",
        "independent-environment matching builds are not yet proven",
    ],
}

print(json.dumps(data, indent=2, sort_keys=True))
PY

echo "=== BUILD PROVENANCE ARTIFACTS ==="
ls -l "$OUT_DIR"
echo

echo "=== BUILD PROVENANCE JSON ==="
cat "$PROVENANCE"
echo

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "RESULT: PASS"
echo "Artifact directory: $OUT_DIR"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
