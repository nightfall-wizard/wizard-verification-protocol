#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP v0.4 FIXTURE RUNNER SKELETON CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

RUNNER="conformance/wvp-v040-release-check-fixture-runner-skeleton.sh"
INDEX="fixtures/release-check/FIXTURE-INDEX.json"

echo "=== VERIFY RUNNER EXISTS ==="
test -s "$RUNNER"
test -x "$RUNNER"
bash -n "$RUNNER"
echo "Runner exists and syntax is OK."

echo "=== RUN JSON MODE ==="
OUT_JSON="$(mktemp)"
"$RUNNER" "$INDEX" --json-only > "$OUT_JSON"
python3 -m json.tool "$OUT_JSON" >/dev/null
echo "JSON mode output is valid JSON."

echo "=== VERIFY JSON CONTENT ==="
python3 - "$OUT_JSON" <<'PY2'
import json
import sys
from pathlib import Path

data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))

if data.get("wvp_module") != "wvp-release-check":
    raise SystemExit("FAIL: wrong module")

if data.get("suite") != "release-check-fixtures-v0.4":
    raise SystemExit("FAIL: wrong suite")

if data.get("runner_stage") != "skeleton":
    raise SystemExit("FAIL: wrong runner stage")

if data.get("status") != "PASS":
    raise SystemExit("FAIL: status not PASS")

if data.get("network_required") is not False:
    raise SystemExit("FAIL: network_required must be false")

if data.get("authentication_required") is not False:
    raise SystemExit("FAIL: authentication_required must be false")

if data.get("release_mutation") is not False:
    raise SystemExit("FAIL: release_mutation must be false")

required = {"FRC-003", "FRC-004", "FRC-005", "FRC-006", "FRC-007"}
implemented = set(data.get("required_implemented", []))

if required != implemented:
    raise SystemExit("FAIL: required implemented fixture set mismatch")

if data.get("fixtures_failed") != 0:
    raise SystemExit("FAIL: fixtures_failed must be zero")

claims = data.get("claims", {})
for key in [
    "audit_claim",
    "legal_compliance_claim",
    "binary_safety_claim",
    "source_to_release_claim",
    "reproducible_build_claim",
    "wallet_safety_claim",
    "investment_suitability_claim",
]:
    if claims.get(key) is not False:
        raise SystemExit(f"FAIL: claim must be false: {key}")

print("JSON content OK.")
PY2

echo "=== RUN HUMAN MODE ==="
"$RUNNER" "$INDEX" | grep -q "RESULT: PASS"
echo "Human mode OK."

echo "=== RUN NEGATIVE TEST ==="
TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR" "$OUT_JSON"' EXIT
cp "$INDEX" "$TMPDIR/index.json"

python3 - "$TMPDIR/index.json" <<'PY2'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))

for row in data["fixtures"]:
    if row.get("id") == "FRC-004":
        row["path"] = "../unsafe"
        break

path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
PY2

set +e
"$RUNNER" "$TMPDIR/index.json" --json-only >/dev/null 2>&1
NEG_RESULT=$?
set -e

echo "NEG_RESULT=$NEG_RESULT"

if [ "$NEG_RESULT" -eq 0 ]; then
  echo "FAIL: negative unsafe path test unexpectedly passed."
  exit 1
fi

echo "Negative test OK."

echo "=== VERIFY NO SECRET-LIKE MATERIAL ==="
PRIVATE_RE='BEGIN (PGP |OPENSSH |RSA |EC |DSA )?PR''IVATE KEY|AGE-SE''CRET-KEY-|ghp_[A-Za-z0-9_]{20,}'
if grep -nE "$PRIVATE_RE" "$RUNNER" "$INDEX"; then
  echo "FAIL: secret-like material found."
  exit 1
fi
echo "No secret-like material found."

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo
echo "=== WVP v0.4 FIXTURE RUNNER SKELETON CONFORMANCE RESULT ==="
echo "RESULT: PASS"
echo "Fixture runner skeleton exists."
echo "JSON output validates."
echo "Offline/read-only boundary is explicit."
echo "Negative unsafe-path test rejects malformed index state."
echo "No audit/legal/binary/reproducible/source-to-release claim is made."
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
