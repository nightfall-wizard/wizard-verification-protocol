# AUNEYA One-Command Local Demo v0.1

Status: protocol research
Scope: local Termux simulation
Value status: non-value simulation only

## Purpose

This document defines the first one-command local AUNEYA demo.

The demo runs the local witness runner and local witness display in one Termux-compatible command.

## Flow

Claim fixture
-> One-Command Local Demo
-> Local Witness Runner
-> Pulse-Flow Report
-> Local Witness CLI Display

## Command

./tools/auneya/auneya_one_command_local_demo.sh

Optional claim path:

./tools/auneya/auneya_one_command_local_demo.sh fixtures/auneya/claims/valid-release-reality.json

## Outputs

The demo writes local temporary outputs under `.tmp/auneya-one-command-demo`.

These outputs are local development artifacts only.

## Non-Value Boundary

The demo does not create a token.

The demo does not create a real reward.

The demo does not create market value.

The demo does not activate a mainnet.

The demo does not perform mining.

The demo only shows a local non-value simulated entry.

The simulated entry is non-transferable.

Legal review is required before any public token launch, listing, sale, transferability or market-value communication.

## Files

- `tools/auneya/auneya_one_command_local_demo.sh`
- `conformance/auneya-one-command-local-demo-v0.1.sh`
