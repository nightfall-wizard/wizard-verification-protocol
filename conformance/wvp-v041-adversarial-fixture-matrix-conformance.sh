#!/usr/bin/env bash
set -Eeuo pipefail

echo "=== WVP v0.4.1 ADVERSARIAL FIXTURE MATRIX CONFORMANCE ==="

INDEX="${1:-fixtures/release-check/FIXTURE-INDEX.json}"

python3 - "$INDEX" <<'PY'
import json
import re
import sys
from pathlib import Path

index_path = Path(sys.argv[1])

REQUIRED_FALSE_NON_CLAIMS = {
    "audit_claim",
    "legal_compliance_claim",
    "binary_safety_claim",
    "source_to_release_claim",
    "reproducible_build_claim",
    "wallet_safety_claim",
    "investment_suitability_claim",
}

EXPECTED_IMPLEMENTED = {
    "FRC-003",
    "FRC-004",
    "FRC-005",
    "FRC-006",
    "FRC-007",
}

EXPECTED_NEGATIVE_FLAGS = {
    "FRC-003": {
        "signature_without_public_key_state": True,
        "signature_verification_must_not_be_claimed": True,
        "missing_public_key_state_must_not_be_silent_success": True,
    },
    "FRC-004": {
        "public_key_without_signature_state": True,
        "public_key_must_not_count_as_signature": True,
        "signature_verification_must_not_be_claimed": True,
        "missing_signature_state_must_not_be_silent_success": True,
    },
    "FRC-005": {
        "duplicate_checksum_state": True,
        "checksum_state_must_not_be_silent_success": True,
    },
    "FRC-006": {
        "duplicate_signature_state": True,
        "signature_state_must_not_be_silent_success": True,
        "public_key_must_not_count_as_signature": True,
    },
    "FRC-007": {
        "public_key_name_contains_signing": True,
        "public_key_must_not_count_as_signature": True,
    },
}

