# WVP Canonical Specification

## Scope

WVP defines reproducible verification baselines for Rust cryptocurrency protocols.

## Evidence labels

- verified
- observed
- belegt
- stark indiziert
- plausibel
- offen
- spekulativ
- nicht überprüft
- nicht gefunden
- nicht ableitbar
- out of scope
- limitation
- reproducible command

## Non-goals

WVP is not:

- an audit
- a security guarantee
- a custody service
- an investment product
- a token
- a paid rating service

<!-- WVP:ANDROID-VS-CI-CONFORMANCE-SPEC:START -->
## Local Android vs CI Build Provenance Conformance

The Android-vs-CI conformance command is:

    ./conformance/release-check-android-vs-ci-build-provenance.sh

Normative behavior:

- The source tree must be clean.
- The checked-out commit must match the compared commit.
- A successful GitHub Actions run must exist for that commit.
- The CI artifact name must match `wvp-ci-build-provenance-<commit>`.
- Both artifacts must contain:
  - `CI-BUILD-PROVENANCE-MANIFEST.json`
  - `BUILD-PROVENANCE.json`
  - `BUILD-ENVIRONMENT-CLASSIFICATION.json`
  - `wvp-release-check-native`
  - `wvp-release-check-native.sha256`
- Artifact-local SHA256 verification must pass.
- Android-Termux and GitHub Actions must be classified as separate environment classes.
- Source commit, package version and Cargo.lock hash must match.
- Binary hash mismatch must not be treated as failure across Android aarch64 and GitHub Actions x86_64.
- `reproducible_build_claim` must remain `false`.
- `source_to_release_proof` must remain `false`.
- `binary_safety_proof` must remain `false`.

This command is local/manual because it depends on an already-created GitHub Actions artifact and authenticated GitHub CLI access.
<!-- WVP:ANDROID-VS-CI-CONFORMANCE-SPEC:END -->

