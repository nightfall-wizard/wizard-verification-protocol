#!/usr/bin/env bash
set -euo pipefail

DOC="docs/security/SECURITY-INVARIANTS.md"
NEG_DIR="test-vectors/release-check/negative"

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

[ -f "$DOC" ] || fail "missing $DOC"
[ -d "$NEG_DIR" ] || fail "missing $NEG_DIR"

for inv in \
  WVP-INV-001 \
  WVP-INV-002 \
  WVP-INV-003 \
  WVP-INV-004 \
  WVP-INV-005 \
  WVP-INV-006 \
  WVP-INV-007
do
  grep -q "$inv" "$DOC" || fail "missing invariant in document: $inv"
done

count="$(find "$NEG_DIR" -maxdepth 1 -type f -name 'FRC-SEC-*.json' | wc -l | tr -d ' ')"
[ "$count" -ge 7 ] || fail "expected at least 7 negative fixtures, found $count"

for f in "$NEG_DIR"/FRC-SEC-*.json; do
  [ -f "$f" ] || fail "no negative fixture files found"

  grep -q '"expected"[[:space:]]*:[[:space:]]*"reject"' "$f" \
    || fail "$f does not explicitly expect reject"

  grep -q '"invariant"[[:space:]]*:[[:space:]]*"WVP-INV-' "$f" \
    || fail "$f does not reference a WVP invariant"

  grep -q '"case_id"[[:space:]]*:[[:space:]]*"FRC-SEC-' "$f" \
    || fail "$f does not contain FRC-SEC case_id"

  grep -q '"description"[[:space:]]*:' "$f" \
    || fail "$f lacks description"

done

grep -R '"expected"[[:space:]]*:[[:space:]]*"accept"' "$NEG_DIR" && \
  fail "negative fixtures must not contain expected accept"

echo "PASS: security invariants and negative release-check fixtures are present and consistent"
