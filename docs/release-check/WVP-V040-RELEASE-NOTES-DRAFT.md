# WVP v0.4 Release Notes Draft

Status: `draft-not-released`

These are draft release notes for a possible future WVP v0.4 release. This file does not create a tag, GitHub release, release asset, signature, audit result, legal clearance, binary safety proof, source-to-release proof, reproducible-build proof, wallet safety claim, or investment advice.

## Draft title

WVP v0.4 — Release-check fixture hardening, semantic runner coverage, and release-readiness evidence

## Draft summary

WVP v0.4 strengthens the release-check track with deterministic fixture coverage, a generic fixture runner, semantic classification checks, a generated runner report, and release-readiness documentation.

The work remains offline, read-only, and non-mutating. It is designed to document what is checked, what is not checked, and which claims are intentionally not made.

## Included draft highlights

- v0.4 scope and plan documented.
- Release-check hardening matrix documented.
- Release-check fixture strategy documented.
- Fixture index validator added.
- Required implemented fixtures covered:
  - `FRC-003`
  - `FRC-004`
  - `FRC-005`
  - `FRC-006`
  - `FRC-007`
- Generic fixture runner skeleton added.
- Semantic classification layer added.
- Semantic coverage guard added.
- Runner report JSON and Markdown artifacts added.
- Release-readiness checklist added.

## CI-backed evidence

The intended v0.4 release candidate must pass these CI gates before any future release action:

- Rust format check.
- Rust clippy with `-D warnings`.
- Rust tests.
- v0.4 scope plan conformance.
- v0.4 release-check hardening matrix conformance.
- v0.4 fixture strategy conformance.
- v0.4 fixture index validator conformance.
- v0.4 fixture runner skeleton conformance.
- v0.4 fixture runner semantic conformance.
- v0.4 fixture runner semantic coverage conformance.
- v0.4 fixture runner report conformance.
- v0.4 release readiness checklist conformance.
- v0.4 release notes draft conformance.

## Draft artifact references

- `docs/roadmap/WVP-V0.4-SCOPE-AND-PLAN.md`
- `docs/roadmap/WVP-V0.4-RELEASE-CHECK-HARDENING-MATRIX.md`
- `docs/roadmap/WVP-V0.4-RELEASE-CHECK-FIXTURE-STRATEGY.md`
- `fixtures/release-check/FIXTURE-INDEX.json`
- `docs/release-check/WVP-V040-FIXTURE-RUNNER-DESIGN.md`
- `conformance/wvp-v040-release-check-fixture-runner-skeleton.sh`
- `conformance/wvp-v040-release-check-fixture-runner-semantic-coverage-conformance.sh`
- `reports/release-check/WVP-V040-FIXTURE-RUNNER-REPORT.json`
- `reports/release-check/WVP-V040-FIXTURE-RUNNER-REPORT.md`
- `docs/release-check/WVP-V040-RELEASE-READINESS-CHECKLIST.md`

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

## Before any future v0.4 release

Before any future v0.4 release is created, the maintainer should confirm:

- the intended release commit is the current green `main` commit;
- the v0.4 release-readiness checklist passes;
- the runner report matches live runner output;
- no v0.4.0 tag exists before the release action;
- no v0.4.0 GitHub release exists before the release action;
- no private key, seed phrase, wallet secret, or API token is staged or committed;
- boundary statements remain explicit.
