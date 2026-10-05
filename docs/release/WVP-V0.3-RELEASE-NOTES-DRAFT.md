# WVP v0.3 Release Notes Draft

Status: draft  
Scope: `wvp-release-check` release-integrity track  
Date: 2026-10-05

## Summary

WVP v0.3 strengthens the release-integrity track for `wvp-release-check`.

The release focuses on evidence quality, claim boundaries, and repeatable conformance commands rather than broad feature expansion.

## Main Additions Since v0.2.0

### Build Provenance Evidence

- single-environment build provenance;
- same-environment repeat-build evidence;
- build environment classification;
- CI build provenance artifact generation;
- Android-vs-CI build provenance comparison;
- reusable Android-vs-CI local conformance command.

### Release Integrity Hardening

- checksum verification;
- signature verification;
- signature tamper-negative tests;
- signature asset matching checks;
- public verification key documentation;
- no-private-signing-material checks.

### v0.3 Readiness Controls

- v0.3 release readiness checklist;
- CI-enforced readiness checklist conformance;
- Android-vs-CI command syntax validation in CI;
- explicit non-claims around audit status, binary safety, source-to-release proof and reproducible builds.

## Explicit Non-Claims

WVP v0.3 must not claim:

- binary safety;
- audit status;
- complete reproducible builds;
- source-to-release proof;
- that cross-architecture binaries should be byte-identical;
- that any third-party cryptocurrency project is secure.

## Expected v0.3 Release Assets

The expected release assets are documented in:

    docs/release/WVP-V0.3-ARTIFACT-NAMING-PLAN.md

## Pre-Release Verification

Before publishing v0.3, the following must pass locally and in CI where applicable:

    cargo fmt --manifest-path reference/rust/wvp-release-check/Cargo.toml -- --check
    cargo clippy --manifest-path reference/rust/wvp-release-check/Cargo.toml -- -D warnings
    cargo test --manifest-path reference/rust/wvp-release-check/Cargo.toml
    ./conformance/release-check-v030-readiness-checklist.sh
    ./conformance/release-check-v030-release-docs.sh

## Release Status

This file is a draft.  
It is not a published release announcement.