SECRET_REGEXES = [
    (r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", "private-key-block"),
    (r"ghp_[A-Za-z0-9]{20,}", "github-classic-token"),
    (r"github_pat_[A-Za-z0-9_]{20,}", "github-fine-grained-token"),
    (r"glpat-[A-Za-z0-9_-]{20,}", "gitlab-token"),
]

SIGNATURE_SUFFIXES = (".sig", ".asc", ".minisig", ".gpg", ".signature")
CHECKSUM_SUFFIXES = (".sha256",)
PUBLIC_KEY_SUFFIXES = (".pem", ".pub")

def fail(msg):
    print("RESULT: FAIL")
    print(msg)
    raise SystemExit(1)

def load_json(path):
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        fail(f"could not parse JSON {path}: {exc}")

def role(asset):
    return str(asset.get("role_hint", "")).lower()

def name(asset):
    return str(asset.get("name", ""))

def is_checksum(asset):
    n = name(asset).lower()
    r = role(asset)
    return (
        r == "checksum"
        or n.endswith(CHECKSUM_SUFFIXES)
        or n in {"sha256sums", "checksums", "checksums.txt"}
        or "checksum" in n
    )

def is_signature(asset):
    n = name(asset).lower()
    r = role(asset)
    return (
        r == "signature"
        or n.endswith(SIGNATURE_SUFFIXES)
    )

def is_public_key(asset):
    n = name(asset).lower()
    r = role(asset)
    return (
        r in {"public_key", "public_verification_key"}
        or (
            n.endswith(PUBLIC_KEY_SUFFIXES)
            and (
                "public" in n
                or "verify" in n
                or "verification" in n
                or "signing" in n
            )
        )
    )

def classify(input_data):
    assets = input_data.get("release", {}).get("assets", [])
    if not isinstance(assets, list):
        fail("release.assets must be a list")

    for asset in assets:
        if not isinstance(asset, dict):
            fail("every release asset must be an object")

    checksum_assets = [a for a in assets if is_checksum(a)]
    signature_assets = [a for a in assets if is_signature(a)]
    public_key_assets = [a for a in assets if is_public_key(a)]

    classified_ids = {id(a) for a in checksum_assets + signature_assets + public_key_assets}

    binary_assets = []
    for asset in assets:
        n = name(asset).lower()
        if role(asset) == "binary":
            binary_assets.append(asset)
            continue
        if id(asset) in classified_ids:
            continue
        if not (
            n.endswith(CHECKSUM_SUFFIXES)
            or n.endswith(SIGNATURE_SUFFIXES)
            or n.endswith(PUBLIC_KEY_SUFFIXES)
        ):
            binary_assets.append(asset)

    public_key_names = [name(a).lower() for a in public_key_assets]

    return {
        "binary_asset_count": len(binary_assets),
        "checksum_asset_count": len(checksum_assets),
        "signature_asset_count": len(signature_assets),
        "public_verification_key_asset_count": len(public_key_assets),
        "signature_without_public_key_state": len(signature_assets) > 0 and len(public_key_assets) == 0,
        "public_key_without_signature_state": len(public_key_assets) > 0 and len(signature_assets) == 0,
        "duplicate_checksum_state": len(checksum_assets) > 1,
        "duplicate_signature_state": len(signature_assets) > 1,
        "public_key_name_contains_signing": any("signing" in n for n in public_key_names),
        "public_key_must_not_count_as_signature": True,
        "signature_verification_must_not_be_claimed": not (len(signature_assets) > 0 and len(public_key_assets) > 0),
        "missing_public_key_state_must_not_be_silent_success": len(signature_assets) > 0 and len(public_key_assets) == 0,
        "missing_signature_state_must_not_be_silent_success": len(public_key_assets) > 0 and len(signature_assets) == 0,
        "checksum_state_must_not_be_silent_success": len(checksum_assets) > 1,
        "signature_state_must_not_be_silent_success": len(signature_assets) > 1,
    }

def scan_for_secrets(path):
    text = path.read_text(errors="replace")
    hits = [label for pattern, label in SECRET_REGEXES if re.search(pattern, text, re.IGNORECASE)]
    if hits:
        fail(f"high-signal secret material found in fixture file {path}: {hits}")

def assert_false_non_claims(fixture_id, expected):
    non_claims = expected.get("non_claims")
    if not isinstance(non_claims, dict):
        fail(f"{fixture_id}: expected.json missing non_claims object")

    for key in REQUIRED_FALSE_NON_CLAIMS:
        if non_claims.get(key) is not False:
            fail(f"{fixture_id}: non_claim {key} must be explicitly false")

def assert_boundary(fixture_id, expected):
    boundary = expected.get("expected_status_boundary")
    if not isinstance(boundary, dict):
        fail(f"{fixture_id}: expected.json missing expected_status_boundary object")

    required = {
        "fixture_is_deterministic": True,
        "live_github_required": False,
        "network_required": False,
        "authentication_required": False,
    }

    for key, value in required.items():
        if boundary.get(key) is not value:
            fail(f"{fixture_id}: expected_status_boundary.{key} must be {value}")

def main():
    if not index_path.exists():
        fail(f"fixture index missing: {index_path}")

    index = load_json(index_path)
    fixtures = index.get("fixtures", [])
    if not isinstance(fixtures, list):
        fail("FIXTURE-INDEX.json fixtures must be a list")

    implemented = {
        f.get("id"): f
        for f in fixtures
        if f.get("status") == "implemented"
    }

    missing = sorted(EXPECTED_IMPLEMENTED - set(implemented))
    if missing:
        fail(f"missing implemented adversarial fixtures: {missing}")

    for fixture_id in sorted(EXPECTED_IMPLEMENTED):
        item = implemented[fixture_id]
        fixture_path = Path(item.get("path", ""))

        if not fixture_path.is_dir():
            fail(f"{fixture_id}: fixture path missing: {fixture_path}")

        input_path = fixture_path / "input.json"
        expected_path = fixture_path / "expected.json"
        readme_path = fixture_path / "README.md"

        for path in [input_path, expected_path, readme_path]:
            if not path.exists():
                fail(f"{fixture_id}: required fixture file missing: {path}")
            scan_for_secrets(path)

        input_data = load_json(input_path)
        expected = load_json(expected_path)

        if input_data.get("fixture_id") != fixture_id:
            fail(f"{fixture_id}: input.json fixture_id mismatch")

        if expected.get("fixture_id") != fixture_id:
            fail(f"{fixture_id}: expected.json fixture_id mismatch")

        actual = classify(input_data)
        expected_classification = expected.get("expected_classification", {})

        if not isinstance(expected_classification, dict):
            fail(f"{fixture_id}: expected_classification must be object")

        for key, value in expected_classification.items():
            if key not in actual:
                fail(f"{fixture_id}: unknown expected_classification key: {key}")
            if actual[key] != value:
                fail(
                    f"{fixture_id}: classification mismatch for {key}: "
                    f"expected {value!r}, actual {actual[key]!r}"
                )

        for key, value in EXPECTED_NEGATIVE_FLAGS[fixture_id].items():
            if expected_classification.get(key) is not value:
                fail(f"{fixture_id}: missing required adversarial flag {key}={value}")

        assert_false_non_claims(fixture_id, expected)
        assert_boundary(fixture_id, expected)

    index_non_claims = index.get("non_claims", {})
    if not isinstance(index_non_claims, dict):
        fail("FIXTURE-INDEX.json non_claims must be object")

    for key in REQUIRED_FALSE_NON_CLAIMS:
        if index_non_claims.get(key) is not False:
            fail(f"FIXTURE-INDEX.json non_claim {key} must be explicitly false")

    safety = index.get("safety", {})
    for key in [
        "api_tokens_allowed",
        "custody_data_allowed",
        "investment_advice_allowed",
        "private_keys_allowed",
        "seed_phrases_allowed",
        "wallet_secrets_allowed",
    ]:
        if safety.get(key) is not False:
            fail(f"FIXTURE-INDEX.json safety.{key} must be explicitly false")

    print(json.dumps({
        "wvp_module": "wvp-release-check",
        "suite": "adversarial-fixture-matrix-v0.4.1",
        "status": "PASS",
        "implemented_fixtures_checked": sorted(EXPECTED_IMPLEMENTED),
        "network_required": False,
        "authentication_required": False,
        "release_mutation": False,
        "private_key_required": False,
        "silent_success_guard": "enforced"
    }, sort_keys=True))

    print("RESULT: PASS")

if __name__ == "__main__":
    main()
PY
