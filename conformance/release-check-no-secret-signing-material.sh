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

check_pattern() {
  pattern="$1"
  if git grep -nF "$pattern" -- . ":!conformance/release-check-no-secret-signing-material.sh" ":!conformance/release-check-signature-tooling-capability.sh" \
      ":!conformance/release-check-public-key-policy.sh" ":!target" 2>/dev/null; then
    BAD=1
  fi
}

check_pattern "-----BEGIN PGP PRIVATE KEY BLOCK-----"
check_pattern "-----BEGIN OPENSSH PRIVATE KEY-----"
check_pattern "-----BEGIN RSA PRIVATE KEY-----"
check_pattern "-----BEGIN EC PRIVATE KEY-----"
check_pattern "-----BEGIN DSA PRIVATE KEY-----"
check_pattern "AGE-SECRET-KEY-"

if [ "$BAD" -ne 0 ]; then
  echo "FAIL: private signing material pattern found"
  false
fi

echo "No private signing material pattern found outside detector scripts."

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "RESULT: PASS"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
