# WVP v0.4 Release Readiness Checklist

Status: `prepared-not-released`

This checklist records release-readiness evidence for WVP v0.4. It does not create a release, tag, release asset, audit result, legal clearance, binary safety proof, source-to-release proof, reproducible-build proof, wallet safety claim, or investment advice.

## Release action status

| Action | Status |
|---|---:|
| Git tag created | `no` |
| GitHub release created | `no` |
| GitHub release asset uploaded | `no` |
| Private key added | `no` |
| Custody function introduced | `no` |
| Paid report function introduced | `no` |
| Investment advice function introduced | `no` |

## Required v0.4 evidence already present

| Evidence | Required path |
|---|---|
| v0.4 scope plan | `docs/roadmap/WVP-V0.4-SCOPE-AND-PLAN.md` |
| release-check hardening matrix | `docs/roadmap/WVP-V0.4-RELEASE-CHECK-HARDENING-MATRIX.md` |
| fixture strategy | `docs/roadmap/WVP-V0.4-RELEASE-CHECK-FIXTURE-STRATEGY.md` |
| fixture index | `fixtures/release-check/FIXTURE-INDEX.json` |
| fixture index validator | `conformance/wvp-v040-release-check-fixture-index-validator.sh` |
| fixture runner design | `docs/release-check/WVP-V040-FIXTURE-RUNNER-DESIGN.md` |
| fixture runner skeleton and semantic layer | `conformance/wvp-v040-release-check-fixture-runner-skeleton.sh` |
| semantic coverage guard | `conformance/wvp-v040-release-check-fixture-runner-semantic-coverage-conformance.sh` |
| runner report JSON | `reports/release-check/WVP-V040-FIXTURE-RUNNER-REPORT.json` |
| runner report Markdown | `reports/release-check/WVP-V040-FIXTURE-RUNNER-REPORT.md` |

## Required implemented fixtures

| Fixture | Required state |
|---|---|
| `FRC-003` | implemented and semantically checked |
| `FRC-004` | implemented and semantically checked |
| `FRC-005` | implemented and semantically checked |
| `FRC-006` | implemented and semantically checked |
| `FRC-007` | implemented and semantically checked |

## Required CI gates

| Gate | Required result |
|---|---:|
| Rust format check | `pass` |
| Rust clippy with `-D warnings` | `pass` |
| Rust tests | `pass` |
| release-check fixture strategy conformance | `pass` |
| fixture index validator conformance | `pass` |
| fixture runner skeleton conformance | `pass` |
| fixture runner semantic conformance | `pass` |
| fixture runner semantic coverage conformance | `pass` |
| fixture runner report conformance | `pass` |

## Release blockers before an actual v0.4 release

- Confirm no unintended tag exists for v0.4.
- Confirm no unintended GitHub release exists for v0.4.
- Confirm no unintended release asset exists for v0.4.
- Confirm current `main` CI is green at the intended release commit.
- Confirm report JSON matches live runner output at the intended release commit.
- Confirm all boundary statements remain explicit.
- Confirm no private key, seed phrase, wallet secret, or API token is staged or committed.

## Boundary statements

- This is not an audit.
- This is not legal clearance.
- This is not a binary safety proof.
- This is not a source-to-release proof.
- This is not a reproducible-build proof.
- This is not a wallet safety claim.
- This is not investment advice.

## Interpretation

A future v0.4 release may only be considered after this checklist, CI, report conformance, and release-mutation checks pass at the intended release commit.
