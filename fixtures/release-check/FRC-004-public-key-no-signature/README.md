# FRC-004 — Public Key Without Signature

Status: implemented as deterministic fixture.

## Purpose

This fixture covers a release-state boundary where a public verification key exists, but no detached signature asset exists.

A public verification key is not a detached signature. The release-check result must not count the public key as a signature and must not claim signature verification success.

## Input focus

The input release contains:

- one binary-like asset;
- one checksum-like asset;
- one public verification key asset;
- no detached signature asset.

## Expected result

Expected classification:

- binary asset count: 1;
- checksum asset count: 1;
- signature asset count: 0;
- public verification key asset count: 1;
- public key without signature state: true;
- public key must not count as signature;
- signature verification must not be claimed;
- missing signature state must not be silent success.

## Boundary

This fixture is not an audit.

It does not prove legal compliance, binary safety, source-to-release correspondence, reproducible builds, consensus correctness, wallet safety, or investment suitability.

It contains no private key, seed phrase, wallet secret, API token, custody data, or trading instruction.
