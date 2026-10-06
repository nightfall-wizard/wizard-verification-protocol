#!/usr/bin/env bash
set -euo pipefail

echo "=== AUNEYA Pulse and Prooflet Flow v0.1 Conformance ==="

python3 - <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

schema_path = Path("schemas/auneya-pulse-flow-v0.1.schema.json")
claim_fixture_dir = Path("fixtures/auneya/claims")
flow_fixture_dir = Path("fixtures/auneya/pulse-flow")

schema = json.loads(schema_path.read_text())

required = set(schema["required"])
flow_types = set(schema["properties"]["flow_type"]["enum"])
pulse_types = set(schema["properties"]["pulses"]["items"]["properties"]["pulse_type"]["enum"])
pulse_statuses = set(schema["properties"]["pulses"]["items"]["properties"]["observed_status"]["enum"])
micro_statuses = set(schema["properties"]["micro_proofs"]["items"]["properties"]["observed_status"]["enum"])
prooflet_statuses = set(schema["properties"]["prooflet"]["properties"]["observed_status"]["enum"])

def fail(path, msg):
    print(f"FAIL {path}: {msg}")
    sys.exit(1)

def parse_dt(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)

def is_sha256(value):
    return isinstance(value, str) and value.startswith("sha256:") and len(value) == 71

def load_claims():
    claims = {}
    for path in claim_fixture_dir.glob("*.json"):
        obj = json.loads(path.read_text())
        claims[obj["claim_id"]] = obj
    return claims

def lawful_claim(obj):
    if not obj:
        return False

    pa = obj["public_access"]

    if pa["requires_authentication"] is True:
        return False

    if pa["requires_payment"] is True:
        return False

    if pa["contains_personal_data"] is True:
        return False

    return pa["lawful_basis"] in {
        "publicly_accessible",
        "owner_authorized",
        "publisher_provided",
    }

def lawful_flow(obj):
    lb = obj["lawful_boundary_confirmation"]

    keys = [
        "public_or_authorized_target",
        "no_private_data_accessed",
        "no_hacked_data_used",
        "no_paywall_bypass_used",
        "no_credentials_used",
        "no_surveillance_performed",
    ]

    return all(lb.get(k) is True for k in keys)

def non_value_reward(obj):
    entry = obj["simulated_reward_entry"]

    if entry["entry_type"] != "non_value_simulation":
        return False

    if entry["unit"] != "simulated_neya":
        return False

    if entry["transferable"] is not False:
        return False

    if entry["market_value_claimed"] is not False:
        return False

    return True

def validate_common(path, obj):
    missing = sorted(required - set(obj.keys()))
    if missing:
        fail(path, f"missing required fields: {missing}")

    if obj["schema_version"] != "auneya-pulse-flow-v0.1":
        fail(path, "wrong schema_version")

    if not obj["flow_id"].startswith("auneya_flow_"):
        fail(path, "flow_id must start with auneya_flow_")

    if obj["flow_type"] not in flow_types:
        fail(path, "invalid flow_type")

    claim_ref = obj["claim_ref"]

    if not claim_ref["claim_id"].startswith("auneya_claim_"):
        fail(path, "invalid claim_id")

    if claim_ref["claim_schema_version"] != "auneya-claim-v0.1":
        fail(path, "wrong claim_schema_version")

    if not is_sha256(claim_ref["claim_hash"]):
        fail(path, "invalid claim_hash")

    witness = obj["witness"]

    if not witness["witness_id"].startswith("witness_"):
        fail(path, "invalid witness_id")

    if witness["device_class"] != "android_termux":
        fail(path, "v0.1 valid flow must be android_termux")

    if witness["environment_class"] != "phone_safe":
        fail(path, "v0.1 valid flow must be phone_safe")

    cadence = obj["cadence"]

    if cadence["pulse_interval_seconds"] != 1:
        fail(path, "v0.1 pulse interval must be 1 second")

    if not obj["pulses"]:
        fail(path, "pulses must not be empty")

    if not obj["micro_proofs"]:
        fail(path, "micro_proofs must not be empty")

    pulse_indexes = [p["pulse_index"] for p in obj["pulses"]]

    if pulse_indexes != list(range(1, len(pulse_indexes) + 1)):
        fail(path, "pulse indexes must be sequential starting at 1")

    pulse_index_set = set(pulse_indexes)

    pulse_times = []

    for pulse in obj["pulses"]:
        if pulse["pulse_type"] not in pulse_types:
            fail(path, "invalid pulse_type")

        if pulse["observed_status"] not in pulse_statuses:
            fail(path, "invalid pulse observed_status")

        pulse_times.append(parse_dt(pulse["observed_at"]))

    for earlier, later in zip(pulse_times, pulse_times[1:]):
        delta = int((later - earlier).total_seconds())
        if delta != cadence["pulse_interval_seconds"]:
            fail(path, "pulse cadence is not one second")

    micro_ids = []

    for mp in obj["micro_proofs"]:
        if not mp["micro_proof_id"].startswith("auneya_micro_proof_"):
            fail(path, "invalid micro_proof_id")

        if not is_sha256(mp["micro_proof_hash"]):
            fail(path, "invalid micro_proof_hash")

        if mp["observed_status"] not in micro_statuses:
            fail(path, "invalid micro proof status")

        if not mp["pulse_indexes"]:
            fail(path, "micro proof must reference at least one pulse")

        for idx in mp["pulse_indexes"]:
            if idx not in pulse_index_set:
                fail(path, "micro proof references missing pulse index")

        micro_ids.append(mp["micro_proof_id"])

    if len(set(micro_ids)) != len(micro_ids):
        fail(path, "duplicate micro_proof_id")

    prooflet = obj["prooflet"]

    if not prooflet["prooflet_id"].startswith("auneya_prooflet_"):
        fail(path, "invalid prooflet_id")

    if prooflet["claim_id"] != claim_ref["claim_id"]:
        fail(path, "prooflet claim_id must match flow claim_id")

    if prooflet["observed_status"] not in prooflet_statuses:
        fail(path, "invalid prooflet status")

    if not is_sha256(prooflet["prooflet_hash"]):
        fail(path, "invalid prooflet_hash")

    for mpid in prooflet["micro_proof_ids"]:
        if mpid not in micro_ids:
            fail(path, "prooflet references missing micro proof")

claims = load_claims()

def validate_flow_semantics(path, obj):
    claim = claims.get(obj["claim_ref"]["claim_id"])

    if not lawful_claim(claim):
        return False, "referenced claim is not lawful-public"

    if not lawful_flow(obj):
        return False, "flow legal boundary confirmation failed"

    if not non_value_reward(obj):
        return False, "simulated reward entry violates non-value boundary"

    return True, "ok"

valid_files = [
    flow_fixture_dir / "valid-phone-release-reality-flow.json",
]

invalid_files = [
    flow_fixture_dir / "invalid-private-target-flow.json",
    flow_fixture_dir / "invalid-value-reward-flow.json",
]

for path in valid_files:
    obj = json.loads(path.read_text())
    validate_common(path, obj)

    ok, msg = validate_flow_semantics(path, obj)
    if not ok:
        fail(path, msg)

for path in invalid_files:
    obj = json.loads(path.read_text())
    validate_common(path, obj)

    ok, msg = validate_flow_semantics(path, obj)
    if ok:
        fail(path, "invalid flow was not rejected")

print("PASS AUNEYA Pulse and Prooflet Flow v0.1 conformance")
PY
