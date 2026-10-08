#!/usr/bin/env bash
set -euo pipefail

echo "=== AUNEYA Recurring Review Evidence v0.1 Conformance ==="

python3 tools/auneya/auneya_recurring_review_evidence_check.py

JSON_OUT="reports/auneya/recurring-review-evidence-v0.1/AUNEYA-RECURRING-REVIEW-EVIDENCE-v0.1.json"
MD_OUT="reports/auneya/recurring-review-evidence-v0.1/AUNEYA-RECURRING-REVIEW-EVIDENCE-v0.1.md"

test -f "$JSON_OUT"
test -f "$MD_OUT"

python3 - <<'PY2'
import json
import sys
from pathlib import Path

path = Path("reports/auneya/recurring-review-evidence-v0.1/AUNEYA-RECURRING-REVIEW-EVIDENCE-v0.1.json")
obj = json.loads(path.read_text(encoding="utf-8"))

def fail(msg):
    print("FAIL:", msg)
    sys.exit(1)

if obj.get("evidence_pack") != "auneya-recurring-review-evidence-v0.1":
    fail("wrong evidence_pack")

if obj.get("overall_status") != "pass":
    failed = [c.get("id") for c in obj.get("checks", []) if c.get("status") != "pass"]
    fail("failed checks: " + ", ".join(failed))

if obj.get("network") != "none":
    fail("network must be none")

for key in ["mainnet_active", "token_created", "market_value_claimed", "transferable"]:
    if obj.get(key) is not False:
        fail(key + " must be false")

state = obj.get("recurring_review_state", {})
if state.get("external_feedback_received") is not False:
    fail("external_feedback_received must be false in initial artifact")

if state.get("fake_feedback_created") is not False:
    fail("fake feedback must not be created")

if state.get("issue_count") != 0:
    fail("initial issue_count must be 0")

if state.get("trail_entries") != []:
    fail("initial trail_entries must be empty")

workflow = obj.get("workflow", {})
if workflow.get("manual_dispatch") is not True:
    fail("manual_dispatch must be true")

if workflow.get("scheduled_check") is not True:
    fail("scheduled_check must be true")

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

print("PASS AUNEYA Recurring Review Evidence v0.1 JSON validation")
PY2

grep -q "Status: PASS" "$MD_OUT"
grep -q "External feedback received: false" "$MD_OUT"
grep -q "Fake feedback created: false" "$MD_OUT"
grep -q "Issue count: 0" "$MD_OUT"
grep -q "workflow_dispatch" "$MD_OUT"
grep -q "Mainnet active: false" "$MD_OUT"
grep -q "Token created: false" "$MD_OUT"
grep -q "Market value claimed: false" "$MD_OUT"
grep -q "Transferable: false" "$MD_OUT"

echo "PASS AUNEYA Recurring Review Evidence v0.1 conformance"

