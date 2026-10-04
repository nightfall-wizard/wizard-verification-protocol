#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP v0.2 RELEASE CANDIDATE DOCS CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

RC_DOC="docs/release/WVP-v0.2-RELEASE-CANDIDATE.md"
CHECKLIST="docs/release/WVP-v0.2-RELEASE-CHECKLIST.md"

test -s "$RC_DOC"
test -s "$CHECKLIST"

grep -Fq "This is not an audit." "$RC_DOC"
grep -Fq "does not prove reproducible builds" "$RC_DOC"
grep -Fq "Detached signatures can be verified" "$RC_DOC"
grep -Fq "Private signing material is not committed" "$RC_DOC"
grep -Fq "tampering is rejected" "$RC_DOC"

grep -Fq "cargo clippy --workspace --all-targets -- -D warnings" "$CHECKLIST"
grep -Fq "Signature tamper-negative conformance passes" "$CHECKLIST"
grep -Fq "Upload .sig" "$CHECKLIST" || grep -Fq "Upload \`.sig\`" "$CHECKLIST"
grep -Fq "Confirm status is \`INFO\`" "$CHECKLIST"
grep -Fq "private key path is inside the repository" "$CHECKLIST"

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "RESULT: PASS"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
