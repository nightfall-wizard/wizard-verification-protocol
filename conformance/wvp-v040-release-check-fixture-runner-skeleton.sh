#!/usr/bin/env bash
set -euo pipefail

INDEX="${1:-fixtures/release-check/FIXTURE-INDEX.json}"
MODE="${2:-human}"

python3 - "$INDEX" "$MODE" <<'PY2'
import json
import sys
from pathlib import Path

index_path = Path(sys.argv[1])
mode = sys.argv[2]

required = {"FRC-003", "FRC-004", "FRC-005", "FRC-006", "FRC-007"}

CLAIMS_FALSE = {
    "audit_claim": False,
    "legal_compliance_claim": False,
    "binary_safety_claim": False,
    "source_to_release_claim": False,
    "reproducible_build_claim": False,
    "wallet_safety_claim": False,
    "investment_suitability_claim": False,
}

def emit_failure(message: str, code: int = 2, fixture_id: str | None = None):
    payload = {
        "wvp_module": "wvp-release-check",
        "suite": "release-check-fixtures-v0.4",
        "runner_stage": "semantic_classification_layer",
        "status": "FAIL",
        "error": message,
        "fixture_id": fixture_id,
        "exit_code": code,
        "offline": True,
        "network_required": False,
        "authentication_required": False,
        "release_mutation": False,
        "claims": CLAIMS_FALSE,
    }
    if mode == "--json-only":
        print(json.dumps(payload, sort_keys=True))
    else:
        print("RESULT: FAIL")
        print(message)
    raise SystemExit(code)

def role(asset):
    return str(asset.get("role_hint", "")).lower()

def name(asset):
    return str(asset.get("name", ""))

def is_checksum(asset):
    n = name(asset).lower()
    r = role(asset)
    return (
        r == "checksum"
        or n.endswith(".sha256")
        or n in {"sha256sums", "checksums", "checksums.txt"}
        or "checksum" in n
    )

def is_signature(asset):
    n = name(asset).lower()
    r = role(asset)
    return (
        r == "signature"
        or n.endswith(".sig")
        or n.endswith(".asc")
        or n.endswith(".minisig")
        or n.endswith(".gpg")
        or n.endswith(".signature")
    )

def is_public_key(asset):
    n = name(asset).lower()
    r = role(asset)
    return (
        r == "public_verification_key"
        or r == "public_key"
        or (
            (n.endswith(".pem") or n.endswith(".pub"))
            and ("public" in n or "verify" in n or "verification" in n or "signing" in n)
        )
    )

def classify_assets(input_data):
    assets = input_data.get("release", {}).get("assets", [])
    if not isinstance(assets, list):
        emit_failure("release.assets must be list")

    checksum_assets = [a for a in assets if isinstance(a, dict) and is_checksum(a)]
    signature_assets = [a for a in assets if isinstance(a, dict) and is_signature(a)]
    public_key_assets = [a for a in assets if isinstance(a, dict) and is_public_key(a)]

    classified_ids = set()
    for asset in checksum_assets + signature_assets + public_key_assets:
        classified_ids.add(id(asset))

    binary_assets = []
    for asset in assets:
        if not isinstance(asset, dict):
            emit_failure("asset row must be object")
        if role(asset) == "binary":
            binary_assets.append(asset)
        elif id(asset) not in classified_ids:
            n = name(asset).lower()
            if not (
                n.endswith(".sha256")
                or n.endswith(".sig")
                or n.endswith(".asc")
                or n.endswith(".minisig")
                or n.endswith(".gpg")
                or n.endswith(".signature")
                or n.endswith(".pem")
                or n.endswith(".pub")
            ):
                binary_assets.append(asset)

    public_key_names = [name(a).lower() for a in public_key_assets]

    actual = {
        "binary_asset_count": len(binary_assets),
        "checksum_asset_count": len(checksum_assets),
        "signature_asset_count": len(signature_assets),
        "public_verification_key_asset_count": len(public_key_assets),
        "signature_without_public_key_state": len(signature_assets) > 0 and len(public_key_assets) == 0,
        "public_key_without_signature_state": len(public_key_assets) > 0 and len(signature_assets) == 0,
        "duplicate_checksum_state": len(checksum_assets) > 1,
        "duplicate_signature_state": len(signature_assets) > 1,
        "public_key_name_contains_signing_state": any("signing" in n for n in public_key_names),
        "public_key_must_not_count_as_signature": True,
        "signature_verification_must_not_be_claimed": not (len(signature_assets) > 0 and len(public_key_assets) > 0),
        "missing_signature_state_must_not_be_silent_success": len(public_key_assets) > 0 and len(signature_assets) == 0,
    }

    return actual

