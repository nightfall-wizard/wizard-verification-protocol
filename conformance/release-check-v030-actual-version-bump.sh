#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP v0.3 ACTUAL VERSION BUMP CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

MANIFEST="reference/rust/wvp-release-check/Cargo.toml"
READINESS_DOC="docs/release/WVP-V0.3-RELEASE-READINESS-CHECKLIST.md"

if [ -s "reference/rust/wvp-release-check/Cargo.lock" ]; then
  LOCKFILE="reference/rust/wvp-release-check/Cargo.lock"
elif [ -s "Cargo.lock" ]; then
  LOCKFILE="Cargo.lock"
else
  echo "FAIL: no Cargo.lock found."
  find . -name Cargo.lock -type f -maxdepth 5 -print -exec ls -la {} \; || true
  exit 1
fi

echo "=== VERIFY FILES EXIST ==="
test -s "$MANIFEST"
test -s "$LOCKFILE"
test -s "$READINESS_DOC"
echo "Manifest: $MANIFEST"
echo "Lockfile: $LOCKFILE"
echo "Readiness doc: $READINESS_DOC"
echo

echo "=== VERIFY CARGO.TOML PACKAGE VERSION ==="
python3 - "$MANIFEST" <<'PY'
from pathlib import Path
import re
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
lines = text.splitlines()

in_package = False
version = None

for line in lines:
    stripped = line.strip()
    if stripped.startswith("[") and stripped.endswith("]"):
        in_package = stripped == "[package]"
        continue

    if in_package:
        match = re.match(r'^version\s*=\s*"([^"]+)"\s*$', stripped)
        if match:
            version = match.group(1)
            break

if version != "0.3.0":
    raise SystemExit(f"FAIL: expected package version 0.3.0, got {version!r}")

print("Cargo.toml package version OK: 0.3.0")
PY
echo

echo "=== VERIFY CARGO.LOCK PACKAGE VERSION ==="
python3 - "$LOCKFILE" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
blocks = text.split("[[package]]")

found = False

for block in blocks:
    if 'name = "wvp-release-check"' in block:
        found = True
        if 'version = "0.3.0"' not in block:
            raise SystemExit("FAIL: Cargo.lock package entry for wvp-release-check is not version 0.3.0")
        break

if not found:
    raise SystemExit("FAIL: Cargo.lock package entry for wvp-release-check not found")

print("Cargo.lock package version OK: 0.3.0")
PY
echo

echo "=== VERIFY READINESS CHECKLIST UPDATED ==="
grep -q '\[x\] v0.3 version bump is prepared' "$READINESS_DOC"
echo "Readiness checklist version-bump item OK."
echo

echo "=== VERIFY NO TAG OR RELEASE EXECUTION ==="
if git tag --list | grep -qx "v0.3.0"; then
  echo "FAIL: v0.3.0 tag already exists. This step must not create a tag."
  exit 1
fi

grep -q "No v0.3.0 release has been published by this document" docs/release/WVP-V0.3-VERSION-BUMP-AND-RELEASE-COMMAND-PLAN.md
grep -q "No tag is created by this document" docs/release/WVP-V0.3-VERSION-BUMP-AND-RELEASE-COMMAND-PLAN.md
grep -q "No signature is created by this document" docs/release/WVP-V0.3-VERSION-BUMP-AND-RELEASE-COMMAND-PLAN.md
echo "No tag/release/signature execution boundary OK."
echo

echo "=== VERIFY NO FALSE 100 PERCENT CLAIM ==="
if grep -nE '100%|100 percent|fully complete|complete project' "$MANIFEST" "$READINESS_DOC"; then
  echo "FAIL: suspicious 100%/complete claim found."
  exit 1
fi
echo "No false 100% claim found."
echo

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "=== WVP v0.3 ACTUAL VERSION BUMP CONFORMANCE RESULT ==="
echo "RESULT: PASS"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
