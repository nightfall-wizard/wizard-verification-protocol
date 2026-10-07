#!/usr/bin/env bash
set -euo pipefail

echo "=== AUNEYA Local Ledger + Wallet Simulator v0.1 Conformance ==="

python3 tools/auneya/auneya_local_ledger_wallet.py --print-wallet

JSON_OUT="reports/auneya/local-ledger-wallet-v0.1/AUNEYA-LOCAL-LEDGER-WALLET-v0.1.json"
MD_OUT="reports/auneya/local-ledger-wallet-v0.1/AUNEYA-LOCAL-LEDGER-WALLET-v0.1.md"
TXT_OUT="reports/auneya/local-ledger-wallet-v0.1/AUNEYA-LOCAL-WALLET-VIEW-v0.1.txt"

test -f "$JSON_OUT"
test -f "$MD_OUT"
test -f "$TXT_OUT"

python3 - <<'PY2'
import json
import sys
from pathlib import Path

path = Path("reports/auneya/local-ledger-wallet-v0.1/AUNEYA-LOCAL-LEDGER-WALLET-v0.1.json")
obj = json.loads(path.read_text(encoding="utf-8"))

def fail(msg):
    print("FAIL:", msg)
    sys.exit(1)

if obj.get("schema_version") != "auneya-local-ledger-wallet-v0.1":
    fail("wrong schema_version")

if obj.get("mode") != "local_non_value_simulation":
    fail("wrong mode")

if obj.get("network") != "none":
    fail("network must be none")

for key in ["mainnet_active", "token_created", "market_value_claimed", "transferable"]:
    if obj.get(key) is not False:
        fail(key + " must be false")

wallet = obj.get("wallet", {})
if wallet.get("wallet_id") != "local-wallet-001":
    fail("wrong wallet_id")

if not str(wallet.get("wallet_address", "")).startswith("auneya-local-"):
    fail("wallet address must be local-only")

for key in ["private_key_created", "seed_phrase_created", "custody_created", "send_enabled", "receive_enabled", "transfer_enabled"]:
    if wallet.get(key) is not False:
        fail(key + " must be false")

if wallet.get("balance") != 3:
    fail("wallet balance must be 3 simulated units")

if wallet.get("unit") != "simulated_neya_non_value_unit":
    fail("wrong wallet unit")

ledger = obj.get("ledger", {})
entries = ledger.get("entries", [])

if ledger.get("ledger_type") != "append_only_local_simulation_ledger":
    fail("wrong ledger_type")

if ledger.get("entry_count") != 3:
    fail("entry_count must be 3")

if len(entries) != 3:
    fail("entries length must be 3")

expected_types = ["claim_accepted", "witness_prooflet", "event_finalized"]
for idx, expected in enumerate(expected_types):
    entry = entries[idx]
    if entry.get("entry_type") != expected:
        fail("wrong entry type at index " + str(idx))
    if entry.get("amount") != 1:
        fail("entry amount must be 1")
    if entry.get("unit") != "simulated_neya_non_value_unit":
        fail("wrong entry unit")
    if not entry.get("entry_hash"):
        fail("entry_hash missing")
    if entry.get("transferable") is True:
        fail("entries must not be transferable")

if not ledger.get("ledger_hash"):
    fail("ledger_hash missing")

boundary = obj.get("boundary", {})
for key in [
    "mainnet_active",
    "token_created",
    "market_value_claimed",
    "transferable",
]:
    if boundary.get(key) is not False:
        fail("boundary must be false: " + key)

for key in [
    "not_investment_advice",
    "not_legal_advice",
    "not_financial_service",
    "legal_review_required_before_launch",
]:
    if boundary.get(key) is not True:
        fail("boundary must be true: " + key)

print("PASS AUNEYA Local Ledger + Wallet Simulator v0.1 JSON validation")
PY2

grep -q "AUNEYA LOCAL LEDGER" "$TXT_OUT"
grep -q "Wallet ID: local-wallet-001" "$TXT_OUT"
grep -q "Balance" "$TXT_OUT"
grep -q "3 simulated_neya_non_value_unit" "$TXT_OUT"
grep -q "claim_accepted" "$TXT_OUT"
grep -q "witness_prooflet" "$TXT_OUT"
grep -q "event_finalized" "$TXT_OUT"
grep -q "no token" "$TXT_OUT"
grep -q "no market value" "$TXT_OUT"
grep -q "no transferability" "$TXT_OUT"
grep -q "no mainnet" "$TXT_OUT"

grep -q "Status: PASS" "$MD_OUT"
grep -q "local ledger and local wallet simulator" "$MD_OUT"
grep -q "It creates no token" "$MD_OUT"
grep -q "It creates no private key" "$MD_OUT"

echo "PASS AUNEYA Local Ledger + Wallet Simulator v0.1 conformance"