def derive_expected_key(key, actual):
    if key in actual:
        return True, actual[key]

    k = key.lower()

    if "duplicate_checksum" in k:
        return True, actual["duplicate_checksum_state"]

    if "duplicate_signature" in k:
        return True, actual["duplicate_signature_state"]

    if "signature_without_public_key" in k:
        return True, actual["signature_without_public_key_state"]

    if "public_key_without_signature" in k:
        return True, actual["public_key_without_signature_state"]

    if "public_key" in k and "must_not_count" in k and "signature" in k:
        return True, actual["public_key_must_not_count_as_signature"]

    if "signature_verification" in k and "must_not_be_claimed" in k:
        return True, actual["signature_verification_must_not_be_claimed"]

    if "missing_signature" in k and "silent_success" in k:
        return True, actual["missing_signature_state_must_not_be_silent_success"]

    if "public_key" in k and "signing" in k and "signature" in k:
        return True, actual["public_key_name_contains_signing_state"] and actual["signature_asset_count"] == 0

    if "public_key" in k and "signing" in k:
        return True, actual["public_key_name_contains_signing_state"]

    return False, None

def compare_expected(fixture_id, input_data, expected_data):
    if input_data.get("fixture_id") != fixture_id:
        emit_failure(f"{fixture_id} input fixture_id mismatch", 2, fixture_id)

    if expected_data.get("fixture_id") != fixture_id:
        emit_failure(f"{fixture_id} expected fixture_id mismatch", 2, fixture_id)

    actual = classify_assets(input_data)

    expected_classification = expected_data.get("expected_classification", {})
    if not isinstance(expected_classification, dict):
        emit_failure(f"{fixture_id} expected_classification must be object", 2, fixture_id)

    mismatches = []
    checked = []
    unchecked = []

    for key, expected_value in expected_classification.items():
        known, actual_value = derive_expected_key(key, actual)
        if not known:
            unchecked.append(key)
            continue

        checked.append(key)
        if actual_value != expected_value:
            mismatches.append({
                "key": key,
                "expected": expected_value,
                "actual": actual_value,
            })

    non_claims = expected_data.get("non_claims", {})
    if isinstance(non_claims, dict):
        for key, value in non_claims.items():
            if value is not False:
                mismatches.append({
                    "key": f"non_claims.{key}",
                    "expected": False,
                    "actual": value,
                })

    safety = input_data.get("safety", {})
    if isinstance(safety, dict):
        for key, value in safety.items():
            if value is not False:
                mismatches.append({
                    "key": f"safety.{key}",
                    "expected": False,
                    "actual": value,
                })

    if mismatches:
        return {
            "id": fixture_id,
            "status": "FAIL",
            "runner_stage": "semantic_classification_layer",
            "actual_classification": actual,
            "checked_expected_keys": checked,
            "unchecked_expected_keys": unchecked,
            "mismatches": mismatches,
        }

    return {
        "id": fixture_id,
        "status": "PASS",
        "runner_stage": "semantic_classification_layer",
        "actual_classification": actual,
        "checked_expected_keys": checked,
        "unchecked_expected_keys": unchecked,
        "mismatches": [],
    }

