# AUNEYA Local Demo Quickstart v0.1

Status: protocol research
Scope: local Termux simulation
Value status: non-value simulation only

## Purpose

This quickstart explains how to run the local AUNEYA demo on Termux.

It is designed for a phone-first user who wants to verify that the local AUNEYA witness loop works.

## What this quickstart runs

The quickstart runs:

Claim fixture
-> One-Command Local Demo
-> Local Witness Runner
-> Pulse-Flow Report
-> Local Witness CLI Display

## One-command local demo

Run this from the repository root:

./tools/auneya/auneya_one_command_local_demo.sh

Expected visible result:

AUNEYA ONE-COMMAND LOCAL DEMO v0.1
AUNEYA LOCAL WITNESS
Token created: false
Market value claimed: false
Transferable: false
Mainnet: not active

## Optional explicit claim

./tools/auneya/auneya_one_command_local_demo.sh fixtures/auneya/claims/valid-release-reality.json

## Local output files

The demo writes local temporary files under:

.tmp/auneya-one-command-demo

These files are local development artifacts only.

They are not mainnet records.

They are not balances.

They are not transferable units.

They are not tokens.

## What this proves

This proves that the repository can locally execute the first AUNEYA witness loop:

- read a lawful public claim fixture
- generate local Pulses
- generate local Micro-Proofs
- generate a local Prooflet
- generate a local non-value simulated entry
- show a Termux-friendly local witness display

## What this does not prove

This does not prove a public network exists.

This does not create AUNEYA.

This does not create neya.

This does not create a real reward.

This does not create market value.

This does not activate a mainnet.

This does not perform mining.

This does not make anything transferable.

## Legal and safety boundary

Only public or owner-authorized claim fixtures are valid.

The local demo rejects private-data claims.

The local demo must not use hacked data.

The local demo must not bypass paywalls.

The local demo must not use private credentials.

The local demo must not perform surveillance.

Legal review is required before any public token launch, listing, sale, transferability or market-value communication.

## Self-check command

Run:

./conformance/auneya-local-demo-quickstart-v0.1.sh

Expected result:

PASS AUNEYA Local Demo Quickstart v0.1 conformance
