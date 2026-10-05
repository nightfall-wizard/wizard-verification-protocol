# FRC-007 — Public Key Name Contains Signing

Status: implemented as deterministic fixture.

## Purpose

This fixture covers a specific release-check classification risk:

A public verification key asset can contain the word `signing` in its filename, but it must not be counted as a detached signature asset.

## Input focus

The input release contains:

- one binary-like asset;
- one checksum asset;
- one public verification key asset named `wvp-release-signing-public-rsa3072.pem`;
- no detached signature asset.

## Expected result

Expected classification:

- binary asset count: 1;
- checksum asset count: 1;
- signature asset count: 0;
- public verification key asset count: 1;
- public key must not count as signature.

## Boundary

This fixture is not an audit.

It does not prove legal compliance, binary safety, source-to-release correspondence, reproducible builds, consensus correctness, wallet safety, or investment suitability.

It contains no private key, seed phrase, wallet secret, API token, custody data, or trading instruction.
