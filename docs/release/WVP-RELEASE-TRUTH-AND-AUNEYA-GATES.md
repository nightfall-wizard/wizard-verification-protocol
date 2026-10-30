# WVP release truth and AUNEYA roadmap execution

## Separate version tracks

- WVP `vX.Y.Z`: only an actual stable tagged GitHub Release is published.
- `reference/rust/wvp-release-check/Cargo.toml`: source package version; may be an unreleased candidate.
- AUNEYA research v1.4: lossless cross-language signed-evidence verification, not a protocol release.
- AUNEYA `auneya-vX.Y.Z`: separate local-research prereleases.

Do not interpret research module numbering as a live WVP release or a token/network launch.

The README links GitHub's live latest stable release instead of making a permanent stale claim.

Historical v0.4 and v0.5 release evidence is retained with an explicit time boundary.

## High-value future engineering gates

1. Document threat model for authenticated peer transport; implement with bounded frames, pinning and forged-peer rejection.
2. Implement replay expiration using bounded persisted state; adversarial clock rollback and crash-recovery tests.
3. Establish CPU, memory, disk, input and connection budgets with measurable limits and denial-of-service testing.
4. Run independent real-device experiments; preserve traces, failure cases and reproducible evidence.
5. Obtain external review with identified reviewers, independent reproduction and follow-up closure.
6. Only after legal assessment and protocol specification, consider economic-network steps.

No script can truthfully assert external audit, Sybil resistance, witness independence, mainnet safety, token issuance or a complete whitepaper implementation.

## Release publication contract

A new patch release requires a clean candidate commit, successful Python/Node/Rust and security gates, a merged PR, confirmed checks on the exact main commit, an immutable tag, and source-only unsigned assets with hash validation.

Publication is blocked when the gates cannot be verified.

No untrusted signing key is generated or private key used.
