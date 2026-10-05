#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP v0.3.0 LOCAL SIGNING EXECUTION GUARD CONFORMANCE ==="

START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

GUARD_SCRIPT="scripts/release/guard-v030-local-signing-execution.sh"
GUARD_DOC="docs/release/WVP-V0.3-LOCAL-SIGNING-EXECUTION-GUARD.md"
SIGN_CHECK="conformance/release-check-v030-detached-signature-procedure.sh"
STAGE_CHECK="conformance/release-check-v030-unsigned-asset-staging.sh"

REPORT="target/wvp-v0.3.0-local-signing-execution-guard/GUARD-REPORT.json"
STAGE_DIR="target/wvp-release-v0.3.0-unsigned"
ASSET_NAME="wvp-release-check-v0.3.0-termux-android-aarch64"
SIGNATURE="$STAGE_DIR/$ASSET_NAME.sig"

echo "=== VERIFY FILES EXIST ==="
test -s "$GUARD_SCRIPT"
test -s "$GUARD_DOC"
test -s "$SIGN_CHECK"
test -s "$STAGE_CHECK"

chmod +x "$GUARD_SCRIPT" "$SIGN_CHECK" "$STAGE_CHECK"
bash -n "$GUARD_SCRIPT"
bash -n "$SIGN_CHECK"
bash -n "$STAGE_CHECK"

echo "Required files exist and shell syntax is valid."
echo

echo "=== RUN GUARD EVALUATION ==="
"$GUARD_SCRIPT" --evaluate
echo

echo "=== VERIFY REPORT EXISTS ==="
test -s "$REPORT"
cat "$REPORT"
echo

echo "=== VERIFY REPORT TERMS ==="
grep -q '"evidence_type": "local-signing-execution-guard"' "$REPORT"
grep -q '"package_version": "0.3.0"' "$REPORT"
grep -q '"planned_tag": "v0.3.0"' "$REPORT"
grep -q '"signing_executed": false' "$REPORT"
grep -q '"signature_created": false' "$REPORT"
grep -q '"tag_created": false' "$REPORT"
grep -q '"github_release_created": false' "$REPORT"
grep -q '"source_to_release_proof": false' "$REPORT"
grep -q '"reproducible_build_claim": false' "$REPORT"
grep -q '"binary_safety_claim": false' "$REPORT"
grep -q '"audit_claim": false' "$REPORT"
echo "Report terms OK."
echo

echo "=== VERIFY DIRTY TREE BLOCKER BEHAVIOR ==="
DIRTY_PROBE=".wvp-local-signing-guard-dirty-probe"
trap 'rm -f "$DIRTY_PROBE"' EXIT

printf 'temporary dirty-tree probe\n' > "$DIRTY_PROBE"

set +e
"$GUARD_SCRIPT" --require-ready > target/wvp-v030-local-signing-guard-dirty-probe.log 2>&1
DIRTY_REQUIRE_RESULT=$?
set -e

rm -f "$DIRTY_PROBE"
trap - EXIT

if [ "$DIRTY_REQUIRE_RESULT" -eq 0 ]; then
  echo "FAIL: require-ready succeeded while source tree was dirty."
  cat target/wvp-v030-local-signing-guard-dirty-probe.log
  exit 1
fi

grep -q "local signing is not approved" target/wvp-v030-local-signing-guard-dirty-probe.log
echo "Dirty-tree refusal OK."
echo

echo "=== VERIFY NO SIGNATURE EXISTS ==="
if [ -e "$SIGNATURE" ]; then
  echo "FAIL: guard created or left a signature."
  exit 1
fi
echo "No signature exists."
echo

echo "=== VERIFY DOC TERMS ==="
grep -q "This guard does not create a signature" "$GUARD_DOC"
grep -q "This guard does not create a tag" "$GUARD_DOC"
grep -q "This guard does not create a GitHub release" "$GUARD_DOC"
grep -q "This guard does not expose private signing material" "$GUARD_DOC"
grep -q "source tree is clean" "$GUARD_DOC"
grep -q "HEAD" "$GUARD_DOC"
grep -q "matches" "$GUARD_DOC"
grep -q "origin/main" "$GUARD_DOC"
grep -q "No v0.3.0 tag is created by this document" "$GUARD_DOC"
grep -q "No GitHub release is created by this document" "$GUARD_DOC"
grep -q "No signature is created by this document" "$GUARD_DOC"
echo "Doc terms OK."
echo

echo "=== VERIFY SCRIPT TERMS ==="
grep -q "approved_for_local_signing" "$GUARD_SCRIPT"
grep -q "source tree is dirty" "$GUARD_SCRIPT"
grep -q "HEAD does not match origin/main" "$GUARD_SCRIPT"
grep -q "detached signature already exists" "$GUARD_SCRIPT"
grep -q "staging manifest source commit does not match HEAD" "$GUARD_SCRIPT"
grep -q "staging manifest was generated from dirty source tree" "$GUARD_SCRIPT"
grep -q "signing_executed" "$GUARD_SCRIPT"
grep -q "signature_created" "$GUARD_SCRIPT"
grep -q "tag_created" "$GUARD_SCRIPT"
grep -q "github_release_created" "$GUARD_SCRIPT"
echo "Script terms OK."
echo

echo "=== VERIFY NO LOCAL v0.3.0 TAG CREATED ==="
if git tag --list | grep -qx "v0.3.0"; then
  echo "FAIL: v0.3.0 tag exists. Guard must not create a tag."
  exit 1
fi
echo "No local v0.3.0 tag found."
echo

echo "=== VERIFY NO FALSE 100 PERCENT CLAIM ==="
if grep -nE '100%|100 percent|fully complete|complete project' "$GUARD_DOC" "$GUARD_SCRIPT" "$REPORT"; then
  echo "FAIL: suspicious 100%/complete claim found."
  exit 1
fi
echo "No false 100% claim found."
echo

echo "=== VERIFY NO SECRET-LIKE MATERIAL IN GUARD FILES ==="
PRIVATE_KEY_PATTERN='BEGIN (PGP |OPENSSH |RSA |EC |DSA )?'
PRIVATE_KEY_PATTERN="${PRIVATE_KEY_PATTERN}PRIVATE KEY"
AGE_SECRET_PATTERN_A='AGE'
AGE_SECRET_PATTERN_B='-SECRET-KEY-'
GITHUB_TOKEN_PATTERN_A='ghp'
GITHUB_TOKEN_PATTERN_B='_[A-Za-z0-9_]{20,}'
SECRET_SCAN_PATTERN="${PRIVATE_KEY_PATTERN}|${AGE_SECRET_PATTERN_A}${AGE_SECRET_PATTERN_B}|${GITHUB_TOKEN_PATTERN_A}${GITHUB_TOKEN_PATTERN_B}"

BAD=0
for f in "$GUARD_SCRIPT" "$GUARD_DOC"; do
  if grep -nE "$SECRET_SCAN_PATTERN" "$f"; then
    BAD=1
  fi
done

if [ "$BAD" -ne 0 ]; then
  echo "FAIL: secret-like material detected."
  exit 1
fi
echo "No secret-like material detected."
echo

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "=== WVP v0.3.0 LOCAL SIGNING EXECUTION GUARD CONFORMANCE RESULT ==="
echo "RESULT: PASS"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
