#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP v0.4 FIXTURE RUNNER SEMANTIC COVERAGE CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

RUNNER="conformance/wvp-v040-release-check-fixture-runner-skeleton.sh"
INDEX="fixtures/release-check/FIXTURE-INDEX.json"
SELF="${BASH_SOURCE[0]}"

echo "=== VERIFY RUNNER EXISTS ==="
test -s "$RUNNER"
test -x "$RUNNER"
bash -n "$RUNNER"
echo "Runner exists and syntax is OK."

echo "=== RUN RUNNER JSON ==="
OUT_JSON="$(mktemp)"
"$RUNNER" "$INDEX" --json-only > "$OUT_JSON"
python3 -m json.tool "$OUT_JSON" >/dev/null
echo "Runner JSON is valid."

echo "=== VERIFY ZERO UNCHECKED EXPECTED KEYS ==="
python3 - "$OUT_JSON" "$INDEX" <<'PY'
import json
import sys
from pathlib import Path

out = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
index = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))

if out.get("status") != "PASS":
    raise SystemExit("FAIL: runner status not PASS")

if out.get("runner_stage") != "semantic_classification_layer":
    raise SystemExit("FAIL: runner is not semantic classification layer")

required = {"FRC-003", "FRC-004", "FRC-005", "FRC-006", "FRC-007"}
results = {row.get("id"): row for row in out.get("fixture_results", [])}

missing = sorted(required - set(results))
if missing:
    raise SystemExit("FAIL: missing fixture results: " + ", ".join(missing))

problems = []

for fixture_id in sorted(required):
    result = results[fixture_id]
    unchecked = result.get("unchecked_expected_keys", [])
    checked = result.get("checked_expected_keys", [])

    if unchecked:
        problems.append(f"{fixture_id} unchecked keys: {unchecked}")

    if not checked:
        problems.append(f"{fixture_id} has no checked expected keys")

    base = None
    for row in index.get("fixtures", []):
        if row.get("id") == fixture_id:
            base = Path(row.get("path", ""))
            break

    if base is None:
        problems.append(f"{fixture_id} missing from index")
        continue

    expected = json.loads((base / "expected.json").read_text(encoding="utf-8"))
    expected_keys = set(expected.get("expected_classification", {}).keys())
    checked_keys = set(checked)

    missing_checked = sorted(expected_keys - checked_keys - set(unchecked))
    if missing_checked:
        problems.append(f"{fixture_id} expected keys neither checked nor unchecked: {missing_checked}")

    if expected_keys and expected_keys != checked_keys:
        problems.append(
            f"{fixture_id} expected keys not fully checked. expected={sorted(expected_keys)} checked={sorted(checked_keys)} unchecked={sorted(unchecked)}"
        )

if out.get("semantic_unchecked_keys_total") != 0:
    problems.append("semantic_unchecked_keys_total is not zero: " + str(out.get("semantic_unchecked_keys_total")))

claims = out.get("claims", {})
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
        problems.append("claim must be false: " + key)

for key in ["network_required", "authentication_required", "release_mutation"]:
    if out.get(key) is not False:
        problems.append(key + " must be false")

if problems:
    for item in problems:
        print("FAIL:", item)
    raise SystemExit(1)

print("Semantic expected-key coverage OK.")
print("Checked fixtures:", ",".join(sorted(required)))
PY

echo "=== RUN NEGATIVE COVERAGE TEST ==="
REPO_ROOT="$(pwd)"
TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR" "$OUT_JSON"' EXIT

cp -R fixtures "$TMPDIR/fixtures"

python3 - "$TMPDIR/fixtures/release-check/FRC-003-signature-no-public-key/expected.json" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
data.setdefault("expected_classification", {})["intentionally_unknown_semantic_key_for_negative_test"] = True
path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY

set +e
(
  cd "$TMPDIR"
  "$REPO_ROOT/$RUNNER" "fixtures/release-check/FIXTURE-INDEX.json" --json-only > "$TMPDIR/out.json" 2>/dev/null
  python3 - "$TMPDIR/out.json" <<'PY'
import json
import sys
from pathlib import Path

data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
total = data.get("semantic_unchecked_keys_total")
raise SystemExit(0 if isinstance(total, int) and total > 0 else 1)
PY
)
NEG_RESULT=$?
set -e

echo "NEG_RESULT=$NEG_RESULT"

if [ "$NEG_RESULT" -ne 0 ]; then
  echo "FAIL: negative unknown-key coverage test did not expose unchecked key."
  exit 1
fi

echo "Negative coverage test OK."

echo "=== VERIFY NO SECRET-LIKE MATERIAL ==="
PRIVATE_RE='BEGIN (PGP |OPENSSH |RSA |EC |DSA )?PR''IVATE KEY|AGE-SE''CRET-KEY-|ghp_[A-Za-z0-9_]{20,}'
if grep -nE "$PRIVATE_RE" "$RUNNER" "$INDEX" "$SELF"; then
  echo "FAIL: secret-like material found."
  exit 1
fi
echo "No secret-like material found."

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo
echo "=== WVP v0.4 FIXTURE RUNNER SEMANTIC COVERAGE CONFORMANCE RESULT ==="
echo "RESULT: PASS"
echo "All expected_classification keys for FRC-003 through FRC-007 are semantically checked."
echo "No unchecked expected keys remain for implemented required fixtures."
echo "Negative unknown-key coverage test exposes unchecked semantic gaps."
echo "Offline/read-only boundary is preserved."
echo "No audit/legal/binary/reproducible/source-to-release claim is made."
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
