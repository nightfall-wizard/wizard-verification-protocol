#!/usr/bin/env bash
set -euo pipefail

echo "=== HISTORICAL v0.3 / CURRENT v0.5 ==="

BEFORE_TAGS="$(git tag --list)"

git fetch -q --no-tags --depth=1 origin refs/tags/v0.3.0

python3 <<'PY'
import subprocess
import tomllib
from pathlib import Path

def historical(path):
    return subprocess.check_output(
        ["git", "show", "FETCH_HEAD:" + path]
    )

def current(path):
    return Path(path).read_bytes()

manifest = "reference/rust/wvp-release-check/Cargo.toml"

old_manifest = tomllib.loads(historical(manifest).decode())
old_lock = tomllib.loads(historical("Cargo.lock").decode())

new_manifest = tomllib.loads(current(manifest).decode())
new_lock = tomllib.loads(current("Cargo.lock").decode())

def package_version(lock):
    versions = [
        p["version"]
        for p in lock["package"]
        if p["name"] == "wvp-release-check"
    ]
    if len(versions) != 1:
        raise SystemExit("FAIL: ambiguous package entry")
    return versions[0]

assert old_manifest["package"]["version"] == "0.3.0"
assert package_version(old_lock) == "0.3.0"

assert tuple(map(int, new_manifest["package"]["version"].split("."))) >= (0,5,0)
assert package_version(new_lock) == new_manifest["package"]["version"]

doc = Path(
    "docs/release/WVP-V0.3-RELEASE-READINESS-CHECKLIST.md"
).read_text()

assert "[x] v0.3 version bump is prepared" in doc

print("PASS: historical v0.3.0 source verified")
print("PASS: current v0.5.0 manifest and lock verified")
PY

AFTER_TAGS="$(git tag --list)"

if [ "$BEFORE_TAGS" != "$AFTER_TAGS" ]; then
  echo "FAIL: local Git tags unexpectedly changed"
  exit 1
fi

echo "PASS: historical and current versions verified"
echo "PASS: no local tags created"
