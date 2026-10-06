# AUNEYA Local Collection Ledger Simulation v0.1

Status: protocol research
Scope: local Termux simulation
Value status: non-value simulation only

## Purpose

This document defines the first local AUNEYA collection ledger simulation.

The ledger counts local simulated entries from lawful public claim runs.

It is a local development ledger only.

It does not create AUNEYA.

It does not create neya.

It does not create a real reward.

It does not create market value.

It does not activate a mainnet.

It does not make anything transferable.

## Record one local simulated entry

python3 tools/auneya/auneya_local_collection_ledger.py --record --claim-key release-reality

Other supported claim keys:

python3 tools/auneya/auneya_local_collection_ledger.py --record --claim-key download-integrity

python3 tools/auneya/auneya_local_collection_ledger.py --record --claim-key website-claim-reality

## Show local simulated ledger

python3 tools/auneya/auneya_local_collection_ledger.py --show

## Reset local simulated ledger

python3 tools/auneya/auneya_local_collection_ledger.py --reset

## Default local ledger file

.auneya/local-collection-ledger.json

This file is local and is not a mainnet record.

## What is counted

The ledger counts:

- local non-value simulated entries
- simulated_neya units from local demo output
- claim key
- claim id
- prooflet id
- local flow id
- local entry hash

## What is not counted

The ledger does not count real AUNEYA.

The ledger does not count real neya.

The ledger does not count transferable units.

The ledger does not count market value.

The ledger does not count mainnet rewards.

## Legal boundary

Only supported lawful public or owner-authorized fixtures are accepted.

Private-data claims are not accepted.

Claims requiring authentication are not accepted.

Claims requiring payment are not accepted.

Claims containing personal data are not accepted.

Claims requiring credential use, paywall bypass, hacked data or surveillance are not accepted.

Legal review is required before any public token launch, listing, sale, transferability or market-value communication.

## Files

- `tools/auneya/auneya_local_collection_ledger.py`
- `conformance/auneya-local-collection-ledger-simulation-v0.1.sh`
