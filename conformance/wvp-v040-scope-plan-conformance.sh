#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP v0.4 SCOPE PLAN CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

DOC="docs/roadmap/WVP-V0.4-SCOPE-AND-PLAN.md"

echo "=== VERIFY DOCUMENT EXISTS ==="
test -s "$DOC"
echo "Document exists."

echo "=== VERIFY REQUIRED v0.4 TRACKS ==="
grep -q "Track 1 — release-check hardening" "$DOC"
grep -q "Track 2 — scorecard security baseline" "$DOC"
grep -q "Track 3 — node-diagnose read-only diagnostics" "$DOC"
grep -q "Track 4 — conformance and test vectors" "$DOC"
grep -q "Track 5 — light-verify design phase" "$DOC"
echo "Required tracks OK."

echo "=== VERIFY LEGAL AND SAFETY BOUNDARY ==="
grep -q "Legal compliance and safety are the first constraint" "$DOC"
grep -q "must not introduce" "$DOC"
grep -q "custody functionality" "$DOC"
grep -q "exchange, broker, or trading functionality" "$DOC"
grep -q "investment advice automation" "$DOC"
grep -q "private-key collection" "$DOC"
grep -q "seed phrase collection" "$DOC"
grep -q "wallet-spending automation" "$DOC"
echo "Legal/safety boundary OK."

echo "=== VERIFY NON-CLAIMS ==="
grep -q "does not prove" "$DOC"
grep -q "audit result" "$DOC"
grep -q "legal compliance" "$DOC"
grep -q "binary safety" "$DOC"
grep -q "source-to-release correspondence" "$DOC"
grep -q "reproducible build" "$DOC"
grep -q "consensus correctness" "$DOC"
grep -q "wallet safety" "$DOC"
grep -q "investment suitability" "$DOC"
echo "Non-claims OK."

echo "=== VERIFY v0.4 IS PLANNED, NOT IMPLEMENTED ==="
grep -q "Status: planned" "$DOC"
grep -q "v0.4 is planned but not implemented" "$DOC"
grep -q "overall WVP system is not complete" "$DOC"
echo "Planning boundary OK."

echo "=== VERIFY NO FALSE COMPLETION CLAIM ==="
if grep -nE 'overall WVP system[: ]+100%|WVP system[: ]+complete|audit passed|legally compliant|binary safety proven|reproducible build proven|source-to-release proven' "$DOC"; then
  echo "FAIL: false completion or proof claim found."
  exit 1
fi
echo "No false completion/proof claim found."

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo
echo "=== WVP v0.4 SCOPE PLAN CONFORMANCE RESULT ==="
echo "RESULT: PASS"
echo "v0.4 scope is documented."
echo "Legal/safety boundary is explicit."
echo "No audit/legal/binary/reproducible/source-to-release claim is made."
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
