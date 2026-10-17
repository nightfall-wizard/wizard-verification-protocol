#!/usr/bin/env bash
set -euo pipefail

DOC="docs/security/CARGO-DEPENDENCY-INVENTORY.md"
BASELINE="security-baselines/cargo-lock.sha256"

ROOT_MANIFEST="Cargo.toml"
CRATE_MANIFEST="reference/rust/wvp-release-check/Cargo.toml"
LOCKFILE="Cargo.lock"
RELEASE_GATE="tools/check_release_quality_gate.sh"
WORKFLOW=".github/workflows/wvp-security-invariants.yml"

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

for f in "$DOC" "$BASELINE" "$ROOT_MANIFEST" "$CRATE_MANIFEST" "$LOCKFILE" "$RELEASE_GATE" "$WORKFLOW"; do
  [ -f "$f" ] || fail "missing required file: $f"
done

command -v sha256sum >/dev/null 2>&1 || fail "sha256sum missing"

CURRENT_HASH="$(sha256sum "$LOCKFILE" | awk '{print $1}')"
BASELINE_HASH="$(awk '{print $1}' "$BASELINE" | head -n 1)"

[ -n "$BASELINE_HASH" ] || fail "empty Cargo.lock hash baseline"

if [ "$CURRENT_HASH" != "$BASELINE_HASH" ]; then
  echo "Current Cargo.lock hash:  $CURRENT_HASH"
  echo "Baseline Cargo.lock hash: $BASELINE_HASH"
  fail "Cargo.lock changed but dependency inventory baseline was not updated"
fi

grep -q "$CURRENT_HASH" "$DOC" || fail "dependency inventory does not contain current Cargo.lock hash"
grep -q "cargo tree --locked" "$DOC" || fail "dependency inventory does not document locked cargo tree"
grep -q "Review Rule" "$DOC" || fail "dependency inventory missing Review Rule"
grep -q "Security Rule" "$DOC" || fail "dependency inventory missing Security Rule"

echo "=== Dependency check: cargo metadata --locked ==="
cargo metadata --locked --format-version 1 --manifest-path "$CRATE_MANIFEST" >/dev/null

echo "=== Dependency check: cargo tree --locked ==="
cargo tree --locked --manifest-path "$CRATE_MANIFEST" >/dev/null

echo "=== Dependency check: direct git dependencies ==="
if grep -RInE '^[[:space:]]*git[[:space:]]*=' . --include='Cargo.toml'; then
  fail "direct Cargo git dependencies are not allowed"
fi

grep -q "check_dependency_inventory.sh" "$RELEASE_GATE" || fail "release gate does not run dependency inventory checker"
grep -q "check_release_quality_gate.sh" "$WORKFLOW" || fail "workflow does not run central release gate"

echo "PASS: Cargo dependency inventory is current and enforced"
