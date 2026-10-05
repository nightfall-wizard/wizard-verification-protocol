#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP v0.4 RELEASE READINESS CHECKLIST CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

CHECKLIST="docs/release-check/WVP-V040-RELEASE-READINESS-CHECKLIST.md"
REPORT_JSON="reports/release-check/WVP-V040-FIXTURE-RUNNER-REPORT.json"
REPORT_MD="reports/release-check/WVP-V040-FIXTURE-RUNNER-REPORT.md"
INDEX="fixtures/release-check/FIXTURE-INDEX.json"
SELF="${BASH_SOURCE[0]}"

echo "=== VERIFY FILES ==="
test -s "$CHECKLIST"
test -s "$REPORT_JSON"
test -s "$REPORT_MD"
test -s "$INDEX"
python3 -m json.tool "$REPORT_JSON" >/dev/null
python3 -m json.tool "$INDEX" >/dev/null
echo "Files OK."

echo "=== VERIFY REQUIRED ARTIFACT PATHS ==="
python3 - "$CHECKLIST" <<'PY2'
from pathlib import Path
import sys

checklist = Path(sys.argv[1]).read_text(encoding="utf-8")
required_paths = [
  "docs/roadmap/WVP-V0.4-SCOPE-AND-PLAN.md",
  "docs/roadmap/WVP-V0.4-RELEASE-CHECK-HARDENING-MATRIX.md",
  "docs/roadmap/WVP-V0.4-RELEASE-CHECK-FIXTURE-STRATEGY.md",
  "fixtures/release-check/FIXTURE-INDEX.json",
  "conformance/wvp-v040-release-check-fixture-index-validator.sh",
  "docs/release-check/WVP-V040-FIXTURE-RUNNER-DESIGN.md",
  "conformance/wvp-v040-release-check-fixture-runner-skeleton.sh",
  "conformance/wvp-v040-release-check-fixture-runner-semantic-coverage-conformance.sh",
  "reports/release-check/WVP-V040-FIXTURE-RUNNER-REPORT.json",
  "reports/release-check/WVP-V040-FIXTURE-RUNNER-REPORT.md"
]

problems = []

for path in required_paths:
    p = Path(path)
    if not p.is_file() or p.stat().st_size == 0:
        problems.append("missing or empty required path: " + path)
    if path not in checklist:
        problems.append("checklist does not mention required path: " + path)

if problems:
    for item in problems:
        print("FAIL:", item)
    raise SystemExit(1)

print("Required artifact paths OK.")
PY2

echo "=== VERIFY CHECKLIST CONTENT ==="
python3 - "$CHECKLIST" "$REPORT_JSON" "$INDEX" <<'PY2'
import json
import sys
from pathlib import Path

checklist = Path(sys.argv[1]).read_text(encoding="utf-8")
report = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
index = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))

problems = []

required_phrases = [
    "Status: `prepared-not-released`",
    "Git tag created",
    "GitHub release created",
    "GitHub release asset uploaded",
    "Private key added",
    "FRC-003",
    "FRC-004",
    "FRC-005",
    "FRC-006",
    "FRC-007",
    "Rust format check",
    "Rust clippy with `-D warnings`",
    "Rust tests",
    "fixture runner report conformance",
    "Confirm no unintended tag exists for v0.4.",
    "Confirm no unintended GitHub release exists for v0.4.",
    "Confirm no unintended release asset exists for v0.4.",
    "This is not an audit.",
    "This is not legal clearance.",
    "This is not a binary safety proof.",
    "This is not a source-to-release proof.",
    "This is not a reproducible-build proof.",
    "This is not a wallet safety claim.",
    "This is not investment advice.",
]

for phrase in required_phrases:
    if phrase not in checklist:
        problems.append("missing phrase: " + phrase)

forbidden_patterns = [
    ("audit passed", r"\\baudit\\s+passed\\b"),
    ("legally compliant", r"\\blegally\\s+compliant\\b"),
    ("legally approved", r"\\blegally\\s+approved\\b"),
    ("binary safe claim", r"\\bbinary\\s+safe\\b"),
    ("source-to-release proven", r"\\bsource-to-release\\s+proven\\b"),
    ("reproducible build proven", r"\\breproducible\\s+build\\s+proven\\b"),
    ("wallet safe claim", r"\\bwallet\\s+safe\\b"),
    ("investment suitable", r"\\binvestment\\s+suitable\\b"),
]

import re
for label, pattern in forbidden_patterns:
    if re.search(pattern, checklist.lower()):
        problems.append("forbidden phrase present: " + label)

if report.get("status") != "PASS":
    problems.append("runner report status is not PASS")

if report.get("fixtures_failed") != 0:
    problems.append("runner report fixtures_failed not zero")

if report.get("semantic_unchecked_keys_total") != 0:
    problems.append("runner report unchecked semantic keys not zero")

required = {"FRC-003", "FRC-004", "FRC-005", "FRC-006", "FRC-007"}
implemented = {
    row.get("id")
    for row in index.get("fixtures", [])
    if row.get("status") == "implemented"
}

missing = sorted(required - implemented)
if missing:
    problems.append("missing implemented fixture ids: " + ",".join(missing))

if problems:
    for item in problems:
        print("FAIL:", item)
    raise SystemExit(1)

print("Checklist content OK.")
PY2

echo "=== VERIFY NO v0.4 RELEASE OR TAG EXISTS ==="
if git ls-remote --tags origin "refs/tags/v0.4.0" | grep -q "v0.4.0"; then
  echo "FAIL: v0.4.0 tag already exists."
  exit 1
fi

set +e
gh release view "v0.4.0" --repo "nightfall-wizard/wizard-verification-protocol" >/dev/null 2>&1
REL_RESULT=$?
set -e

if [ "$REL_RESULT" -eq 0 ]; then
  echo "FAIL: v0.4.0 GitHub release already exists."
  exit 1
fi

echo "No v0.4.0 tag or GitHub release exists."
echo

echo "=== VERIFY NO SECRET-LIKE MATERIAL ==="
PRIVATE_RE='BEGIN (PGP |OPENSSH |RSA |EC |DSA )?PR''IVATE KEY|AGE-SE''CRET-KEY-|ghp_[A-Za-z0-9_]{20,}'
if grep -nE "$PRIVATE_RE" "$CHECKLIST" "$REPORT_JSON" "$REPORT_MD" "$SELF"; then
  echo "FAIL: secret-like material found."
  exit 1
fi
echo "No secret-like material found."

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo
echo "=== WVP v0.4 RELEASE READINESS CHECKLIST CONFORMANCE RESULT ==="
echo "RESULT: PASS"
echo "Release readiness checklist exists."
echo "Required v0.4 evidence paths are present."
echo "Runner report status is PASS."
echo "No v0.4.0 tag exists."
echo "No v0.4.0 GitHub release exists."
echo "Boundary statements are explicit."
echo "No audit/legal/binary/reproducible/source-to-release claim is made."
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
