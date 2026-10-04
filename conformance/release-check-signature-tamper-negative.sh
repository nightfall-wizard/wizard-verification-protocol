#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP SIGNATURE TAMPER-NEGATIVE CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

cargo test --workspace --locked signature_tamper -- --nocapture
cargo test --workspace --locked signature_verification_accepts_valid_signature -- --nocapture

DOC="docs/release/SIGNATURE-TAMPER-NEGATIVE-TESTING.md"
test -s "$DOC"

grep -Fq "modified signed asset fails" "$DOC"
grep -Fq "modified detached signature fails" "$DOC"
grep -Fq "wrong public verification key fails" "$DOC"
grep -Fq "fail closed" "$DOC"

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "RESULT: PASS"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
