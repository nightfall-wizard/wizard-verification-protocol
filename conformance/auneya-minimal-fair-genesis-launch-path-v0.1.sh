#!/usr/bin/env bash
set -euo pipefail

echo "=== AUNEYA Minimal Fair-Genesis Launch Path v0.1 Conformance ==="

DOC="docs/auneya/AUNEYA-MINIMAL-FAIR-GENESIS-LAUNCH-PATH-V0.1.md"
JSON_FIXTURE="fixtures/auneya/legal/minimal-fair-genesis-launch-path-v0.1.json"

test -f "$DOC"
test -f "$JSON_FIXTURE"

echo "=== Dokument-Inhalte prüfen ==="
grep -q "AUNEYA Minimal Fair-Genesis Launch Path v0.1" "$DOC"
grep -q "Finish the open-source protocol code" "$DOC"
grep -q "Do not create coins before final legal mainnet genesis" "$DOC"
grep -q "Do not sell coins" "$DOC"
grep -q "Do not manually allocate coins" "$DOC"
grep -q "Do not request personal data in exchange for coins" "$DOC"
grep -q "Do not hold wallets, keys or coins for other users" "$DOC"
grep -q "Do not operate an exchange, broker, custody service or advisory service" "$DOC"
grep -q "Do not communicate an official price or listing promise" "$DOC"
grep -q "Publish a Final Genesis Notice before any mainnet genesis" "$DOC"
grep -q "Start with genesis supply 0" "$DOC"
grep -q "every user can run the software independently" "$DOC"
grep -q "Units may arise only automatically from valid post-genesis protocol work" "$DOC"
grep -q "genesis supply: 0 AUNEYA" "$DOC"
grep -q "premine: no" "$DOC"
grep -q "ICO: no" "$DOC"
grep -q "sale: no" "$DOC"
grep -q "official price: no" "$DOC"
grep -q "listing promise: no" "$DOC"
grep -q "legal review before genesis: required" "$DOC"
grep -q "users control their own wallets" "$DOC"
grep -q "users control their own keys" "$DOC"
grep -q "no maintainer custody" "$DOC"
grep -q "Prohibited public communication categories" "$DOC"
grep -q "purchase solicitation" "$DOC"
grep -q "investment solicitation" "$DOC"
grep -q "value-increase claims" "$DOC"
grep -q "return claims" "$DOC"
grep -q "yield claims" "$DOC"
grep -q "exchange-access promises" "$DOC"
grep -q "trading-venue promises" "$DOC"
grep -q "official valuation targets" "$DOC"
grep -q "simulation-to-mainnet conversion claims" "$DOC"
grep -q "testnet-to-mainnet conversion claims" "$DOC"

echo "=== Maschinenlesbare Policy prüfen ==="
python3 - <<'PY'
import json
import sys
from pathlib import Path

path = Path("fixtures/auneya/legal/minimal-fair-genesis-launch-path-v0.1.json")
obj = json.loads(path.read_text())

def fail(msg):
    print(f"FAIL {path}: {msg}")
    sys.exit(1)

if obj["schema_version"] != "auneya-minimal-fair-genesis-launch-path-v0.1":
    fail("wrong schema_version")

if obj["status"] != "protocol_research":
    fail("wrong status")

for key in [
    "launches_mainnet",
    "creates_token",
    "creates_auneya",
    "creates_neya",
    "creates_real_reward",
    "claims_market_value",
    "makes_transferable",
]:
    if obj.get(key) is not False:
        fail(f"{key} must be false")

path_items = obj["minimal_launch_path"]
if len(path_items) != 12:
    fail("minimal launch path must contain exactly 12 steps")

required_path_items = [
    "finish_open_source_protocol_code",
    "do_not_create_coins_before_final_legal_mainnet_genesis",
    "do_not_sell_coins",
    "do_not_manually_allocate_coins",
    "do_not_request_personal_data_in_exchange_for_coins",
    "do_not_hold_wallets_keys_or_coins_for_other_users",
    "do_not_operate_exchange_broker_custody_or_advisory_service",
    "do_not_communicate_official_price_or_listing_promise",
    "publish_final_genesis_notice_before_mainnet_genesis",
    "start_with_genesis_supply_0",
    "after_final_genesis_every_user_can_run_software_independently",
    "units_arise_only_automatically_from_valid_post_genesis_protocol_work",
]

for item in required_path_items:
    if item not in path_items:
        fail(f"missing launch path item: {item}")

pre = obj["pre_genesis"]
for key in [
    "mainnet_live",
    "auneya_exists",
    "neya_exists",
    "mainnet_balance_exists",
    "transferable_unit_exists",
    "official_price_exists",
    "listing_promised",
    "public_token_sale_exists",
    "premine_exists",
    "ico_exists",
    "claim_to_future_coins_exists",
    "simulation_converts_to_mainnet",
    "testnet_converts_to_mainnet",
]:
    if pre.get(key) is not False:
        fail(f"pre_genesis.{key} must be false")

genesis = obj["genesis"]
if genesis["genesis_supply_auneya"] != 0:
    fail("genesis supply must be 0")

