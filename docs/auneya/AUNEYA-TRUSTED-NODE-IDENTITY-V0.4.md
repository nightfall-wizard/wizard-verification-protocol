# AUNEYA Trusted Node Identity v0.4

Local research identity trust for the existing authenticated ACK v0.3 loopback sender.

## Identity registry

- Node identities are pinned to Ed25519 public keys stored in a private local SQLite database.
- Initial enrollment requires confirmation of a full SHA-256 fingerprint.
- Existing node identities cannot be silently replaced.
- Unrecognized nodes fail closed.

## Key rotation

- Rotation requires the existing trusted key's Ed25519 signature.
- Rotation also requires the new private key's signature.
- The operator must explicitly confirm the new key fingerprint.
- Epochs are strictly sequential.
- Signed events bind node ID, chain ID, genesis, old fingerprint and new fingerprint.
- Replayed or outdated rotation requests are rejected.
- Registry updates and event digests are recorded atomically.

## Revocation

Revocation requires a valid signature from the currently trusted key.

Revoked identities cannot authorize ACK delivery through the v0.4 sender.

Automatic restoration is not supported.

## Integration

The existing AUNEYA v0.3 signed-ACK protocol is reused.

The v0.4 sender obtains its trusted ACK key from the local registry.

A registry write lock is held during ACK verification, preventing concurrent local rotation or revocation.

Use only one delivery worker per sender outbox.

## Test

bash conformance/auneya-trusted-node-identity-v0.4.sh

## Manual operations

Public-key fingerprint:

python3 tools/auneya/auneya_trusted_node_identity_v04.py fingerprint --public PUBLIC.pem

Initial enrollment requires an independently checked fingerprint:

python3 tools/auneya/auneya_trusted_node_identity_v04.py enroll --registry REGISTRY.sqlite --node-id node_receiver_research_001 --public PUBLIC.pem --confirm-fingerprint ACTUAL_64_CHARACTER_FINGERPRINT

Other supported commands:

- inspect
- prepare-rotation
- prepare-revocation
- apply-event
- flush-once
- worker

Use --help to inspect required arguments.

Never commit private keys, identity database files or local operator event files.

## Security limitations

- Local research only, using 127.0.0.1.
- Two separate local processes, not independently operated devices.
- No transport encryption, mutual TLS or peer discovery.
- Initial trust must be provisioned through a trustworthy channel.
- An attacker controlling the local account or the currently trusted private key can defeat this trust model.
- Dual signatures establish possession of old and new keys, not independent governance authorization.
- Revocation is local and is not distributed to other devices.
- Legacy v0.2 and v0.3 CLI commands remain available without v0.4 registry enforcement.
- No Android hardware-backed key protection.
- No distributed consensus, mainnet, actual token or wallet.
- No independent security audit.
