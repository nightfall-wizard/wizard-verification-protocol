# WVP v0.3 Reproducible-Build Evidence Plan

## Objective

WVP v0.3 starts the reproducible-build evidence path.

The goal is not to claim reproducibility too early.

The goal is to make build evidence explicit, machine-checkable and CI-covered.

## Phase 1

Create a build provenance script for `wvp-release-check`.

The script records:

- source commit
- source dirty state
- package version
- Rust compiler version
- Cargo version
- operating system information
- Cargo.lock hash
- release binary hash
- build command
- evidence classification

## Phase 2

Add same-environment repeat-build checks.

## Phase 3

Add independent-environment build comparison.

## Phase 4

Only after independent matching builds exist, consider release-grade reproducible-build wording.

## Required wording discipline

Allowed wording:

- build provenance
- build evidence
- single-environment evidence
- reproducible-build evidence path

Disallowed wording until proven:

- reproducible build achieved
- reproducible release
- source-to-binary proof
- independently reproducible binary

## Current v0.3 starting point

WVP v0.3 starts with:

- `single-environment-build-provenance`
- `reproducible_build_claim: false`
