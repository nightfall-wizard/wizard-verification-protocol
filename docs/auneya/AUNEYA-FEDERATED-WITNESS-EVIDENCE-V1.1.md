# AUNEYA/WVP v1.1 — Offline Federated Witness Evidence

Status: additive offline research feature.

No mainnet, token, value or reward.

## Purpose

Federate independently archived signed witness evidence.

AUNEYA v0.9 verifies self-contained signed capsules.
v1.0 provides atomic local archive storage.
v1.1 adds deterministic cross-capsule reconciliation.

## Verification

The implementation:

1. Requires independently retained checkpoint pins.
2. Requires an expected challenge SHA-256.
3. Verifies canonical archived evidence.
4. Reuses existing Ed25519 verification.
5. Rejects wrong checkpoint anchors.
6. Rejects wrong challenge identifiers.
7. Deduplicates identical capsules.
8. Deduplicates identical signed observations.
9. Detects contradictory signed status claims.
10. Detects public-key reuse across identities.
11. Stores capsules transactionally in SQLite.
12. Rechecks stored capsules when generating reports.
13. Produces deterministic federation commitments.

Maximum: 16 capsules per challenge.

## Import

python3 tools/auneya/auneya_federation_v11.py import \
  --store private-federation.sqlite \
  --capsule operator-batch.json \
  --pin YOUR_INDEPENDENT_CHECKPOINT_SHA256 \
  --challenge-sha256 EXPECTED_CHALLENGE_SHA256

## Report

python3 tools/auneya/auneya_federation_v11.py report \
  --store private-federation.sqlite \
  --pin YOUR_INDEPENDENT_CHECKPOINT_SHA256 \
  --challenge-sha256 EXPECTED_CHALLENGE_SHA256

The expected challenge hash must originate from a
separately trusted original challenge document.

It is calculated as:

sha256(v5.canonical(challenge))

## Security boundary

Signed statements are authenticated, not certified true.

Multiple public keys do not establish independent operators.

This implementation does not prove:

- historical freshness;
- physical device independence;
- human identity independence;
- Sybil resistance;
- consensus validity;
- Nightfall chain correctness;
- actual observation truth;
- distributed agreement;
- mainnet readiness;
- economic security.

An independent checkpoint pin remains a trust requirement.

Local database compromise and physical storage failure
remain outside the solved threat model.

This version does not implement external P2P networking.

## Non-value boundary

No real token.
No real wallet.
No real rewards.
No asset transfers.
No mainnet activation.
No investment claim.

## Tests

python3 -m unittest discover \
  -s tests \
  -p 'test_auneya_federation_v11.py' -v

Existing v0.8–v1.0 tests must continue passing.
