# AUNEYA/WVP Engineering Roadmap v1.9

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
PARTIALLY IMPLEMENTED (v1.8 authenticated loopback receipts).

Implemented:

- Bounded localhost TCP.
- Signed v1.6 envelope admission.
- Private pinned peer enrollment.
- Operator-controlled rotation and revocation.
- Strict framing.
- Request read deadlines.
- Local persistent replay protection.
- Adversarial TCP regression tests.

Additional v1.8 capability:

- Ed25519-signed responder receipts.
- Independent responder-key pinning.
- Cryptographic request/response binding.
- Fresh client nonces.
- Authenticated status verification.
- Adversarial forged-response tests.

Not implemented:

- Authenticated remote transport.
- Independent physical-device tests.
- Public peer discovery.
- Network-wide rate limiting.
- Independently trusted time.
- End-to-end packet trace certification.


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
PARTIALLY IMPLEMENTED (v1.9 operator-signed offline replay snapshots).

v1.9 checks SQLite replay history, signs a canonical complete state digest,
verifies externally supplied checkpoints, and rejects historical rollback.

Independent checkpoint retention, remote witness storage, availability
and anti-rollback high-water marks are NOT implemented.

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


## v1.8 Security Boundary

AUNEYA v1.8 authenticates local responder
acknowledgments.

It does not prove independent physical devices,
public network security, global consensus,
external storage integrity or trusted time.

The next priority is Gate 3:
externally anchored monotonic replay state.

Reference:

AUNEYA-AUTHENTICATED-RECEIPTS-V1.8.md

## v1.9 next security checkpoint

Operator-signed offline checkpoint tooling is implemented
as a Gate 3 research sub-step.

See AUNEYA-EXTERNAL-REPLAY-ANCHORS-V1.9.md.

Independent storage and cross-device tests remain blocked
pending real external validation.

No claims of production readiness or economic activation.


## v1.10: independent offline keeper high-water (research)

Implemented:

- Separate signer-bound keeper store.
- Chained authenticated witness receipts.
- Monotonic checkpoint admission.
- External high-water receipt checking.
- Database rollback regression tests.
- Adversarial signature and replay tests.
- Interrupted receipt export recovery.

Not completed:

- Independent physical-device trials.
- Remote witness availability.
- Independent retention certification.
- Rollback immunity without an outside receipt.
- Trusted time.
- Signing-key compromise recovery.
- Public reproducibility validation.
- Independent security audit.

Gate 3 remains partially implemented.

Reference:
AUNEYA-INDEPENDENT-HIGHWATER-V1.10.md.

## v1.11: Authenticated Multi-Keeper Quorum

Status: Implemented as offline research capability.

New capabilities:

- Multiple authenticated keeper receipts.
- Explicit minimum signer quorum.
- Independently configured signer fingerprints.
- Deterministic WVP verification report.
- Signed checkpoint predecessor continuity.
- Signed keeper receipt predecessor continuity.
- Detection of supplied same-height equivocation.
- Adversarial cryptographic regression tests.
- Automated GitHub Actions checks.

Source:

tools/auneya/auneya_quorum_v111.py

Specification:

docs/auneya/AUNEYA-MULTI-KEEPER-QUORUM-V1.11.md

Tests:

tests/test_auneya_quorum_v111.py

Remaining Gate 3 work:

- Independent physical-device experiments.
- Authenticated external retention.
- Durable external high-water floors.
- Real remote outage experiments.
- Signing-key compromise recovery.
- Independent operator validation.
- Real-world equivocation detection experiments.

Gate 3 remains PARTIALLY IMPLEMENTED.

Gate 4 remains INCOMPLETE.

Gate 5 remains NOT COMPLETED.

Gate 6 remains BLOCKED.

No production or economic activation is authorized.
