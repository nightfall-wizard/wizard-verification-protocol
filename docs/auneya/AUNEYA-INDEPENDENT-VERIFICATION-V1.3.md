# AUNEYA/WVP v1.3 — Independent JavaScript Verification

Status: additive offline non-value research.

Not a protocol release.

## Purpose

WVP v1.2 exports canonical signed evidence bundles.

Its exporter and verifier share Python dependencies.

v1.3 adds a second-language Node.js implementation
without Python verifier dependencies, SQLite archive
access, or external npm packages.

## Security checks

The independent implementation checks:

- Independently supplied SHA-256 anchors.
- Private regular files and directories.
- Canonical manifests and evidence capsules.
- Exact capsule hashes and sizes.
- Complete declared file lists.
- Registry checkpoint hashes and identity histories.
- Ed25519 public-key fingerprints.
- Challenge identity and claimed observation times.
- Nightfall chain and protocol identity.
- Domain-separated Ed25519 signatures.
- Archived batch report reconstruction.
- Federation report reconstruction.
- Duplicate observations.
- Signer contradictions.
- Duplicate public-key identities.
- Federation commitments.

## Command

node tools/auneya/auneya_independent_v13.js verify \
  --bundle PRIVATE_V12_DIRECTORY \
  --pin INDEPENDENT_CHECKPOINT_SHA256 \
  --challenge-sha256 INDEPENDENT_CHALLENGE_SHA256 \
  --expected-manifest-sha256 INDEPENDENT_MANIFEST_SHA256

The three anchors must be obtained independently
from a trusted source.

## Differential tests

python3 -m unittest discover \
  -s tests \
  -p 'test_auneya_independent_v13.py' \
  -v

The suite generates signed evidence using the
existing Python implementation.

It requires positive-result equivalence and
adversarial rejection in both implementations.

WVP Required Checks executes the new suite.

## Precision boundary

JavaScript integers outside the exact safe-integer
range are rejected.

Consequently, full coverage of all valid Python
v1.2 integer representations is not yet claimed.

Future work must introduce lossless integer parsing.

## Trust boundary

This verification does not prove:

- Witness operator independence.
- Sybil resistance.
- Historical observation freshness.
- Blockchain consensus.
- Actual blockchain ownership.
- Production readiness.
- Independent security audit.
- Protection against all filesystem races.

It creates no wallet, token, real reward,
transferable value or mainnet.

No market value is promised.

Legal review remains necessary before any
future token launch or value communication.

## Next engineering steps

Authenticated P2P transport, replay expiry,
resource budgets, adversarial multi-device
experiments and independent external review.
