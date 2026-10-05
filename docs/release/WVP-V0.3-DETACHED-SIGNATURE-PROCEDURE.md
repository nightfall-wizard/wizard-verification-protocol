# WVP v0.3.0 Detached Signature Procedure

Status: procedure prepared
Scope: `wvp-release-check` v0.3.0
Date: 2026-10-05

## Purpose

This document defines the detached signature procedure for the staged `wvp-release-check` v0.3.0 asset.

This document does not create a signature.
This document does not create a tag.
This document does not create a GitHub release.
This document does not expose private signing material.
This document does not prove binary safety.
This document does not prove source-to-release correspondence.
This document does not prove reproducible builds.
This document is not an audit.

## Procedure Script

    ./scripts/release/sign-v030-staged-asset.sh

## Dry Run

The safe default check is:

    ./scripts/release/sign-v030-staged-asset.sh --dry-run

Dry-run must not require a private signing key and must not create:

- `v0.3.0` tag;
- GitHub release;
- detached signature file.

## Signing Mode

Actual signing is explicit and local:

    WVP_SIGNING_PRIVATE_KEY=/path/outside/repo/private-signing-key.pem \
    WVP_VERIFY_PUBLIC_KEY=/path/to/public-verification-key.pem \
    ./scripts/release/sign-v030-staged-asset.sh --sign

The private signing key must:

- be supplied only as a path through `WVP_SIGNING_PRIVATE_KEY`;
- exist outside the repository;
- not be committed;
- not be copied into the repository;
- not be printed into logs;
- not be included in CI secrets for this procedure step.

## Expected Staged Asset

    target/wvp-release-v0.3.0-unsigned/wvp-release-check-v0.3.0-termux-android-aarch64

## Expected Checksum

    target/wvp-release-v0.3.0-unsigned/wvp-release-check-v0.3.0-termux-android-aarch64.sha256

## Expected Detached Signature

Only the explicit signing mode may create:

    target/wvp-release-v0.3.0-unsigned/wvp-release-check-v0.3.0-termux-android-aarch64.sig

## Required Verification

After signing, the procedure must verify the signature with:

    openssl dgst -sha256 -verify <public-key-file> -signature wvp-release-check-v0.3.0-termux-android-aarch64.sig wvp-release-check-v0.3.0-termux-android-aarch64

## Boundary

No v0.3.0 tag is created by this document.
No GitHub release is created by this document.
No signature is created by this document.
No private signing material is committed by this document.

The signing procedure is prepared, but the release is still not published.
