#!/usr/bin/env bash
set -euo pipefail

DOC="docs/RELEASE-QUALITY-GATE.md"
WORKFLOW=".github/workflows/wvp-security-invariants.yml"

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

[ -f "$DOC" ] || fail "missing $DOC"
[ -f "$WORKFLOW" ] || fail "missing $WORKFLOW"

for required in \
  "tools/check_security_invariants.sh" \
  "tools/check_security_evidence_matrix.sh" \
  "tools/check_security_threat_model.sh" \
  "tools/check_rust_defensive_code.sh" \
  "cargo fmt --all -- --check" \
  "cargo test --all"
do
  grep -q "$required" "$DOC" || fail "release quality document missing: $required"
done

grep -q "check_release_quality_gate.sh" "$WORKFLOW" || fail "workflow does not run release quality gate"

echo "=== Gate 1: security invariants ==="
bash tools/check_security_invariants.sh

echo "=== Gate 2: security evidence matrix ==="
bash tools/check_security_evidence_matrix.sh

echo "=== Gate 3: security threat model ==="
bash tools/check_security_threat_model.sh

echo "=== Gate 4: Rust defensive-code baseline ==="
bash tools/check_rust_defensive_code.sh

echo "=== Gate 5: Rust formatting ==="
cargo fmt --all -- --check

echo "=== Gate 6: full Rust test suite ==="
cargo test --all

echo "PASS: release quality gate passed"
