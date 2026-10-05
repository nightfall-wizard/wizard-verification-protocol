# FRC-003 — Signature Without Public Key

Status: implemented as deterministic fixture.

## Purpose

This fixture covers a release-state boundary where a detached signature exists, but no public verification key is present.

A signature cannot be verified without public key material. The release-check result must not silently claim signature verification success in this state.

## Input focus

The input release contains:

- one binary-like asset;
- one checksum-like asset;
- one detached signature asset;
- no public verification key asset.

## Expected result

Expected classification:

- binary asset count: 1;
- checksum asset count: 1;
- signature asset count: 1;
- public verification key asset count: 0;
- signature without public key state: true;
- signature verification must not be claimed;
- missing public key state must not be silent success.

## Boundary

This fixture is not an audit.

It does not prove legal compliance, binary safety, source-to-release correspondence, reproducible builds, consensus correctness, wallet safety, or investment suitability.

It contains no private key, seed phrase, wallet secret, API token, custody data, or trading instruction.
