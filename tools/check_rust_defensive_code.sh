#!/usr/bin/env bash
set -euo pipefail

SRC_DIR="reference/rust/wvp-release-check/src"
BASELINE="security-baselines/rust-risk-patterns.baseline"
POLICY="docs/security/DEFENSIVE-CODING-POLICY.md"
REPORT="docs/security/RUST-RISK-PATTERN-BASELINE.md"

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

[ -d "$SRC_DIR" ] || fail "missing production source directory: $SRC_DIR"
[ -f "$BASELINE" ] || fail "missing baseline: $BASELINE"
[ -f "$POLICY" ] || fail "missing policy: $POLICY"
[ -f "$REPORT" ] || fail "missing report: $REPORT"

get_baseline() {
  local key="$1"
  grep "^${key}=" "$BASELINE" | cut -d= -f2
}

count_pattern() {
  local pattern="$1"
  { grep -RInE "$pattern" "$SRC_DIR" --include='*.rs' 2>/dev/null || true; } | wc -l | tr -d ' '
}

check_not_increased() {
  local key="$1"
  local label="$2"
  local pattern="$3"
  local baseline
  local current

  baseline="$(get_baseline "$key")"
  current="$(count_pattern "$pattern")"

  [ -n "$baseline" ] || fail "missing baseline key: $key"

  if [ "$current" -gt "$baseline" ]; then
    echo "Current findings for $label:"
    grep -RInE "$pattern" "$SRC_DIR" --include='*.rs' || true
    fail "$label increased from $baseline to $current"
  fi
}

check_not_increased "unwrap_calls" "unwrap calls" 'unwrap[[:space:]]*\('
check_not_increased "dot_unwrap_calls" ".unwrap calls" '\.unwrap[[:space:]]*\('
check_not_increased "expect_calls" "expect calls" 'expect[[:space:]]*\('
check_not_increased "dot_expect_calls" ".expect calls" '\.expect[[:space:]]*\('
check_not_increased "panic_calls" "panic calls" 'panic![[:space:]]*\('
check_not_increased "todo_calls" "todo calls" 'todo![[:space:]]*\('
check_not_increased "unimplemented_calls" "unimplemented calls" 'unimplemented![[:space:]]*\('
check_not_increased "dbg_calls" "dbg calls" 'dbg![[:space:]]*\('
check_not_increased "unsafe_markers" "unsafe markers" '(^|[^A-Za-z0-9_])unsafe([^A-Za-z0-9_]|$)'
check_not_increased "allow_unused" "allow unused markers" 'allow[[:space:]]*\([[:space:]]*unused'
check_not_increased "allow_dead_code" "allow dead_code markers" 'allow[[:space:]]*\([[:space:]]*dead_code'

grep -q "Baseline Rule" "$POLICY" || fail "policy missing Baseline Rule"
grep -q "Review Rule" "$POLICY" || fail "policy missing Review Rule"
grep -q "Security Principle" "$POLICY" || fail "policy missing Security Principle"

echo "PASS: Rust defensive-code baseline is enforced and no tracked risk pattern increased"
