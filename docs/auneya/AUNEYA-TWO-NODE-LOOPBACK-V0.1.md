# AUNEYA Two-Node Loopback v0.1

## Status

Experimental local network research.

## Architecture

Two independent operating-system processes:

- Sender Node A
- Receiver Node B

Communication: HTTP over 127.0.0.1.

The nodes have separate SQLite replay databases.

## Security checks

- Existing Ed25519 witness-proof verifier
- Existing witness-proof schema verification
- Expected chain identity
- Pinned genesis identifier
- Trusted witness identity
- Trusted local public key
- Payload tampering rejection
- Invalid signature rejection
- Cross-chain message rejection
- Persistent local replay rejection

## Limitations

Both nodes run on the same device.

No independent peers are established.

HTTP is restricted to local loopback.

No transport-layer authentication or encryption.

There is no distributed consensus, peer discovery,
reliable delivery, or atomic cross-node persistence.

Genesis identity is locally pinned, not independently
authenticated by a production genesis registry.

The fixture is simulated research evidence.
Signature verification does not establish observation truth.

No mainnet, real wallet, token, reward, asset,
custody, transferability or market value.

No independent security audit is claimed.

## Verification

bash conformance/auneya-two-node-loopback-v0.1.sh
