#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP v0.4 FIXTURE RUNNER REPORT CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

RUNNER="conformance/wvp-v040-release-check-fixture-runner-skeleton.sh"
INDEX="fixtures/release-check/FIXTURE-INDEX.json"
REPORT_JSON="reports/release-check/WVP-V040-FIXTURE-RUNNER-REPORT.json"
REPORT_MD="reports/release-check/WVP-V040-FIXTURE-RUNNER-REPORT.md"
SELF="${BASH_SOURCE[0]}"

echo "=== VERIFY FILES ==="
test -s "$RUNNER"
test -x "$RUNNER"
test -s "$INDEX"
test -s "$REPORT_JSON"
test -s "$REPORT_MD"
bash -n "$RUNNER"
python3 -m json.tool "$REPORT_JSON" >/dev/null
echo "Files OK."

echo "=== RUN LIVE RUNNER ==="
LIVE_JSON="$(mktemp)"
"$RUNNER" "$INDEX" --json-only > "$LIVE_JSON"
python3 -m json.tool "$LIVE_JSON" >/dev/null
echo "Live runner JSON OK."

echo "=== VERIFY REPORT MATCHES LIVE RUNNER SUMMARY ==="
python3 - "$LIVE_JSON" "$REPORT_JSON" "$REPORT_MD" <<'PY'
import json
import sys
from pathlib import Path

live = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
report = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
md = Path(sys.argv[3]).read_text(encoding="utf-8")

problems = []

required = {"FRC-003", "FRC-004", "FRC-005", "FRC-006", "FRC-007"}

if report.get("artifact") != "WVP-V040-FIXTURE-RUNNER-REPORT":
    problems.append("wrong artifact name")

for key in [
    "wvp_module",
    "suite",
    "runner_stage",
    "semantic_mode",
    "status",
    "fixtures_total",
    "fixtures_implemented",
    "fixtures_passed",
    "fixtures_warned",
    "fixtures_failed",
    "semantic_unchecked_keys_total",
    "offline",
    "network_required",
    "authentication_required",
    "release_mutation",
]:
    if report.get(key) != live.get(key):
        problems.append(f"summary mismatch for {key}: report={report.get(key)!r} live={live.get(key)!r}")

if report.get("status") != "PASS":
    problems.append("report status not PASS")

if report.get("fixtures_failed") != 0:
    problems.append("fixtures_failed not zero")

if report.get("semantic_unchecked_keys_total") != 0:
    problems.append("semantic_unchecked_keys_total not zero")

live_results = {item.get("id"): item for item in live.get("fixture_results", [])}
report_results = {item.get("id"): item for item in report.get("fixture_results", [])}

missing_live = sorted(required - set(live_results))
missing_report = sorted(required - set(report_results))

if missing_live:
    problems.append("missing live fixture results: " + ",".join(missing_live))

if missing_report:
    problems.append("missing report fixture results: " + ",".join(missing_report))

for fixture_id in sorted(required):
    live_item = live_results.get(fixture_id, {})
    report_item = report_results.get(fixture_id, {})

    for key in ["status", "checked_expected_keys", "unchecked_expected_keys", "mismatches"]:
        if report_item.get(key) != live_item.get(key):
            problems.append(f"{fixture_id} mismatch for {key}")

    if report_item.get("status") != "PASS":
        problems.append(f"{fixture_id} not PASS in report")

    if report_item.get("unchecked_expected_keys"):
        problems.append(f"{fixture_id} has unchecked expected keys")

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
        problems.append("claim must be false: " + key)

boundaries = report.get("boundaries", {})
for key in [
    "not_an_audit",
    "not_legal_clearance",
    "not_binary_safety_proof",
    "not_source_to_release_proof",
    "not_reproducible_build_proof",
    "not_wallet_safety_claim",
    "not_investment_advice",
]:
    if boundaries.get(key) is not True:
        problems.append("boundary must be true: " + key)

for phrase in [
    "This is not an audit.",
    "This is not legal clearance.",
    "This is not a binary safety proof.",
    "This is not a source-to-release proof.",
    "This is not a reproducible-build proof.",
    "This is not a wallet safety claim.",
    "This is not investment advice.",
]:
    if phrase not in md:
        problems.append("missing markdown boundary phrase: " + phrase)

if problems:
    for item in problems:
        print("FAIL:", item)
    raise SystemExit(1)

print("Report matches live runner summary.")
PY

echo "=== VERIFY NO SECRET-LIKE MATERIAL ==="
PRIVATE_RE='BEGIN (PGP |OPENSSH |RSA |EC |DSA )?PR''IVATE KEY|AGE-SE''CRET-KEY-|ghp_[A-Za-z0-9_]{20,}'
if grep -nE "$PRIVATE_RE" "$REPORT_JSON" "$REPORT_MD" "$SELF"; then
  echo "FAIL: secret-like material found."
  exit 1
fi
echo "No secret-like material found."

rm -f "$LIVE_JSON"

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo
echo "=== WVP v0.4 FIXTURE RUNNER REPORT CONFORMANCE RESULT ==="
echo "RESULT: PASS"
echo "Runner report JSON exists."
echo "Runner report Markdown exists."
echo "Report summary matches live runner output."
echo "Boundary statements are explicit."
echo "No audit/legal/binary/reproducible/source-to-release claim is made."
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
