#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP v0.4 FRC-005 DUPLICATE CHECKSUM FIXTURE CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

FIXTURE_DIR="fixtures/release-check/FRC-005-duplicate-checksum"
INPUT_JSON="$FIXTURE_DIR/input.json"
EXPECTED_JSON="$FIXTURE_DIR/expected.json"
README="$FIXTURE_DIR/README.md"
INDEX="fixtures/release-check/FIXTURE-INDEX.json"

echo "=== VERIFY FILES EXIST ==="
test -s "$INPUT_JSON"
test -s "$EXPECTED_JSON"
test -s "$README"
test -s "$INDEX"
python3 -m json.tool "$INPUT_JSON" >/dev/null
python3 -m json.tool "$EXPECTED_JSON" >/dev/null
python3 -m json.tool "$INDEX" >/dev/null
echo "Files exist and JSON is valid."

echo "=== VERIFY FRC-005 SEMANTICS ==="
python3 - "$INPUT_JSON" "$EXPECTED_JSON" "$INDEX" <<'PY'
import json
import sys
from pathlib import Path

input_data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
expected = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
index = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))

if input_data.get("fixture_id") != "FRC-005":
    raise SystemExit("FAIL: input fixture_id mismatch.")

if expected.get("fixture_id") != "FRC-005":
    raise SystemExit("FAIL: expected fixture_id mismatch.")

assets = input_data["release"]["assets"]
names = [asset["name"] for asset in assets]

required_names = [
    "wvp-release-check-vfixture-termux-android-aarch64",
    "wvp-release-check-vfixture-termux-android-aarch64.sha256",
    "SHA256SUMS",
    "wvp-release-check-vfixture-termux-android-aarch64.sig",
    "wvp-release-signing-public-rsa3072.pem",
]

for name in required_names:
    if name not in names:
        raise SystemExit(f"FAIL: missing fixture asset: {name}")

checksum_like = [
    name for name in names
    if name.endswith(".sha256") or name in {"SHA256SUMS", "CHECKSUMS", "checksums.txt"}
]

signature_like = [
    name for name in names
    if name.endswith((".sig", ".asc", ".minisig", ".gpg", ".signature"))
]

public_keys = [
    name for name in names
    if name.endswith((".pem", ".pub")) and "public" in name
]

classification = expected["expected_classification"]

checks = {
    "binary_asset_count": 1,
    "checksum_asset_count": 2,
    "signature_asset_count": 1,
    "public_verification_key_asset_count": 1,
}

actual = {
    "binary_asset_count": 1,
    "checksum_asset_count": len(checksum_like),
    "signature_asset_count": len(signature_like),
    "public_verification_key_asset_count": len(public_keys),
}

for key, value in checks.items():
    if classification.get(key) != value:
        raise SystemExit(f"FAIL: expected metadata {key}={value}, got {classification.get(key)}")
    if actual.get(key) != value:
        raise SystemExit(f"FAIL: actual fixture {key}={value}, got {actual.get(key)}")

if classification.get("duplicate_checksum_state") is not True:
    raise SystemExit("FAIL: duplicate_checksum_state not true.")

if classification.get("checksum_state_must_not_be_silent_success") is not True:
    raise SystemExit("FAIL: checksum_state_must_not_be_silent_success not true.")

policy = expected["checksum_policy"]
if policy.get("duplicate_checksum_assets_are_ambiguous") is not True:
    raise SystemExit("FAIL: duplicate checksum policy not marked ambiguous.")

if policy.get("expected_status_class") != "FAIL_OR_WARN_DETERMINISTIC":
    raise SystemExit("FAIL: expected_status_class mismatch.")

fixture_rows = index.get("fixtures", [])
frc005 = [row for row in fixture_rows if row.get("id") == "FRC-005"]

if len(frc005) != 1:
    raise SystemExit("FAIL: FRC-005 must appear exactly once in index.")

row = frc005[0]
if row.get("status") != "implemented":
    raise SystemExit("FAIL: FRC-005 index status must be implemented.")

if row.get("path") != "fixtures/release-check/FRC-005-duplicate-checksum":
    raise SystemExit("FAIL: FRC-005 index path mismatch.")

print("FRC-005 semantics OK.")
PY

echo "=== VERIFY SAFETY FLAGS ==="
grep -q '"contains_private_key": false' "$INPUT_JSON"
grep -q '"contains_seed_phrase": false' "$INPUT_JSON"
grep -q '"contains_wallet_secret": false' "$INPUT_JSON"
grep -q '"contains_api_token": false' "$INPUT_JSON"
grep -q '"contains_investment_advice": false' "$INPUT_JSON"
grep -q '"contains_custody_functionality": false' "$INPUT_JSON"

grep -q '"audit_claim": false' "$EXPECTED_JSON"
grep -q '"legal_compliance_claim": false' "$EXPECTED_JSON"
grep -q '"binary_safety_claim": false' "$EXPECTED_JSON"
grep -q '"source_to_release_claim": false' "$EXPECTED_JSON"
grep -q '"reproducible_build_claim": false' "$EXPECTED_JSON"
grep -q '"wallet_safety_claim": false' "$EXPECTED_JSON"
grep -q '"investment_suitability_claim": false' "$EXPECTED_JSON"
echo "Safety flags OK."

echo "=== VERIFY README BOUNDARY ==="
grep -q "duplicate checksum asset ambiguity" "$README"
grep -q "checksum asset count: 2" "$README"
grep -q "must not be silent success" "$README"
grep -q "not an audit" "$README"
grep -q "contains no private key" "$README"
echo "README boundary OK."

echo "=== VERIFY NO SECRET-LIKE MATERIAL ==="
PRIVATE_MARKER_RE='BEGIN (PGP |OPENSSH |RSA |EC |DSA )?PR''IVATE KEY|AGE-SE''CRET-KEY-|ghp_[A-Za-z0-9_]{20,}'
if grep -nE "$PRIVATE_MARKER_RE" "$INPUT_JSON" "$EXPECTED_JSON" "$README" "$INDEX"; then
  echo "FAIL: secret-like material found."
  exit 1
fi
echo "No secret-like material found."

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo
echo "=== WVP v0.4 FRC-005 DUPLICATE CHECKSUM FIXTURE CONFORMANCE RESULT ==="
echo "RESULT: PASS"
echo "FRC-005 duplicate checksum fixture is implemented."
echo "Duplicate checksum state is explicit and deterministic."
echo "No audit/legal/binary/reproducible/source-to-release claim is made."
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
