# WVP v0.4.1 Adversarial Fixture Matrix

## Purpose

This gate hardens the release-check fixture layer against silent success.

It checks that implemented adversarial fixtures remain deterministic, offline, non-mutating, and explicitly negative when release evidence is incomplete, ambiguous, duplicated, or easy to misclassify.

## Fixtures covered

- FRC-003: signature without public verification key
- FRC-004: public verification key without signature
- FRC-005: duplicate checksum evidence
- FRC-006: duplicate signature evidence
- FRC-007: public-key filename contains `signing` but must not count as a signature

## Required security boundaries

The gate requires every implemented adversarial fixture to preserve:

- no audit claim
- no legal-compliance claim
- no binary-safety claim
- no source-to-release claim
- no reproducible-build claim
- no wallet-safety claim
- no investment-suitability claim

## Required execution boundaries

The gate also requires:

- deterministic fixture behavior
- no live GitHub dependency
- no network requirement
- no authentication requirement
- no private key
- no wallet secret
- no seed phrase
- no API token
- no custody functionality
- no release mutation

## Non-claims

This gate does not prove binary safety, reproducible builds, source-to-release equivalence, legal compliance, wallet safety, or investment quality.

It only proves that adversarial release-evidence fixtures are represented and checked in a way that prevents obvious silent-success failure modes.
