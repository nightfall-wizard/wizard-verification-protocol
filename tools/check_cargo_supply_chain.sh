#!/usr/bin/env bash
set -euo pipefail

ROOT_MANIFEST="Cargo.toml"
CRATE_MANIFEST="reference/rust/wvp-release-check/Cargo.toml"
LOCKFILE="Cargo.lock"
POLICY="docs/security/SUPPLY-CHAIN-POLICY.md"
RELEASE_GATE="tools/check_release_quality_gate.sh"
WORKFLOW=".github/workflows/wvp-security-invariants.yml"

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

[ -f "$ROOT_MANIFEST" ] || fail "missing root Cargo.toml"
[ -f "$CRATE_MANIFEST" ] || fail "missing crate Cargo.toml: $CRATE_MANIFEST"
[ -f "$LOCKFILE" ] || fail "missing Cargo.lock"
[ -f "$POLICY" ] || fail "missing supply-chain policy"
[ -f "$RELEASE_GATE" ] || fail "missing release quality gate"
[ -f "$WORKFLOW" ] || fail "missing workflow"

echo "=== Supply-chain check: cargo metadata --locked ==="
cargo metadata --locked --format-version 1 --manifest-path "$CRATE_MANIFEST" >/dev/null

echo "=== Supply-chain check: direct git dependencies ==="
if grep -RInE '^[[:space:]]*git[[:space:]]*=' . --include='Cargo.toml'; then
  fail "direct Cargo git dependencies are not allowed by WVP supply-chain policy"
fi

grep -q "Cargo.lock" "$POLICY" || fail "policy does not mention Cargo.lock"
grep -q "cargo metadata --locked" "$POLICY" || fail "policy does not mention locked metadata"
grep -q "git =" "$POLICY" || fail "policy does not mention Git dependency control"

grep -q "check_cargo_supply_chain.sh" "$RELEASE_GATE" || fail "release gate does not run supply-chain checker"
grep -q "check_release_quality_gate.sh" "$WORKFLOW" || fail "workflow does not run central release quality gate"

echo "PASS: Cargo supply-chain reproducibility gate passed"
