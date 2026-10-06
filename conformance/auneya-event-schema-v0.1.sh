#!/usr/bin/env bash
set -euo pipefail

echo "=== AUNEYA Event Schema v0.1 Conformance ==="

python3 - <<'PY'
import json
import sys
from pathlib import Path

event_schema_path = Path("schemas/auneya-event-v0.1.schema.json")
claim_fixture_dir = Path("fixtures/auneya/claims")
proof_fixture_dir = Path("fixtures/auneya/witness-proofs")
event_fixture_dir = Path("fixtures/auneya/events")

schema = json.loads(event_schema_path.read_text())

required = set(schema["required"])
event_types = set(schema["properties"]["event_type"]["enum"])
event_statuses = set(schema["properties"]["event_status"]["enum"])
matching_statuses = set(schema["properties"]["quorum"]["properties"]["required_matching_status"]["enum"])
signature_statuses = set(schema["properties"]["integrity"]["properties"]["signature_status"]["enum"])

def fail(path, msg):
    print(f"FAIL {path}: {msg}")
    sys.exit(1)

def load_claims(path):
    out = {}
    for p in path.glob("*.json"):
        obj = json.loads(p.read_text())
        out[obj["claim_id"]] = obj
    return out

def load_proofs(path):
    out = {}
    for p in path.glob("*.json"):
        obj = json.loads(p.read_text())
        out[obj["proof_id"]] = obj
    return out

claims = load_claims(claim_fixture_dir)
proofs = load_proofs(proof_fixture_dir)

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

def lawful_proof(obj):
    if not obj:
        return False

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

def lawful_event(obj):
    lb = obj["lawful_boundary_confirmation"]

    keys = [
        "only_lawful_public_or_authorized_proofs",
        "no_private_data_accessed",
        "no_hacked_data_used",
        "no_paywall_bypass_used",
        "no_credentials_used",
        "no_surveillance_performed",
    ]

    return all(lb.get(k) is True for k in keys)

def is_sha256(value):
    return isinstance(value, str) and value.startswith("sha256:") and len(value) == 71

def validate_common(path, obj):
    missing = sorted(required - set(obj.keys()))
    if missing:
        fail(path, f"missing required fields: {missing}")

    if obj["schema_version"] != "auneya-event-v0.1":
        fail(path, "wrong schema_version")

    if not obj["event_id"].startswith("auneya_event_"):
        fail(path, "event_id must start with auneya_event_")

    if obj["event_type"] not in event_types:
        fail(path, "invalid event_type")

    if not obj["claim_id"].startswith("auneya_claim_"):
        fail(path, "claim_id must start with auneya_claim_")

    if obj["claim_schema_version"] != "auneya-claim-v0.1":
        fail(path, "wrong claim_schema_version")

    if not is_sha256(obj["claim_hash"]):
        fail(path, "invalid claim_hash")

    if obj["event_status"] not in event_statuses:
        fail(path, "invalid event_status")

    q = obj["quorum"]

    if q["required_matching_status"] not in matching_statuses:
        fail(path, "invalid required_matching_status")

    if q["actual_witnesses"] != len(obj["witness_proofs"]):
        fail(path, "actual_witnesses must match witness_proofs length")

    if q["independent_witnesses"] > q["actual_witnesses"]:
        fail(path, "independent_witnesses cannot exceed actual_witnesses")

    if q["min_witnesses"] > q["actual_witnesses"]:
        fail(path, "min_witnesses cannot exceed actual_witnesses")

    if not obj["witness_proofs"]:
        fail(path, "witness_proofs must not be empty")

    for ref in obj["witness_proofs"]:
        if not ref["proof_id"].startswith("auneya_proof_"):
            fail(path, "invalid proof_id")

        if ref["proof_schema_version"] != "auneya-witness-proof-v0.1":
            fail(path, "invalid proof_schema_version")

        if not is_sha256(ref["proof_hash"]):
            fail(path, "invalid proof_hash")

        if not ref["witness_id"].startswith("witness_"):
            fail(path, "invalid witness_id")

        if ref["observed_status"] not in matching_statuses:
            fail(path, "invalid observed_status")

    if obj["integrity"]["signature_status"] not in signature_statuses:
        fail(path, "invalid signature_status")

    if not is_sha256(obj["integrity"]["event_hash"]):
        fail(path, "invalid event_hash")

def validate_event_semantics(path, obj):
    claim = claims.get(obj["claim_id"])

    if not lawful_claim(claim):
        return False, "referenced claim is not lawful-public"

    if not lawful_event(obj):
        return False, "event legal boundary confirmation failed"

    proof_ids = []
    witness_ids = []
    statuses = []

    for ref in obj["witness_proofs"]:
        proof = proofs.get(ref["proof_id"])

        if not proof:
            return False, f"referenced proof not found: {ref['proof_id']}"

        if not lawful_proof(proof):
            return False, f"referenced proof is not lawful: {ref['proof_id']}"

        if proof["claim_id"] != obj["claim_id"]:
            return False, "proof claim_id does not match event claim_id"

        if proof["claim_hash"] != obj["claim_hash"]:
            return False, "proof claim_hash does not match event claim_hash"

        if proof["integrity"]["proof_hash"] != ref["proof_hash"]:
            return False, "proof_hash reference mismatch"

        if proof["witness"]["witness_id"] != ref["witness_id"]:
            return False, "witness_id reference mismatch"

        if proof["observed_status"] != ref["observed_status"]:
            return False, "observed_status reference mismatch"

        proof_ids.append(ref["proof_id"])
        witness_ids.append(ref["witness_id"])
        statuses.append(ref["observed_status"])

    if len(set(proof_ids)) != len(proof_ids):
        return False, "duplicate proof_id"

    if len(set(witness_ids)) != len(witness_ids):
        return False, "duplicate witness_id"

    if obj["quorum"]["independent_witnesses"] != len(set(witness_ids)):
        return False, "independent_witnesses does not match unique witness count"

    if obj["quorum"]["required_matching_status"] not in statuses:
        return False, "required status not present"

    if obj["event_status"] in {"witnessed", "sealed"}:
        if len(set(statuses)) != 1:
            return False, "non-dispute event requires matching statuses"

        if statuses[0] != obj["quorum"]["required_matching_status"]:
            return False, "status does not match quorum required status"

    return True, "ok"

valid_files = [
    event_fixture_dir / "valid-witnessed-release-reality-event.json",
]

invalid_files = [
    event_fixture_dir / "invalid-duplicate-witness-event.json",
    event_fixture_dir / "invalid-private-data-event.json",
]

for path in valid_files:
    obj = json.loads(path.read_text())
    validate_common(path, obj)

    ok, msg = validate_event_semantics(path, obj)
    if not ok:
        fail(path, msg)

for path in invalid_files:
    obj = json.loads(path.read_text())
    validate_common(path, obj)

    ok, msg = validate_event_semantics(path, obj)
    if ok:
        fail(path, "invalid event was not rejected")

print("PASS AUNEYA Event Schema v0.1 conformance")
PY
