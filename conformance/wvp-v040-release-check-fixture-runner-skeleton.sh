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

def fail(message: str, code: int = 2):
    if mode == "--json-only":
        print(json.dumps({
            "wvp_module": "wvp-release-check",
            "suite": "release-check-fixtures-v0.4",
            "status": "FAIL",
            "error": message,
            "exit_code": code,
            "claims": {
                "audit_claim": False,
                "legal_compliance_claim": False,
                "binary_safety_claim": False,
                "source_to_release_claim": False,
                "reproducible_build_claim": False,
                "wallet_safety_claim": False,
                "investment_suitability_claim": False
            }
        }, sort_keys=True))
    else:
        print("RESULT: FAIL")
        print(message)
    raise SystemExit(code)

if not index_path.is_file():
    fail("fixture index missing")

try:
    data = json.loads(index_path.read_text(encoding="utf-8"))
except Exception as exc:
    fail(f"fixture index invalid json: {exc}")

fixtures = data.get("fixtures")
if not isinstance(fixtures, list):
    fail("index.fixtures must be list")

seen = set()
implemented = []

for row in fixtures:
    if not isinstance(row, dict):
        fail("fixture row must be object")

    fixture_id = row.get("id")
    status = row.get("status")
    path_value = row.get("path")

    if not isinstance(fixture_id, str) or not fixture_id.startswith("FRC-"):
        fail("invalid fixture id")

    if fixture_id in seen:
        fail(f"duplicate fixture id: {fixture_id}")

    seen.add(fixture_id)

    if status not in {"planned", "implemented", "reserved"}:
        fail(f"invalid fixture status: {fixture_id}")

    if status != "implemented":
        continue

    if not isinstance(path_value, str) or not path_value:
        fail(f"implemented fixture missing path: {fixture_id}")

    if path_value.startswith("/") or ".." in path_value:
        fail(f"unsafe fixture path: {fixture_id}")

    if not path_value.startswith("fixtures/release-check/"):
        fail(f"fixture path outside release-check tree: {fixture_id}")

    base = Path(path_value)
    required_files = {
        "input": base / "input.json",
        "expected": base / "expected.json",
        "readme": base / "README.md",
    }

    for label, path in required_files.items():
        if not path.is_file():
            fail(f"{fixture_id} missing {label}")

    input_data = json.loads(required_files["input"].read_text(encoding="utf-8"))
    expected_data = json.loads(required_files["expected"].read_text(encoding="utf-8"))

    if input_data.get("fixture_id") != fixture_id:
        fail(f"{fixture_id} input fixture_id mismatch")

    if expected_data.get("fixture_id") != fixture_id:
        fail(f"{fixture_id} expected fixture_id mismatch")

    implemented.append({
        "id": fixture_id,
        "path": path_value,
        "status": "PASS",
        "runner_stage": "skeleton_validation_only"
    })

implemented_ids = {item["id"] for item in implemented}
missing = sorted(required - implemented_ids)
if missing:
    fail("required implemented fixtures missing: " + ",".join(missing))

result = {
    "wvp_module": "wvp-release-check",
    "suite": "release-check-fixtures-v0.4",
    "runner_stage": "skeleton",
    "status": "PASS",
    "fixtures_total": len(fixtures),
    "fixtures_implemented": len(implemented),
    "fixtures_passed": len(implemented),
    "fixtures_warned": 0,
    "fixtures_failed": 0,
    "required_implemented": sorted(required),
    "fixture_results": implemented,
    "offline": True,
    "network_required": False,
    "authentication_required": False,
    "release_mutation": False,
    "claims": {
        "audit_claim": False,
        "legal_compliance_claim": False,
        "binary_safety_claim": False,
        "source_to_release_claim": False,
        "reproducible_build_claim": False,
        "wallet_safety_claim": False,
        "investment_suitability_claim": False
    }
}

if mode == "--json-only":
    print(json.dumps(result, sort_keys=True))
else:
    print("=== WVP v0.4 RELEASE-CHECK FIXTURE RUNNER SKELETON ===")
    print(f"Index: {index_path}")
    print("RESULT: PASS")
    print(f"fixtures_total={result['fixtures_total']}")
    print(f"fixtures_implemented={result['fixtures_implemented']}")
    print("runner_stage=skeleton_validation_only")
    print(json.dumps(result, indent=2, sort_keys=True))
PY2
