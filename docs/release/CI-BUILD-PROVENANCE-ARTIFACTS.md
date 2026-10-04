# CI Build Provenance Artifacts

## Status

This document defines WVP CI build provenance artifact generation.

This is not a reproducible-build proof.

This is not independent reproducibility evidence by itself.

This is not a source-to-release proof.

This is not an audit.

## Purpose

GitHub Actions can produce build evidence during CI.

The purpose of this layer is to preserve CI-side build provenance as a downloadable artifact.

This makes CI build evidence easier to inspect and compare later.

## Artifact contents

The CI build provenance artifact should include:

- `CI-BUILD-PROVENANCE-MANIFEST.json`
- `BUILD-PROVENANCE.json`
- `BUILD-ENVIRONMENT-CLASSIFICATION.json`
- native CI-built binary copy
- SHA256 checksum for the native CI-built binary
- logs used to derive artifact paths

## Required claim state

The required claim remains:

- `reproducible_build_claim: false`

The expected evidence type is:

- `ci-build-provenance-artifact-generation`

## Environment separation

The CI artifact must include an environment classification.

For GitHub Actions Linux runners, the expected environment class is:

- `github-actions-linux-x86_64`

For Android Termux local generation, the expected environment class is:

- `android-termux-aarch64`

These classes must not be merged without explicit comparison.

## Filename discipline

Binary filenames are not evidence of target platform.

The authoritative evidence fields are:

- environment class
- uname
- rustc version
- cargo version
- source commit
- Cargo.lock hash
- binary SHA256

## Limitations

A CI artifact does not prove that a release asset was built from source.

A CI artifact does not prove independent reproducibility.

A CI artifact does not prove binary safety.

A CI artifact can be used as input for later Linux-vs-Android comparison.