for key in [
    "premine",
    "ico",
    "sale",
    "manual_allocation",
    "official_price",
    "listing_promise",
    "investment_claim",
    "return_profit_or_yield_promise",
    "automatic_conversion_from_simulation",
    "automatic_conversion_from_testnet",
    "automatic_conversion_from_contribution_history",
]:
    if genesis.get(key) is not False:
        fail(f"genesis.{key} must be false")

if genesis["legal_review_before_genesis_required"] is not True:
    fail("legal review before genesis must be required")

post = obj["post_genesis"]
for key in [
    "users_run_own_software",
    "users_control_own_wallets",
    "users_control_own_keys",
    "units_arise_only_by_final_protocol_rules",
    "units_arise_only_from_valid_post_genesis_witness_or_ledger_work",
]:
    if post.get(key) is not True:
        fail(f"post_genesis.{key} must be true")

for key in [
    "maintainer_account_required",
    "maintainer_custody_required",
    "central_issuer_manual_distribution_required",
    "maintainer_sale_required",
]:
    if post.get(key) is not False:
        fail(f"post_genesis.{key} must be false")

services = obj["prohibited_services"]
for key in [
    "custody_of_third_party_assets",
    "custody_of_private_keys",
    "exchange_services",
    "brokerage",
    "investment_advice",
    "portfolio_management",
    "market_making",
    "listing_coordination",
    "paid_token_allocation",
    "paid_token_sale",
    "guaranteed_liquidity",
    "fiat_on_ramp",
    "fiat_off_ramp",
]:
    if services.get(key) is not True:
        fail(f"prohibited service must be true: {key}")

categories = set(obj["prohibited_communication_categories"])
for item in [
    "purchase_solicitation",
    "investment_solicitation",
    "value_increase_claims",
    "return_claims",
    "yield_claims",
    "exchange_access_promises",
    "trading_venue_promises",
    "official_valuation_targets",
    "guaranteed_future_allocation_claims",
    "simulation_to_mainnet_conversion_claims",
    "testnet_to_mainnet_conversion_claims",
]:
    if item not in categories:
        fail(f"missing prohibited communication category: {item}")

gate = set(obj["legal_gate_required_before_final_mainnet_genesis"])
for item in [
    "written_legal_review_completed_for_target_jurisdiction",
    "crypto_financial_regulatory_review_completed",
    "tax_accounting_review_completed",
    "service_boundary_reviewed",
    "custody_boundary_reviewed",
    "no_sale_rule_published",
    "no_premine_rule_published",
    "no_ico_rule_published",
    "no_official_price_rule_published",
    "no_listing_promise_rule_published",
]:
    if item not in gate:
        fail(f"missing legal gate item: {item}")

print("PASS minimal fair-genesis launch path validation")
PY

echo "=== Riskante positive Aussagen dürfen nicht vorkommen ==="
python3 - <<'PY2'
from pathlib import Path
import base64
import sys

targets = [
    Path("docs/auneya/AUNEYA-MINIMAL-FAIR-GENESIS-LAUNCH-PATH-V0.1.md"),
    Path("fixtures/auneya/legal/minimal-fair-genesis-launch-path-v0.1.json"),
]

encoded_blocklist = [
    "Z3VhcmFudGVlZCBwcm9maXQ=",
    "cHJvZml0IGd1YXJhbnRlZQ==",
    "Z3VhcmFudGVlZCByZXR1cm4=",
    "bWFya2V0IHZhbHVlIGlzIGd1YXJhbnRlZWQ=",
    "d2lsbCBpbmNyZWFzZSBpbiB2YWx1ZQ==",
    "Z3VhcmFudGVlZCB5aWVsZA==",
    "Z3VhcmFudGVlZCBpbmNvbWU=",
    "bGlzdGluZyBzb29u",
    "ZXhjaGFuZ2Ugc29vbg==",
    "ZWFybHkgYmVmb3JlIGxpc3Rpbmc=",
    "MTAweA==",
    "cGFzc2l2ZSBpbmNvbWU=",
    "YnV5IG5vdw==",
    "cHJpY2UgdGFyZ2V0",
    "YXVuZXlhIHdpbGwgaW5jcmVhc2UgaW4gdmFsdWU=",
    "YXVuZXlhIGhhcyBhIGd1YXJhbnRlZWQgcmV0dXJu",
    "YXVuZXlhIGhhcyBndWFyYW50ZWVkIHlpZWxk",
    "YXVuZXlhIGxpc3RpbmcgaXMgY29taW5n",
    "ZXhjaGFuZ2UgbGF1bmNoIGlzIGNvbWluZw==",
    "b2ZmaWNpYWwgcHJpY2UgdGFyZ2V0",
]

blocked = [
    base64.b64decode(item).decode("utf-8").lower()
    for item in encoded_blocklist
]

hits = []

for path in targets:
    data = path.read_text(errors="replace").lower()
    for phrase in blocked:
        if phrase in data:
            hits.append(str(path))
            break

if hits:
    print("FAIL: blocked legal wording detected")
    for path in sorted(set(hits)):
        print(path)
    sys.exit(1)

print("PASS risky wording check")
PY2

echo "PASS AUNEYA Minimal Fair-Genesis Launch Path v0.1 conformance"
