# WVP Signature Artifact Policy

## Purpose

WVP must distinguish between checksum integrity and cryptographic authenticity.

A checksum can detect accidental or malicious byte changes after publication, but it does not prove who created or authorized the release.

## Rule

A release must not be treated as fully verified unless it provides verifiable signature material.

Recognized signature indicators include release assets or files whose names indicate:

- `.sig`
- `.asc`
- `.gpg`
- `.minisig`
- `signature`

## Required WVP behavior

If a release has checksum assets but no signature assets, WVP must keep the result below full verification.

For the current release-check baseline, this means:

- checksum verification may pass
- signature asset discovery may still be zero
- status must remain `WARN`
- limitations must explicitly state that signature verification is not implemented yet

## Forbidden shortcut

WVP must not create fake signature confidence from:

- GitHub release existence
- tag existence
- checksum existence
- asset count
- successful checksum verification

## Current state

WVP v0.1.0 verifies release checksum integrity, but does not yet verify cryptographic release signatures.

Therefore the correct status is `WARN`, not `INFO`.
