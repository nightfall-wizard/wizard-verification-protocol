# AUNEYA Authenticated ACK v0.3

## Purpose

Research-only cryptographically authenticated delivery receipts.

This is a separate authenticated protocol built on the existing
AUNEYA Durable Delivery v0.2 implementation.

The legacy v0.2 CLI still accepts unsigned responses.
Use the v0.3 receiver and worker for authenticated ACK mode.

## Security

- Separate Ed25519 receiver acknowledgement key.
- Domain-separated signed acknowledgement.
- Pinned receiver public key.
- Pinned receiver identity.
- Chain and genesis binding.
- Message ID binding.
- Fresh 128-bit nonce for each delivery attempt.
- Strict JSON envelope validation.
- Duplicate key rejection.
- Signed accepted and already_accepted states.
- No acknowledgement after invalid signature.
- Sender marks delivered only after valid signature verification.

## Persistent delivery

The sender uses the existing SQLite outbox.

The receiver uses the existing SQLite inbox.

An accepted proof is committed before its acknowledgement.

Lost acknowledgements leave the sender pending.

A duplicate delivery generates a fresh signed acknowledgement.

## Automated tests

Run:

bash conformance/auneya-authenticated-ack-v0.3.sh

Tests include:

- Valid Ed25519 acknowledgement.
- Invalid or forged signature.
- Wrong receiver public key.
- Wrong receiver identity.
- Wrong message ID.
- Modified status.
- Modified chain.
- Modified genesis.
- Replayed nonce.
- Unsigned acknowledgement.
- Unexpected acknowledgement fields.
- Replayed captured acknowledgement.
- Invalid witness-proof signature.
- Duplicate JSON object keys.
- Lost acknowledgement after database commit.
- Receiver restart.
- Sender restart.
- Exactly one persisted receiver proof.

## Key management

The self-test generates temporary Ed25519 key pairs.

No signing keys are committed.

The receiver ACK private key must have owner-only permissions.

The sender must receive and verify the trusted ACK public key
through a separate trusted provisioning process.

Never use the witness signing key as the receiver ACK key.

## Limitations

Only loopback networking on 127.0.0.1.

No independent devices.

No encrypted transport or production mutual authentication.

A signed receipt confirms possession of the trusted private
ACK key, not the real-world truth of the proof.

No distributed consensus.

No production identity registry.

No production key rotation or revocation process.

No mainnet, token, monetary reward, real wallet or market value.

No independent security audit.
