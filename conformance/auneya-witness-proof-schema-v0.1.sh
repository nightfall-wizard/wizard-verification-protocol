#!/usr/bin/env bash
set -euo pipefail

echo "=== AUNEYA Witness Proof Schema v0.1 Conformance ==="

python3 - <<'PY'
import json
import sys
from pathlib import Path

proof_schema_path = Path("schemas/auneya-witness-proof-v0.1.schema.json")
claim_fixture_dir = Path("fixtures/auneya/claims")
proof_fixture_dir = Path("fixtures/auneya/witness-proofs")

schema = json.loads(proof_schema_path.read_text())

required = set(schema["required"])
proof_types = set(schema["properties"]["proof_type"]["enum"])
observed_status_values = set(schema["properties"]["observed_status"]["enum"])
evidence_values = set(schema["properties"]["evidence"]["items"]["properties"]["evidence_type"]["enum"])
device_classes = set(schema["properties"]["witness"]["properties"]["device_class"]["enum"])
environment_classes = set(schema["properties"]["witness"]["properties"]["environment_class"]["enum"])
software_names = set(schema["properties"]["witness"]["properties"]["software_name"]["enum"])
signature_statuses = set(schema["properties"]["integrity"]["properties"]["signature_status"]["enum"])

def fail(path, msg):
    print(f"FAIL {path}: {msg}")
    sys.exit(1)

def load_claims():
    claims = {}
    for path in claim_fixture_dir.glob("*.json"):
        obj = json.loads(path.read_text())
        claims[obj["claim_id"]] = obj
    return claims

def lawful_claim(obj):
    pa = obj["public_access"]
    if pa["requires_authentication"] is True:
        return False
    if pa["requires_payment"] is True:
        return False
    if pa["contains_personal_data"] is True:
        return False
    return pa["lawful_basis"] in {"publicly_accessible", "owner_authorized", "publisher_provided"}

def lawful_proof(obj):
    lb = obj["lawful_boundary_confirmation"]
    required_true = [
        "public_or_authorized_target",
        "no_private_data_accessed",
        "no_hacked_data_used",
        "no_paywall_bypass_used",
        "no_credentials_used",
        "no_surveillance_performed",
    ]
    return all(lb.get(k) is True for k in required_true)

def validate_common(path, obj):
    missing = sorted(required - set(obj.keys()))
    if missing:
        fail(path, f"missing required fields: {missing}")

    if obj["schema_version"] != "auneya-witness-proof-v0.1":
        fail(path, "wrong schema_version")

    if not obj["proof_id"].startswith("auneya_proof_"):
        fail(path, "proof_id must start with auneya_proof_")

    if obj["proof_type"] not in proof_types:
        fail(path, f"invalid proof_type: {obj['proof_type']}")

    if not obj["claim_id"].startswith("auneya_claim_"):
        fail(path, "claim_id must start with auneya_claim_")

    if obj["claim_schema_version"] != "auneya-claim-v0.1":
        fail(path, "wrong claim_schema_version")

    if not obj["claim_hash"].startswith("sha256:") or len(obj["claim_hash"]) != 71:
        fail(path, "invalid claim_hash")

    witness = obj["witness"]

    if not witness["witness_id"].startswith("witness_"):
        fail(path, "witness_id must start with witness_")

    if witness["device_class"] not in device_classes:
        fail(path, "invalid device_class")

    if witness["environment_class"] not in environment_classes:
        fail(path, "invalid environment_class")

    if witness["software_name"] not in software_names:
        fail(path, "invalid software_name")

    if obj["observed_status"] not in observed_status_values:
        fail(path, "invalid observed_status")

    if not obj["evidence"]:
        fail(path, "evidence must not be empty")

    for ev in obj["evidence"]:
        if ev["evidence_type"] not in evidence_values:
            fail(path, f"invalid evidence_type: {ev['evidence_type']}")
        if not ev["evidence_hash"].startswith("sha256:") or len(ev["evidence_hash"]) != 71:
            fail(path, "invalid evidence_hash")

    if obj["integrity"]["signature_status"] not in signature_statuses:
        fail(path, "invalid signature_status")

    if not obj["integrity"]["proof_hash"].startswith("sha256:") or len(obj["integrity"]["proof_hash"]) != 71:
        fail(path, "invalid proof_hash")

    timing = obj["timing"]
    if "duration_ms" in timing and timing["duration_ms"] < 0:
        fail(path, "duration_ms must be non-negative")

claims = load_claims()

valid_files = [
    proof_fixture_dir / "valid-release-reality-prooflet.json",
    proof_fixture_dir / "valid-download-integrity-prooflet.json",
]

invalid_files = [
    proof_fixture_dir / "invalid-private-data-proof.json",
]

for path in valid_files:
    obj = json.loads(path.read_text())
    validate_common(path, obj)

    claim = claims.get(obj["claim_id"])
    if not claim:
        fail(path, f"referenced claim not found: {obj['claim_id']}")

    if not lawful_claim(claim):
        fail(path, "referenced claim is not lawful-public")

    if not lawful_proof(obj):
        fail(path, "valid proof failed lawful boundary confirmation")

for path in invalid_files:
    obj = json.loads(path.read_text())
    validate_common(path, obj)

    claim = claims.get(obj["claim_id"])
    claim_is_lawful = lawful_claim(claim) if claim else False
    proof_is_lawful = lawful_proof(obj)

    if claim_is_lawful and proof_is_lawful:
        fail(path, "invalid proof was not rejected")

print("PASS AUNEYA Witness Proof Schema v0.1 conformance")
PY
