#!/usr/bin/env bash
set -euo pipefail

echo "=== AUNEYA Claim Schema v0.1 Conformance ==="

python3 - <<'PY'
import json
import sys
from pathlib import Path

schema_path = Path("schemas/auneya-claim-v0.1.schema.json")
fixture_dir = Path("fixtures/auneya/claims")

schema = json.loads(schema_path.read_text())

required = set(schema["required"])
claim_types = set(schema["properties"]["claim_type"]["enum"])
target_kinds = set(schema["properties"]["target"]["properties"]["kind"]["enum"])
evidence_values = set(schema["properties"]["evidence_requirements"]["items"]["enum"])
status_values = set(schema["properties"]["status"]["enum"])
access_types = set(schema["properties"]["public_access"]["properties"]["access_type"]["enum"])
lawful_basis_values = set(schema["properties"]["public_access"]["properties"]["lawful_basis"]["enum"])

def fail(path, msg):
    print(f"FAIL {path}: {msg}")
    sys.exit(1)

def validate_common(path, obj):
    missing = sorted(required - set(obj.keys()))
    if missing:
        fail(path, f"missing required fields: {missing}")

    if obj["schema_version"] != "auneya-claim-v0.1":
        fail(path, "wrong schema_version")

    if not obj["claim_id"].startswith("auneya_claim_"):
        fail(path, "claim_id must start with auneya_claim_")

    if obj["claim_type"] not in claim_types:
        fail(path, f"invalid claim_type: {obj['claim_type']}")

    if obj["target"]["kind"] not in target_kinds:
        fail(path, f"invalid target kind: {obj['target']['kind']}")

    if obj["public_access"]["access_type"] not in access_types:
        fail(path, "invalid access_type")

    if obj["public_access"]["lawful_basis"] not in lawful_basis_values:
        fail(path, "invalid lawful_basis")

    for evidence in obj["evidence_requirements"]:
        if evidence not in evidence_values:
            fail(path, f"invalid evidence requirement: {evidence}")

    if obj["status"] not in status_values:
        fail(path, f"invalid status: {obj['status']}")

    if obj["expiry_policy"]["max_age_seconds"] < 60:
        fail(path, "expiry max_age_seconds too small")

    if obj["expiry_policy"]["max_age_seconds"] > 2592000:
        fail(path, "expiry max_age_seconds too large")

    lb = obj["legal_boundary"]
    for key in [
        "private_data_prohibited",
        "hacked_data_prohibited",
        "paywall_bypass_prohibited",
        "credential_use_prohibited",
        "surveillance_prohibited",
    ]:
        if lb.get(key) is not True:
            fail(path, f"legal boundary must set {key}=true")

def is_lawful_public_claim(obj):
    pa = obj["public_access"]

    if pa["requires_authentication"] is True:
        return False

    if pa["requires_payment"] is True:
        return False

    if pa["contains_personal_data"] is True:
        return False

    if pa["lawful_basis"] not in {"publicly_accessible", "owner_authorized", "publisher_provided"}:
        return False

    return True

valid_files = [
    fixture_dir / "valid-release-reality.json",
    fixture_dir / "valid-download-integrity.json",
    fixture_dir / "valid-website-claim-reality.json",
]

invalid_files = [
    fixture_dir / "invalid-private-data-claim.json",
]

for path in valid_files:
    obj = json.loads(path.read_text())
    validate_common(path, obj)
    if not is_lawful_public_claim(obj):
        fail(path, "valid fixture was rejected by lawful-public boundary")

for path in invalid_files:
    obj = json.loads(path.read_text())
    validate_common(path, obj)
    if is_lawful_public_claim(obj):
        fail(path, "invalid fixture was not rejected")

print("PASS AUNEYA Claim Schema v0.1 conformance")
PY
