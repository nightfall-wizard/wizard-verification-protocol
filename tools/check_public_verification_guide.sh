#!/usr/bin/env bash
set -euo pipefail

VERIFY_DOC="docs/releases/WVP-v0.5-VERIFY.md"
QUALITY_DOC="docs/RELEASE-QUALITY-GATE.md"
RELEASE_GATE="tools/check_release_quality_gate.sh"
WORKFLOW=".github/workflows/wvp-security-invariants.yml"

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

[ -f "$VERIFY_DOC" ] || fail "missing public verification guide"
[ -f "$QUALITY_DOC" ] || fail "missing release quality document"
[ -f "$RELEASE_GATE" ] || fail "missing central release gate"
[ -f "$WORKFLOW" ] || fail "missing CI workflow"

for required in \
  "Public Verification Guide" \
  "Minimum Verification Command" \
  "bash tools/check_release_quality_gate.sh" \
  "PASS: release quality gate passed" \
  "Individual Verification Commands" \
  "Expected Evidence" \
  "Failure Rule" \
  "Non-Goals"
do
  grep -q "$required" "$VERIFY_DOC" || fail "verification guide missing: $required"
done

for gate in \
  "tools/check_security_invariants.sh" \
  "tools/check_security_evidence_matrix.sh" \
  "tools/check_security_threat_model.sh" \
  "tools/check_rust_defensive_code.sh" \
  "tools/check_cargo_supply_chain.sh" \
  "tools/check_dependency_inventory.sh" \
  "tools/check_release_evidence_bundle.sh" \
  "tools/check_public_verification_guide.sh" \
  "tools/check_security_artifact_manifest.sh" \
  "cargo fmt --all -- --check" \
  "cargo test --all"
do
  grep -q "$gate" "$VERIFY_DOC" || fail "verification guide missing gate: $gate"
  grep -q "$gate" "$QUALITY_DOC" || fail "release quality document missing gate: $gate"
done

grep -q "check_public_verification_guide.sh" "$RELEASE_GATE" || fail "central release gate does not run public verification checker"
grep -q "check_release_quality_gate.sh" "$WORKFLOW" || fail "workflow does not run central release quality gate"

echo "PASS: public verification guide is complete and linked to the central quality gate"
