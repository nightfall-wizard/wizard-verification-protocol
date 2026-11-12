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

## v1.12 Portable quorum capsules and recipient high-water floors

Status: Experimental implementation only.

Implemented:

- Portable canonical quorum evidence.
- Strict bounded resource consumption.
- Separately configured signer pins.
- Existing v1.11 signature validation.
- Deterministic WVP classification.
- Atomic recipient high-water floors.
- Contiguous signed predecessor checks.
- Replay and same-height conflict rejection.
- Adversarial cryptographic regression tests.
- Automated GitHub Actions checks.

Not completed:

- Independent physical-device experiments.
- Independent external retention certification.
- Operator-diversity verification.
- Remote outage recovery experiments.
- Compromised-key recovery.
- Independent protocol audit.

Gate 3 remains PARTIALLY IMPLEMENTED.
Gate 4 remains INCOMPLETE.
Gate 5 remains NOT COMPLETED.
Gate 6 remains BLOCKED.

No mainnet or economic activation is authorized.

## Independent project and next Gate 3 milestone

WVP/AUNEYA is independently led by nightfall-wizard, not owned, operated or governed by nightfallcoin.org or any external crypto project. See [governance](../PROJECT-INDEPENDENCE.md). The next technical priority is [real-device Gate 3 acceptance](AUNEYA-GATE3-DEVICE-ACCEPTANCE.md). No mainnet or economic activation.

## v1.13 — Recipient-signed Gate 3 acceptance

Status: Experimental research implementation.

Implemented:

- Independently pinned recipient signatures.
- Ed25519 acceptance statements.
- Portable capsule commitments.
- Signed anchor commitments.
- Recipient trust-policy commitments.
- Recipient high-water floor commitments.
- Canonical bounded evidence.
- Adversarial regression tests.
- Automated GitHub CI.
- Deterministic README integration.

Not completed:

- Independent physical-device acceptance.
- Independently certified external retention.
- Remote outage experiments.
- Signing-key recovery.
- Independent protocol replication.
- Independent security review.

Gate 3: PARTIALLY IMPLEMENTED.
Gate 4: INCOMPLETE.
Gate 5: NOT COMPLETED.
Gate 6: BLOCKED.

No public network or economic activation.

## v1.14 — Independent offline recipient-history audit

Status: Implemented as experimental, non-value offline research tooling.

- Complete v1.12 signed multi-keeper quorum is independently re-verified.
- Each v1.13 recipient ACK is independently signature/pin-verified.
- Recipient and quorum commitments are compared exactly.
- Signed predecessor, contiguous sequence, replay and duplicate rejection.
- External latest ACK SHA-256 must be supplied out of band.
- No state mutation during verification; optional exclusive private report.
- Real Ed25519 two-sequence regression tests and CI.
- Deterministic README evidence synchronization.

Gate 3: PARTIALLY IMPLEMENTED. A pin stored beside a compromised producer
is insufficient to prove independent retention. Physical second-device
acceptance, outage/rollback, recovery and independent review remain open.

Gate 4: INCOMPLETE.
Gate 5: NOT COMPLETED.
Gate 6: BLOCKED.

No public P2P, mainnet or economic activation.

See AUNEYA-GATE3-OFFLINE-AUDIT-V1.14.md.

## v1.15 — Independent Cross-Language Recipient ACK Verification

Status: Experimental non-value research.

Implemented:

- Independent Node.js Ed25519 recipient ACK verification.
- Python/Node cross-language conformance.
- Canonical lossless JSON verification.
- Large integer interoperability.
- Deterministic signed public test vectors.
- Independent recipient public-key pin checking.
- Externally supplied latest ACK head checking.
- Optional capsule commitment verification.
- Optional recipient high-water commitment verification.
- Adversarial regression tests.
- Dedicated GitHub Actions CI.

Remaining work:

- Independent full-quorum cross-language verification.
- Normative schemas.
- Real independent physical-device experiments.
- External retention validation.
- Remote outage and rollback recovery experiments.
- Independent security review.

