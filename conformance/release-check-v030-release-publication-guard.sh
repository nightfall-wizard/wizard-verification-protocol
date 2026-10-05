#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP v0.3.0 RELEASE PUBLICATION GUARD CONFORMANCE ==="

START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

PUB_SCRIPT="scripts/release/guard-v030-release-publication.sh"
PUB_DOC="docs/release/WVP-V0.3-RELEASE-PUBLICATION-GUARD.md"
STAGE_CHECK="conformance/release-check-v030-unsigned-asset-staging.sh"

REPORT="target/wvp-v0.3.0-release-publication-guard/PUBLICATION-GUARD-REPORT.json"
STAGE_DIR="target/wvp-release-v0.3.0-unsigned"
ASSET_NAME="wvp-release-check-v0.3.0-termux-android-aarch64"
SIGNATURE="$STAGE_DIR/$ASSET_NAME.sig"

echo "=== VERIFY FILES EXIST ==="
test -s "$PUB_SCRIPT"
test -s "$PUB_DOC"
test -s "$STAGE_CHECK"

chmod +x "$PUB_SCRIPT" "$STAGE_CHECK"
bash -n "$PUB_SCRIPT"
bash -n "$STAGE_CHECK"

echo "Required files exist and shell syntax is valid."
echo

echo "=== RUN UNSIGNED STAGING FIRST ==="
"$STAGE_CHECK"
echo

echo "=== VERIFY NO SIGNATURE EXISTS BEFORE PUBLICATION GUARD ==="
if [ -e "$SIGNATURE" ]; then
  echo "FAIL: signature exists before publication guard conformance."
  exit 1
fi
echo "No signature exists."
echo

echo "=== RUN PUBLICATION GUARD EVALUATION ==="
"$PUB_SCRIPT" --evaluate
echo

echo "=== VERIFY REPORT EXISTS ==="
test -s "$REPORT"
cat "$REPORT"
echo

echo "=== VERIFY REPORT TERMS ==="
grep -q '"evidence_type": "release-publication-guard"' "$REPORT"
grep -q '"package_version": "0.3.0"' "$REPORT"
grep -q '"planned_tag": "v0.3.0"' "$REPORT"
grep -q '"release_publication_executed": false' "$REPORT"
grep -q '"signing_executed": false' "$REPORT"
grep -q '"signature_created": false' "$REPORT"
grep -q '"tag_created": false' "$REPORT"
grep -q '"github_release_created": false' "$REPORT"
grep -q '"source_to_release_proof": false' "$REPORT"
grep -q '"reproducible_build_claim": false' "$REPORT"
grep -q '"binary_safety_claim": false' "$REPORT"
grep -q '"audit_claim": false' "$REPORT"
grep -q '"approved_for_release_publication": false' "$REPORT"
grep -q "detached signature missing" "$REPORT"
echo "Report terms OK."
echo

echo "=== VERIFY REQUIRE-READY REFUSES MISSING SIGNATURE ==="
set +e
"$PUB_SCRIPT" --require-ready > target/wvp-v030-publication-guard-missing-signature.log 2>&1
REQUIRE_READY_RESULT=$?
set -e

if [ "$REQUIRE_READY_RESULT" -eq 0 ]; then
  echo "FAIL: require-ready succeeded without detached signature."
  cat target/wvp-v030-publication-guard-missing-signature.log
  exit 1
fi

grep -q "release publication is not approved" target/wvp-v030-publication-guard-missing-signature.log
grep -q "detached signature missing" target/wvp-v030-publication-guard-missing-signature.log
echo "Missing-signature refusal OK."
echo

echo "=== VERIFY NO SIGNATURE EXISTS ==="
if [ -e "$SIGNATURE" ]; then
  echo "FAIL: publication guard created or left a signature."
  exit 1
fi
echo "No signature exists."
echo

echo "=== VERIFY DOC TERMS ==="
grep -q "This guard does not create a signature" "$PUB_DOC"
grep -q "This guard does not create a tag" "$PUB_DOC"
grep -q "This guard does not create a GitHub release" "$PUB_DOC"
grep -q "This guard does not expose private signing material" "$PUB_DOC"
grep -q "source tree is clean" "$PUB_DOC"
grep -q "detached signature exists" "$PUB_DOC"
grep -q "detached signature verifies" "$PUB_DOC"
grep -q "No v0.3.0 tag is created by this document" "$PUB_DOC"
grep -q "No GitHub release is created by this document" "$PUB_DOC"
grep -q "No signature is created by this document" "$PUB_DOC"
echo "Doc terms OK."
echo

echo "=== VERIFY SCRIPT TERMS ==="
grep -q "approved_for_release_publication" "$PUB_SCRIPT"
grep -q "remote v0.3.0 tag already exists" "$PUB_SCRIPT"
grep -q "GitHub v0.3.0 release already exists" "$PUB_SCRIPT"
grep -q "detached signature missing" "$PUB_SCRIPT"
grep -q "signature verification failed" "$PUB_SCRIPT"
grep -q "release_publication_executed" "$PUB_SCRIPT"
grep -q "github_release_created" "$PUB_SCRIPT"
grep -q "source_to_release_proof" "$PUB_SCRIPT"
echo "Script terms OK."
echo

echo "=== VERIFY NO LOCAL v0.3.0 TAG CREATED ==="
if git tag --list | grep -qx "v0.3.0"; then
  echo "FAIL: v0.3.0 tag exists. Publication guard must not create a tag."
  exit 1
fi
echo "No local v0.3.0 tag found."
echo

echo "=== VERIFY NO FALSE 100 PERCENT CLAIM ==="
if grep -nE '100%|100 percent|fully complete|complete project' "$PUB_DOC" "$PUB_SCRIPT" "$REPORT"; then
  echo "FAIL: suspicious 100%/complete claim found."
  exit 1
fi
echo "No false 100% claim found."
echo

echo "=== VERIFY NO SECRET-LIKE MATERIAL IN PUBLICATION GUARD FILES ==="
PRIVATE_KEY_PATTERN='BEGIN (PGP |OPENSSH |RSA |EC |DSA )?'
PRIVATE_KEY_PATTERN="${PRIVATE_KEY_PATTERN}PRIVATE KEY"
AGE_SECRET_PATTERN_A='AGE'
AGE_SECRET_PATTERN_B='-SECRET-KEY-'
GITHUB_TOKEN_PATTERN_A='ghp'
GITHUB_TOKEN_PATTERN_B='_[A-Za-z0-9_]{20,}'
SECRET_SCAN_PATTERN="${PRIVATE_KEY_PATTERN}|${AGE_SECRET_PATTERN_A}${AGE_SECRET_PATTERN_B}|${GITHUB_TOKEN_PATTERN_A}${GITHUB_TOKEN_PATTERN_B}"

BAD=0
for f in "$PUB_SCRIPT" "$PUB_DOC"; do
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

echo "=== WVP v0.3.0 RELEASE PUBLICATION GUARD CONFORMANCE RESULT ==="
echo "RESULT: PASS"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
