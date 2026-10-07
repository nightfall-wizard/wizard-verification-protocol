# WVP Incident Review — Nightfall Issue #40 / PR #43

## Summary

This WVP review captures public evidence for Nightfall issue #40 and PR #43.

The reviewed incident is a mining-during-sync liveness failure where a node can mine while still behind a fresh peer, causing or deepening a private fork.

## Finding

PR #43 is the correct next review target because it addresses the root-cause candidate directly:

> Once a fresh peer is known to be ahead, the node is syncing, not isolated.

The catch-up timeout must not release mining in that branch.

## Positive signals

- The patch is narrow.
- The change is local to mining hold-off behavior.
- The stale-peer fallback remains conceptually separate.
- Regression coverage targets the observed failure shape.
- The PR does not appear to alter wallet keys, rewards, wire protocol, or emission rules.

## Remaining risk

This does not prove:

- full consensus correctness
- full reorg recovery
- wallet safety
- privacy correctness
- release safety
- binary reproducibility
- independent audit status

## Correct ordering

1. Review and validate PR #43 first.
2. Treat PR #42 as recovery-only follow-up.
3. Keep PR #9 separate as reorg-liveness hardening.
4. Do not merge broad diagnostic or feature work into this incident fix.

## WVP position

This is a strong candidate for a real security-adjacent maintainer-quality review.

The highest-value Nightfall Wizard action is not more feature code. It is public, adversarial, reproducible incident verification.