Gate 3: PARTIALLY IMPLEMENTED.
Gate 4: INCOMPLETE.
Gate 5: NOT COMPLETED.
Gate 6: BLOCKED.

No public network activation.
No mainnet activation.
No economic activation.

Reference:
AUNEYA-GATE3-CROSS-LANGUAGE-V1.15.md.

## v1.16 — Independent full-quorum cross-language verification

Status: experimental non-value research.

A separate Node.js implementation re-validates v1.12 signed quorum
capsules and the exact v1.11 WVP report commitment, with optional
v1.15 ACK binding.

Signed predecessor continuity, full pin checking and adversarial
Python/Node regression tests are included.

Remaining engineering requirements:

- Normative cross-implementation schemas.
- Larger-capsule parser parity.
- Independent physical-device acceptance.
- External durable retention.
- Real outage and rollback evidence.
- Trusted-time design.
- Independent protocol and security review.

Gate 3: PARTIALLY IMPLEMENTED.

Gate 4: INCOMPLETE.

Gate 5: NOT COMPLETED.

Gate 6: BLOCKED.

No mainnet, public-network launch or economic activation.

Reference: AUNEYA-GATE3-FULL-QUORUM-V1.16.md.

## v1.17 research — dual-runtime quorum acceptance

Cryptographic Python/Node quorum agreement and deterministic WVP evidence.
Independent devices, external retention and audits are still missing;
no mainnet or economic activation is authorized.

## v1.18 — Offline dual-runtime evidence contract (research)

Gate 4 gains a canonical machine-readable report with an exact JSON Schema,
strong typed non-claims, SHA-256 links, deterministic re-verification and
adversarial negative tests.

This is not protocol consensus standardization.

Gate 3 remains PARTIALLY IMPLEMENTED pending real two-device acceptance,
independent retention and rollback/recovery experiments.

Gate 4 remains INCOMPLETE pending independent replication, normative wire
schemas and outside review.

Gate 5 is NOT COMPLETED.

Gate 6 remains BLOCKED.

See [v1.18 contract](AUNEYA-GATE4-DUAL-EVIDENCE-V1.18.md).

## v1.19 — Deterministic adversarial dual-runtime conformance (research)

Implemented: Python and Node.js independently reject 15 deterministically
mutated quorum capsules, including forged signed records and untrusted receipt
substitution. Each attack is individually rehashed, so cryptographic/parser
checks rather than an old external hash must reject it. A reproducible WVP
report records case hashes and two explicit rejection results. Dedicated CI and
README evidence integration verify the regression suite.

Gate 3 remains PARTIAL: separate real devices and external durable anchors
remain unproven. Gate 4 remains INCOMPLETE: normative wire schemas, independent
reproduction and independent review are outstanding. Gates 5/6 remain blocked.
No network, token, audit or economic activation occurs.

See [v1.19 conformance](AUNEYA-GATE4-ADVERSARIAL-V1.19.md).

## v1.20 candidate wire conformance

Bounded structural schema, genuine dual-runtime Ed25519 checks,
15 rehashed adversarial negatives and deterministic report.
Gate 3 partial: two independently operated devices still missing.
Gate 4 incomplete: outside replication and normative review missing.
Gates 5/6 blocked; no production/economic activation.

## v1.21 — Deterministic Differential Rejection Research

Status: experimental, non-value offline implementation.

Implemented:

- 100+ deterministic adversarial mutations.
- Real cryptographically signed baseline evidence.
- Python and Node.js verification agreement.
- Fail-closed rejection requirements.
- Independent expected SHA-256 commitment input.
- Deterministic machine-readable results.
- Runtime resource budgets.
- CI integration.
- Generated README traceability.
- Regression tests.

Gate 3 remains partially implemented.

Gate 4 remains incomplete.

Gate 5 remains incomplete.

Gate 6 remains blocked.

Next external engineering milestone:

Real second-device acceptance, independent high-water
retention, rollback/recovery experiments, signed recipient
ACK preservation and independently reviewed test evidence.

No production network or economic activation.

See AUNEYA-GATE4-DIFFERENTIAL-V1.21.md.
