# AUNEYA v1.21 — Differential Cryptographic Rejection

Status: experimental, offline, non-value WVP/AUNEYA research.

No published v1.21 release is implied.

## Objective

Harden the existing WVP/AUNEYA cryptographic evidence
verification stack against malformed input, tampering
and disagreements between independent implementations.

## Implementation

An authentic externally pinned v1.12 capsule is checked
against the existing v1.18 dual-runtime evidence contract
and the v1.20 wire profile.

The campaign generates over 100 deterministic attack cases.

Attack classes include:

- Existing v1.19 adversarial tests.
- Sequence type and boundary manipulation.
- Research chain identity modification.
- SHA-256 commitment modification.
- Invalid quorum structures.
- Invalid predecessor structures.
- Unknown JSON properties.
- Noncanonical JSON framing.
- Signed anchor corruption.
- Signed keeper receipt corruption.

Every mutation receives a fresh SHA-256 digest.

Both Python and Node.js must explicitly reject every attack.

Unexpected acceptance, runtime disagreement, crashing,
source mutation or exhaustion of the runtime budget
causes the campaign to fail.

## Termux reproduction

Run:

    python3 -m unittest discover -s tests -p test_auneya_guard_v121.py -v

    python3 tools/readme_truth.py --check

Existing authentic capsule verification requires
an independently supplied expected capsule SHA-256.

## Security boundaries

This is local differential software verification.

It does not establish:

- Independent physical witness devices.
- Independent operator identity.
- Independent remote storage.
- Global trusted time.
- Sybil resistance.
- Network consensus.
- Public production P2P networking.
- Independent security auditing.
- Legal authorization.
- Mainnet readiness.
- Economic activation.

Gate 3 remains partially implemented.

Gate 4 remains incomplete.

Gate 5 remains incomplete.

Gate 6 remains blocked.

No token or economic activation.

## Next engineering priority

Conduct real physical-device acceptance using two
independently controlled Termux devices with separately
maintained trust pins and high-water evidence.

Record real rollback, outage, recovery, signed recipient
ACK and sanitized evidence results.

Local simulations cannot prove independent devices.
