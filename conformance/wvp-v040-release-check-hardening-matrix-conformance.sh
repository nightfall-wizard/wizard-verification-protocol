#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP v0.4 RELEASE-CHECK HARDENING MATRIX CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

DOC="docs/roadmap/WVP-V0.4-RELEASE-CHECK-HARDENING-MATRIX.md"

echo "=== VERIFY DOCUMENT EXISTS ==="
test -s "$DOC"
echo "Document exists."

echo "=== VERIFY ISSUE IDS ==="
for id in RCH-001 RCH-002 RCH-003 RCH-004 RCH-005 RCH-006 RCH-007 RCH-008 RCH-009 RCH-010; do
  grep -q "$id" "$DOC"
done
echo "Issue IDs OK."

echo "=== VERIFY P0 COVERAGE ==="
grep -q "RCH-001" "$DOC"
grep -q "RCH-002" "$DOC"
grep -q "RCH-003" "$DOC"
grep -q "RCH-004" "$DOC"
grep -q "P0 implementation order" "$DOC"
grep -q "lock down asset classification rules" "$DOC"
grep -q "public key not counted as signature" "$DOC"
grep -q "duplicate checksum/signature negative fixtures" "$DOC"
grep -q "missing public key negative fixture" "$DOC"
echo "P0 coverage OK."

echo "=== VERIFY REQUIRED TEST CLASSES ==="
grep -q "valid release with checksum, detached signature, and public key" "$DOC"
grep -q "release with checksum but no signature" "$DOC"
grep -q "release with signature but no public key" "$DOC"
grep -q "release with public key but no signature" "$DOC"
grep -q "release with duplicate checksum files" "$DOC"
grep -q "release with duplicate signature files" "$DOC"
grep -q "release with public key name containing" "$DOC"
grep -q "repository with no releases" "$DOC"
echo "Required test classes OK."

echo "=== VERIFY LEGAL AND SAFETY BOUNDARY ==="
grep -q "Legal compliance and safety remain the first constraint" "$DOC"
grep -q "custody functionality" "$DOC"
grep -q "exchange, broker, or trading functionality" "$DOC"
grep -q "investment advice automation" "$DOC"
grep -q "private-key collection" "$DOC"
grep -q "seed phrase collection" "$DOC"
grep -q "wallet-spending automation" "$DOC"
echo "Legal/safety boundary OK."

echo "=== VERIFY NON-CLAIMS ==="
grep -q "must not claim" "$DOC"
grep -q "audit result" "$DOC"
grep -q "legal compliance" "$DOC"
grep -q "binary safety" "$DOC"
grep -q "source-to-release correspondence" "$DOC"
grep -q "reproducible build" "$DOC"
grep -q "consensus correctness" "$DOC"
grep -q "wallet safety" "$DOC"
grep -q "investment suitability" "$DOC"
echo "Non-claims OK."

echo "=== VERIFY NON-GOALS ==="
grep -q "does not implement the fixes by itself" "$DOC"
grep -q "a tag" "$DOC"
grep -q "a GitHub release" "$DOC"
grep -q "a release asset" "$DOC"
grep -q "a private signing key" "$DOC"
grep -q "wallet functionality" "$DOC"
grep -q "custody functionality" "$DOC"
grep -q "exchange functionality" "$DOC"
grep -q "legal certification" "$DOC"
grep -q "security audit certification" "$DOC"
echo "Non-goals OK."

echo "=== VERIFY NO FALSE PROOF CLAIM ==="
if grep -nE 'audit passed|legally compliant|binary safety proven|reproducible build proven|source-to-release proven|wallet safety proven|investment suitable' "$DOC"; then
  echo "FAIL: false proof claim found."
  exit 1
fi
echo "No false proof claim found."

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo
echo "=== WVP v0.4 RELEASE-CHECK HARDENING MATRIX CONFORMANCE RESULT ==="
echo "RESULT: PASS"
echo "Release-check hardening issue matrix is documented."
echo "P0 issues are explicit."
echo "Legal/safety boundary is explicit."
echo "No audit/legal/binary/reproducible/source-to-release claim is made."
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
