#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP v0.3 RELEASE DOCS CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

NOTES="docs/release/WVP-V0.3-RELEASE-NOTES-DRAFT.md"
NAMING="docs/release/WVP-V0.3-ARTIFACT-NAMING-PLAN.md"

echo "=== VERIFY FILES EXIST ==="
test -s "$NOTES"
test -s "$NAMING"
echo "Release docs exist."
echo

echo "=== VERIFY RELEASE NOTES REQUIRED TERMS ==="
grep -q "WVP v0.3 Release Notes Draft" "$NOTES"
grep -q "Build Provenance Evidence" "$NOTES"
grep -q "Release Integrity Hardening" "$NOTES"
grep -q "v0.3 Readiness Controls" "$NOTES"
grep -q "Explicit Non-Claims" "$NOTES"
grep -q "binary safety" "$NOTES"
grep -q "audit status" "$NOTES"
grep -q "source-to-release proof" "$NOTES"
grep -q "complete reproducible builds" "$NOTES"
echo "Release notes terms OK."
echo

echo "=== VERIFY ARTIFACT NAMING REQUIRED TERMS ==="
grep -q "WVP v0.3 Artifact Naming Plan" "$NAMING"
grep -q "v0.3.0" "$NAMING"
grep -q "0.3.0" "$NAMING"
grep -q "wvp-release-check-v0.3.0-termux-android-aarch64" "$NAMING"
grep -q "wvp-release-check-v0.3.0-termux-android-aarch64.sha256" "$NAMING"
grep -q "wvp-release-check-v0.3.0-termux-android-aarch64.sig" "$NAMING"
grep -q "wvp-ci-build-provenance-<git-commit-sha>" "$NAMING"
grep -q "sha256sum -c" "$NAMING"
grep -q "openssl dgst -sha256 -verify" "$NAMING"
echo "Artifact naming terms OK."
echo

echo "=== VERIFY NON-CLAIM BOUNDARY ==="
grep -q "must not claim" "$NAMING"
grep -q "must not claim" "$NOTES"
grep -q "No v0.3.0 release has been published by this document" "$NAMING"
grep -q "not a published release announcement" "$NOTES"
echo "Non-claim boundary OK."
echo

echo "=== VERIFY NO FALSE 100 PERCENT CLAIM ==="
if grep -nE '100%|100 percent|fully complete|complete project' "$NOTES" "$NAMING"; then
  echo "FAIL: suspicious 100%/complete claim found."
  exit 1
fi
echo "No false 100% claim found."
echo

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "=== WVP v0.3 RELEASE DOCS CONFORMANCE RESULT ==="
echo "RESULT: PASS"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
