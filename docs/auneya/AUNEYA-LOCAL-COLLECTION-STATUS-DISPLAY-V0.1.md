# AUNEYA Local Collection Status Display v0.1

Status: protocol research
Scope: local Termux simulation
Value status: non-value simulation only

## Purpose

This document defines the local AUNEYA collection status display.

The display reads a local collection ledger simulation and shows a Termux-friendly status view.

## Show local simulated collection status

python3 tools/auneya/auneya_local_collection_status.py --ledger .auneya/local-collection-ledger.json

## Compact mode

python3 tools/auneya/auneya_local_collection_status.py --ledger .auneya/local-collection-ledger.json --compact

## What is shown

The display shows:

- local simulated ledger path
- total simulated entries
- total simulated_neya counted
- latest simulated entry
- recent simulated entries
- non-value boundaries

## What this does not show

The display does not show a real AUNEYA balance.

The display does not show real neya.

The display does not show a transferable balance.

The display does not show market value.

The display does not show mainnet rewards.

## Non-Value Boundary

The display does not create a token.

The display does not create AUNEYA.

The display does not create neya.

The display does not create a real reward.

The display does not create market value.

The display does not activate a mainnet.

The display does not make anything transferable.

Legal review is required before any public token launch, listing, sale, transferability or market-value communication.

## Files

- `tools/auneya/auneya_local_collection_status.py`
- `conformance/auneya-local-collection-status-display-v0.1.sh`
