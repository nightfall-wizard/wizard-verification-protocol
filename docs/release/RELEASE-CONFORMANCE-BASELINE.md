# WVP Release Conformance Baseline

## Purpose

WVP release conformance must verify the currently published release state without hard-coding a single permanent release tag.

## Rule

Conformance scripts should resolve the latest GitHub release dynamically unless a specific historical regression test intentionally pins a tag.

## Current required checks

The latest release must provide:

- a release tag
- at least one downloadable release asset
- at least one checksum asset
- a checksum file that verifies with `sha256sum -c`

## Current expected limitation

The latest release is still expected to have no cryptographic signature artifact.

Therefore the correct current result remains `WARN`, not `INFO`.

## Reason

Checksum verification proves byte integrity against the published checksum file.

It does not prove cryptographic authorship.

WVP must not upgrade to full verification until signature verification is implemented and passing.
