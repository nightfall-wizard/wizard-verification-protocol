#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP v0.3 VERSION AND RELEASE COMMAND PLAN CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

PLAN="docs/release/WVP-V0.3-VERSION-BUMP-AND-RELEASE-COMMAND-PLAN.md"

echo "=== VERIFY FILE EXISTS ==="
test -s "$PLAN"
echo "Plan exists: $PLAN"
echo

echo "=== VERIFY VERSION TERMS ==="
grep -q "v0.3.0" "$PLAN"
grep -q "0.3.0" "$PLAN"
grep -q "0.2.0" "$PLAN"
grep -q "reference/rust/wvp-release-check/Cargo.toml" "$PLAN"
grep -q 'version = "0.3.0"' "$PLAN"
echo "Version terms OK."
echo

echo "=== VERIFY COMMAND TERMS ==="
grep -q "cargo build --release --locked" "$PLAN"
grep -q "target/wvp-release-v0.3.0" "$PLAN"
grep -q "sha256sum" "$PLAN"
grep -q "openssl dgst -sha256 -sign" "$PLAN"
grep -q "openssl dgst -sha256 -verify" "$PLAN"
grep -q "git tag -a v0.3.0" "$PLAN"
grep -q "gh release create v0.3.0" "$PLAN"
echo "Command terms OK."
echo

echo "=== VERIFY ARTIFACT TERMS ==="
grep -q "wvp-release-check-v0.3.0-termux-android-aarch64" "$PLAN"
grep -q "wvp-release-check-v0.3.0-termux-android-aarch64.sha256" "$PLAN"
grep -q "wvp-release-check-v0.3.0-termux-android-aarch64.sig" "$PLAN"
echo "Artifact terms OK."
echo

echo "=== VERIFY SECRET SAFETY TERMS ==="
grep -q "Private signing material must not be committed" "$PLAN"
grep -q "Private signing material must not be copied into the repository" "$PLAN"
grep -q "Private signing material must not be printed into logs" "$PLAN"
grep -q "<private-key-file-outside-repo>" "$PLAN"
echo "Secret safety terms OK."
echo

echo "=== VERIFY NON-CLAIM BOUNDARY ==="
grep -q "must not claim" "$PLAN"
grep -q "not claim" "$PLAN"
grep -q "No v0.3.0 release has been published by this document" "$PLAN"
grep -q "No tag is created by this document" "$PLAN"
grep -q "No signature is created by this document" "$PLAN"
grep -q "source-to-release-proof" "$PLAN"
grep -q "reproducible-build proof" "$PLAN"
grep -q "audit" "$PLAN"
echo "Non-claim boundary OK."
echo

echo "=== VERIFY NO FALSE 100 PERCENT CLAIM ==="
if grep -nE '100%|100 percent|fully complete|complete project' "$PLAN"; then
  echo "FAIL: suspicious 100%/complete claim found."
  exit 1
fi
echo "No false 100% claim found."
echo

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "=== WVP v0.3 VERSION AND RELEASE COMMAND PLAN CONFORMANCE RESULT ==="
echo "RESULT: PASS"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
