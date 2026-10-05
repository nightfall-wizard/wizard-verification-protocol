#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP v0.4 FIXTURE INDEX VALIDATOR CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

VALIDATOR="conformance/wvp-v040-release-check-fixture-index-validator.sh"
INDEX="fixtures/release-check/FIXTURE-INDEX.json"

echo "=== VERIFY VALIDATOR EXISTS ==="
test -s "$VALIDATOR"
test -x "$VALIDATOR"
bash -n "$VALIDATOR"
echo "Validator exists and syntax is OK."

echo "=== RUN VALIDATOR ON REAL INDEX ==="
"$VALIDATOR" "$INDEX"
echo "Real index validation OK."

echo "=== RUN NEGATIVE TESTS ==="
TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

cp "$INDEX" "$TMPDIR/good.json"

python3 - "$TMPDIR" <<'PY2'
import json
import sys
from pathlib import Path

tmp = Path(sys.argv[1])
good = json.loads((tmp / "good.json").read_text(encoding="utf-8"))

bad_missing = json.loads(json.dumps(good))
bad_missing["fixtures"] = [
    row for row in bad_missing["fixtures"]
    if row.get("id") != "FRC-003"
]
(tmp / "missing-required.json").write_text(
    json.dumps(bad_missing, indent=2) + "\n",
    encoding="utf-8",
)

bad_duplicate = json.loads(json.dumps(good))
bad_duplicate["fixtures"].append(dict(bad_duplicate["fixtures"][0]))
(tmp / "duplicate-id.json").write_text(
    json.dumps(bad_duplicate, indent=2) + "\n",
    encoding="utf-8",
)

bad_path = json.loads(json.dumps(good))
for row in bad_path["fixtures"]:
    if row.get("id") == "FRC-004":
        row["path"] = "../unsafe"
        break
(tmp / "unsafe-path.json").write_text(
    json.dumps(bad_path, indent=2) + "\n",
    encoding="utf-8",
)
PY2

set +e
"$VALIDATOR" "$TMPDIR/missing-required.json" >/dev/null 2>&1
NEG_MISSING_RESULT=$?

"$VALIDATOR" "$TMPDIR/duplicate-id.json" >/dev/null 2>&1
NEG_DUPLICATE_RESULT=$?

"$VALIDATOR" "$TMPDIR/unsafe-path.json" >/dev/null 2>&1
NEG_PATH_RESULT=$?
set -e

echo "NEG_MISSING_RESULT=$NEG_MISSING_RESULT"
echo "NEG_DUPLICATE_RESULT=$NEG_DUPLICATE_RESULT"
echo "NEG_PATH_RESULT=$NEG_PATH_RESULT"

if [ "$NEG_MISSING_RESULT" -eq 0 ]; then
  echo "FAIL: missing-required negative test unexpectedly passed."
  exit 1
fi

if [ "$NEG_DUPLICATE_RESULT" -eq 0 ]; then
  echo "FAIL: duplicate-id negative test unexpectedly passed."
  exit 1
fi

if [ "$NEG_PATH_RESULT" -eq 0 ]; then
  echo "FAIL: unsafe-path negative test unexpectedly passed."
  exit 1
fi

echo "Negative tests OK."

echo "=== VERIFY NO SECRET-LIKE MATERIAL ==="
PRIVATE_RE='BEGIN (PGP |OPENSSH |RSA |EC |DSA )?PR''IVATE KEY|AGE-SE''CRET-KEY-|ghp_[A-Za-z0-9_]{20,}'
if grep -nE "$PRIVATE_RE" "$VALIDATOR" "$INDEX"; then
  echo "FAIL: secret-like material found."
  exit 1
fi
echo "No secret-like material found."

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo
echo "=== WVP v0.4 FIXTURE INDEX VALIDATOR CONFORMANCE RESULT ==="
echo "RESULT: PASS"
echo "Fixture index validator exists."
echo "Real index validates."
echo "Negative tests reject malformed index states."
echo "No audit/legal/binary/reproducible/source-to-release claim is made."
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
