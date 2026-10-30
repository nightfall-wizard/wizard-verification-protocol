# AUNEYA/WVP Engineering Roadmap

Status: Post-v1.5 research development.

No mainnet or economic activation is authorized.

## GATE 1 — Authenticated Peer Evidence v1.6

Implementation status:
Local research capability implemented.

Requirements:

- Canonical framed messages.
- Ed25519 signature verification.
- Independently pinned identities.
- Bounded resource consumption.
- Research network domain separation.
- Persistent replay sequence.
- Atomic SQLite transactions.
- Real cryptographic tests.
- Adversarial failure injection.

Acceptance evidence:

- Passing local regression tests.
- Passing GitHub Actions checks.
- Reviewed source diff.
- Reproducible signed test vectors.

This gate does not prove a functioning peer-to-peer network.

## GATE 2 — Actual Peer Transport

Status:
NOT IMPLEMENTED.

Requirements:

- Explicit identity enrollment.
- Public-key rotation.
- Public-key revocation.
- Authenticated transport.
- Local socket test harness.
- Controlled second-device experiments.
- Read deadlines.
- Connection limits.
- Rate limits.
- Input budgets.
- Backpressure.
- Forged-peer rejection.
- Slow-reader tests.
- Message-flood tests.
- Reproducible packet traces.

## GATE 3 — External Replay Anchors

Status:
NOT IMPLEMENTED.

Requirements:

- Externally retained monotonic checkpoints.
- Independently verified state commitments.
- Crash recovery.
- Ledger migration procedures.
- Clock-fault testing.
- Storage rollback testing.
- Independent state restoration testing.

Local SQLite alone is insufficient for network-wide replay resistance.

## GATE 4 — Public Technical Reproducibility

Status:
INCOMPLETE.

Requirements:

- Machine-readable WVP acceptance evidence.
- Cross-implementation signed test vectors.
- High unsigned 64-bit integer interoperability.
- Deterministic verification outcomes.
- Stable normative schemas.
- Versioned formal protocol whitepaper.
- Independently reproducible test reports.
- Independent maintainer/operator reviews.

## GATE 5 — External Validation

Status:
NOT COMPLETED.

Requirements:

- Independent physical-device experiments.
- Independent cryptographic review.
- Privacy assessment.
- Abuse-resistance review.
- Legal assessment.
- Economic model review.
- Independent security audit.
- Governance approval.

## GATE 6 — Production Decision

Status:
BLOCKED.

Production deployment requires explicit authorization.

No automated promotion to mainnet.

No silent token issuance.

No unreviewed economic activation.

Every proposed release must distinguish:

1. Research implementation.
2. Tested technical capability.
3. Reviewed capability.
4. Published software release.
5. Independently audited production system.

Those categories are not interchangeable.
