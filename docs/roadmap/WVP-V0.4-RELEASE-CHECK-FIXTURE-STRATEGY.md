# WVP v0.4 Release-Check Fixture Strategy

Status: planned.

## Purpose

This document defines the fixture strategy for v0.4 `wvp-release-check` hardening.

Fixtures make release-state behavior reproducible without depending only on live GitHub state.

The strategy supports the v0.4 release-check hardening matrix and prepares later implementation work.

## Safety priority

Legal compliance and safety remain the first constraint.

Fixtures must not contain:

- private keys;
- seed phrases;
- wallet secrets;
- API tokens;
- GitHub tokens;
- personal data;
- custody data;
- trading instructions;
- investment advice.

Fixtures must not create claims of:

- audit completion;
- legal compliance;
- binary safety;
- reproducible build proof;
- source-to-release proof;
- wallet safety;
- investment suitability.

## Planned fixture root

Fixture root:

- fixtures/release-check/

## Planned fixture files

Each future fixture directory should contain:

- input.json;
- expected.json;
- README.md.

## Fixture classes

| Fixture ID | Priority | Name | Expected behavior |
|---|---:|---|---|
| FRC-001 | P0 | valid-signed-release | INFO with checksum and signature verification passing. |
| FRC-002 | P0 | checksum-no-signature | WARN with checksum passing and signature not verified. |
| FRC-003 | P0 | signature-no-public-key | Signature cannot be verified without public key. |
| FRC-004 | P0 | public-key-no-signature | Public key must not count as signature. |
| FRC-005 | P0 | duplicate-checksum | Deterministic ambiguity status. |
| FRC-006 | P0 | duplicate-signature | Deterministic ambiguity status. |
| FRC-007 | P0 | public-key-name-contains-signing | Public signing key asset must not count as signature. |
| FRC-008 | P1 | malformed-asset-names | Deterministic classification result. |
| FRC-009 | P1 | no-assets | Explicit missing-asset status. |
| FRC-010 | P1 | no-releases | Explicit no-release status. |

## Determinism rules

Fixture tests should avoid dependence on:

- current time;
- live GitHub API availability;
- GitHub download counts;
- network success;
- local authentication state;
- local filesystem paths outside the repository.

## Live-vs-fixture boundary

Live checks remain useful for public release verification.

Fixture checks are required for deterministic regression coverage.

A live check failure may indicate:

- GitHub API failure;
- authentication failure;
- network failure;
- release-state failure.

A fixture failure should indicate:

- code behavior changed;
- expected behavior changed;
- fixture is malformed.

## P0 fixture implementation order

1. create `FRC-007` public-key-name-contains-signing fixture;
2. create `FRC-005` duplicate-checksum fixture;
3. create `FRC-006` duplicate-signature fixture;
4. create `FRC-003` signature-no-public-key fixture;
5. create `FRC-004` public-key-no-signature fixture;
6. create `FRC-001` valid-signed-release fixture;
7. wire fixture runner into CI.

## Non-goals

This step does not implement the fixture runner.

This step does not change `wvp-release-check` behavior.

This step does not create:

- a tag;
- a GitHub release;
- a release asset;
- private signing material;
- wallet functionality;
- custody functionality;
- exchange functionality;
- legal certification;
- audit certification.
