#!/usr/bin/env bash
set -euo pipefail

echo "=== WVP SIGNATURE TOOLING CAPABILITY CONFORMANCE ==="
START_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
START_EPOCH="$(date +%s)"
echo "Startzeit: $START_TS"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

DOC="docs/release/SIGNATURE-TOOLING-CAPABILITY.md"

test -s "$DOC"

grep -Fq "WVP v0.2 adds real release-signature verification" "$DOC"
grep -Fq "Private signing keys must never be committed" "$DOC"
grep -Fq "Only public verification material may be committed" "$DOC"
grep -Fq "checksum passed and signature passed: eligible for INFO" "$DOC"

echo "=== LOCAL TOOL DISCOVERY ==="
FOUND=0

if command -v openssl >/dev/null 2>&1; then
  echo "openssl: found"
  openssl version || true
  FOUND=1
else
  echo "openssl: not-found"
fi

if command -v gpg >/dev/null 2>&1; then
  echo "gpg: found"
  gpg --version | head -n 3 || true
  FOUND=1
else
  echo "gpg: not-found"
fi

if command -v minisign >/dev/null 2>&1; then
  echo "minisign: found"
  minisign -v || true
  FOUND=1
else
  echo "minisign: not-found"
fi

if [ "$FOUND" -ne 1 ]; then
  echo "FAIL: no supported signature verification tool found"
  false
fi

echo "=== SECRET HEADER SCAN ==="
BAD=0

for pattern in \
  "-----BEGIN PGP PRIVATE KEY BLOCK-----" \
  "-----BEGIN OPENSSH PRIVATE KEY-----" \
  "-----BEGIN RSA PRIVATE KEY-----" \
  "-----BEGIN EC PRIVATE KEY-----" \
  "-----BEGIN DSA PRIVATE KEY-----" \
  "AGE-SECRET-KEY-"; do
  if git grep -nF "$pattern" -- . ":!conformance/release-check-no-secret-signing-material.sh" ":!conformance/release-check-signature-tooling-capability.sh" \
      ":!conformance/release-check-public-key-policy.sh" ":!target" 2>/dev/null; then
    BAD=1
  fi
done

if [ "$BAD" -ne 0 ]; then
  echo "FAIL: private signing material pattern found"
  false
fi

END_TS="$(date '+%Y-%m-%d %H:%M:%S %Z')"
END_EPOCH="$(date +%s)"
DURATION="$((END_EPOCH - START_EPOCH))"

echo "RESULT: PASS"
echo "Endzeit: $END_TS"
echo "Dauer Sekunden: $DURATION"
