# WVP Release Signing Key Policy

WVP v0.2 introduces public release verification material.

## Purpose

The public verification key allows release signatures to be checked without trusting release metadata alone.

## Private key rule

The private release signing key must stay outside this repository.

The private release signing key must not be committed.

The private release signing key must not be printed in logs.

The private release signing key must not be uploaded as a release asset.

Only public verification material may be committed.

## Current public material

Committed public material:

- `keys/release/wvp-release-signing-public.pem`
- `keys/release/wvp-release-signing-public.pem.sha256`

## Algorithm

Current WVP bootstrap signing path:

- OpenSSL
- RSA-3072
- SHA-256
- detached signature asset

## Scope

This is not an audit.

This does not prove that a release is safe.

This does not prove that a build is reproducible.

This only establishes a public verification key path for later detached signature verification.
