#!/usr/bin/env bash
set -Eeuo pipefail

DIFF="artifacts/nightfall/nightfall-pr-043.diff"
EVIDENCE="reports/nightfall/incident-040-pr043-evidence.json"
REPORT="reports/nightfall/incident-040-pr043-review.md"
THREAT="docs/review/NIGHTFALL-INCIDENT-040-THREAT-MODEL.md"

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

ok() {
  echo "OK: $*"
}

[ -s "$DIFF" ] || fail "missing PR #43 diff"
[ -s "$EVIDENCE" ] || fail "missing evidence JSON"
[ -s "$REPORT" ] || fail "missing review report"
[ -s "$THREAT" ] || fail "missing threat model"

grep -q "No catch-up escape here on purpose" "$DIFF" || \
  fail "diff does not contain catch-up escape boundary"

grep -q "a_fresh_ahead_peer_holds_mining_however_long_the_sync_takes" "$DIFF" || \
  fail "missing long-sync fresh-peer regression test"

grep -q "an_ahead_peer_going_stale_still_releases_mining" "$DIFF" || \
  fail "missing stale-peer release regression test"

grep -q "Some(195_920)" "$DIFF" || \
  fail "missing expected wait distance assertion"

grep -q '"claims_audit": false' "$EVIDENCE" || \
  fail "evidence must reject audit claim"

grep -q '"claims_consensus_correctness": false' "$EVIDENCE" || \
  fail "evidence must reject consensus-correctness claim"

grep -q "full reorg recovery" "$REPORT" || \
  fail "report must state residual reorg-recovery risk"

grep -q "If a peer is fresh and ahead" "$THREAT" || \
  fail "threat model must state fresh-peer-ahead invariant"

ok "PR #43 incident-verification evidence is present"
ok "Regression markers found"
ok "Non-claims preserved"
ok "Threat model present"
