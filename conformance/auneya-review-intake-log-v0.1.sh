#!/usr/bin/env bash
set -euo pipefail

echo "=== AUNEYA Review Intake Log v0.1 Conformance ==="

python3 tools/auneya/auneya_review_intake_log_check.py

JSON_OUT="reports/auneya/review-intake-log-v0.1/AUNEYA-REVIEW-INTAKE-LOG-v0.1.json"
MD_OUT="reports/auneya/review-intake-log-v0.1/AUNEYA-REVIEW-INTAKE-LOG-v0.1.md"

test -f "$JSON_OUT"
test -f "$MD_OUT"

python3 - <<'PY2'
import json
import sys
from pathlib import Path

path = Path("reports/auneya/review-intake-log-v0.1/AUNEYA-REVIEW-INTAKE-LOG-v0.1.json")
obj = json.loads(path.read_text(encoding="utf-8"))

def fail(msg):
    print("FAIL:", msg)
    sys.exit(1)

if obj.get("evidence_pack") != "auneya-review-intake-log-v0.1":
    fail("wrong evidence_pack")

if obj.get("overall_status") != "pass":
    failed = [c.get("id") for c in obj.get("checks", []) if c.get("status") != "pass"]
    fail("failed checks: " + ", ".join(failed))

if obj.get("network") != "none":
    fail("network must be none")

for key in ["mainnet_active", "token_created", "market_value_claimed", "transferable"]:
    if obj.get(key) is not False:
        fail(key + " must be false")

intake = obj.get("review_intake_state", {})
if intake.get("zero_intake_state") is not True:
    fail("zero_intake_state must be true")

if intake.get("external_review_received") is not False:
    fail("external_review_received must be false for this initial artifact")

if intake.get("fake_reviewer_feedback_created") is not False:
    fail("fake reviewer feedback must not be created")

if intake.get("intake_entries") != []:
    fail("initial intake_entries must be empty")

score = obj.get("score", {})
if score.get("percent", 0) < 100:
    fail("score must be 100 percent")

boundary = obj.get("boundary", {})
for key in [
    "no_token",
    "no_market_value",
    "no_transferability",
    "no_mainnet",
    "not_investment_advice",
    "not_legal_advice",
    "not_financial_service",
    "legal_review_required_before_launch",
]:
    if boundary.get(key) is not True:
        fail("boundary not true: " + key)

print("PASS AUNEYA Review Intake Log v0.1 JSON validation")
PY2

grep -q "Status: PASS" "$MD_OUT"
grep -q "Zero-intake state: true" "$MD_OUT"
grep -q "External review received: false" "$MD_OUT"
grep -q "Fake reviewer feedback created: false" "$MD_OUT"
grep -q "Mainnet active: false" "$MD_OUT"
grep -q "Token created: false" "$MD_OUT"
grep -q "Market value claimed: false" "$MD_OUT"
grep -q "Transferable: false" "$MD_OUT"

echo "PASS AUNEYA Review Intake Log v0.1 conformance"

