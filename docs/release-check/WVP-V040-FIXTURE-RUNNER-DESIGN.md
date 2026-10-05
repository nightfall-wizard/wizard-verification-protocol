# WVP v0.4 Release-Check Fixture Runner Design

Status: design anchor.

## Purpose

This document defines the future runner contract for WVP v0.4 release-check fixtures.

It is not a runner implementation.

## Implemented fixture IDs

The design currently binds these deterministic fixtures:

- FRC-003
- FRC-004
- FRC-005
- FRC-006
- FRC-007

## Runner contract

A future runner SHOULD:

- read `fixtures/release-check/FIXTURE-INDEX.json`;
- select fixtures with `status: implemented`;
- require `input.json`, `expected.json`, and `README.md`;
- validate JSON syntax;
- classify fixture input deterministically;
- compare actual classification to expected classification;
- emit human-readable output;
- emit machine-readable JSON output;
- return deterministic exit codes.

## Exit-code model

- `0`: all selected implemented fixtures pass;
- `1`: at least one selected implemented fixture fails;
- `2`: fixture index, fixture structure, or input syntax is invalid.

## Status model

Required status classes:

- `PASS`
- `WARN`
- `FAIL`
- `INFO`
- `OUT_OF_SCOPE`

The runner MUST NOT treat missing signatures, duplicate signatures, duplicate checksums, signature-without-public-key, or public-key-without-signature as silent success.

## Offline boundary

The runner MUST NOT require:

- live GitHub API access;
- GitHub authentication;
- network access;
- paid infrastructure;
- tag creation;
- release creation;
- release asset upload;
- wallet access;
- custody access;
- customer funds;
- investment data.

## Secret boundary

The runner MUST NOT read, print, export, upload, infer, or request:

- seed phrases;
- private keys;
- wallet secrets;
- API tokens;
- exchange credentials;
- custody credentials.

## Non-claims

This design does not claim or prove:

- audit completion;
- legal compliance;
- binary safety;
- source-to-release correspondence;
- reproducible builds;
- consensus correctness;
- wallet safety;
- investment suitability.

## Expected result shape

A future runner SHOULD produce fields equivalent to:

- `wvp_module`
- `suite`
- `status`
- `fixtures_total`
- `fixtures_passed`
- `fixtures_warned`
- `fixtures_failed`
- `claims.audit_claim`
- `claims.legal_compliance_claim`
- `claims.investment_suitability_claim`

## Nightfall boundary

Nightfall may be used as a WVP reference target.

This is not an audit of Nightfall.

This is not a claim that Nightfall is secure, legally cleared, investment-suitable, reproducibly built, or release-verified.

## Implementation boundary

This step intentionally adds only the design contract and CI-backed conformance.

It does not add the generic fixture runner.
