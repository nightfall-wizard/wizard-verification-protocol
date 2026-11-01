# AUNEYA/WVP v1.11

## Authenticated Multi-Keeper Quorum

Status: Experimental research.

Production readiness: Not established.

Economic activation: Disabled.

Independent audit: Not completed.

## 1. Objective

AUNEYA v1.11 extends the existing v1.9/v1.10
checkpoint architecture with authenticated
multi-keeper evidence verification.

The implementation validates:

- Ed25519-signed anchor checkpoints.
- Ed25519-signed keeper receipts.
- Independently pinned public keys.
- Distinct cryptographic signer identities.
- Minimum quorum size.
- Canonical JSON encoding.
- Exact research-chain identity.
- Monotonic checkpoint sequences.
- Signed predecessor relationships.
- Observed conflicting same-height checkpoints.
- Observed conflicting keeper receipts.

## 2. Trust model

The verifier consumes an operator-pinned trust
policy and a separate evidence bundle.

Cryptographic authentication of public-key pins
must happen outside the evidence bundle.

A trust policy stored beside the evidence
does not independently establish trust.

## 3. Trust policy

Format:

auneya-quorum-trust-v1.11

Required fields:

- format
- chain_id
- anchor_public
- anchor_pin
- threshold
- keepers

Each keeper has:

- pin
- public

The threshold must be between 2 and 16.

The number of configured keepers must be
at least the threshold and at most 16.

All keeper pins must be unique.

The producer signer cannot also count as
a keeper signer.

## 4. Evidence bundle

Format:

auneya-quorum-evidence-v1.11

Required fields:

- format
- anchor
- receipts

Each receipt reference has:

- pin
- path

Every supplied receipt is authenticated.

Unknown or duplicate keeper identities
are rejected.

A bundle with insufficient valid receipts
is rejected.

## 5. Canonical encoding

Input documents must be one canonical
ASCII JSON line followed by LF.

Encoding uses:

- Sorted object keys.
- No unnecessary whitespace.
- Integer-only numeric values.
- No duplicate JSON keys.
- No trailing JSON documents.

Private input files require mode 0600.

Private input directories require mode 0700.

Existing v1.9/v1.10 cryptographic verification
remains authoritative.

## 6. Continuity

Checkpoints above genesis require an
immediately preceding signed bundle.

Current and previous evidence must bind:

- The same chain.
- Consecutive sequence numbers.
- The preceding anchor hash.
- Increasing message count.
- Consecutive keeper receipt numbers.
- Each keeper's preceding receipt hash.
- Each keeper's preceding anchor hash.

Changing quorum membership requires a
separate enrollment and rotation procedure.

## 7. Equivocation

An optional comparison checks two supplied
bundles at the same chain and height.

The verifier rejects:

- Conflicting signed anchor hashes.
- Conflicting same-height receipt hashes
  from an overlapping pinned signer.

Only supplied contradictions can be detected.

This does not create global transparency
or prove the absence of hidden forks.

## 8. Deterministic report

Report format:

wvp-auneya-quorum-verdict-v1.11

The report contains:

- Research chain identity.
- Checkpoint sequence.
- Signed anchor digest.
- Message count.
- Verified keeper count.
- Required quorum.
- Sorted keeper receipt digests.
- Explicit security claim boundaries.

The same authenticated inputs produce
the same report.

## 9. CLI

Example:

python3 tools/auneya/auneya_quorum_v111.py \
  --trust /private/trust.json \
  --bundle /private/bundle-1.json

Subsequent checkpoint:

python3 tools/auneya/auneya_quorum_v111.py \
  --trust /private/trust.json \
  --bundle /private/bundle-2.json \
  --previous /private/bundle-1.json

Equivocation comparison:

python3 tools/auneya/auneya_quorum_v111.py \
  --trust /private/trust.json \
  --bundle /private/bundle-1.json \
  --compare /private/alternative-1.json

Optional:

--output /private/unique-report.json

The output file is created exclusively.

Existing reports are never silently overwritten.

## 10. Acceptance requirements

Acceptance requires:

1. Valid anchor signatures.
2. Valid keeper signatures.
3. Correct independently configured key pins.
4. Distinct signer keys.
5. Sufficient signed quorum.
6. Valid canonical framing.
7. Correct chain binding.
8. Valid supplied history continuity.
9. No observed equivocation.
10. Passing adversarial regression tests.

## 11. Explicit limitations

Different signing keys do not prove
different physical devices.

A quorum does not prove factual truth.

An operator controlling multiple keeper
private keys can simulate multiple identities.

A supplied predecessor is not necessarily
the globally latest checkpoint.

Without independent high-water retention,
a complete storage rollback may remain
undetected.

The verifier does not prove:

- Independent physical devices.
- Independent human operators.
- Remote data availability.
- Immutable external retention.
- Network-wide replay immunity.
- Sybil resistance.
- Trusted global time.
- Public P2P networking.
- Decentralized consensus.
- Economic security.
- Production readiness.

## 12. Roadmap

Gate 3:

Research capability expanded.

Still partially implemented.

Gate 4:

Deterministic machine-readable evidence
and adversarial tests added.

Independent interoperability remains open.

Gate 5:

Independent validation not completed.

Gate 6:

Production remains blocked.

No mainnet activation.

No token issuance.

No real economic rewards.

No transferability.

No independent security audit claimed.
