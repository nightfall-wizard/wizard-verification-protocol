#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP v0.3.0 DETACHED SIGNATURE PROCEDURE CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

SIGN_SCRIPT="scripts/release/sign-v030-staged-asset.sh"
SIGN_DOC="docs/release/WVP-V0.3-DETACHED-SIGNATURE-PROCEDURE.md"
STAGE_CHECK="conformance/release-check-v030-unsigned-asset-staging.sh"

STAGE_DIR="target/wvp-release-v0.3.0-unsigned"
ASSET_NAME="wvp-release-check-v0.3.0-termux-android-aarch64"
SIGNATURE="$STAGE_DIR/$ASSET_NAME.sig"

echo "=== VERIFY FILES EXIST ==="
test -s "$SIGN_SCRIPT"
test -s "$SIGN_DOC"
test -s "$STAGE_CHECK"

chmod +x "$SIGN_SCRIPT" "$STAGE_CHECK"
bash -n "$SIGN_SCRIPT"
bash -n "$STAGE_CHECK"
echo "Required files exist and shell syntax is valid."
echo

echo "=== RUN UNSIGNED STAGING FIRST ==="
"$STAGE_CHECK"
echo

echo "=== VERIFY NO SIGNATURE EXISTS BEFORE DRY RUN ==="
if [ -e "$SIGNATURE" ]; then
  echo "FAIL: signature exists before dry-run."
  exit 1
fi
echo "No signature exists before dry-run."
echo

echo "=== RUN SIGNATURE PROCEDURE DRY RUN ==="
"$SIGN_SCRIPT" --dry-run
echo

echo "=== VERIFY DRY RUN CREATED NO SIGNATURE ==="
if [ -e "$SIGNATURE" ]; then
  echo "FAIL: dry-run created a signature."
  exit 1
fi
echo "Dry-run did not create signature."
echo

echo "=== VERIFY SIGN MODE REFUSES MISSING PRIVATE KEY ==="
set +e
"$SIGN_SCRIPT" --sign > target/wvp-v030-sign-missing-key.log 2>&1
SIGN_MISSING_KEY_RESULT=$?
set -e

if [ "$SIGN_MISSING_KEY_RESULT" -eq 0 ]; then
  echo "FAIL: sign mode succeeded without private key."
  cat target/wvp-v030-sign-missing-key.log
  exit 1
fi

grep -q "WVP_SIGNING_PRIVATE_KEY" target/wvp-v030-sign-missing-key.log
echo "Missing private-key refusal OK."
echo

echo "=== VERIFY DOC TERMS ==="
grep -q "This document does not create a signature" "$SIGN_DOC"
grep -q "This document does not create a tag" "$SIGN_DOC"
grep -q "This document does not create a GitHub release" "$SIGN_DOC"
grep -q "This document does not expose private signing material" "$SIGN_DOC"
grep -q "WVP_SIGNING_PRIVATE_KEY" "$SIGN_DOC"
grep -q "WVP_VERIFY_PUBLIC_KEY" "$SIGN_DOC"
grep -q "outside the repository" "$SIGN_DOC"
grep -q "not be committed" "$SIGN_DOC"
grep -q "not be copied into the repository" "$SIGN_DOC"
grep -q "not be printed into logs" "$SIGN_DOC"
grep -q "openssl dgst -sha256 -verify" "$SIGN_DOC"
grep -q "No v0.3.0 tag is created by this document" "$SIGN_DOC"
grep -q "No GitHub release is created by this document" "$SIGN_DOC"
grep -q "No signature is created by this document" "$SIGN_DOC"
echo "Doc terms OK."
echo

echo "=== VERIFY SCRIPT SAFETY TERMS ==="
grep -q "WVP_SIGNING_PRIVATE_KEY" "$SIGN_SCRIPT"
grep -q "WVP_VERIFY_PUBLIC_KEY" "$SIGN_SCRIPT"
grep -q "relative_to(repo)" "$SIGN_SCRIPT"
grep -q "openssl dgst -sha256 -sign" "$SIGN_SCRIPT"
grep -q "openssl dgst -sha256 -verify" "$SIGN_SCRIPT"
grep -q "No local" "$SIGN_SCRIPT"
echo "Script safety terms OK."
echo

echo "=== VERIFY NO LOCAL v0.3.0 TAG CREATED ==="
if git tag --list | grep -qx "v0.3.0"; then
  echo "FAIL: v0.3.0 tag exists. Signature procedure must not create a tag."
  exit 1
fi
echo "No local v0.3.0 tag found."
echo

echo "=== VERIFY NO FALSE 100 PERCENT CLAIM ==="
if grep -nE '100%|100 percent|fully complete|complete project' "$SIGN_DOC" "$SIGN_SCRIPT"; then
  echo "FAIL: suspicious 100%/complete claim found."
  exit 1
fi
echo "No false 100% claim found."
echo

echo "=== VERIFY NO SECRET-LIKE MATERIAL IN SIGNATURE PROCEDURE FILES ==="
PRIVATE_KEY_PATTERN='BEGIN (PGP |OPENSSH |RSA |EC |DSA )?'
PRIVATE_KEY_PATTERN="${PRIVATE_KEY_PATTERN}PRIVATE KEY"
AGE_SECRET_PATTERN_A='AGE'
AGE_SECRET_PATTERN_B='-SECRET-KEY-'
GITHUB_TOKEN_PATTERN_A='ghp'
GITHUB_TOKEN_PATTERN_B='_[A-Za-z0-9_]{20,}'
SECRET_SCAN_PATTERN="${PRIVATE_KEY_PATTERN}|${AGE_SECRET_PATTERN_A}${AGE_SECRET_PATTERN_B}|${GITHUB_TOKEN_PATTERN_A}${GITHUB_TOKEN_PATTERN_B}"

BAD=0
for f in "$SIGN_SCRIPT" "$SIGN_DOC"; do
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

echo "=== WVP v0.3.0 DETACHED SIGNATURE PROCEDURE CONFORMANCE RESULT ==="
echo "RESULT: PASS"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
