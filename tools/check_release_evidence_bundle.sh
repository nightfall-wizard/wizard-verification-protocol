#!/usr/bin/env bash
set -euo pipefail

RC_DOC="docs/releases/WVP-v0.5-RC1.md"
QUALITY_DOC="docs/RELEASE-QUALITY-GATE.md"
RELEASE_GATE="tools/check_release_quality_gate.sh"
WORKFLOW=".github/workflows/wvp-security-invariants.yml"

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

[ -f "$RC_DOC" ] || fail "missing release evidence bundle"
[ -f "$QUALITY_DOC" ] || fail "missing release quality document"
[ -f "$RELEASE_GATE" ] || fail "missing central release gate"
[ -f "$WORKFLOW" ] || fail "missing CI workflow"

for required in \
  "WVP v0.5-RC1" \
  "Release Candidate Identity" \
  "Required Gates" \
  "Evidence Summary" \
  "Security Posture" \
  "Non-Goals" \
  "Release Rule"
do
  grep -q "$required" "$RC_DOC" || fail "release evidence bundle missing: $required"
done

for gate in \
  "tools/check_security_invariants.sh" \
  "tools/check_security_evidence_matrix.sh" \
  "tools/check_security_threat_model.sh" \
  "tools/check_rust_defensive_code.sh" \
  "tools/check_cargo_supply_chain.sh" \
  "tools/check_dependency_inventory.sh" \
  "tools/check_release_evidence_bundle.sh" \
  "tools/check_security_artifact_manifest.sh" \
  "cargo fmt --all -- --check" \
  "cargo test --all"
do
  grep -q "$gate" "$RC_DOC" || fail "release evidence bundle missing gate: $gate"
  grep -q "$gate" "$QUALITY_DOC" || fail "release quality document missing gate: $gate"
done

grep -q "check_release_evidence_bundle.sh" "$RELEASE_GATE" || fail "central release gate does not run release evidence checker"
grep -q "check_release_quality_gate.sh" "$WORKFLOW" || fail "workflow does not run central release quality gate"

echo "PASS: release evidence bundle is complete and linked to the central quality gate"
