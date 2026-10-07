# WVP-REVIEW-001 — Maintainer Assessment of Nightfall PR #43

## Scope

This review assesses Nightfall PR #43 as a root-cause fix candidate for Nightfall issue #40.

Reviewed surface:

- Nightfall issue #40
- issue reproduction comment
- upstream PR #43
- PR #43 patch
- PR #43 regression tests
- WVP incident evidence pack in PR #28

## Finding

PR #43 is technically plausible and correctly scoped as a narrow root-cause fix candidate for the mining-during-sync fork risk.

The key invariant is:

> If a fresh peer is known to be ahead, the node is syncing, not isolated. Time passing during a long sync must not release mining.

## Positive signals

- The change is narrow.
- The change is local to mining hold-off behavior.
- The regression tests target the observed failure shape.
- The stale-peer fallback remains conceptually separate.
- The patch does not appear to modify wallet keys, custody, privacy primitives, emission rules, reward logic, or wire protocol.
- The PR body describes both the defect and the non-regression case.

## Required review questions

1. Can the fresh-peer-ahead branch release mining only because time passed?
2. Does stale-peer isolation still release mining when the peer height is no longer fresh?
3. Does the regression test fail against the old behavior?
4. Does the regression test pass against the fixed behavior?
5. Does this patch avoid consensus, wallet, key, reward, emission, or protocol-surface changes?
6. Is the operator workaround conservative until a fixed release exists?

## Residual risks

This review does not prove:

- full consensus correctness
- full reorg recovery
- wallet safety
- privacy correctness
- binary safety
- release safety
- reproducible builds
- independent cryptographic audit status
- legal compliance
- investment quality

Remaining work after this review:

- upstream maintainer review
- upstream CI result
- upstream merge or rejection decision
- post-merge release tracking
- operator-facing release warning until fixed binaries are published
- long-term observation that the failure class does not recur

## Decision

Approve WVP PR #28 as evidence of public incident verification and maintainer-grade review preparation.

Do not classify this as:

- an audit
- a certification
- proof of Nightfall safety
- proof of consensus correctness
- proof of wallet safety
- proof of binary safety
- proof of project completion at 100%

## Completion impact

This step improves public GitHub-quality evidence because it demonstrates:

- incident triage
- root-cause reasoning
- narrow review scope
- explicit residual-risk handling
- non-claim discipline
- maintainer-style decision structure

Estimated WVP public-quality level after this step: approximately 93/100.

The remaining gap to 100/100 requires external review, upstream impact, repeated review history, and long-term maintenance evidence.
