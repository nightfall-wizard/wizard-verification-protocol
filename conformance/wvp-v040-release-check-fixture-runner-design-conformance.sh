#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP v0.4 FIXTURE RUNNER DESIGN CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

DOC="docs/release-check/WVP-V040-FIXTURE-RUNNER-DESIGN.md"
INDEX="fixtures/release-check/FIXTURE-INDEX.json"

echo "=== VERIFY FILES ==="
test -s "$DOC"
test -s "$INDEX"
python3 -m json.tool "$INDEX" >/dev/null
echo "Files OK."

echo "=== VERIFY FIXTURE INDEX ==="
python3 - "$INDEX" <<'PY2'
import json
import sys
from pathlib import Path

index = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
fixtures = index.get("fixtures", [])
ids = {f.get("id"): f for f in fixtures}

required = ["FRC-003", "FRC-004", "FRC-005", "FRC-006", "FRC-007"]

for fixture_id in required:
    row = ids.get(fixture_id)
    if not row:
        raise SystemExit(f"FAIL: missing {fixture_id}")
    if row.get("status") != "implemented":
        raise SystemExit(f"FAIL: {fixture_id} not implemented")
    p = Path(row.get("path", ""))
    for name in ["input.json", "expected.json", "README.md"]:
        if not (p / name).is_file():
            raise SystemExit(f"FAIL: {fixture_id} missing {name}")

print("Fixture index OK.")
PY2

echo "=== VERIFY DESIGN CONTENT ==="
python3 - "$DOC" <<'PY2'
import sys
from pathlib import Path

text = Path(sys.argv[1]).read_text(encoding="utf-8")

required = [
    "Status: design anchor.",
    "It is not a runner implementation.",
    "FRC-003",
    "FRC-004",
    "FRC-005",
    "FRC-006",
    "FRC-007",
    "Exit-code model",
    "Status model",
    "Offline boundary",
    "Secret boundary",
    "Non-claims",
    "Nightfall boundary",
    "This is not an audit of Nightfall.",
    "It does not add the generic fixture runner.",
    "The runner MUST NOT require:",
    "The runner MUST NOT read, print, export, upload, infer, or request:",
]

missing = [x for x in required if x not in text]
if missing:
    raise SystemExit("FAIL: missing required text: " + repr(missing))

for forbidden in [
    "audit passed",
    "legally compliant",
    "guarantees security",
    "investment recommendation",
    "price prediction",
    "send funds",
    "custody service",
]:
    if forbidden.lower() in text.lower():
        raise SystemExit("FAIL: forbidden claim: " + forbidden)

print("Design content OK.")
PY2

echo "=== VERIFY NO SECRET-LIKE MATERIAL ==="
PRIVATE_RE='BEGIN (PGP |OPENSSH |RSA |EC |DSA )?PR''IVATE KEY|AGE-SE''CRET-KEY-|ghp_[A-Za-z0-9_]{20,}'
if grep -nE "$PRIVATE_RE" "$DOC" "$INDEX"; then
  echo "FAIL: secret-like material found."
  exit 1
fi
echo "No secret-like material found."

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo
echo "=== WVP v0.4 FIXTURE RUNNER DESIGN CONFORMANCE RESULT ==="
echo "RESULT: PASS"
echo "Fixture runner design anchor exists."
echo "Offline boundary exists."
echo "Secret boundary exists."
echo "No audit/legal/binary/reproducible/source-to-release claim is made."
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
