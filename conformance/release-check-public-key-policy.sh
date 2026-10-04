#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP PUBLIC RELEASE VERIFICATION KEY CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

DOC="docs/release/RELEASE-SIGNING-KEY-POLICY.md"
PUB="keys/release/wvp-release-signing-public.pem"
PUB_SHA="keys/release/wvp-release-signing-public.pem.sha256"

test -s "$DOC"
test -s "$PUB"
test -s "$PUB_SHA"

grep -Fq "Only public verification material may be committed" "$DOC"
grep -Fq "The private release signing key must stay outside this repository" "$DOC"
grep -Fq "detached signature asset" "$DOC"
grep -Fq "RSA-3072" "$DOC"
grep -Fq "SHA-256" "$DOC"

echo "=== OPENSSL PUBLIC KEY PARSE ==="
openssl pkey -pubin -in "$PUB" -text -noout >/dev/null

echo "=== PUBLIC KEY FINGERPRINT CHECK ==="
ACTUAL="$(
  openssl pkey -pubin -in "$PUB" -pubout -outform DER \
    | sha256sum \
    | awk '{print $1}'
)"
EXPECTED="$(tr -d '[:space:]' < "$PUB_SHA")"

echo "Expected: $EXPECTED"
echo "Actual:   $ACTUAL"

if [ "$ACTUAL" != "$EXPECTED" ]; then
  echo "FAIL: public key fingerprint mismatch"
  false
fi

echo "=== TRACKED PRIVATE MATERIAL PATH SAFETY CHECK ==="
BAD_PATHS="$(
  git ls-files \
    | grep -Ei '(^|/)(.*private.*\.pem|.*private-key.*|.*\.secret$|.*\.seed$|.*\.wallet$)$' \
    | grep -Ev '^(conformance/release-check-no-secret-signing-material\.sh|conformance/release-check-signature-tooling-capability\.sh|conformance/release-check-public-key-policy\.sh)$' \
    || true
)"

if [ -n "$BAD_PATHS" ]; then
  echo "$BAD_PATHS"
  echo "FAIL: suspicious tracked private-material path found"
  false
fi

echo "No suspicious tracked private-material path found."

echo "=== PRIVATE HEADER SCAN ==="
BAD=0

check_pattern() {
  pattern="$1"
  if git grep -nF "$pattern" -- . \
    ":!conformance/release-check-no-secret-signing-material.sh" \
    ":!conformance/release-check-signature-tooling-capability.sh" \
    ":!conformance/release-check-public-key-policy.sh" \
    ":!target" 2>/dev/null; then
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
