# WVP v0.2.0 Post-Release Verification

## Status

WVP v0.2.0 has been released.

This document records the post-release verification result.

This is not an audit.

This is not a reproducible-build proof.

This is not a binary-safety proof.

## Published release

Release tag:

- `v0.2.0`

Published assets:

- `wvp-release-check-termux-android-aarch64`
- `wvp-release-check-termux-android-aarch64.sha256`
- `wvp-release-check-termux-android-aarch64.sig`

## Verified after publication

The published release was checked after upload.

Verified properties:

- GitHub release exists
- remote tag exists
- exactly three release assets exist
- published binary downloads successfully
- published `.sha256` downloads successfully
- published `.sig` downloads successfully
- published checksum verifies successfully
- published detached signature verifies successfully
- `wvp-release-check` self-verifies the latest release as `INFO`
- latest release tag is `v0.2.0`
- checksum verification passes
- signature verification passes
- signature verification error is `null`

## WVP self-verification expectation

A successful live self-check must report:

- `"version": "0.2.0"`
- `"status": "INFO"`
- `"latest_release_tag": "v0.2.0"`
- `"latest_release_asset_count": 3`
- `"checksum_asset_count": 1`
- `"signature_asset_count": 1`
- `"checksum_verification_passed": true`
- `"signature_verification_passed": true`
- `"signature_verification_error": null`

## Limitations

This is not an audit.

This does not prove reproducible builds.

This does not prove binary safety.

This does not verify wallet safety.

This does not verify cryptographic protocol correctness.

This verifies release checksum and detached signature integrity for the published WVP v0.2.0 release asset set.
