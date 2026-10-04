# WVP Signature Verification Execution

WVP v0.2 now performs detached release signature verification when a signature asset and public verification key are available.

## Current verification path

`wvp-release-check` verifies:

1. GitHub release metadata exists.
2. A checksum asset exists.
3. The checksum matches the downloaded release binary.
4. A detached `.sig` asset exists.
5. The `.sig` verifies against the release binary using the committed public key.

## Public key

Current public key path:

- `keys/release/wvp-release-signing-public.pem`

## Private key

The private release signing key remains outside this repository.

It must not be committed.

It must not be printed in logs.

It must not be uploaded as a release asset.

## Status effect

If checksum verification passes and signature verification passes, the release-check status may become `INFO`.

If checksum verification fails, status is `FAIL`.

If signature verification is attempted and fails, status is `FAIL`.

If signature discovery exists but verification cannot be performed, status remains `WARN`.

## Scope

This is not an audit.

This does not prove reproducible builds.

This does not prove the release is safe.

This proves that the downloaded release asset matches its checksum and detached signature under the configured public key.
