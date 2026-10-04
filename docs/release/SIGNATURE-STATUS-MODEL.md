# WVP Signature Status Model

WVP v0.2 separates signature discovery from signature verification.

## Rule

A discovered signature asset is not the same as a verified signature.

## JSON fields

`wvp-release-check` must expose these fields:

- `signature_asset_count`
- `signature_verification_attempted`
- `signature_verification_passed`
- `signature_verification_error`

## Status logic

- checksum verification failed: `FAIL`
- signature verification attempted and failed: `FAIL`
- checksum passed but signature missing: `WARN`
- checksum passed but signature asset is only discovered and not verified: `WARN`
- checksum passed and signature passed: eligible for `INFO`

## Scope

This is not an audit.

This step does not create a signing key.

This step does not commit private signing material.

This step does not upload a release signature.

This step only hardens the status model so that asset discovery cannot be misclassified as verification.
