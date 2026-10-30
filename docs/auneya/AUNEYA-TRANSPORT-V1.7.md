# AUNEYA/WVP v1.7 — Bounded Authenticated Loopback Transport

Status: additive local non-value research capability.

No public peer network.

## Protocol boundary

This module sends unmodified v1.6 signed envelopes
over loopback TCP.

Each connection sends one four-byte big-endian length
plus canonical JSON v1.6 frame, then performs a TCP
write half-close.

The receiver requires EOF after exactly one frame.

Frames are handed to the unchanged v1.6 Ed25519 gate
and atomic local SQLite replay ledger.

A local JSON acknowledgment is returned.

Acknowledgments are not signed or independently
authenticated.

## Resource limits

- Maximum JSON frame: 65,536 bytes.
- Complete request deadline: 2 seconds.
- Connection backlog: 8.
- Maximum connections per server invocation: 64.
- Only 127.0.0.1 loopback binding.
- Default idle exit: 10 seconds.
- Rejected requests consume connection budget.
- Serial request processing.
- Private policy and replay ledger.

The peer public-key SHA-256 fingerprint must originate
from an independently trusted source.

## Local Termux usage

Create a private directory:

    mkdir -p "$HOME/auneya-v17-private"
    chmod 700 "$HOME/auneya-v17-private"

Provide an independently verified peer public PEM file
with permissions 0600.

Enroll a trusted peer:

    python3 tools/auneya/auneya_transport_v17.py enroll \
      --policy "$HOME/auneya-v17-private/policy.json" \
      --key "$HOME/auneya-v17-private/peer.pem" \
      --key-sha256 INDEPENDENT_PEM_SHA256 \
      --sender phone-alpha \
      --chain-id auneya-research-v1 \
      --checkpoint-sha256 INDEPENDENT_CHECKPOINT_SHA256 \
      --challenge-sha256 INDEPENDENT_CHALLENGE_SHA256 \
      --manifest-sha256 INDEPENDENT_MANIFEST_SHA256

Start a local bounded receiver:

    python3 tools/auneya/auneya_transport_v17.py serve \
      --policy "$HOME/auneya-v17-private/policy.json" \
      --ledger "$HOME/auneya-v17-private/replay.sqlite" \
      --ready-file "$HOME/auneya-v17-private/ready.json" \
      --port 17017 \
      --max-connections 16

Send an already signed v1.6 frame:

    python3 tools/auneya/auneya_transport_v17.py send \
      --frame "$HOME/auneya-v17-private/frame.bin" \
      --port 17017

The signed frame must be generated independently.
No private production key is generated or committed.

## Key rotation

Use the rotate action with the same parameters
as enroll but a different independently pinned
public key.

Rotation does not reset the replay ledger.

Existing counter and epoch requirements remain.

## Revocation

    python3 tools/auneya/auneya_transport_v17.py revoke \
      --policy "$HOME/auneya-v17-private/policy.json"

Revocation blocks subsequent peer messages.

Network messages cannot enroll, rotate or revoke
trusted identities.

## Regression tests

    python3 -m unittest discover \
      -s tests \
      -p 'test_auneya_transport_v17.py' \
      -v

Tests cover:

- Real Ed25519 signatures.
- Real TCP loopback communication.
- SQLite replay persistence.
- Forged signatures.
- Duplicate messages.
- Truncated frames.
- Trailing data.
- Oversized input.
- Read deadlines.
- Revoked identities.
- Public-key rotation.
- Loopback restrictions.

## Security boundaries

This implementation does not prove:

- Independent physical devices.
- Trusted network time.
- Public peer discovery.
- Authenticated response messages.
- Network-wide replay resistance.
- Distributed consensus.
- Sybil resistance.
- External rollback protection.
- Independent security audit.
- Mainnet readiness.
- Token issuance.
- Economic activation.

Gate 2 remains incomplete.

This implementation is a bounded and testable
loopback transport sub-gate.

No private production signing keys are committed.
