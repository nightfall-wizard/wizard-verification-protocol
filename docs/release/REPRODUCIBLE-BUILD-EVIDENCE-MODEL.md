# Reproducible-Build Evidence Model

## Status

This document defines the first WVP reproducible-build evidence layer.

This is not a reproducible-build proof.

This is not a binary-safety proof.

This is not an audit.

## Problem

A release checksum and detached signature prove that a published asset matches the signed asset.

They do not prove that the signed asset was produced from the claimed source code.

They do not prove that another builder can reproduce the same binary.

## Evidence classes

### No evidence

No build environment, source state or binary hash is recorded.

### Single-environment build provenance

A build was performed in one environment and the following data was recorded:

- source commit
- dirty or clean source state
- package version
- Rust compiler version
- Cargo version
- operating system information
- Cargo.lock hash
- produced binary hash
- build command
- output artifact names

This is useful evidence.

This is not reproducibility proof.

### Repeated same-environment evidence

The same source is built more than once in the same environment and the binary hash is compared.

This can detect instability in one environment.

This is still not full reproducibility proof.

### Independent-environment reproducibility evidence

The same source is built in at least two independent environments and the binary hash is compared.

This is stronger evidence.

### Release-grade reproducible-build claim

A release-grade reproducible-build claim requires:

- clean source tree
- pinned source commit
- pinned dependencies
- documented build command
- documented environment
- at least two independent successful builds
- matching binary hashes
- preserved evidence artifacts

## WVP v0.3 baseline

WVP v0.3 begins with single-environment build provenance.

The first goal is to record evidence without overclaiming.

The expected claim is:

- `reproducible_build_claim: false`

The expected evidence type is:

- `single-environment-build-provenance`

## Limitations

Single-environment provenance does not prove reproducibility.

A matching checksum does not prove source-build correspondence.

A detached signature does not prove source-build correspondence.

A clean CI run does not prove reproducibility.

A reproducible-build claim must not be made until independent-environment evidence exists.
