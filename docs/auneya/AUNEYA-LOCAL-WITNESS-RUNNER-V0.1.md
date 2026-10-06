# AUNEYA Local Witness Runner v0.1

Status: protocol research
Scope: local Termux simulation
Value status: non-value simulation only

## Purpose

This document defines the first local AUNEYA witness runner.

The runner reads a lawful public AUNEYA claim fixture and emits a local AUNEYA Pulse and Prooflet Flow v0.1 report.

## Flow

Claim fixture
-> local runner
-> Pulse
-> Micro-Proof
-> Prooflet
-> local non-value pulse-flow report

## Command

python3 tools/auneya/auneya_local_witness_runner.py --claim fixtures/auneya/claims/valid-release-reality.json --out .tmp/auneya-local-runner/local-flow.json

## Legal Boundary

The runner rejects claims that require authentication, payment, personal data, hacked data, paywall bypass, credentials or surveillance.

## Non-Value Boundary

The runner does not create a token.

The runner does not create a real reward.

The runner does not create market value.

The runner does not activate a mainnet.

The runner does not perform mining.

The runner only emits a local non-value simulated reward entry.

The simulated reward entry is non-transferable.

Legal review is required before any public token launch, listing, sale, transferability or market-value communication.

## Files

- `tools/auneya/auneya_local_witness_runner.py`
- `conformance/auneya-local-witness-runner-v0.1.sh`
