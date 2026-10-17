#!/usr/bin/env bash
set -Eeuo pipefail

DOC="docs/review/WVP-REVIEW-001-NIGHTFALL-PR043-MAINTAINER-ASSESSMENT.md"
JSON="reports/nightfall/wvp-review-001-maintainer-assessment.json"
STATUS="maintenance/WVP-REVIEW-001-STATUS.md"

fail(){ echo "FAIL: $*" >&2; exit 1; }
ok(){ echo "OK: $*"; }

[ -s "$DOC" ] || fail "missing maintainer assessment doc"
[ -s "$JSON" ] || fail "missing maintainer assessment json"
[ -s "$STATUS" ] || fail "missing maintainer status"

grep -q "If a fresh peer is known to be ahead" "$DOC" || \
  fail "missing fresh-peer-ahead invariant"

grep -q "technically plausible and correctly scoped" "$DOC" || \
  fail "missing technical assessment"

grep -q "Residual risks" "$DOC" || \
  fail "missing residual risk section"

grep -q "Do not classify this as" "$DOC" || \
  fail "missing non-claim boundary"

grep -q '"claims_audit": false' "$JSON" || \
  fail "audit non-claim missing"

grep -q '"claims_certification": false' "$JSON" || \
  fail "certification non-claim missing"

grep -q '"claims_consensus_correctness": false' "$JSON" || \
  fail "consensus non-claim missing"

grep -q '"claims_wallet_safety": false' "$JSON" || \
  fail "wallet non-claim missing"

grep -q '"claims_binary_safety": false' "$JSON" || \
  fail "binary non-claim missing"

grep -q '"claims_project_100_percent_complete": false' "$JSON" || \
  fail "100 percent non-claim missing"

grep -q "cannot be honestly closed by a local Termux command alone" "$STATUS" || \
  fail "anti-fake-100 boundary missing"

ok "WVP-REVIEW-001 maintainer assessment present"
ok "Fresh-peer-ahead invariant recorded"
ok "Residual risks recorded"
ok "Non-claims preserved"
ok "Fake-100 boundary preserved"
