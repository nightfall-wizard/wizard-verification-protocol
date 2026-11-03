# AUNEYA/WVP v1.15 — Independent Recipient ACK Interoperability

Status: Experimental, non-value research.

Gate 3: PARTIALLY IMPLEMENTED.
Gate 4: INCOMPLETE.
Gate 5: NOT COMPLETED.
Gate 6: BLOCKED.

## Objective

Version 1.15 introduces independent Node.js verification
of v1.13 recipient-signed Gate 3 acknowledgement evidence.

The verifier does not use Python for signature verification.

It uses:

- Native Node.js Ed25519 cryptography.
- Existing v1.4 lossless JSON parsing.
- Strict canonical JSON byte verification.
- Independently configured recipient public-key pins.
- Externally supplied ACK head commitments.
- Optional capsule commitment checking.
- Optional high-water floor commitment checking.
- Bounded input parsing.
- Fail-closed validation.

## Cryptographic binding

The original v1.13 signature domain is preserved:

AUNEYA/WVP:GATE3-RECIPIENT-ACK:V1.13

The exact domain includes a terminating NUL byte.

The signature covers canonical signed body bytes.

No protocol signature format is changed.

## Independent trust inputs

The verifier requires:

1. A signed recipient ACK.
2. The recipient public-key PEM.
3. The independently obtained public-key SHA-256.
4. The independently retained latest ACK SHA-256.

The expected latest ACK hash must originate outside
the producer's potential rollback domain.

A digest copied from the same compromised storage
does not constitute independent retention.

## Command

node tools/auneya/auneya_gate3_interop_v115.js \
  --receipt "$HOME/.auneya-keeper/ack.json" \
  --recipient-public "$HOME/.auneya-keeper/recipient-public.pem" \
  --pin "$INDEPENDENT_RECIPIENT_PIN" \
  --expected-head "$INDEPENDENT_ACK_HEAD" \
  --capsule "$HOME/.auneya-keeper/capsule.json" \
  --floor "$HOME/.auneya-keeper/floor.json"

The public-key file must be mode 0600 and reside
inside a directory with mode 0700.

The --capsule and --floor arguments are optional.

## Cross-language conformance

The deterministic vectors use a public RFC 8032
Ed25519 test seed.

That seed is exclusively for public testing.

It must never be used as a real recipient identity.

The vectors cover:

- Signature domain separation.
- Canonical bytes.
- Exact PEM SHA-256 fingerprint.
- Complete ACK SHA-256.
- Large integer sequence 9007199254740993.
- Python and Node.js verification agreement.

## Adversarial rejection

Tests cover:

- Incorrect expected ACK head.
- Incorrect recipient public-key pin.
- Altered signed body.
- Forged Ed25519 signature.
- Unsupported security claims.
- Noncanonical JSON.
- Duplicate JSON keys.
- Capsule substitution.
- High-water floor substitution.
- Symbolic links.
- Unsafe key permissions.
- Excessively large ACKs.

## Verification boundary

An authenticated ACK proves that the matching
recipient private key signed its canonical body.

It does not independently prove that the
underlying v1.12 multi-keeper quorum is authentic.

For the complete v1.12 quorum and history,
run the Python v1.14 offline auditor.

external_head_matched means that the supplied
digest matches the received ACK.

It does not prove that the caller actually
retained that digest on a separate device.

quorum_independently_verified remains false.

independent_devices_proven remains false.

external_retention_proven remains false.

economic_activation remains false.

No public network, consensus, token issuance,
mainnet activation or production approval.

## Reproduction

python3 -m unittest discover \
  -s tests \
  -p 'test_auneya_gate3_interop_v115.py' \
  -v

python3 -m unittest discover \
  -s tests \
  -p 'test_auneya_gate3_audit_v114.py' \
  -v

python3 tools/readme_truth.py --check

## Remaining acceptance criteria

Two genuinely separate physical devices.

Independent recipient-controlled storage.

Independently enrolled cryptographic trust roots.

Actual artifact transfer.

Actual producer rollback experiments.

Outage and recovery experiments.

Independent reviewer validation.

Public sanitized reproducibility evidence.

Independent security and privacy assessment.

The whitepaper remains a research draft.

## Legacy signature domain compatibility

The existing v1.13 recipient ACK signer calls the v1.9
anchor cryptographic helper.

That helper itself prepends the v1.9 external-anchor
domain to the supplied v1.13 message.

The actual Ed25519 signed message is the byte
concatenation:

1. ASCII `AUNEYA/WVP:EXTERNAL-ANCHOR:V1.9` and NUL.
2. ASCII `AUNEYA/WVP:GATE3-RECIPIENT-ACK:V1.13` and NUL.
3. Canonical ASCII JSON of the exact signed ACK body.

Both historical domains must be verified in this order.

No existing v1.13 signature or serialization is changed.

A signature created with only one domain is NOT valid
v1.13 evidence.
