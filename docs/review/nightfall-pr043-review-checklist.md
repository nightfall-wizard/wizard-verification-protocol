# Review Checklist — Nightfall PR #43

## PR

- Repository: `Instinctes/nightfall`
- PR: `#43`
- Title: `Do not mine while a fresh peer is known to be ahead`

## Required checks

- [ ] Fix is narrow.
- [ ] Fresh-peer-ahead branch cannot release mining only because time passed.
- [ ] Stale-peer fallback remains possible.
- [ ] No consensus rule change is introduced.
- [ ] No wallet/key handling change is introduced.
- [ ] No emission/reward change is introduced.
- [ ] Regression test fails against the old behavior.
- [ ] Regression test passes against the fixed behavior.
- [ ] Operator guidance remains conservative until release.
- [ ] Review avoids claiming audit or full correctness.

## Review verdict template

Technically plausible and correctly scoped.

The patch appears to address the most direct root-cause candidate for issue #40: mining was released during sync even though a fresh peer was still known to be ahead.

The change should remain narrow. It should not be merged as proof of full reorg recovery, wallet safety, or consensus correctness. It should be treated as a root-cause fix candidate requiring maintainer review, CI, and operational validation.
