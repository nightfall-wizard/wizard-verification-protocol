# Nightfall Incident #40 / PR #43 Threat Model

## Scope

This document models the specific failure class reported in Nightfall issue #40 and the proposed fix in PR #43.

The reviewed failure class is:

> A node begins mining while it is still behind a fresh peer, creating or deepening a private fork during sync.

## Assets at risk

- canonical node liveness
- miner time and energy
- wallet balance perception during local fork state
- operator trust in `mining: true`
- network convergence confidence

## Failure path

1. Local node is behind the network.
2. A fresh peer reports a higher height.
3. The node remains in catch-up longer than `MAX_CATCHUP_WAIT_SECS`.
4. The old logic releases mining even though a fresh peer is still ahead.
5. Mining occurs on a stale historical local tip.
6. The node deepens a private fork.
7. Later peer chains do not connect cleanly to the local tip.
8. The node can become permanently stalled on a fork.

## Expected invariant

If a peer is fresh and ahead, the node is not isolated.

Therefore:

> Mining must remain blocked while a fresh peer is known to be ahead, regardless of catch-up duration.

## Correct isolation boundary

The catch-up escape is only safe after the peer height becomes stale.

Fresh peer ahead:

- block mining

Stale peer height:

- isolation fallback may release mining

## Non-claims

This document does not claim:

- Nightfall is safe
- PR #43 proves full consensus correctness
- PR #43 proves wallet safety
- PR #43 proves full reorg recovery
- this is an external audit
- this is legal, financial, or investment advice
