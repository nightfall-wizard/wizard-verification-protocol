# WVP Release-Reality Capability Index v0.1

## Purpose

This document summarizes the implemented capabilities and explicit boundaries of the WVP Release-Reality Check v0.1 subsystem.

Machine-readable source:

`capabilities/wvp-release-reality-capability-index-v0.1.json`

## Implemented capabilities

The subsystem records public GitHub repository and release metadata, including repository visibility, release presence, tag reference presence, release asset names, checksum-like asset presence, detached-signature-like asset presence, public verification key asset presence, SECURITY.md presence, README presence, license presence, and GitHub workflow presence.

## Implemented gates

- `conformance/wvp-release-reality-schema-output-alignment.sh`
- `conformance/wvp-release-reality-deterministic-fixture-gate.sh`
- `conformance/wvp-release-reality-post-merge-verification.sh`
- `conformance/wvp-release-reality-capability-index-gate.sh`

## Deterministic fixtures

- RR-001 repo with release
- RR-002 repo without release
- RR-003 checksum asset without detached signature
- RR-004 detached signature without checksum asset
- RR-005 public verification key without detached signature
- RR-006 missing SECURITY.md
- RR-007 invalid owner/repo format
- RR-008 release API not verifiable

## Hard boundaries

A public verification key is not a detached signature.

Metadata presence is not validation.

Release presence is not an audit.

Checksum asset presence is not checksum validation.

Signature asset presence is not signature validation.

Repository hygiene is not protocol security.

No private keys, seed phrases, wallet secrets, API tokens, custody data or user-funds data are read, printed, uploaded or committed.

## Explicit non-capabilities

This subsystem does not prove audit status, legal clearance, investment quality, custody safety, binary safety, source-to-binary correspondence, reproducible builds, protocol security, checksum correctness, signature correctness, official project status, or malware absence.

## Interpretation

The capability index is a subsystem map. It is not a release approval, audit report, legal review, investment recommendation or custody safety statement.
