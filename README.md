# Wizard Verification Protocol — WVP

Built by nightfall-wizard.

## Category

Proof-of-Project-Reality

## Core Sentence

Wizard Verification Protocol turns project claims into verifiable reality.

## Adversarial Principle

No claim without proof. No proof without reproduction. No verification without adversarial testing.

## Purpose

WVP is a mobile-built, zero-budget verification standard for checking whether crypto and open-source projects are technically, organizationally and economically real.

## Schelling Point Goal

When someone wants to verify whether a project is real, they should think of WVP.

Without WVP, a project check is incomplete.

## Current Status

Bootstrap implementation in progress.

## Current Modules

- wvp-release-check
- wvp-scorecard
- wvp-node-diagnose
- wvp-conformance
- wvp-light-verify

<!-- WVP:ANDROID-VS-CI-CONFORMANCE:START -->
## Android vs CI Build Provenance Conformance

WVP includes a local, authenticated Android-vs-CI conformance command:

    ./conformance/release-check-android-vs-ci-build-provenance.sh

This command downloads the GitHub Actions build-provenance artifact for the checked-out commit, generates a fresh Android-Termux artifact locally, compares both artifacts, and validates that the result stays within the correct claim boundary.

It verifies:

- same source commit;
- same package version;
- same Cargo.lock hash;
- Android-Termux and GitHub Actions are separate environment classes;
- cross-architecture binary differences are not treated as failure;
- no reproducible-build claim is made.

It does not prove:

- binary safety;
- source-to-release correspondence;
- full reproducible builds;
- audit status.
<!-- WVP:ANDROID-VS-CI-CONFORMANCE:END -->


<!-- WVP:V040-PUBLIC-STATUS:START -->
## WVP v0.4 Public Status

Status: `prepared-not-released`

WVP v0.4 release preparation is complete, but v0.4.0 has not been released.

Current public interpretation:

- v0.4 release evidence has been prepared.
- v0.4 release notes draft exists.
- v0.4 final pre-release gate exists.
- v0.4 controlled release plan exists.
- v0.4 pre-release preparation is intentionally stopped before release execution.
- A real v0.4.0 release requires a separate explicit release execution step.

Release action status:

| Action | Status |
|---|---:|
| v0.4.0 Git tag created | `no` |
| v0.4.0 GitHub release created | `no` |
| v0.4.0 GitHub release asset uploaded | `no` |
| Private key added | `no` |
| Signature created | `no` |

Prepared evidence:

- `docs/release-check/WVP-V040-PRE-RELEASE-PREP-STOP-MARKER.md`
- `docs/release-check/WVP-V040-CONTROLLED-RELEASE-PLAN.md`
- `docs/release-check/WVP-V040-FINAL-PRE-RELEASE-GATE.md`
- `docs/release-check/WVP-V040-RELEASE-NOTES-DRAFT.md`
- `docs/release-check/WVP-V040-RELEASE-READINESS-CHECKLIST.md`
- `reports/release-check/WVP-V040-FIXTURE-RUNNER-REPORT.json`
- `reports/release-check/WVP-V040-FIXTURE-RUNNER-REPORT.md`
- `fixtures/release-check/FIXTURE-INDEX.json`

Reference commit at status alignment:

- `1b6bfadbab943f023871f8adedc04982b580980e`

Explicit non-claims:

- This is not an audit.
- This is not legal clearance.
- This is not a binary safety proof.
- This is not a source-to-release proof.
- This is not a reproducible-build proof.
- This is not a wallet safety claim.
- This is not investment advice.
- This is not a custody, broker, exchange, or paid-report function.
<!-- WVP:V040-PUBLIC-STATUS:END -->

<!-- WVP:AUNEYA-PROTOCOL-CHARTER:START -->
## AUNEYA Protocol Charter

AUNEYA is the working architecture for a phone-first witness network for the provable web.

WVP remains the technical verification core.

AUNEYA is currently documented as non-value protocol research and simulation only.

Documents:

- `docs/auneya/AUNEYA-PROTOCOL-CHARTER.md`
- `docs/auneya/AUNEYA-PROVABLE-WEB-SCOPE.md`
- `docs/auneya/AUNEYA-NON-VALUE-SIMULATION-NOTICE.md`

Explicit non-claims:

- No token is created by this step.
- No token sale is offered.
- No market value is claimed.
- No return, profit, yield or financial outcome is offered or promised.
- Legal review is required before any public token launch, listing, sale, transferability or market-value communication.
<!-- WVP:AUNEYA-PROTOCOL-CHARTER:END -->

<!-- WVP:AUNEYA-CLAIM-SCHEMA-V01:START -->
## AUNEYA Claim Schema v0.1

AUNEYA Claim Schema v0.1 defines the first machine-readable claim format for the provable web.

It defines:

- claim identity
- claim type
- lawful public target
- evidence requirements
- expiry policy
- legal boundary
- non-value notice

Files:

- `schemas/auneya-claim-v0.1.schema.json`
- `docs/auneya/AUNEYA-CLAIM-SCHEMA-V0.1.md`
- `fixtures/auneya/claims/`
- `conformance/auneya-claim-schema-v0.1.sh`

Explicit non-claims:

- No token is created by this schema.
- No reward is created by this schema.
- No market value is claimed.
- Legal review is required before any public token launch, listing, sale, transferability or market-value communication.
<!-- WVP:AUNEYA-CLAIM-SCHEMA-V01:END -->

