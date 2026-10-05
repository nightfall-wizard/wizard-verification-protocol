# WVP v0.4 Capabilities and Usage Guide

Status: `usable-prepared-not-released`

WVP v0.4 is a prepared release-check verification track. It is usable as a CI-backed release-hygiene and fixture-conformance system, but v0.4.0 has not been released.

## What WVP v0.4 can do

WVP v0.4 can help a maintainer inspect and document release-check states for GitHub-hosted software projects.

It can:

- check GitHub release metadata;
- inspect release asset naming and release-check evidence;
- distinguish checksum assets from signature assets;
- distinguish public verification key assets from signature assets;
- flag missing-signature states;
- flag signature-without-public-key states;
- flag public-key-without-signature states;
- flag duplicate-checksum states;
- flag duplicate-signature states;
- avoid treating a public key name containing `signing` as a signature fixture;
- validate the release-check fixture index;
- run deterministic fixture conformance checks;
- run a generic fixture runner;
- run semantic classification checks for implemented required fixtures;
- expose unchecked semantic expected keys;
- produce a fixture runner report in JSON and Markdown;
- preserve offline, read-only, non-mutating execution boundaries;
- document release readiness without creating a release.

## Implemented required fixtures

- `FRC-003`
- `FRC-004`
- `FRC-005`
- `FRC-006`
- `FRC-007`

## Main v0.4 artifacts

- `README.md`
- `fixtures/release-check/FIXTURE-INDEX.json`
- `docs/release-check/WVP-V040-FIXTURE-RUNNER-DESIGN.md`
- `reports/release-check/WVP-V040-FIXTURE-RUNNER-REPORT.json`
- `reports/release-check/WVP-V040-FIXTURE-RUNNER-REPORT.md`
- `docs/release-check/WVP-V040-RELEASE-READINESS-CHECKLIST.md`
- `docs/release-check/WVP-V040-RELEASE-NOTES-DRAFT.md`
- `docs/release-check/WVP-V040-FINAL-PRE-RELEASE-GATE.md`
- `docs/release-check/WVP-V040-CONTROLLED-RELEASE-PLAN.md`
- `docs/release-check/WVP-V040-PRE-RELEASE-PREP-STOP-MARKER.md`

## Practical local usage

Run the Rust release-check help output:

    cargo run --manifest-path reference/rust/wvp-release-check/Cargo.toml -- --help

Run the full Rust checks:

    cargo fmt --manifest-path reference/rust/wvp-release-check/Cargo.toml -- --check
    cargo clippy --manifest-path reference/rust/wvp-release-check/Cargo.toml -- -D warnings
    cargo test --manifest-path reference/rust/wvp-release-check/Cargo.toml
    cargo build --release --locked --manifest-path reference/rust/wvp-release-check/Cargo.toml

Run the v0.4 fixture runner report conformance:

    ./conformance/wvp-v040-release-check-fixture-runner-report-conformance.sh

Run the semantic coverage guard:

    ./conformance/wvp-v040-release-check-fixture-runner-semantic-coverage-conformance.sh

Run the public status alignment check:

    ./conformance/wvp-v040-public-status-alignment-conformance.sh

## Practical interpretation

If CI is green, WVP v0.4 currently means:

- the release-check implementation builds;
- Rust formatting, clippy, tests, and release build pass;
- fixture index structure is checked;
- implemented required fixtures are covered;
- semantic expected keys for implemented required fixtures are checked;
- the runner report matches live runner output;
- public documentation states the prepared-not-released status;
- no v0.4.0 tag or GitHub release is created by these preparation steps.

## What WVP v0.4 cannot do

WVP v0.4 cannot prove that a target project is secure.

It does not:

- audit the full target codebase;
- prove legal clearance;
- prove binary safety;
- prove source-to-release equivalence;
- prove reproducible builds;
- prove wallet safety;
- prove economic value;
- prove asset suitability for any financial objective;
- provide custody, broker, exchange, or paid-report functionality;
- create or manage private keys;
- create a release signature;
- create a v0.4.0 tag;
- create a v0.4.0 GitHub release;
- upload a v0.4.0 GitHub release asset.

## Correct use

Use WVP v0.4 as release-hygiene evidence.

A correct use is:

- inspect whether release metadata and assets are internally consistent;
- detect missing or ambiguous release-check states;
- document what has been observed;
- document what has not been verified;
- run the same checks locally and in GitHub Actions;
- keep audit, legal, binary, reproducible-build, wallet, and investment claims out of the result.

## Incorrect use

Do not use WVP v0.4 to claim:

- a project is audited;
- a project is legally cleared;
- binaries are safe;
- source-to-release equivalence is proven;
- reproducible builds are proven;
- wallets are safe;
- an asset has acceptable investment risk;
- a release is complete when only preparation evidence exists.

## Explicit non-claims

- This is not an audit.
- This is not legal clearance.
- This is not a binary safety proof.
- This is not a source-to-release proof.
- This is not a reproducible-build proof.
- This is not a wallet safety claim.
- This is not investment advice.
- This is not a custody, broker, exchange, or paid-report function.

## Release status

| Action | Status |
|---|---:|
| v0.4.0 Git tag created | `no` |
| v0.4.0 GitHub release created | `no` |
| v0.4.0 GitHub release asset uploaded | `no` |
| Private key added | `no` |
| Signature created | `no` |

## Operational next state

The correct next state after this guide is to stop and observe.

A real v0.4.0 release must be a separate explicit release execution step. It must not be implied by this guide, the README public status block, release notes draft, final pre-release gate, controlled release plan, or stop marker.
