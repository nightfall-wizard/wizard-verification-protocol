#!/usr/bin/env bash
set -euo pipefail

echo "=== AUNEYA Local Dashboard v0.1 Conformance ==="

python3 tools/auneya/auneya_local_dashboard.py --build --print-url

JSON_OUT="reports/auneya/local-dashboard-v0.1/AUNEYA-LOCAL-DASHBOARD-v0.1.json"
MD_OUT="reports/auneya/local-dashboard-v0.1/AUNEYA-LOCAL-DASHBOARD-v0.1.md"
HTML_OUT="reports/auneya/local-dashboard-v0.1/index.html"

test -f "$JSON_OUT"
test -f "$MD_OUT"
test -f "$HTML_OUT"

python3 - <<'PY2'
import json
import sys
from pathlib import Path

path = Path("reports/auneya/local-dashboard-v0.1/AUNEYA-LOCAL-DASHBOARD-v0.1.json")
obj = json.loads(path.read_text(encoding="utf-8"))

def fail(msg):
    print("FAIL:", msg)
    sys.exit(1)

if obj.get("schema_version") != "auneya-local-dashboard-v0.1":
    fail("wrong schema_version")

if obj.get("mode") != "local_browser_dashboard_read_only":
    fail("wrong mode")

if obj.get("status") != "pass":
    fail("status must be pass")

dashboard = obj.get("dashboard", {})
for key in ["mobile_first", "read_only", "static_html"]:
    if dashboard.get(key) is not True:
        fail("dashboard must be true: " + key)

for key in [
    "external_dependencies",
    "input_forms",
    "send_controls",
    "receive_controls",
    "transfer_controls",
    "private_key_fields",
    "seed_phrase_fields",
]:
    if dashboard.get(key) is not False:
        fail("dashboard must be false: " + key)

wallet = obj.get("wallet_snapshot", {})
if not str(wallet.get("wallet_address", "")).startswith("auneya-local-"):
    fail("wallet address must be local-only")

if wallet.get("balance") != 3:
    fail("wallet balance must be 3")

ledger = obj.get("ledger_snapshot", {})
if ledger.get("entry_count") != 3:
    fail("ledger entry count must be 3")

if not ledger.get("ledger_hash"):
    fail("ledger hash missing")

boundary = obj.get("boundary", {})
for key in [
    "mainnet_active",
    "token_created",
    "market_value_claimed",
    "transferable",
    "private_key_created",
    "seed_phrase_created",
    "custody_created",
    "send_enabled",
    "receive_enabled",
    "transfer_enabled",
]:
    if boundary.get(key) is not False:
        fail("boundary must be false: " + key)

for key in [
    "read_only",
    "not_investment_advice",
    "not_legal_advice",
    "not_financial_service",
    "legal_review_required_before_launch",
]:
    if boundary.get(key) is not True:
        fail("boundary must be true: " + key)

print("PASS AUNEYA Local Dashboard v0.1 JSON validation")
PY2

grep -q "AUNEYA LOCAL DASHBOARD" "$HTML_OUT"
grep -q "Read-only local non-value simulation" "$HTML_OUT"
grep -q "Wallet" "$HTML_OUT"
grep -q "Balance" "$HTML_OUT"
grep -q "Ledger Entries" "$HTML_OUT"
grep -q "History" "$HTML_OUT"
grep -q "Boundary" "$HTML_OUT"
grep -q "auneya-local-" "$HTML_OUT"
grep -q "simulated_neya_non_value_unit" "$HTML_OUT"
grep -q "no token" "$HTML_OUT"
grep -q "no market value" "$HTML_OUT"
grep -q "no transferability" "$HTML_OUT"
grep -q "no mainnet" "$HTML_OUT"

if grep -qi "<form" "$HTML_OUT"; then
  echo "FAIL: dashboard must not contain forms"
  exit 1
fi

grep -q "Status: PASS" "$MD_OUT"
grep -q "local browser dashboard read-only" "$MD_OUT"
grep -q "Mobile-first" "$MD_OUT"
grep -q "Read-only" "$MD_OUT"
grep -q "It creates no token" "$MD_OUT"

echo "PASS AUNEYA Local Dashboard v0.1 conformance"
