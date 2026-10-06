# AUNEYA

AUNEYA is the working architecture for a phone-first witness network for the provable web.

WVP remains the technical verification core.

## Documents

- `AUNEYA-PROTOCOL-CHARTER.md`
- `AUNEYA-PROVABLE-WEB-SCOPE.md`
- `AUNEYA-NON-VALUE-SIMULATION-NOTICE.md`

## Legal Status

AUNEYA is a working name.

Trademark clearance is pending.

No token is created by these documents.

No market value is claimed.

No return, profit, yield or financial outcome is offered or promised.

Legal review is required before any public token launch, listing, sale, transferability or market-value communication.

## Claim Schema

- `AUNEYA-CLAIM-SCHEMA-V0.1.md`
- `../../schemas/auneya-claim-v0.1.schema.json`
- `../../conformance/auneya-claim-schema-v0.1.sh`

The claim schema defines the first machine-readable AUNEYA claim format for the provable web.

## Witness Proof Schema

- `AUNEYA-WITNESS-PROOF-SCHEMA-V0.1.md`
- `../../schemas/auneya-witness-proof-v0.1.schema.json`
- `../../conformance/auneya-witness-proof-schema-v0.1.sh`

The witness proof schema defines the first machine-readable AUNEYA proof format produced after a lawful public claim is checked.

## Event Schema

- `AUNEYA-EVENT-SCHEMA-V0.1.md`
- `../../schemas/auneya-event-v0.1.schema.json`
- `../../conformance/auneya-event-schema-v0.1.sh`

The event schema defines how multiple lawful witness proofs for the same claim form an Auneya Event.

## Pulse and Prooflet Flow

- `AUNEYA-PULSE-AND-PROOFLET-FLOW-V0.1.md`
- `../../schemas/auneya-pulse-flow-v0.1.schema.json`
- `../../conformance/auneya-pulse-flow-v0.1.sh`

The pulse flow defines the first phone-first witness loop: Pulse -> Micro-Proof -> Prooflet.

## Local Witness Runner

- `AUNEYA-LOCAL-WITNESS-RUNNER-V0.1.md`
- `../../tools/auneya/auneya_local_witness_runner.py`
- `../../conformance/auneya-local-witness-runner-v0.1.sh`

The local witness runner generates a local non-value pulse-flow report from a lawful public claim fixture.

## Local Witness CLI Display

- `AUNEYA-LOCAL-WITNESS-CLI-DISPLAY-V0.1.md`
- `../../tools/auneya/auneya_local_witness_display.py`
- `../../fixtures/auneya/local-runner/example-local-witness-display.txt`
- `../../conformance/auneya-local-witness-display-v0.1.sh`

The local witness CLI display prints a clean Termux status view from a local non-value pulse-flow report.

## One-Command Local Demo

- `AUNEYA-ONE-COMMAND-LOCAL-DEMO-V0.1.md`
- `../../tools/auneya/auneya_one_command_local_demo.sh`
- `../../fixtures/auneya/local-runner/example-one-command-local-demo.txt`
- `../../conformance/auneya-one-command-local-demo-v0.1.sh`

The one-command local demo runs the local witness runner and CLI display in one Termux-compatible command.

## Local Demo Quickstart

- `AUNEYA-LOCAL-DEMO-QUICKSTART-V0.1.md`
- `../../fixtures/auneya/local-runner/example-local-demo-quickstart.txt`
- `../../conformance/auneya-local-demo-quickstart-v0.1.sh`

The local demo quickstart explains how to run the one-command local AUNEYA demo from Termux.

## Local Claim Selection

- `AUNEYA-LOCAL-CLAIM-SELECTION-V0.1.md`
- `../../tools/auneya/auneya_local_claim_select.py`
- `../../fixtures/auneya/local-runner/example-local-claim-selection-list.txt`
- `../../fixtures/auneya/local-runner/example-local-claim-selection-demo.txt`
- `../../conformance/auneya-local-claim-selection-v0.1.sh`

The local claim selector lets a Termux user choose between supported lawful public claim fixtures before running the local demo.

## Local Collection Ledger Simulation

- `AUNEYA-LOCAL-COLLECTION-LEDGER-SIMULATION-V0.1.md`
- `../../tools/auneya/auneya_local_collection_ledger.py`
- `../../fixtures/auneya/local-runner/example-local-collection-ledger.json`
- `../../fixtures/auneya/local-runner/example-local-collection-ledger-record.txt`
- `../../fixtures/auneya/local-runner/example-local-collection-ledger-show.txt`
- `../../conformance/auneya-local-collection-ledger-simulation-v0.1.sh`

The local collection ledger simulation persistently counts local non-value simulated entries without creating AUNEYA, neya, market value or transferability.

## Local Collection Status Display

- `AUNEYA-LOCAL-COLLECTION-STATUS-DISPLAY-V0.1.md`
- `../../tools/auneya/auneya_local_collection_status.py`
- `../../fixtures/auneya/local-runner/example-local-collection-status-display.txt`
- `../../fixtures/auneya/local-runner/example-local-collection-status-compact.txt`
- `../../conformance/auneya-local-collection-status-display-v0.1.sh`

The local collection status display shows local simulated collection totals in a clean Termux view without creating AUNEYA, neya, market value or transferability.

## Local Collect Command

- `AUNEYA-LOCAL-COLLECT-COMMAND-V0.1.md`
- `../../tools/auneya/auneya_local_collect.sh`
- `../../fixtures/auneya/local-runner/example-local-collect-command.txt`
- `../../fixtures/auneya/local-runner/example-local-collect-ledger.json`
- `../../conformance/auneya-local-collect-command-v0.1.sh`

The local collect command records and displays a local non-value simulated collection entry with one Termux command.
