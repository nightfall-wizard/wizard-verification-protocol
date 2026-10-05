#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP v0.4 FRC-007 FIXTURE CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

FIXTURE_DIR="fixtures/release-check/FRC-007-public-key-name-contains-signing"
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

echo "=== VERIFY FRC-007 SEMANTICS ==="
python3 - "$INPUT_JSON" "$EXPECTED_JSON" "$INDEX" <<'PY'
import json
import sys
from pathlib import Path

input_data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
expected = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
index = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))

if input_data.get("fixture_id") != "FRC-007":
    raise SystemExit("FAIL: input fixture_id mismatch.")

if expected.get("fixture_id") != "FRC-007":
    raise SystemExit("FAIL: expected fixture_id mismatch.")

assets = input_data["release"]["assets"]
names = [asset["name"] for asset in assets]

required_names = [
    "wvp-release-check-vfixture-termux-android-aarch64",
    "wvp-release-check-vfixture-termux-android-aarch64.sha256",
    "wvp-release-signing-public-rsa3072.pem",
]

for name in required_names:
    if name not in names:
        raise SystemExit(f"FAIL: missing fixture asset: {name}")

signature_suffixes = tuple(expected["signature_suffix_policy"]["allowed_signature_suffixes"])
signature_like = [name for name in names if name.endswith(signature_suffixes)]

if signature_like:
    raise SystemExit(f"FAIL: fixture unexpectedly contains signature-like assets: {signature_like}")

if "signing" not in "wvp-release-signing-public-rsa3072.pem":
    raise SystemExit("FAIL: public key test name no longer contains signing.")

classification = expected["expected_classification"]

checks = {
    "binary_asset_count": 1,
    "checksum_asset_count": 1,
    "signature_asset_count": 0,
    "public_verification_key_asset_count": 1,
}

for key, value in checks.items():
    if classification.get(key) != value:
        raise SystemExit(f"FAIL: expected {key}={value}, got {classification.get(key)}")

if classification.get("public_key_must_not_count_as_signature") is not True:
    raise SystemExit("FAIL: public_key_must_not_count_as_signature not true.")

fixture_rows = index.get("fixtures", [])
frc007 = [row for row in fixture_rows if row.get("id") == "FRC-007"]

if len(frc007) != 1:
    raise SystemExit("FAIL: FRC-007 must appear exactly once in index.")

row = frc007[0]
if row.get("status") != "implemented":
    raise SystemExit("FAIL: FRC-007 index status must be implemented.")

if row.get("path") != "fixtures/release-check/FRC-007-public-key-name-contains-signing":
    raise SystemExit("FAIL: FRC-007 index path mismatch.")

print("FRC-007 semantics OK.")
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
grep -q "must not be counted as a detached signature asset" "$README"
grep -q "signature asset count: 0" "$README"
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
echo "=== WVP v0.4 FRC-007 FIXTURE CONFORMANCE RESULT ==="
echo "RESULT: PASS"
echo "FRC-007 fixture is implemented."
echo "Public key name containing signing is not a signature fixture."
echo "No audit/legal/binary/reproducible/source-to-release claim is made."
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
