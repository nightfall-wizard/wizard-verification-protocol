# AUNEYA/WVP v1.6 — Authenticated Offline Peer Envelope Gate

Status: additive non-value research.

Compatible with unchanged v0.5–v1.5 formats.

## What is new

- Bounded four-byte network-order length prefix followed by canonical ASCII JSON.
- Ed25519 signature with protocol-specific domain separation.
- Sender and research chain identity.
- Independent public-key, checkpoint, challenge and manifest pins.
- SHA-256 pinning of the exact public PEM file bytes.
- Maximum 65,536 JSON bytes.
- Duplicate JSON keys rejected.
- Unknown fields rejected.
- Floating-point input rejected.
- Trailing bytes rejected.
- Maximum 120-second message lifetime.
- Maximum 30-second local clock skew.
- Persistent SQLite replay detection.
- Strict sender/chain counters.
- Sequential replay epochs.
- Atomic database transactions.
- Synchronous durable local writes.
- Private filesystem permissions.
- Bounded database capacity.
- Real Ed25519 adversarial tests.
- No production private signing key committed.

## CLI

All inputs and the ledger parent must be private.

Directories: 0700.

Files: 0600.

Peer public-key bytes and all expected digests must come from independently trusted sources.

Example:

    python3 tools/auneya/auneya_peer_gate_v16.py accept \
      --frame PRIVATE/frame.bin \
      --key PRIVATE/peer-public.pem \
      --key-sha256 INDEPENDENT_PEER_PEM_SHA256 \
      --sender phone-alpha \
      --chain-id auneya-research-v1 \
      --checkpoint-sha256 INDEPENDENT_CHECKPOINT_SHA256 \
      --challenge-sha256 INDEPENDENT_CHALLENGE_SHA256 \
      --manifest-sha256 INDEPENDENT_MANIFEST_SHA256 \
      --ledger PRIVATE/peer-replay.sqlite

The verify action checks signatures and envelope constraints without committing replay state.

The accept action commits replay state.

A new peer must start at epoch 1, counter 1.

Following messages must increment the counter.

A new epoch must be exactly one greater than the previous epoch and restart the counter at 1.

## Evidence binding

The caller must independently verify underlying evidence using the existing AUNEYA evidence verification chain.

Envelope hashes only bind the authenticated message to external pins.

They do not establish the actual truth of observations.

## Security limitations

- Offline framed-message verification only.
- No socket listener.
- No functioning distributed peer network.
- No standardized public-key fingerprint scheme.
- PEM-file hashing binds exact file bytes only.
- No independently trusted time source.
- No network-wide replay protection.
- No external rollback anchors.
- Deleting or rolling back all persistent local state is not prevented by this module.
- No complete protection against filesystem races.
- No independent physical devices proven.
- No witness independence proven.
- No Sybil resistance proven.
- No factual correctness proven.
- No network consensus proven.
- No independent security audit.
- No transferable token.
- No real rewards.
- No wallet activation.
- No mainnet activation.

## Testing

    python3 -m unittest discover \
      -s tests \
      -p 'test_auneya_peer_gate_v16.py' \
      -v

All existing WVP/AUNEYA regression tests remain mandatory.
