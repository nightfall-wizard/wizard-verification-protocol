# AUNEYA Witness-Proof Integration v0.2

Status: experimental research adapter.
Value status: non-value simulation only.

## Purpose

Connect the existing AUNEYA INV-006 Ed25519 verifier to
the existing AUNEYA witness-proof v0.1 data structure.

The original witness-proof schema remains unchanged.

## Verification

The adapter:

1. Requires the existing witness-proof schema version.
2. Requires signed status and Ed25519 algorithm.
3. Canonicalizes the proof excluding integrity metadata.
4. Recomputes and checks its SHA-256 proof hash.
5. Verifies a detached signature using the existing
   chain-bound attestation verifier.
6. Uses externally supplied chain identity, witness identity,
   public key and signature file.

## Important limitations

- Experimental adapter, not production consensus.
- Not a full JSON Schema validator.
- Does not validate external evidence truth.
- Does not implement trusted witness key registration.
- Does not prevent duplicate use within the same chain.
- Does not bind genesis hash independently.
- No independent audit.
- Does not modify the existing local witness runner.
- Does not enable tokens, transfers, custody or real rewards.
- External review is required before production use.
