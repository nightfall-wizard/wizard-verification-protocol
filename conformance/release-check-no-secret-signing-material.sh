#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP NO-SECRET SIGNATURE MATERIAL CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

DOC="docs/release/SIGNATURE-VERIFICATION-IMPLEMENTATION-PATH.md"
test -s "$DOC"

grep -Fq "No signing private key may be committed" "$DOC"
grep -Fq "public verification material only" "$DOC"
grep -Fq "signature verification failed: FAIL" "$DOC"
grep -Fq "signature verification passed and checksum passed" "$DOC"

echo "=== SECRET HEADER SCAN ==="
BAD=0
for pattern in \
  "-----BEGIN PGP PRIVATE KEY BLOCK-----" \
  "-----BEGIN OPENSSH PRIVATE KEY-----" \
  "-----BEGIN RSA PRIVATE KEY-----" \
  "-----BEGIN EC PRIVATE KEY-----" \
  "-----BEGIN DSA PRIVATE KEY-----" \
  "AGE-SECRET-KEY-"; do
  if git grep -nF "$pattern" -- . ":!conformance/release-check-no-secret-signing-material.sh" ":!target" 2>/dev/null; then
    BAD=1
  fi
done

if [ "$BAD" -ne 0 ]; then
  echo "FAIL: secret signing material pattern found"
  false
fi

echo "No private signing material pattern found."

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "RESULT: PASS"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
