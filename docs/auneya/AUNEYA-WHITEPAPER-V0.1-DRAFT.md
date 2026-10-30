# AUNEYA: Provable Web Witness Protocol

## Whitepaper v0.1 — Technical Research Draft

**Status:** Research draft.

**Core:** Wizard Verification Protocol (WVP).

**Maintainer:** nightfall-wizard.

**Network:** Not launched.

**Economic activation:** Disabled.

**Independent audit:** Not completed.

This is not an approved final protocol specification or a public launch whitepaper.

## 1. Mission

Public digital claims should be checked using reproducible, bounded and cryptographically bound evidence rather than popularity or reputation.

WVP classifies what technical evidence establishes.

AUNEYA researches how multiple independent phones might witness and exchange evidence about lawful public digital claims.

The system does not claim to establish absolute truth.

## 2. Threat model

The design assumes potentially malicious participants.

Relevant adversarial conditions include:

- Forged peer messages.
- Manipulated observations.
- Replayed evidence.
- Local clock rollback.
- Storage rollback.
- Malicious peer identities.
- Sybil identities.
- Hostile message framing.
- Oversized inputs.
- Forged release metadata.
- Unavailable communication networks.
- Cross-implementation inconsistencies.
- Unexpected process termination.
- Interrupted database transactions.

Publicly accessible information must not automatically be treated as trustworthy.

Private or unlawfully accessed data is excluded.

## 3. Existing technical capabilities

### WVP

Release-reality verification.

Evidence classification.

Source/release distinction.

Negative test vectors.

Reproducibility and provenance boundaries.

### AUNEYA

v0.5:
Signed challenges.

v0.6:
Registry checkpoint binding.

v0.7:
Pinned observations.

v0.8:
Multi-witness evidence.

v0.9:
Canonical evidence archives.

v1.0:
Atomic local evidence archiving.

v1.1:
Federation research.

v1.2:
Portable evidence verification.

v1.3:
Independent Ed25519 verification.

v1.4:
Lossless cross-language interoperability.

v1.5:
Local temporal evidence admission.

v1.6:
Authenticated offline peer-envelope verification and sequential replay state.

Every capability remains subject to its documented limitations.

## 4. Evidence protocol

The conceptual processing pipeline is:

Lawful public claim

→ explicit verification challenge

→ independently pinned checkpoint

→ signed observations

→ signed receipts

→ canonical evidence capsule

→ multi-witness evidence bundle

→ independent cryptographic verification

→ local temporal admission

→ optional authenticated peer evidence envelope.

Evidence hashes must originate from independently trusted sources when independence is claimed.

Copying evidence and a corresponding digest from the same potentially compromised device does not create independent trust.

## 5. Identity model

An authenticated research peer must provide:

- Explicit sender identifier.
- Research chain identity.
- Independently pinned public key.
- Current epoch.
- Contiguous counter.
- Issuance timestamp.
- Expiration timestamp.
- Checkpoint hash.
- Challenge hash.
- Manifest hash.
- Valid Ed25519 signature.

The signed payload uses canonical ASCII JSON and protocol-specific domain separation.

A cryptographic public key does not establish physical device uniqueness or human identity.

## 6. Transport preparation

The initial peer envelope format uses:

- Four-byte network-order message length.
- Bounded canonical JSON payload.
- Ed25519 authentication.
- Explicit expected network identity.
- External SHA-256 anchors.
- Persistent local replay protection.

This implementation defines an offline verification boundary.

It does not constitute a functioning peer-to-peer network.

Actual network transport requires separate development and adversarial testing.

## 7. Replay security

For each sender and research chain, the receiver maintains:

- Last accepted epoch.
- Last accepted counter.
- Last accepted local clock value.
- Previously accepted challenge identifiers.
- Previously accepted manifest identifiers.

Updates are performed atomically.

Repeated challenges or manifests are rejected.

Out-of-order counters are rejected.

Local clock rollback is rejected relative to persisted receiver state.

Local persistence does not prevent an attacker controlling storage from restoring an older database.

Externally anchored state remains a future requirement.

## 8. Reproducibility

A technically credible implementation requires adversarial regression tests covering:

- Forged signatures.
- Modified signed payloads.
- Incorrect public-key pins.
- Incorrect research network identity.
- Invalid challenge anchors.
- Truncated message frames.
- Trailing bytes.
- Duplicate JSON fields.
- Oversized messages.
- Expired messages.
- Replayed counters.
- Reused evidence identifiers.
- Invalid epoch transitions.
- Local clock rollback.
- Atomic database failure recovery.

Successful local tests do not establish production security.

## 9. Consensus and decentralization

The current implementation does not establish:

- Final network consensus.
- Leader selection.
- Permissionless membership security.
- Privacy-preserving witness independence.
- Censorship resistance.
- Network-wide replay protection.
- Distributed recovery.
- Finality.
- Production interoperability.
- Independent validator agreement.

Multiple signatures alone do not establish decentralization.

## 10. Proposed economic architecture

The existing AUNEYA Charter documents these research parameters:

Maximum supply:
108,000,000 AUNEYA.

Smallest unit:
neya.

One AUNEYA:
1,000,000,000 neya.

Proposed genesis supply:
0.

Premine:
No.

ICO:
No.

Staking:
No.

Halving:
No.

Emission, reservoir depletion, maintenance rewards, fees and burns remain research concepts.

They require a complete specification, independent economic validation and legal assessment before any consideration of transferable economic activity.

No token is created by this document.

No value, return, reward, allocation or listing is promised.

## 11. Privacy requirements

Only public or lawfully accessible digital information belongs within the proposed verification scope.

Excluded activities include:

- Private-account monitoring.
- Private-message collection.
- Surveillance of private individuals.
- Access-control bypass.
- Credential theft.
- Unauthorized collection.
- Hacked data processing.
- Unlawful scraping.

Future network development must undergo independent privacy and abuse-resistance review.

## 12. Graduation requirements

Before production consideration:

1. Independent threat-model review.
2. Authenticated bounded peer transport.
3. Externally anchored replay state.
4. Trusted-time strategy.
5. Key rotation and revocation.
6. Privacy and abuse-resistance analysis.
7. Independent physical-device experiments.
8. Reproducible network traces.
9. Cross-language conformance testing.
10. Formal network consensus specification.
11. Economic model formalization.
12. Independent security audit.
13. Independent legal assessment.
14. Public governance review.
15. Explicit release authorization.

No one-command script satisfies all independent requirements.

## 13. Normative research references

AUNEYA-PROTOCOL-CHARTER.md

AUNEYA-PROVABLE-WEB-SCOPE.md

AUNEYA-ADVERSARIAL-INVARIANT-MATRIX-V0.1.md

AUNEYA-CHAIN-IDENTITY-GENESIS-BOUNDARY-V0.1.md

AUNEYA-TEMPORAL-ADMISSION-V1.5.md

AUNEYA-PEER-EVIDENCE-GATE-V1.6.md

This document remains a draft until reviewed and formally approved.


## 14. v1.7 local transport research update (non-normative)

AUNEYA v1.7 adds a bounded localhost-only TCP
test transport around unmodified v1.6 signed
envelope verification and durable local
replay protection.

Operator-pinned peer enrollment, rotation
and revocation are local administrative actions.

Only the inbound peer statement is
Ed25519-authenticated.

The response acknowledgment is not authenticated.

This is a Gate 2 sub-step, not a functional
public decentralized network.

Remaining Gate 2, 3, 4, 5 and 6 requirements
are not waived.

References:

AUNEYA-TRANSPORT-V1.7.md

AUNEYA-ROADMAP-V1.7.md
