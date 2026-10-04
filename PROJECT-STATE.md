# PROJECT-STATE

Updated: 2026-10-05 00:40:44 CEST

## Project

Wizard Verification Protocol — WVP

## Builder

nightfall-wizard

## Category

Proof-of-Project-Reality

## Current stage

WVP v0.3 same-environment repeat-build comparison implemented.

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
- wvp-release-check package version is 0.2.0
- local v0.2 release build script exists
- local release build script creates binary, checksum and detached signature without upload
- v0.2 version and build script conformance is covered by CI
- Git tag v0.2.0 exists
- GitHub release v0.2.0 exists
- v0.2.0 release includes binary, checksum and detached signature assets
- published v0.2.0 checksum verification passes
- published v0.2.0 detached signature verification passes
- wvp-release-check self-verifies v0.2.0 as INFO
- v0.2.0 post-release verification is covered by CI conformance
- v0.3 reproducible-build evidence model exists
- v0.3 build provenance script exists
- v0.3 single-environment build provenance conformance exists
- v0.3 same-environment repeat-build comparison exists
- v0.3 same-environment repeat-build conformance is covered by CI

## Current progress

WVP v0.1 baseline: 100 percent.

WVP v0.2 signature verification: 100 percent.

WVP v0.3 reproducible-build evidence: 20 percent after commit, push and CI verification.

## Next target

Add independent-environment build evidence placeholder and CI/Linux-vs-Android evidence separation.

## Safety state

No seeds, wallet files, tokens or private signing keys are stored in this repository.
