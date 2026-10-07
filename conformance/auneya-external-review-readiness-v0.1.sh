#!/usr/bin/env bash
set -euo pipefail

echo "=== AUNEYA External Review Readiness v0.1 Conformance ==="

python3 tools/auneya/auneya_external_review_readiness.py

JSON_OUT="reports/auneya/external-review-readiness-v0.1/AUNEYA-EXTERNAL-REVIEW-READINESS-v0.1.json"
MD_OUT="reports/auneya/external-review-readiness-v0.1/AUNEYA-EXTERNAL-REVIEW-READINESS-v0.1.md"

test -f "$JSON_OUT"
test -f "$MD_OUT"

python3 - <<'PY2'
import json
import sys
from pathlib import Path

path = Path("reports/auneya/external-review-readiness-v0.1/AUNEYA-EXTERNAL-REVIEW-READINESS-v0.1.json")
obj = json.loads(path.read_text(encoding="utf-8"))

def fail(msg):
    print("FAIL:", msg)
    sys.exit(1)

if obj.get("evidence_pack") != "auneya-external-review-readiness-v0.1":
    fail("wrong evidence_pack")

if obj.get("overall_status") != "pass":
    failed = [c.get("id") for c in obj.get("checks", []) if c.get("status") != "pass"]
    fail("failed checks: " + ", ".join(failed))

if obj.get("network") != "none":
    fail("network must be none")

for key in ["mainnet_active", "token_created", "market_value_claimed", "transferable"]:
    if obj.get(key) is not False:
        fail(key + " must be false")

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

print("PASS AUNEYA External Review Readiness v0.1 JSON validation")
PY2

grep -q "Status: PASS" "$MD_OUT"
grep -q "Mainnet active: false" "$MD_OUT"
grep -q "Token created: false" "$MD_OUT"
grep -q "Market value claimed: false" "$MD_OUT"
grep -q "Transferable: false" "$MD_OUT"

echo "PASS AUNEYA External Review Readiness v0.1 conformance"

