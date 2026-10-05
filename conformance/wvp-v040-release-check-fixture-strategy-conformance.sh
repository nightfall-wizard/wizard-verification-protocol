#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP v0.4 RELEASE-CHECK FIXTURE STRATEGY CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

DOC="docs/roadmap/WVP-V0.4-RELEASE-CHECK-FIXTURE-STRATEGY.md"
FIXTURE_README="fixtures/release-check/README.md"
FIXTURE_INDEX="fixtures/release-check/FIXTURE-INDEX.json"

echo "=== VERIFY FILES EXIST ==="
test -s "$DOC"
test -s "$FIXTURE_README"
test -s "$FIXTURE_INDEX"
python3 -m json.tool "$FIXTURE_INDEX" >/dev/null
echo "Files exist and JSON is valid."

echo "=== VERIFY FIXTURE IDS ==="
for id in FRC-001 FRC-002 FRC-003 FRC-004 FRC-005 FRC-006 FRC-007 FRC-008 FRC-009 FRC-010; do
  grep -q "$id" "$DOC"
  grep -q "$id" "$FIXTURE_INDEX"
done
echo "Fixture IDs OK."

echo "=== VERIFY SAFETY BOUNDARY ==="
grep -q "Legal compliance and safety remain the first constraint" "$DOC"
grep -q "private keys" "$DOC"
grep -q "seed phrases" "$DOC"
grep -q "wallet secrets" "$DOC"
grep -q "API tokens" "$DOC"
grep -q "custody data" "$DOC"
grep -q "investment advice" "$DOC"
grep -q "Fixtures are not audits" "$FIXTURE_README"
echo "Safety boundary OK."

echo "=== VERIFY LIVE VS FIXTURE BOUNDARY ==="
grep -q "Live-vs-fixture boundary" "$DOC"
grep -q "Live checks remain useful" "$DOC"
grep -q "Fixture checks are required" "$DOC"
grep -q "A live check failure may indicate" "$DOC"
grep -q "A fixture failure should indicate" "$DOC"
echo "Live-vs-fixture boundary OK."

echo "=== VERIFY NON-GOALS ==="
grep -q "does not implement the fixture runner" "$DOC"
grep -q "does not change" "$DOC"
grep -q "a tag" "$DOC"
grep -q "a GitHub release" "$DOC"
grep -q "a release asset" "$DOC"
grep -q "private signing material" "$DOC"
grep -q "wallet functionality" "$DOC"
grep -q "custody functionality" "$DOC"
grep -q "exchange functionality" "$DOC"
echo "Non-goals OK."

echo "=== VERIFY INDEX SAFETY FLAGS ==="
grep -q '"private_keys_allowed": false' "$FIXTURE_INDEX"
grep -q '"seed_phrases_allowed": false' "$FIXTURE_INDEX"
grep -q '"wallet_secrets_allowed": false' "$FIXTURE_INDEX"
grep -q '"api_tokens_allowed": false' "$FIXTURE_INDEX"
grep -q '"custody_data_allowed": false' "$FIXTURE_INDEX"
grep -q '"investment_advice_allowed": false' "$FIXTURE_INDEX"
grep -q '"audit_claim": false' "$FIXTURE_INDEX"
grep -q '"legal_compliance_claim": false' "$FIXTURE_INDEX"
grep -q '"binary_safety_claim": false' "$FIXTURE_INDEX"
grep -q '"source_to_release_claim": false' "$FIXTURE_INDEX"
grep -q '"reproducible_build_claim": false' "$FIXTURE_INDEX"
echo "Index safety flags OK."

echo "=== VERIFY NO SECRET-LIKE MATERIAL ==="
PRIVATE_MARKER_RE='BEGIN (PGP |OPENSSH |RSA |EC |DSA )?PR''IVATE KEY|AGE-SE''CRET-KEY-|ghp_[A-Za-z0-9_]{20,}'
if grep -nE "$PRIVATE_MARKER_RE" "$DOC" "$FIXTURE_README" "$FIXTURE_INDEX"; then
  echo "FAIL: secret-like material found."
  exit 1
fi
echo "No secret-like material found."

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo
echo "=== WVP v0.4 RELEASE-CHECK FIXTURE STRATEGY CONFORMANCE RESULT ==="
echo "RESULT: PASS"
echo "Fixture strategy is documented."
echo "Fixture index is valid JSON."
echo "Safety boundary is explicit."
echo "No audit/legal/binary/reproducible/source-to-release claim is made."
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
