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

<!-- WVP:AUNEYA-WITNESS-PROOF-SCHEMA-V01:START -->
## AUNEYA Witness Proof Schema v0.1

AUNEYA Witness Proof Schema v0.1 defines the first machine-readable proof format for checked lawful public claims.

It defines:

- proof identity
- claim reference
- witness identity class
- observed status
- evidence hashes
- lawful boundary confirmation
- timing metadata
- proof integrity metadata

Files:

- `schemas/auneya-witness-proof-v0.1.schema.json`
- `docs/auneya/AUNEYA-WITNESS-PROOF-SCHEMA-V0.1.md`
- `fixtures/auneya/witness-proofs/`
- `conformance/auneya-witness-proof-schema-v0.1.sh`

Explicit non-claims:

- No token is created by this schema.
- No reward is created by this schema.
- No market value is claimed.
- Legal review is required before any public token launch, listing, sale, transferability or market-value communication.
<!-- WVP:AUNEYA-WITNESS-PROOF-SCHEMA-V01:END -->

<!-- WVP:AUNEYA-EVENT-SCHEMA-V01:START -->
## AUNEYA Event Schema v0.1

AUNEYA Event Schema v0.1 defines how multiple lawful witness proofs for the same public claim form an Auneya Event.

It defines:

- event identity
- claim reference
- witness proof references
- quorum rules
- independent witness count
- event status
- lawful boundary confirmation
- event integrity metadata

Files:

- `schemas/auneya-event-v0.1.schema.json`
- `docs/auneya/AUNEYA-EVENT-SCHEMA-V0.1.md`
- `fixtures/auneya/events/`
- `conformance/auneya-event-schema-v0.1.sh`

Explicit non-claims:

- No token is created by this schema.
- No reward is created by this schema.
- No market value is claimed.
- Legal review is required before any public token launch, listing, sale, transferability or market-value communication.
<!-- WVP:AUNEYA-EVENT-SCHEMA-V01:END -->

<!-- WVP:AUNEYA-PULSE-FLOW-V01:START -->
## AUNEYA Pulse and Prooflet Flow v0.1

AUNEYA Pulse and Prooflet Flow v0.1 defines the first phone-first witness loop.

It defines:

- one-second Pulse cadence
- Micro-Proof grouping
- Prooflet creation
- lawful public boundary checks
- non-value simulated reward entries

Files:

- `schemas/auneya-pulse-flow-v0.1.schema.json`
- `docs/auneya/AUNEYA-PULSE-AND-PROOFLET-FLOW-V0.1.md`
- `fixtures/auneya/pulse-flow/`
- `conformance/auneya-pulse-flow-v0.1.sh`

Explicit non-claims:

- No token is created by this schema.
- No real reward is created by this schema.
- No market value is claimed.
- Simulated reward entries are non-transferable and non-value only.
- Legal review is required before any public token launch, listing, sale, transferability or market-value communication.
<!-- WVP:AUNEYA-PULSE-FLOW-V01:END -->

<!-- WVP:AUNEYA-LOCAL-WITNESS-RUNNER-V01:START -->
## AUNEYA Local Witness Runner v0.1

AUNEYA Local Witness Runner v0.1 generates a local non-value pulse-flow report from a lawful public claim fixture.

It defines:

- Termux-local witness execution
- lawful claim rejection
- Pulse generation
- Micro-Proof generation
- Prooflet generation
- non-value simulated reward entry generation

Files:

- `tools/auneya/auneya_local_witness_runner.py`
- `docs/auneya/AUNEYA-LOCAL-WITNESS-RUNNER-V0.1.md`
- `fixtures/auneya/local-runner/example-local-witness-flow.json`
- `conformance/auneya-local-witness-runner-v0.1.sh`

Explicit non-claims:

- No token is created by this runner.
- No real reward is created by this runner.
- No market value is claimed.
- No mainnet is activated.
- Simulated reward entries are non-transferable and non-value only.
- Legal review is required before any public token launch, listing, sale, transferability or market-value communication.
<!-- WVP:AUNEYA-LOCAL-WITNESS-RUNNER-V01:END -->

<!-- WVP:AUNEYA-LOCAL-WITNESS-CLI-DISPLAY-V01:START -->
## AUNEYA Local Witness CLI Display v0.1

AUNEYA Local Witness CLI Display v0.1 prints a clean Termux status view from a local non-value pulse-flow report.

It shows:

- local non-value simulation mode
- claim identity
- witness identity
- pulse count
- micro-proof count
- prooflet identity
- simulated non-value entry
- legal boundary confirmations

Files:

