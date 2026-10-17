#!/usr/bin/env bash
set -euo pipefail

MATRIX="docs/security/SECURITY-EVIDENCE-MATRIX.md"
INVARIANTS="docs/security/SECURITY-INVARIANTS.md"
NEG_DIR="test-vectors/release-check/negative"
TEST_FILE="reference/rust/wvp-release-check/tests/security_negative_fixtures.rs"
WORKFLOW=".github/workflows/wvp-security-invariants.yml"
RELEASE_GATE="tools/check_release_quality_gate.sh"

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

[ -f "$MATRIX" ] || fail "missing $MATRIX"
[ -f "$INVARIANTS" ] || fail "missing $INVARIANTS"
[ -d "$NEG_DIR" ] || fail "missing $NEG_DIR"
[ -f "$TEST_FILE" ] || fail "missing $TEST_FILE"
[ -f "$WORKFLOW" ] || fail "missing $WORKFLOW"

for inv in \
  WVP-INV-001 \
  WVP-INV-002 \
  WVP-INV-003 \
  WVP-INV-004 \
  WVP-INV-005 \
  WVP-INV-006 \
  WVP-INV-007
do
  grep -q "$inv" "$INVARIANTS" || fail "$inv missing from invariant document"
  grep -q "$inv" "$MATRIX" || fail "$inv missing from evidence matrix"
done

for fixture in \
  FRC-SEC-001-missing-digest.json \
  FRC-SEC-002-path-traversal.json \
  FRC-SEC-003-duplicate-artifact.json \
  FRC-SEC-004-missing-signature.json \
  FRC-SEC-005-network-dependent-verification.json \
  FRC-SEC-006-silent-downgrade.json \
  FRC-SEC-007-ambiguous-network-context.json
do
  [ -f "$NEG_DIR/$fixture" ] || fail "missing negative fixture: $fixture"
  grep -q "$fixture" "$MATRIX" || fail "$fixture missing from evidence matrix"
done

grep -q "security_negative_fixtures" "$MATRIX" || fail "matrix does not reference executable test target"
grep -q "reference/rust/wvp-release-check/tests/security_negative_fixtures.rs" "$MATRIX" || fail "matrix does not reference executable test file path"

grep -q "negative_security_fixtures_are_executable_specification" "$TEST_FILE" || fail "test file does not contain executable fixture specification test"
grep -q "negative_fixture_directory_is_version_controlled" "$TEST_FILE" || fail "test file does not contain fixture directory guard test"

if grep -q "check_release_quality_gate.sh" "$WORKFLOW"; then
  [ -f "$RELEASE_GATE" ] || fail "workflow uses release gate, but $RELEASE_GATE is missing"

  grep -q "check_security_invariants.sh" "$RELEASE_GATE" || fail "release gate does not run invariant checker"
  grep -q "check_security_evidence_matrix.sh" "$RELEASE_GATE" || fail "release gate does not run evidence matrix checker"
  grep -q "check_security_threat_model.sh" "$RELEASE_GATE" || fail "release gate does not run threat model checker"
  grep -q "check_rust_defensive_code.sh" "$RELEASE_GATE" || fail "release gate does not run defensive-code checker"
  grep -q "cargo fmt --all -- --check" "$RELEASE_GATE" || fail "release gate does not run cargo fmt check"
  grep -q "cargo test --all" "$RELEASE_GATE" || fail "release gate does not run cargo test --all"
else
  grep -q "cargo test --all" "$WORKFLOW" || fail "workflow does not run cargo test --all"
  grep -q "check_security_invariants.sh" "$WORKFLOW" || fail "workflow does not run invariant checker"
  grep -q "check_security_evidence_matrix.sh" "$WORKFLOW" || fail "workflow does not run evidence matrix checker"
fi

echo "PASS: security evidence matrix is complete and linked to invariants, fixtures, tests, and CI"
