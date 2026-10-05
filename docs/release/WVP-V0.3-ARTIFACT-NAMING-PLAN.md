# WVP v0.3 Artifact Naming Plan

Status: draft  
Scope: `wvp-release-check` release assets  
Date: 2026-10-05

## Purpose

This document defines the intended artifact names for the WVP v0.3 release.

It prevents ambiguous release assets and keeps checksums, signatures, platform labels and verification commands predictable.

## Version

Planned release tag:

    v0.3.0

Planned package version:

    0.3.0

## Primary Android-Termux Asset

Expected binary asset:

    wvp-release-check-v0.3.0-termux-android-aarch64

Expected checksum asset:

    wvp-release-check-v0.3.0-termux-android-aarch64.sha256

Expected signature asset:

    wvp-release-check-v0.3.0-termux-android-aarch64.sig

## Optional Native CI Evidence Asset

Expected CI build provenance artifact name format:

    wvp-ci-build-provenance-<git-commit-sha>

This is a GitHub Actions artifact, not necessarily a release asset.

## Required Naming Rules

- version must be present in release asset names;
- platform must be present in binary asset names;
- checksum file must end in `.sha256`;
- signature file must end in `.sig`;
- release asset names must not imply audit status;
- release asset names must not imply reproducible-build proof;
- release asset names must not imply source-to-release proof;
- release asset names must not imply binary safety.

## Expected Verification Commands

Checksum verification:

    sha256sum -c wvp-release-check-v0.3.0-termux-android-aarch64.sha256

Signature verification:

    openssl dgst -sha256 -verify <public-key-file> -signature wvp-release-check-v0.3.0-termux-android-aarch64.sig wvp-release-check-v0.3.0-termux-android-aarch64

## Explicit Non-Claims

The artifact names must not claim:

- audit;
- safety;
- reproducibility;
- source-to-release proof;
- third-party project security.

## Current Status

Draft only.  
No v0.3.0 release has been published by this document.