if not index_path.is_file():
    emit_failure("fixture index missing")

try:
    data = json.loads(index_path.read_text(encoding="utf-8"))
except Exception as exc:
    emit_failure(f"fixture index invalid json: {exc}")

fixtures = data.get("fixtures")
if not isinstance(fixtures, list):
    emit_failure("index.fixtures must be list")

seen = set()
implemented_results = []

for row in fixtures:
    if not isinstance(row, dict):
        emit_failure("fixture row must be object")

    fixture_id = row.get("id")
    status = row.get("status")
    path_value = row.get("path")

    if not isinstance(fixture_id, str) or not fixture_id.startswith("FRC-"):
        emit_failure("invalid fixture id")

    if fixture_id in seen:
        emit_failure(f"duplicate fixture id: {fixture_id}")

    seen.add(fixture_id)

    if status not in {"planned", "implemented", "reserved"}:
        emit_failure(f"invalid fixture status: {fixture_id}")

    if status != "implemented":
        continue

    if not isinstance(path_value, str) or not path_value:
        emit_failure(f"implemented fixture missing path: {fixture_id}")

    if path_value.startswith("/") or ".." in path_value:
        emit_failure(f"unsafe fixture path: {fixture_id}")

    if not path_value.startswith("fixtures/release-check/"):
        emit_failure(f"fixture path outside release-check tree: {fixture_id}")

    base = Path(path_value)
    input_path = base / "input.json"
    expected_path = base / "expected.json"
    readme_path = base / "README.md"

    for p in [input_path, expected_path, readme_path]:
        if not p.is_file():
            emit_failure(f"{fixture_id} missing {p.name}")

    try:
        input_data = json.loads(input_path.read_text(encoding="utf-8"))
        expected_data = json.loads(expected_path.read_text(encoding="utf-8"))
    except Exception as exc:
        emit_failure(f"{fixture_id} invalid fixture JSON: {exc}", 2, fixture_id)

    implemented_results.append(compare_expected(fixture_id, input_data, expected_data))

implemented_ids = {item["id"] for item in implemented_results}
missing = sorted(required - implemented_ids)
if missing:
    emit_failure("required implemented fixtures missing: " + ",".join(missing))

failed = [item for item in implemented_results if item["status"] != "PASS"]
unchecked_total = sum(len(item["unchecked_expected_keys"]) for item in implemented_results)

result = {
    "wvp_module": "wvp-release-check",
    "suite": "release-check-fixtures-v0.4",
    "runner_stage": "semantic_classification_layer",
    "semantic_mode": "known_expected_keys_checked",
    "status": "FAIL" if failed else "PASS",
    "fixtures_total": len(fixtures),
    "fixtures_implemented": len(implemented_results),
    "fixtures_passed": len([item for item in implemented_results if item["status"] == "PASS"]),
    "fixtures_warned": 0,
    "fixtures_failed": len(failed),
    "semantic_unchecked_keys_total": unchecked_total,
    "required_implemented": sorted(required),
    "fixture_results": implemented_results,
    "offline": True,
    "network_required": False,
    "authentication_required": False,
    "release_mutation": False,
    "claims": CLAIMS_FALSE,
}

if mode == "--json-only":
    print(json.dumps(result, sort_keys=True))
else:
    print("=== WVP v0.4 RELEASE-CHECK FIXTURE RUNNER SEMANTIC LAYER ===")
    print(f"Index: {index_path}")
    print(f"RESULT: {result['status']}")
    print(f"fixtures_total={result['fixtures_total']}")
    print(f"fixtures_implemented={result['fixtures_implemented']}")
    print(f"fixtures_failed={result['fixtures_failed']}")
    print(f"semantic_unchecked_keys_total={result['semantic_unchecked_keys_total']}")
    print("runner_stage=semantic_classification_layer")
    print(json.dumps(result, indent=2, sort_keys=True))

if failed:
    raise SystemExit(1)
PY2
