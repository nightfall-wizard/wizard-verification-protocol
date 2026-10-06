#!/usr/bin/env bash
set -euo pipefail

echo "=== AUNEYA Local Witness Runner v0.1 Conformance ==="

TMP_DIR=".tmp/auneya-local-runner"
VALID_OUT="$TMP_DIR/valid-local-flow.json"
INVALID_OUT="$TMP_DIR/invalid-private-flow.json"

rm -rf "$TMP_DIR"
mkdir -p "$TMP_DIR"

python3 tools/auneya/auneya_local_witness_runner.py \
  --claim fixtures/auneya/claims/valid-release-reality.json \
  --out "$VALID_OUT" \
  --witness-id witness_android_termux_local_001 \
  --start-time 2026-10-06T00:08:00Z

test -f "$VALID_OUT"

python3 - <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

path = Path(".tmp/auneya-local-runner/valid-local-flow.json")
obj = json.loads(path.read_text())

def fail(msg):
    print(f"FAIL {path}: {msg}")
    sys.exit(1)

def parse_dt(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)

def is_sha256(value):
    return isinstance(value, str) and value.startswith("sha256:") and len(value) == 71

if obj["schema_version"] != "auneya-pulse-flow-v0.1":
    fail("wrong schema_version")

if obj["flow_type"] != "phone_witness_loop":
    fail("wrong flow_type")

if obj["witness"]["device_class"] != "android_termux":
    fail("wrong device_class")

if obj["witness"]["environment_class"] != "phone_safe":
    fail("wrong environment_class")

if obj["cadence"]["pulse_interval_seconds"] != 1:
    fail("pulse interval must be one second")

if len(obj["pulses"]) != 4:
    fail("runner must produce four pulses in v0.1")

if len(obj["micro_proofs"]) != 2:
    fail("runner must produce two micro proofs in v0.1")

if not obj["prooflet"]["prooflet_id"].startswith("auneya_prooflet_"):
    fail("invalid prooflet id")

if obj["prooflet"]["claim_id"] != obj["claim_ref"]["claim_id"]:
    fail("prooflet claim id must match claim ref")

for key in [
    "public_or_authorized_target",
    "no_private_data_accessed",
    "no_hacked_data_used",
    "no_paywall_bypass_used",
    "no_credentials_used",
    "no_surveillance_performed",
]:
    if obj["lawful_boundary_confirmation"].get(key) is not True:
        fail(f"legal boundary failed: {key}")

reward = obj["simulated_reward_entry"]

if reward["entry_type"] != "non_value_simulation":
    fail("reward entry must be non_value_simulation")

if reward["unit"] != "simulated_neya":
    fail("reward unit must be simulated_neya")

if reward["transferable"] is not False:
    fail("reward entry must be non-transferable")

if reward["market_value_claimed"] is not False:
    fail("reward entry must not claim market value")

if reward["amount"] <= 0:
    fail("valid local flow should have positive simulated amount")

for value in [
    obj["claim_ref"]["claim_hash"],
    obj["prooflet"]["prooflet_hash"],
]:
    if not is_sha256(value):
        fail("invalid sha256 value")

pulse_times = [parse_dt(p["observed_at"]) for p in obj["pulses"]]

for earlier, later in zip(pulse_times, pulse_times[1:]):
    if int((later - earlier).total_seconds()) != 1:
        fail("pulse cadence is not one second")

micro_ids = {mp["micro_proof_id"] for mp in obj["micro_proofs"]}

for mpid in obj["prooflet"]["micro_proof_ids"]:
    if mpid not in micro_ids:
        fail("prooflet references missing micro proof")

print("PASS local runner output validation")
PY

set +e
python3 tools/auneya/auneya_local_witness_runner.py \
  --claim fixtures/auneya/claims/invalid-private-data-claim.json \
  --out "$INVALID_OUT" \
  --witness-id witness_android_termux_local_001 \
  --start-time 2026-10-06T00:09:00Z
STATUS=$?
set -e

if [ "$STATUS" -eq 0 ]; then
  echo "FAIL: private-data claim was not rejected"
  exit 1
fi

if [ -f "$INVALID_OUT" ]; then
  echo "FAIL: invalid private flow output should not exist"
  exit 1
fi

echo "PASS AUNEYA Local Witness Runner v0.1 conformance"
