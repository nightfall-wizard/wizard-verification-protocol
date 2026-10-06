# AUNEYA Local Witness CLI Display v0.1

Status: protocol research
Scope: local Termux simulation
Value status: non-value simulation only

## Purpose

This document defines the first local AUNEYA Termux display for a generated pulse-flow report.

The display reads a local AUNEYA Pulse and Prooflet Flow v0.1 report and prints a phone-first status view.

## Flow

Claim fixture
-> Local Witness Runner
-> Pulse-Flow Report
-> Local Witness CLI Display

## Command

python3 tools/auneya/auneya_local_witness_display.py --input .tmp/auneya-local-runner/local-flow.json

Compact mode:

python3 tools/auneya/auneya_local_witness_display.py --input .tmp/auneya-local-runner/local-flow.json --compact

## Display Sections

The display shows local non-value mode, claim identity, witness identity, pulse count, micro-proof count, prooflet identity, simulated non-value entry, legal boundary confirmations and explicit non-value notice.

## Non-Value Boundary

The display does not create a token.

The display does not create a real reward.

The display does not create market value.

The display does not activate a mainnet.

The display does not perform mining.

The display only shows a local non-value simulated entry.

The simulated entry is non-transferable.

Legal review is required before any public token launch, listing, sale, transferability or market-value communication.

## Files

- `tools/auneya/auneya_local_witness_display.py`
- `conformance/auneya-local-witness-display-v0.1.sh`
