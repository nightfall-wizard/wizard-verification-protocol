# AUNEYA Local Ledger + Wallet Simulator v0.1

Status: protocol research
Scope: local ledger and local wallet simulator
Network: none
Mainnet active: false
Token created: false
Market value claimed: false
Transferable: false

## Purpose

This document defines the first tangible AUNEYA local ledger and local wallet simulator.

It is designed to make the AUNEYA proof flow visible in Termux:

- local claim entry
- local witness prooflet entry
- local event finalization entry
- local ledger history
- local wallet address
- local simulated balance
- JSON export
- Markdown export
- terminal wallet view

## What this is

This is a local non-value simulation.

It creates a local identity wallet view and an append-only local simulation ledger.

The local wallet has:

- a local wallet ID
- a local-only address
- a simulated balance
- visible history
- exportable JSON and Markdown reports

## What this is not

This is not a real wallet.

It does not create a private key.
It does not create a seed phrase.
It does not create custody.
It does not enable send.
It does not enable receive.
It does not enable transfer.
It does not create a token.
It does not create market value.
It does not activate mainnet.
It is not investment advice.
It is not legal advice.
It is not a custody, broker, exchange or financial service.

## Local ledger model

The local ledger is append-only for the demo.

It records three local entries:

1. `claim_accepted`
2. `witness_prooflet`
3. `event_finalized`

Each entry records:

- entry ID
- entry type
- amount
- unit
- claim ID
- prooflet ID where applicable
- event ID where applicable
- running balance
- entry hash

## Local wallet model

The wallet is a local identity wallet simulator.

It contains:

- `wallet_id`
- `wallet_address`
- `wallet_type`
- `balance`
- `unit`
- `send_enabled`
- `receive_enabled`
- `transfer_enabled`

Send, receive and transfer are false.

The unit is:

    simulated_neya_non_value_unit

This unit has no monetary value and no transferability.

## Commands

Run the local demo:

    python3 tools/auneya/auneya_local_ledger_wallet.py --print-wallet

Run conformance:

    bash conformance/auneya-local-ledger-wallet-v0.1.sh

## Exports

The simulator writes:

- `reports/auneya/local-ledger-wallet-v0.1/AUNEYA-LOCAL-LEDGER-WALLET-v0.1.json`
- `reports/auneya/local-ledger-wallet-v0.1/AUNEYA-LOCAL-LEDGER-WALLET-v0.1.md`
- `reports/auneya/local-ledger-wallet-v0.1/AUNEYA-LOCAL-WALLET-VIEW-v0.1.txt`

## Boundary

This is a local ledger and local wallet simulator only.

It creates no token.
It creates no market value.
It creates no transferability.
It activates no mainnet.
It creates no private key.
It creates no seed phrase.
It creates no custody.
It is not investment advice.
It is not legal advice.
It is not a custody, broker, exchange or financial service.

Legal review is required before any public token launch, listing, sale, transferability or market-value communication.

