# FRC-005 — Duplicate Checksum

Status: implemented as deterministic fixture.

## Purpose

This fixture covers duplicate checksum asset ambiguity.

A release containing more than one checksum-like asset must not be treated as a silent success. The implementation may choose `WARN` or `FAIL`, but the state must be deterministic and explicit.

## Input focus

The input release contains:

- one binary-like asset;
- two checksum-like assets;
- one detached signature asset;
- one public verification key asset.

## Expected result

Expected classification:

- binary asset count: 1;
- checksum asset count: 2;
- signature asset count: 1;
- public verification key asset count: 1;
- duplicate checksum state: true;
- checksum state must not be silent success.

## Boundary

This fixture is not an audit.

It does not prove legal compliance, binary safety, source-to-release correspondence, reproducible builds, consensus correctness, wallet safety, or investment suitability.

It contains no private key, seed phrase, wallet secret, API token, custody data, or trading instruction.
