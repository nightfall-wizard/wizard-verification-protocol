#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP v0.4 FINAL PRE-RELEASE GATE CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

FINAL_GATE="docs/release-check/WVP-V040-FINAL-PRE-RELEASE-GATE.md"
RELEASE_NOTES="docs/release-check/WVP-V040-RELEASE-NOTES-DRAFT.md"
CHECKLIST="docs/release-check/WVP-V040-RELEASE-READINESS-CHECKLIST.md"
REPORT_JSON="reports/release-check/WVP-V040-FIXTURE-RUNNER-REPORT.json"
REPORT_MD="reports/release-check/WVP-V040-FIXTURE-RUNNER-REPORT.md"
INDEX="fixtures/release-check/FIXTURE-INDEX.json"
SELF="${BASH_SOURCE[0]}"

echo "=== VERIFY FILES ==="
for p in \
  "$FINAL_GATE" \
  "$RELEASE_NOTES" \
  "$CHECKLIST" \
  "$REPORT_JSON" \
  "$REPORT_MD" \
  "$INDEX"
do
  test -s "$p"
done

python3 -m json.tool "$REPORT_JSON" >/dev/null
python3 -m json.tool "$INDEX" >/dev/null
echo "Files OK."

echo "=== VERIFY FINAL GATE CONTENT ==="
python3 - "$FINAL_GATE" "$REPORT_JSON" "$INDEX" <<'PY'
import json
import re
import sys
from pathlib import Path

gate = Path(sys.argv[1]).read_text(encoding="utf-8")
report = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
index = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))

problems = []

required_phrases = [
    "Status: `prepared-not-released`",
    "WVP v0.4 Final Pre-Release Gate",
    "v0.4.0 Git tag created",
    "v0.4.0 GitHub release created",
    "v0.4.0 GitHub release asset uploaded",
    "WVP v0.4 final pre-release gate conformance",
    "FRC-003",
    "FRC-004",
    "FRC-005",
    "FRC-006",
    "FRC-007",
    "This is not an audit.",
    "This is not legal clearance.",
    "This is not a binary safety proof.",
    "This is not a source-to-release proof.",
    "This is not a reproducible-build proof.",
    "This is not a wallet safety claim.",
    "This is not investment advice.",
    "This is not a custody, broker, exchange, or paid-report function.",
    "It does not mean v0.4 has been released.",
]

for phrase in required_phrases:
    if phrase not in gate:
        problems.append("missing phrase: " + phrase)

required_paths = [
    "docs/roadmap/WVP-V0.4-SCOPE-AND-PLAN.md",
    "docs/roadmap/WVP-V0.4-RELEASE-CHECK-HARDENING-MATRIX.md",
    "docs/roadmap/WVP-V0.4-RELEASE-CHECK-FIXTURE-STRATEGY.md",
    "docs/release-check/WVP-V040-FIXTURE-RUNNER-DESIGN.md",
    "reports/release-check/WVP-V040-FIXTURE-RUNNER-REPORT.json",
    "reports/release-check/WVP-V040-FIXTURE-RUNNER-REPORT.md",
    "docs/release-check/WVP-V040-RELEASE-READINESS-CHECKLIST.md",
    "docs/release-check/WVP-V040-RELEASE-NOTES-DRAFT.md",
]

for path in required_paths:
    p = Path(path)
    if not p.is_file() or p.stat().st_size == 0:
        problems.append("missing or empty referenced path: " + path)
    if path not in gate:
        problems.append("final gate does not mention path: " + path)

required = {"FRC-003", "FRC-004", "FRC-005", "FRC-006", "FRC-007"}
implemented = {
    row.get("id")
    for row in index.get("fixtures", [])
    if row.get("status") == "implemented"
}

missing = sorted(required - implemented)
if missing:
    problems.append("missing implemented fixture ids: " + ",".join(missing))

if report.get("status") != "PASS":
    problems.append("runner report status is not PASS")

if report.get("fixtures_failed") != 0:
    problems.append("runner report fixtures_failed not zero")

if report.get("semantic_unchecked_keys_total") != 0:
    problems.append("runner report unchecked semantic keys not zero")

claims = report.get("claims", {})
for key in [
    "audit_claim",
    "legal_compliance_claim",
    "binary_safety_claim",
    "source_to_release_claim",
    "reproducible_build_claim",
    "wallet_safety_claim",
    "investment_suitability_claim",
]:
    if claims.get(key) is not False:
        problems.append("runner report claim must be false: " + key)

forbidden_patterns = [
    ("audit passed", r"\baudit\s+passed\b"),
    ("legally compliant", r"\blegally\s+compliant\b"),
    ("legally approved", r"\blegally\s+approved\b"),
    ("binary safe claim", r"\bbinary\s+safe\b"),
    ("source-to-release proven", r"\bsource-to-release\s+proven\b"),
    ("reproducible build proven", r"\breproducible\s+build\s+proven\b"),
    ("wallet safe claim", r"\bwallet\s+safe\b"),
    ("investment suitable", r"\binvestment\s+suitable\b"),
    ("released status", r"\bstatus:\s*`released`\b"),
]

lower = gate.lower()
for label, pattern in forbidden_patterns:
    if re.search(pattern, lower):
        problems.append("forbidden phrase present: " + label)

if problems:
    for item in problems:
        print("FAIL:", item)
    raise SystemExit(1)

print("Final pre-release gate content OK.")
PY

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
if grep -nE "$PRIVATE_RE" "$FINAL_GATE" "$RELEASE_NOTES" "$CHECKLIST" "$SELF"; then
  echo "FAIL: secret-like material found."
  exit 1
fi
echo "No secret-like material found."

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo
echo "=== WVP v0.4 FINAL PRE-RELEASE GATE CONFORMANCE RESULT ==="
echo "RESULT: PASS"
echo "Final pre-release gate exists."
echo "Gate status is prepared-not-released."
echo "Required v0.4 evidence paths are present."
echo "Runner report status is PASS."
echo "No v0.4.0 tag exists."
echo "No v0.4.0 GitHub release exists."
echo "Boundary statements are explicit."
echo "No audit/legal/binary/reproducible/source-to-release claim is made."
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
