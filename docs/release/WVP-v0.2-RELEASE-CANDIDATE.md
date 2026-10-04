# WVP v0.2 Release Candidate

## Status

This document defines the WVP v0.2 release-candidate scope.

This is not a release tag.

This is not an audit.

This is not a security certification.

## Release-candidate target

WVP v0.2 focuses on release integrity verification.

The release candidate is acceptable only if the reference implementation can prove the following from CI:

1. GitHub release metadata can be inspected.
2. Release checksum assets can be discovered.
3. Release checksums can be verified.
4. Detached signature assets can be discovered.
5. Detached signatures can be verified with the committed public key.
6. Signature verification fails closed when tampering is detected.
7. Private signing material is not committed.
8. Public verification material is committed.
9. CI runs all conformance checks successfully.

## Completed technical proof

Current v0.2 work includes:

- checksum verification
- detached signature asset upload for `v0.1.1`
- public release verification key
- private signing key outside the repository
- internal detached signature verification in `wvp-release-check`
- deterministic `.sha256` and `.sig` asset matching
- tamper-negative tests for modified asset, modified signature and wrong public key
- CI conformance coverage for signature verification

## Required before v0.2.0 release

Before a real `v0.2.0` release exists, the project must still perform:

1. final local full check
2. final CI full check
3. version bump from `0.1.1` to `0.2.0`
4. build release binary
5. create checksum asset
6. create detached signature asset
7. verify release assets locally
8. publish release
9. verify published release using WVP itself

## Safety requirements

The private signing key must remain outside the repository.

The private signing key must not be printed in logs.

The private signing key must not be uploaded as a release asset.

The repository must contain only public verification material.

## Non-goals

WVP v0.2 does not prove reproducible builds.

WVP v0.2 does not prove the binary is safe.

WVP v0.2 does not audit the source code.

WVP v0.2 does not verify wallet safety.

WVP v0.2 does not verify cryptographic protocol correctness.

## Expected release-candidate result

A passing v0.2 release candidate means:

- release metadata is inspectable
- checksum verification works
- detached signature verification works
- tampering is rejected
- private signing material is not present in the repository
- CI validates the above
