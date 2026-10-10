# AUNEYA Attestation Binding v0.1

Status: experimental research implementation.
Value status: non-value simulation only.

## Security objective

Implements a testable reference for AUNEYA-INV-006,
AUNEYA-CHAIN-005 and cross-chain aspects of AUNEYA-CHAIN-006.

Ed25519 signatures authenticate a domain-separated message
containing the chain id, witness id and SHA-256 payload hash.

Encoding: fixed ASCII domain prefix, followed by three
UTF-8 fields, each prefixed by a two-byte big-endian length.

The verifier must receive the expected chain id, witness id,
payload and trusted public key from an independent context.
It must not derive trust from untrusted attestation metadata.

## Run

bash conformance/auneya-attestation-binding-v0.1.sh

## Limitations

- Research-only standalone reference, not production consensus.
- No integration into existing v0.1 witness-proof schema.
- No key registration, revocation, expiry or identity registry.
- No same-chain duplicate-attestation prevention.
- No independent security audit.
- File-path checks alone do not eliminate TOCTOU races.
- Local test keys are temporary and not real witness identities.
- A valid signature proves key possession, not observation truth.
- No token, monetary reward, custody or asset transfer.
