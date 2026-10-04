# WVP Safe Signature Verification Path

## Purpose

WVP must be able to verify release authenticity without storing signing secrets in the repository.

## Hard rule

No signing private key may be committed to this repository.

No signing private key may be printed into CI logs.

No signing private key may be embedded in scripts, docs, tests, fixtures or release assets.

## Allowed material

The repository may contain public verification material only.

Allowed examples:

- public signing key
- key fingerprint
- documented signature verification command
- signed release artifact
- detached signature artifact

## Future verification states

- no signature asset: WARN
- signature asset discovered but verification unsupported: WARN
- signature verification failed: FAIL
- signature verification passed and checksum passed: eligible for INFO, unless another blocker remains

## Current state

WVP v0.1.0 verifies checksum integrity only.

Cryptographic release-signature verification is not implemented yet.

The correct current status remains WARN.
