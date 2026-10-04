#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP SIGNATURE ASSET MATCHING CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

cargo test --workspace --locked asset_matching -- --nocapture

DOC="docs/release/SIGNATURE-ASSET-MATCHING.md"
test -s "$DOC"

grep -Fq "exactly one checksum manifest ending in" "$DOC"
grep -Fq "exactly one detached signature asset ending in" "$DOC"
grep -Fq "more than one" "$DOC"

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "RESULT: PASS"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
