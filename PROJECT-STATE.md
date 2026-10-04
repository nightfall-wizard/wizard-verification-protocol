# PROJECT-STATE

Updated: 2026-10-05 00:05:08 CEST

## Project

Wizard Verification Protocol — WVP

## Builder

nightfall-wizard

## Category

Proof-of-Project-Reality

## Current stage

WVP v0.2 controlled version bump and local release build preparation.

## Completed

- WVP v0.1.1 release baseline is complete
- checksum verification is implemented
- release checksum verification is end-to-end proven
- OpenSSL signature tooling path is detected
- no-secret scan excludes detector scripts containing intentional sentinel patterns
- signature discovery is separated from signature verification
- JSON fields for signature verification status are implemented
- INFO now requires checksum verification and signature verification to pass
- public release verification key is committed
- private release signing key is kept outside the repository
- public key fingerprint conformance is implemented
- detached release signature asset exists for v0.1.1
- detached release signature is verified by conformance using the committed public key
- wvp-release-check internally verifies detached release signatures
- wvp-release-check reaches INFO when checksum and signature verification both pass
- release asset matching now requires exactly one .sha256 asset
- release asset matching now requires exactly one .sig asset
- negative unit tests cover missing and duplicate signature/checksum assets
- tamper-negative tests reject modified signed assets
- tamper-negative tests reject modified detached signatures
- tamper-negative tests reject wrong public verification keys
- v0.2 release-candidate documentation exists
- v0.2 release checklist exists
- v0.2 release-candidate documentation is covered by CI conformance
- wvp-release-check package version is prepared as 0.2.0
- local v0.2 release build script exists
- local release build script creates binary, checksum and detached signature without upload
- v0.2 version and build script conformance is covered by CI

## Current progress

WVP v0.1 baseline: 100 percent.

WVP v0.2 signature verification: 90 percent after commit, push and CI verification.

## Next target

Create controlled v0.2.0 GitHub release with binary, checksum and detached signature assets.

## Safety state

No seeds, wallet files, tokens or private signing keys are stored in this repository.
