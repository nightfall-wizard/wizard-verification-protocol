# AUNEYA Local Claim Composer v0.1

Status: protocol research
Scope: local claim composer and dashboard live-refresh sandbox
Network: none
Mainnet active: false
Token created: false
Market value claimed: false
Transferable: false

## Purpose

This document defines the AUNEYA local claim composer.

The composer turns the local dashboard from a read-only view into a local interactive sandbox.

## What this is

This is a local non-value simulation.

It allows a user to enter a public local demo claim and generate local simulated evidence:

1. `claim_accepted`
2. `witness_prooflet`
3. `event_finalized`

Each accepted local claim adds three simulated ledger entries and increases the simulated non-value balance by three units.

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

Build the local composer sandbox:

    python3 tools/auneya/auneya_local_claim_composer.py --reset --demo-claim "Public local demo claim" --build --print-url

Serve locally in Termux:

    python3 tools/auneya/auneya_local_claim_composer.py --serve

Then open:

    http://127.0.0.1:8766/index.html

Stop the local server with:

    CTRL+C

## Live-refresh sandbox

The browser UI uses:

- `/api/state`
- `/claim`
- local state JSON
- local static HTML refresh
- no external dependencies

The live-refresh sandbox remains local-only.

## Claim boundaries

Claims must not include:

- seed phrase
- private key
- custody request
- token price
- market value
- investment language
- profit claim
- mainnet launch claim
- transferability claim

## Exports

The composer writes:

- `reports/auneya/local-claim-composer-v0.1/index.html`
- `reports/auneya/local-claim-composer-v0.1/AUNEYA-LOCAL-CLAIM-COMPOSER-STATE-v0.1.json`
- `reports/auneya/local-claim-composer-v0.1/AUNEYA-LOCAL-CLAIM-COMPOSER-v0.1.json`
- `reports/auneya/local-claim-composer-v0.1/AUNEYA-LOCAL-CLAIM-COMPOSER-v0.1.md`

## Boundary

This is a local claim composer and dashboard live-refresh sandbox.

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
