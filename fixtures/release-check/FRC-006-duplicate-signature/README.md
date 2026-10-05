# FRC-006 — Duplicate Signature

Status: implemented as deterministic fixture.

## Purpose

This fixture covers duplicate signature asset ambiguity.

A release containing more than one signature-like asset must not be treated as a silent success. The implementation may choose `WARN` or `FAIL`, but the state must be deterministic and explicit.

## Input focus

The input release contains:

- one binary-like asset;
- one checksum-like asset;
- two signature-like assets;
- one public verification key asset.

## Expected result

Expected classification:

- binary asset count: 1;
- checksum asset count: 1;
- signature asset count: 2;
- public verification key asset count: 1;
- duplicate signature state: true;
- signature state must not be silent success;
- public verification key must not count as signature.

## Boundary

This fixture is not an audit.

It does not prove legal compliance, binary safety, source-to-release correspondence, reproducible builds, consensus correctness, wallet safety, or investment suitability.

It contains no private key, seed phrase, wallet secret, API token, custody data, or trading instruction.
