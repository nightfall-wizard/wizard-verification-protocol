# WVP v0.4.0 Controlled Release Plan

Status: `planned-not-released`

This document describes a controlled plan for a possible future WVP v0.4.0 release. It does not create a tag, GitHub release, release asset, signature, audit result, legal clearance, binary safety proof, source-to-release proof, reproducible-build proof, wallet safety claim, or investment advice.

## Intended release target

| Field | Value |
|---|---|
| Intended version | `v0.4.0` |
| Intended branch | `main` |
| Intended commit at plan creation | `e5d21d8d97d8d7c480478d2e1980d8e4bfbd0a32` |
| Release status | `not released` |
| Tag status | `not created` |
| GitHub release status | `not created` |
| Release asset status | `not uploaded` |
| Signature status | `not created` |

## Required pre-release evidence

| Evidence | Path |
|---|---|
| Final pre-release gate | `docs/release-check/WVP-V040-FINAL-PRE-RELEASE-GATE.md` |
| Release notes draft | `docs/release-check/WVP-V040-RELEASE-NOTES-DRAFT.md` |
| Release readiness checklist | `docs/release-check/WVP-V040-RELEASE-READINESS-CHECKLIST.md` |
| Fixture runner report JSON | `reports/release-check/WVP-V040-FIXTURE-RUNNER-REPORT.json` |
| Fixture runner report Markdown | `reports/release-check/WVP-V040-FIXTURE-RUNNER-REPORT.md` |
| Fixture index | `fixtures/release-check/FIXTURE-INDEX.json` |

## Controlled release sequence for a future manual release

A future manual release should only proceed in this order:

1. Confirm the working tree is clean.
2. Fetch origin and tags.
3. Confirm local `HEAD` equals `origin/main`.
4. Confirm the intended release commit is the latest green `main` commit.
5. Confirm all v0.4 CI gates pass.
6. Confirm no `v0.4.0` tag exists.
7. Confirm no `v0.4.0` GitHub release exists.
8. Confirm no private key, seed phrase, wallet secret, or API token is staged or committed.
9. Confirm final pre-release gate conformance passes.
10. Confirm release notes draft conformance passes.
11. Confirm release readiness checklist conformance passes.
12. Only after all checks pass, create the tag and release in a separate explicit release step.

## Required CI gates before any future release action

- Rust format check.
- Rust clippy with `-D warnings`.
- Rust tests.
- WVP v0.4 scope plan conformance.
- WVP v0.4 release-check hardening matrix conformance.
- WVP v0.4 release-check fixture strategy conformance.
- WVP v0.4 FRC-003 conformance.
- WVP v0.4 FRC-004 conformance.
- WVP v0.4 FRC-005 conformance.
- WVP v0.4 FRC-006 conformance.
- WVP v0.4 FRC-007 conformance.
- WVP v0.4 fixture runner design conformance.
- WVP v0.4 fixture index validator conformance.
- WVP v0.4 fixture runner skeleton conformance.
- WVP v0.4 fixture runner semantic conformance.
- WVP v0.4 fixture runner semantic coverage conformance.
- WVP v0.4 fixture runner report conformance.
- WVP v0.4 release readiness checklist conformance.
- WVP v0.4 release notes draft conformance.
- WVP v0.4 final pre-release gate conformance.
- WVP v0.4 controlled release plan conformance.

## Explicit non-claims

- This is not an audit.
- This is not legal clearance.
- This is not a binary safety proof.
- This is not a source-to-release proof.
- This is not a reproducible-build proof.
- This is not a wallet safety claim.
- This is not investment advice.
- This is not a custody, broker, exchange, or paid-report function.

## Release action status

| Action | Status |
|---|---:|
| v0.4.0 Git tag created | `no` |
| v0.4.0 GitHub release created | `no` |
| v0.4.0 GitHub release asset uploaded | `no` |
| Private key added | `no` |
| Signature created | `no` |

## Legal and operational boundary

This plan is a preparation artifact only. Any real public release action must be explicit, separate, intentional, and checked again at the actual release commit.
