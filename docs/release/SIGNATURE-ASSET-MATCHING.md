# WVP Signature Asset Matching

WVP v0.2 requires deterministic release verification inputs.

## Current rule

`wvp-release-check` requires:

- exactly one checksum manifest ending in `.sha256`
- exactly one detached signature asset ending in `.sig`
- the signed asset name must equal the signature asset name without the `.sig` suffix

Example:

- signed asset: `wvp-release-check-termux-android-aarch64`
- signature asset: `wvp-release-check-termux-android-aarch64.sig`

## Failure cases

Verification must fail if:

- no `.sha256` asset exists
- more than one `.sha256` asset exists
- no `.sig` asset exists
- more than one `.sig` asset exists
- the signed asset referenced by the `.sig` name is missing
- OpenSSL signature verification fails

## Scope

This is not an audit.

This does not prove reproducible builds.

This reduces ambiguity in release asset selection and prevents accidental verification of the wrong signature asset.
