# WVP v0.3.0 Unsigned Release Asset Staging

Status: staging plan and local staging procedure
Scope: `wvp-release-check` v0.3.0
Date: 2026-10-05

## Purpose

This document defines the unsigned release asset staging procedure for `wvp-release-check` v0.3.0.

This is not a published release.
This is not a tag.
This is not a signature event.
This is not a source-to-release proof.
This is not a reproducible-build proof.
This is not a binary-safety proof.
This is not an audit.

## Staging Script

    ./scripts/release/stage-v030-unsigned-asset.sh

## Expected Staging Directory

    target/wvp-release-v0.3.0-unsigned

## Expected Asset

    wvp-release-check-v0.3.0-termux-android-aarch64

## Expected Checksum Asset

    wvp-release-check-v0.3.0-termux-android-aarch64.sha256

## Signature Status

No signature is created in this step.

The expected signature filename is reserved for a later signing step:

    wvp-release-check-v0.3.0-termux-android-aarch64.sig

This file must not exist after unsigned staging.

## Expected Manifest

    STAGING-MANIFEST.json

The manifest must state:

- `staging_only: true`
- `tag_created: false`
- `github_release_created: false`
- `signature_created: false`
- `source_to_release_proof: false`
- `reproducible_build_claim: false`
- `binary_safety_claim: false`
- `audit_claim: false`

## Explicit Non-Claims

Unsigned staging must not claim:

- that v0.3.0 has been released;
- that a v0.3.0 tag exists;
- that a GitHub release exists;
- that a detached signature exists;
- that the staged binary is safe;
- that the staged binary was independently reproduced;
- that the staged binary was built by CI;
- that the staged binary is identical to a future published release asset;
- that the project has been audited.

## Current Boundary

This step prepares local unsigned release assets only.

No v0.3.0 tag is created by this document.
No GitHub release is created by this document.
No signature is created by this document.
