#!/usr/bin/env bash
set -euo pipefail

echo "=== AUNEYA Local Claim Composer v0.1 Conformance ==="

python3 tools/auneya/auneya_local_claim_composer.py \
  --reset \
  --demo-claim "Public local demo claim" \
  --build \
  --print-url

STATE_OUT="reports/auneya/local-claim-composer-v0.1/AUNEYA-LOCAL-CLAIM-COMPOSER-STATE-v0.1.json"
JSON_OUT="reports/auneya/local-claim-composer-v0.1/AUNEYA-LOCAL-CLAIM-COMPOSER-v0.1.json"
MD_OUT="reports/auneya/local-claim-composer-v0.1/AUNEYA-LOCAL-CLAIM-COMPOSER-v0.1.md"
HTML_OUT="reports/auneya/local-claim-composer-v0.1/index.html"

test -f "$STATE_OUT"
test -f "$JSON_OUT"
test -f "$MD_OUT"
test -f "$HTML_OUT"

python3 - <<'PY2'
import json
import sys
from pathlib import Path

state = json.loads(Path("reports/auneya/local-claim-composer-v0.1/AUNEYA-LOCAL-CLAIM-COMPOSER-STATE-v0.1.json").read_text(encoding="utf-8"))
report = json.loads(Path("reports/auneya/local-claim-composer-v0.1/AUNEYA-LOCAL-CLAIM-COMPOSER-v0.1.json").read_text(encoding="utf-8"))

def fail(msg):
    print("FAIL:", msg)
    sys.exit(1)

if state.get("schema_version") != "auneya-local-claim-composer-v0.1":
    fail("wrong state schema_version")

if report.get("schema_version") != "auneya-local-claim-composer-v0.1":
    fail("wrong report schema_version")

if state.get("mode") != "local_claim_composer_live_refresh_sandbox":
    fail("wrong state mode")

if report.get("mode") != "local_claim_composer_live_refresh_sandbox":
    fail("wrong report mode")

if state.get("network") != "none":
    fail("network must be none")

for key in ["mainnet_active", "token_created", "market_value_claimed", "transferable"]:
    if state.get(key) is not False:
        fail(key + " must be false")

wallet = state.get("wallet", {})
if wallet.get("balance") != 6:
    fail("wallet balance must be 6 after one demo claim")

if wallet.get("unit") != "simulated_neya_non_value_unit":
    fail("wrong unit")

for key in [
    "private_key_created",
    "seed_phrase_created",
    "custody_created",
    "send_enabled",
    "receive_enabled",
    "transfer_enabled",
]:
    if wallet.get(key) is not False:
        fail("wallet field must be false: " + key)

ledger = state.get("ledger", {})
if ledger.get("entry_count") != 6:
    fail("entry_count must be 6 after one demo claim")

entries = ledger.get("entries", [])
if len(entries) != 6:
    fail("entries length must be 6")

expected_tail = ["claim_accepted", "witness_prooflet", "event_finalized"]
actual_tail = [e.get("entry_type") for e in entries[-3:]]
if actual_tail != expected_tail:
    fail("tail entries wrong: " + repr(actual_tail))

for entry in entries[-3:]:
    if entry.get("amount") != 1:
        fail("new entry amount must be 1")
    if entry.get("unit") != "simulated_neya_non_value_unit":
        fail("new entry unit wrong")
    if entry.get("transferable") is not False:
        fail("new entry transferable must be false")
    if not entry.get("entry_hash"):
        fail("entry_hash missing")

claims = state.get("claims", [])
if len(claims) != 1:
    fail("claim count must be 1")

claim = claims[0]
if claim.get("claim_text") != "Public local demo claim":
    fail("claim text mismatch")

if claim.get("entries_added") != 3:
    fail("claim entries_added must be 3")

composer = state.get("composer", {})
if composer.get("claim_count") != 1:
    fail("composer claim_count must be 1")

if composer.get("live_refresh_enabled") is not True:
    fail("live refresh must be enabled")

if composer.get("form_enabled") is not True:
    fail("form must be enabled")

boundary = state.get("boundary", {})
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
    "local_only",
    "live_refresh_sandbox",
    "not_investment_advice",
    "not_legal_advice",
    "not_financial_service",
    "legal_review_required_before_launch",
]:
    if boundary.get(key) is not True:
        fail("boundary must be true: " + key)

dashboard = report.get("dashboard", {})
for key in ["mobile_first", "live_refresh_enabled", "local_only"]:
    if dashboard.get(key) is not True:
        fail("dashboard must be true: " + key)

if dashboard.get("external_dependencies") is not False:
    fail("external_dependencies must be false")

print("PASS AUNEYA Local Claim Composer v0.1 JSON validation")
PY2

grep -q "AUNEYA LOCAL CLAIM COMPOSER" "$HTML_OUT"
grep -q "Local live-refresh sandbox" "$HTML_OUT"
grep -q "Create Local Claim" "$HTML_OUT"
grep -q "/api/state" "$HTML_OUT"
grep -q "/claim" "$HTML_OUT"
grep -q "fetch('/api/state'" "$HTML_OUT"
grep -q "setInterval" "$HTML_OUT"
grep -q "Public local demo claim" "$HTML_OUT"
grep -q "claim_accepted" "$HTML_OUT"
grep -q "witness_prooflet" "$HTML_OUT"
grep -q "event_finalized" "$HTML_OUT"
grep -q "no token" "$HTML_OUT"
grep -q "no market value" "$HTML_OUT"
grep -q "no transferability" "$HTML_OUT"
grep -q "no mainnet" "$HTML_OUT"
grep -q "no private key" "$HTML_OUT"
grep -q "no seed phrase" "$HTML_OUT"

grep -q "Status: PASS" "$MD_OUT"
grep -q "local claim composer live-refresh sandbox" "$MD_OUT"
grep -q "Claim count" "$MD_OUT"
grep -q "It creates no token" "$MD_OUT"

echo "PASS AUNEYA Local Claim Composer v0.1 conformance"
