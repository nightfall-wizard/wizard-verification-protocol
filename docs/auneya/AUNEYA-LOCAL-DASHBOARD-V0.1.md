# AUNEYA Local Dashboard v0.1

Status: protocol research
Scope: local browser dashboard and mobile-first read-only UI
Network: none
Mainnet active: false
Token created: false
Market value claimed: false
Transferable: false

## Purpose

This document defines the AUNEYA local browser dashboard.

The dashboard makes the existing local ledger and local wallet simulator visible in a mobile-first browser UI.

## What this is

This is a local read-only dashboard.

It reads the local ledger wallet JSON artifact and renders:

- wallet ID
- local wallet address
- simulated non-value balance
- ledger entry count
- ledger hash
- ledger entries
- history
- boundary status

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

## Commands

Build the dashboard:

    python3 tools/auneya/auneya_local_dashboard.py --build --print-url

Serve locally in Termux:

    python3 tools/auneya/auneya_local_dashboard.py --serve

Then open:

    http://127.0.0.1:8765/index.html

Stop the local server with:

    CTRL+C

## Exports

The dashboard writes:

- `reports/auneya/local-dashboard-v0.1/index.html`
- `reports/auneya/local-dashboard-v0.1/AUNEYA-LOCAL-DASHBOARD-v0.1.json`
- `reports/auneya/local-dashboard-v0.1/AUNEYA-LOCAL-DASHBOARD-v0.1.md`

## Read-only rule

The dashboard is read-only.

It must not contain:

- send button
- receive button
- transfer button
- private-key field
- seed-phrase field
- custody flow
- token creation flow
- market-value display
- mainnet activation flow

## Boundary

This is a local browser dashboard for the AUNEYA local ledger and wallet simulator.

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
