# PROJECT-STATE

Updated: 2026-10-04 23:46:08 CEST

## Project

Wizard Verification Protocol — WVP

## Builder

nightfall-wizard

## Category

Proof-of-Project-Reality

## Current stage

WVP v0.2 detached release signature asset.

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

## Current progress

WVP v0.1 baseline: 100 percent.

WVP v0.2 signature verification: 40 percent after commit, push and CI verification.

## Next target

Implement signature verification execution inside wvp-release-check.

## Safety state

No seeds, wallet files, tokens or private signing keys are stored in this repository.
