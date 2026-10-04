# PROJECT-STATE

Updated: 2026-10-05 00:00:36 CEST

## Project

Wizard Verification Protocol — WVP

## Builder

nightfall-wizard

## Category

Proof-of-Project-Reality

## Current stage

WVP v0.2 release-candidate documentation.

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

## Current progress

WVP v0.1 baseline: 100 percent.

WVP v0.2 signature verification: 80 percent after commit, push and CI verification.

## Next target

Prepare controlled v0.2.0 version bump and release-build script.

## Safety state

No seeds, wallet files, tokens or private signing keys are stored in this repository.
