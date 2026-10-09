#!/usr/bin/env bash
set -euo pipefail

THREAT_MODEL="docs/security/THREAT-MODEL.md"
INVARIANTS="docs/security/SECURITY-INVARIANTS.md"
EVIDENCE="docs/security/SECURITY-EVIDENCE-MATRIX.md"
WORKFLOW=".github/workflows/wvp-security-invariants.yml"

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

[ -f "$THREAT_MODEL" ] || fail "missing $THREAT_MODEL"
[ -f "$INVARIANTS" ] || fail "missing $INVARIANTS"
[ -f "$EVIDENCE" ] || fail "missing $EVIDENCE"
[ -f "$WORKFLOW" ] || fail "missing $WORKFLOW"

for asset in \
  ASSET-001 \
  ASSET-002 \
  ASSET-003 \
  ASSET-004 \
  ASSET-005
do
  grep -q "$asset" "$THREAT_MODEL" || fail "$asset missing from threat model"
done

for boundary in \
  TB-001 \
  TB-002 \
  TB-003 \
  TB-004 \
  TB-005
do
  grep -q "$boundary" "$THREAT_MODEL" || fail "$boundary missing from threat model"
done

for threat in \
  THREAT-001 \
  THREAT-002 \
  THREAT-003 \
  THREAT-004 \
  THREAT-005 \
  THREAT-006 \
  THREAT-007
do
  grep -q "$threat" "$THREAT_MODEL" || fail "$threat missing from threat model"
done

for inv in \
  WVP-INV-001 \
  WVP-INV-002 \
  WVP-INV-003 \
  WVP-INV-004 \
  WVP-INV-005 \
  WVP-INV-006 \
  WVP-INV-007
do
  grep -q "$inv" "$THREAT_MODEL" || fail "$inv missing from threat model"
  grep -q "$inv" "$INVARIANTS" || fail "$inv missing from invariants"
  grep -q "$inv" "$EVIDENCE" || fail "$inv missing from evidence matrix"
done

for fixture in \
  FRC-SEC-001 \
  FRC-SEC-002 \
  FRC-SEC-003 \
  FRC-SEC-004 \
  FRC-SEC-005 \
  FRC-SEC-006 \
  FRC-SEC-007
do
  grep -q "$fixture" "$THREAT_MODEL" || fail "$fixture missing from threat model"
  grep -q "$fixture" "$EVIDENCE" || fail "$fixture missing from evidence matrix"
done

grep -q "Fail-Closed Principle" "$THREAT_MODEL" || fail "missing fail-closed principle"
grep -q "Explicit Non-Goals" "$THREAT_MODEL" || fail "missing explicit non-goals"
grep -q "Review Rule" "$THREAT_MODEL" || fail "missing review rule"
grep -q "Maintenance Rule" "$THREAT_MODEL" || fail "missing maintenance rule"

echo "PASS: security threat model is complete and linked to invariants, evidence, fixtures, and CI"
