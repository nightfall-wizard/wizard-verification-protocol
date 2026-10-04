# Same-Environment Repeat-Build Comparison

## Status

This document defines the WVP same-environment repeat-build comparison layer.

This is not a reproducible-build proof.

This is not a binary-safety proof.

This is not an audit.

## Purpose

Single-environment build provenance records one build.

Same-environment repeat-build comparison performs two separate builds in the same environment and compares the resulting binary hashes.

This can detect some build instability.

This does not prove independent reproducibility.

## Required evidence

A same-environment repeat-build comparison must record:

- source commit
- dirty or clean source state
- package version
- Rust compiler version
- Cargo version
- operating system information
- Cargo.lock hash
- first build binary hash
- second build binary hash
- whether both binary hashes match
- whether both binary sizes match
- build commands
- evidence limitations

## Expected claim state

The expected claim remains:

- `reproducible_build_claim: false`

The expected evidence type is:

- `same-environment-repeat-build-comparison`

## Passing condition

The comparison passes only if:

- build A succeeds
- build B succeeds
- build A binary exists
- build B binary exists
- build A binary SHA256 equals build B binary SHA256
- build A binary size equals build B binary size

## Limitations

Same-environment repeat-build comparison does not prove independent reproducibility.

It does not prove that a different machine can reproduce the same binary.

It does not prove that the published release binary was produced from source.

It does not replace independent-environment evidence.

It does not replace a release audit.
