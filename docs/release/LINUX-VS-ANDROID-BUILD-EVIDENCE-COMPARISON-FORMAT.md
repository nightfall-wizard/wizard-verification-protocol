# Linux-vs-Android Build Evidence Comparison Format

## Status

This document defines the WVP build evidence comparison format.

This is not a reproducible-build proof.

This is not a source-to-release proof.

This is not a binary-safety proof.

This is not an audit.

## Purpose

WVP can now generate build provenance artifacts in different environment classes.

The next requirement is a comparison format.

The comparison format records whether two build provenance artifacts agree on:

- source commit
- package version
- Cargo.lock hash
- Rust compiler version
- Cargo version
- environment class
- binary SHA256
- binary size

## Supported evidence classes

The comparison format supports:

- `android-termux-aarch64`
- `github-actions-linux-x86_64`
- `linux-aarch64`
- `linux-x86_64`
- `unknown`

## Linux-vs-Android use case

The intended comparison is:

- Android/Termux evidence from `android-termux-aarch64`
- CI/Linux evidence from `github-actions-linux-x86_64`

This comparison is useful because it separates mobile-built evidence from CI evidence.

## Important limitation

A Linux x86_64 native binary and an Android aarch64 native binary are not expected to be byte-identical.

A binary hash mismatch across different architecture or operating-system classes is not automatically a failure.

A matching source commit and Cargo.lock hash are useful evidence.

A matching binary hash across independent environments would be stronger evidence, but it must not be assumed.

## Required claim state

The required claim remains:

- `reproducible_build_claim: false`

The comparison evidence type is:

- `build-provenance-artifact-comparison`

## Required output fields

A comparison output must include:

- left artifact directory
- right artifact directory
- left environment class
- right environment class
- source commit match
- package version match
- Cargo.lock hash match
- rustc version match
- cargo version match
- binary SHA256 match
- binary size match
- same environment class
- independent environment comparison performed
- Linux-vs-Android comparison detected
- reproducible build claim state
- limitations

## Passing condition

The format-level comparison passes if:

- both artifact directories exist
- both contain `CI-BUILD-PROVENANCE-MANIFEST.json`
- both contain `BUILD-PROVENANCE.json`
- both contain `BUILD-ENVIRONMENT-CLASSIFICATION.json`
- both contain `wvp-release-check-native`
- both contain `wvp-release-check-native.sha256`
- both checksums verify
- comparison JSON is generated
- comparison JSON states `reproducible_build_claim: false`

## Limitations

This comparison format does not prove reproducibility.

This comparison format does not prove a release asset was built from source.

This comparison format does not prove binary safety.

This comparison format only makes evidence differences explicit and machine-readable.

## Termux log path note

Conformance scripts must not assume `/tmp` exists.

Portable WVP conformance logs should be written under `target/` so the same scripts work on Android/Termux and GitHub Actions.
