#!/usr/bin/env bash
set -Eeuo pipefail

case "${1:-}" in
  stage)
    SCRIPT="conformance/release-check-v030-unsigned-asset-staging.sh"
    ;;
  signature)
    SCRIPT="conformance/release-check-v030-detached-signature-procedure.sh"
    ;;
  guard)
    SCRIPT="conformance/release-check-v030-local-signing-execution-guard.sh"
    ;;
  *)
    echo "Invalid historical test mode" >&2
    exit 2
    ;;
esac

REPO="nightfall-wizard/wizard-verification-protocol"
TEMP="$(mktemp -d)"
trap 'rm -rf "$TEMP"' EXIT

git -C "$TEMP" init -q

git -C "$TEMP" remote add origin \
  "https://github.com/$REPO.git"

git -C "$TEMP" fetch -q \
  --no-tags --depth=1 origin refs/tags/v0.3.0

git -C "$TEMP" \
  -c advice.detachedHead=false \
  checkout -q --detach FETCH_HEAD

if [ -n "$(git -C "$TEMP" tag -l v0.3.0)" ]; then
  echo "FAIL: Unexpected local historical tag"
  exit 1
fi

python3 - "$TEMP" <<'PY'
import sys
import tomllib
from pathlib import Path

root = Path(sys.argv[1])

manifest = tomllib.loads(
    (root / "reference/rust/wvp-release-check/Cargo.toml").read_text()
)

lock = tomllib.loads(
    (root / "Cargo.lock").read_text()
)

assert manifest["package"]["version"] == "0.3.0"

versions = [
    p["version"] for p in lock["package"]
    if p["name"] == "wvp-release-check"
]

assert versions == ["0.3.0"]

print("PASS: historical version and lock verified")
PY

echo "HISTORICAL COMMIT:"
git -C "$TEMP" rev-parse HEAD

(
  cd "$TEMP"
  bash "$SCRIPT"
)

echo "PASS: historical test complete"
