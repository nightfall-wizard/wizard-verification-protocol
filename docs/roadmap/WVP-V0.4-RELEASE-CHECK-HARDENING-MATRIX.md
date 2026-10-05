# WVP v0.4 Release-Check Hardening Issue Matrix

Status: planned.

## Purpose

This document translates the v0.4 `wvp-release-check` hardening track into concrete implementation issues.

The goal is not to add new release claims. The goal is to make release-state inspection stricter, more deterministic, easier to test, and harder to misinterpret.

## Priority rule

Legal compliance and safety remain the first constraint.

This hardening matrix must not introduce:

- custody functionality;
- exchange, broker, or trading functionality;
- investment advice automation;
- private-key collection;
- seed phrase collection;
- wallet-spending automation;
- legal-compliance guarantees;
- audit claims;
- binary-safety claims;
- reproducible-build claims;
- source-to-release proof claims.

## Issue matrix

| ID | Priority | Area | Problem | Planned outcome | Evidence |
|---|---:|---|---|---|---|
| RCH-001 | P0 | Asset classification | Signature asset detection must only count real signature-like assets. | Suffix-based classification for `.sig`, `.asc`, `.minisig`, `.gpg`, or `.signature`. | Unit tests and live conformance. |
| RCH-002 | P0 | Public key handling | Public verification key must not be counted as a signature asset. | Public key asset is separate from signature asset classification. | Negative fixture. |
| RCH-003 | P0 | Duplicate assets | Multiple checksum or signature assets can create ambiguous verification state. | Fail or warn deterministically when duplicate critical assets exist. | Unit tests. |
| RCH-004 | P0 | Missing assets | Missing checksum, signature, or public key should not be silently accepted. | Explicit status and error fields for each missing critical artifact. | Positive and negative fixtures. |
| RCH-005 | P1 | JSON stability | Output must be deterministic enough for conformance tests. | Stable fields, stable status model, stable limitation text. | Fixture snapshots. |
| RCH-006 | P1 | Status taxonomy | INFO/WARN/FAIL must be easier to reason about. | Documented status rules for release found, asset found, checksum verified, signature verified. | Documentation and tests. |
| RCH-007 | P1 | Error reporting | Verification errors must be clear without leaking secrets. | Error strings describe failure class, not private material. | Negative tests. |
| RCH-008 | P1 | GitHub CLI dependency | Live inspection depends on external GitHub CLI/API state. | Better separation between local fixtures and live GitHub checks. | Offline fixture conformance. |
| RCH-009 | P2 | Network failures | GitHub/API/download failures can look like release failures. | Distinguish network/tooling failure from release-integrity failure. | Simulated failure fixture. |
| RCH-010 | P2 | Documentation | Users must not confuse metadata inspection with an audit. | Stronger limitation text in docs and output. | Conformance grep checks. |

## P0 implementation order

Recommended P0 order:

1. lock down asset classification rules;
2. add fixture for public key not counted as signature;
3. add duplicate checksum/signature negative fixtures;
4. add missing public key negative fixture;
5. update status output only after fixtures exist;
6. wire conformance into CI.

## Required test classes

v0.4 release-check hardening should include these test classes:

- valid release with checksum, detached signature, and public key;
- release with checksum but no signature;
- release with signature but no public key;
- release with public key but no signature;
- release with duplicate checksum files;
- release with duplicate signature files;
- release with public key name containing `signing`;
- release with malformed asset names;
- release with no assets;
- repository with no releases.

## Status boundary

The hardening work may improve classification and diagnostics.

It still must not claim:

- audit result;
- legal compliance;
- binary safety;
- source-to-release correspondence;
- reproducible build;
- consensus correctness;
- wallet safety;
- investment suitability.

## Exit criteria

This matrix is complete enough when:

- every P0 issue has a fixture or test plan;
- every P0 issue has a conformance expectation;
- limitations remain explicit;
- CI covers the matrix document;
- no private key, seed phrase, token, or wallet secret is added.

## Non-goals

This matrix does not implement the fixes by itself.

It does not create:

- a tag;
- a GitHub release;
- a release asset;
- a private signing key;
- wallet functionality;
- custody functionality;
- exchange functionality;
- legal certification;
- security audit certification.
