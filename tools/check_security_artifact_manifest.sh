#!/usr/bin/env bash
set -euo pipefail

DOC="docs/security/SECURITY-ARTIFACT-MANIFEST.md"
BASELINE="security-baselines/security-artifact-manifest.sha256"
RELEASE_GATE="tools/check_release_quality_gate.sh"
QUALITY_DOC="docs/RELEASE-QUALITY-GATE.md"
WORKFLOW=".github/workflows/wvp-security-invariants.yml"

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

[ -f "$DOC" ] || fail "missing $DOC"
[ -f "$BASELINE" ] || fail "missing $BASELINE"
[ -f "$RELEASE_GATE" ] || fail "missing $RELEASE_GATE"
[ -f "$QUALITY_DOC" ] || fail "missing $QUALITY_DOC"
[ -f "$WORKFLOW" ] || fail "missing $WORKFLOW"

command -v sha256sum >/dev/null 2>&1 || fail "sha256sum missing"

required_files=(
  "docs/security/SECURITY-INVARIANTS.md"
  "docs/security/SECURITY-EVIDENCE-MATRIX.md"
  "docs/security/THREAT-MODEL.md"
  "docs/security/DEFENSIVE-CODING-POLICY.md"
  "docs/security/RUST-RISK-PATTERN-BASELINE.md"
  "docs/security/SUPPLY-CHAIN-POLICY.md"
  "docs/security/CARGO-DEPENDENCY-INVENTORY.md"
  "docs/security/SECURITY-ARTIFACT-MANIFEST.md"
  "docs/RELEASE-QUALITY-GATE.md"
  "tools/check_security_invariants.sh"
  "tools/check_security_evidence_matrix.sh"
  "tools/check_security_threat_model.sh"
  "tools/check_rust_defensive_code.sh"
  "tools/check_cargo_supply_chain.sh"
  "tools/check_dependency_inventory.sh"
  "tools/check_security_artifact_manifest.sh"
  "tools/check_release_quality_gate.sh"
  "security-baselines/rust-risk-patterns.baseline"
  "security-baselines/cargo-lock.sha256"
  "reference/rust/wvp-release-check/tests/security_negative_fixtures.rs"
  "test-vectors/release-check/negative/FRC-SEC-001-missing-digest.json"
  "test-vectors/release-check/negative/FRC-SEC-002-path-traversal.json"
  "test-vectors/release-check/negative/FRC-SEC-003-duplicate-artifact.json"
  "test-vectors/release-check/negative/FRC-SEC-004-missing-signature.json"
  "test-vectors/release-check/negative/FRC-SEC-005-network-dependent-verification.json"
  "test-vectors/release-check/negative/FRC-SEC-006-silent-downgrade.json"
  "test-vectors/release-check/negative/FRC-SEC-007-ambiguous-network-context.json"
  "Cargo.lock"
)

for f in "${required_files[@]}"; do
  [ -f "$f" ] || fail "controlled security artifact missing: $f"
  grep -q "  $f$" "$BASELINE" || fail "controlled artifact missing from baseline: $f"
done

echo "=== Security artifact manifest: sha256 verification ==="
sha256sum -c "$BASELINE"

grep -q "Security Artifact Manifest" "$DOC" || fail "manifest document missing title"
grep -q "Controlled Artifact Classes" "$DOC" || fail "manifest document missing controlled artifact classes"
grep -q "Maintenance Rule" "$DOC" || fail "manifest document missing maintenance rule"

grep -q "check_security_artifact_manifest.sh" "$QUALITY_DOC" || fail "release quality document does not list artifact manifest gate"
grep -q "check_security_artifact_manifest.sh" "$RELEASE_GATE" || fail "release gate does not run artifact manifest checker"
grep -q "check_release_quality_gate.sh" "$WORKFLOW" || fail "workflow does not run central release quality gate"

echo "PASS: security artifact manifest is complete and all controlled artifacts match committed hashes"