- `tools/auneya/auneya_local_witness_display.py`
- `docs/auneya/AUNEYA-LOCAL-WITNESS-CLI-DISPLAY-V0.1.md`
- `fixtures/auneya/local-runner/example-local-witness-display.txt`
- `conformance/auneya-local-witness-display-v0.1.sh`

Explicit non-claims:

- No token is created by this display.
- No real reward is created by this display.
- No market value is claimed.
- No mainnet is activated.
- Simulated entries are non-transferable and non-value only.
- Legal review is required before any public token launch, listing, sale, transferability or market-value communication.
<!-- WVP:AUNEYA-LOCAL-WITNESS-CLI-DISPLAY-V01:END -->

<!-- WVP:AUNEYA-ONE-COMMAND-LOCAL-DEMO-V01:START -->
## AUNEYA One-Command Local Demo v0.1

AUNEYA One-Command Local Demo v0.1 runs the local witness runner and local witness CLI display in one Termux-compatible command.

It shows:

- local non-value simulation mode
- local claim processing
- Pulse generation
- Micro-Proof generation
- Prooflet generation
- local display output
- explicit non-value boundaries

Command:

`./tools/auneya/auneya_one_command_local_demo.sh`

Files:

- `tools/auneya/auneya_one_command_local_demo.sh`
- `docs/auneya/AUNEYA-ONE-COMMAND-LOCAL-DEMO-V0.1.md`
- `fixtures/auneya/local-runner/example-one-command-local-demo.txt`
- `conformance/auneya-one-command-local-demo-v0.1.sh`

Explicit non-claims:

- No token is created by this demo.
- No real reward is created by this demo.
- No market value is claimed.
- No mainnet is activated.
- Simulated entries are non-transferable and non-value only.
- Legal review is required before any public token launch, listing, sale, transferability or market-value communication.
<!-- WVP:AUNEYA-ONE-COMMAND-LOCAL-DEMO-V01:END -->

<!-- WVP:AUNEYA-LOCAL-DEMO-QUICKSTART-V01:START -->
## AUNEYA Local Demo Quickstart v0.1

Run the local AUNEYA demo from Termux:

`./tools/auneya/auneya_one_command_local_demo.sh`

This runs:

- local claim fixture processing
- local Pulse generation
- local Micro-Proof generation
- local Prooflet generation
- local CLI display output

Self-check:

`./conformance/auneya-local-demo-quickstart-v0.1.sh`

Files:

- `docs/auneya/AUNEYA-LOCAL-DEMO-QUICKSTART-V0.1.md`
- `fixtures/auneya/local-runner/example-local-demo-quickstart.txt`
- `conformance/auneya-local-demo-quickstart-v0.1.sh`

Explicit non-claims:

- No token is created by this quickstart.
- No AUNEYA is created by this quickstart.
- No neya is created by this quickstart.
- No real reward is created by this quickstart.
- No market value is claimed.
- No mainnet is activated.
- Simulated entries are non-transferable and non-value only.
- Legal review is required before any public token launch, listing, sale, transferability or market-value communication.
<!-- WVP:AUNEYA-LOCAL-DEMO-QUICKSTART-V01:END -->

<!-- WVP:AUNEYA-LOCAL-CLAIM-SELECTION-V01:START -->
## AUNEYA Local Claim Selection v0.1

Choose a supported lawful public claim fixture from Termux:

`python3 tools/auneya/auneya_local_claim_select.py --list`

Run the local demo with a selected claim:

`python3 tools/auneya/auneya_local_claim_select.py --claim-key release-reality --run-demo`

Supported local claim keys:

- `release-reality`
- `download-integrity`
- `website-claim-reality`

Self-check:

`./conformance/auneya-local-claim-selection-v0.1.sh`

Files:

- `tools/auneya/auneya_local_claim_select.py`
- `docs/auneya/AUNEYA-LOCAL-CLAIM-SELECTION-V0.1.md`
- `fixtures/auneya/local-runner/example-local-claim-selection-list.txt`
- `fixtures/auneya/local-runner/example-local-claim-selection-demo.txt`
- `conformance/auneya-local-claim-selection-v0.1.sh`

Explicit non-claims:

- No token is created by this selector.
- No AUNEYA is created by this selector.
- No neya is created by this selector.
- No real reward is created by this selector.
- No market value is claimed.
- No mainnet is activated.
- Simulated entries are non-transferable and non-value only.
- Legal review is required before any public token launch, listing, sale, transferability or market-value communication.
<!-- WVP:AUNEYA-LOCAL-CLAIM-SELECTION-V01:END -->

