# AUNEYA Witness Proof Schema v0.1

Status: protocol research  
Scope: provable web  
Value status: non-value simulation only

## Purpose

This document defines the first machine-readable AUNEYA witness proof format.

A witness proof is created after a lawful public claim has been checked by a witness.

The proof records:

- which claim was checked
- which witness class checked it
- what status was observed
- what evidence hashes were produced
- which lawful boundary confirmations apply
- when the check happened
- proof integrity metadata

## Relationship to Claim Schema

AUNEYA Claim Schema v0.1 defines what may be checked.

AUNEYA Witness Proof Schema v0.1 defines the structured proof created after checking.

Formula:

Claim
-> witness check
-> witness proof
-> later Auneya Event

## Proof Types

Initial proof types:

- `pulse_observation`
- `micro_proof`
- `prooflet`
- `claim_observation`

## Observed Status Values

A witness proof may report:

- `verified`
- `false`
- `unverifiable`
- `stale`
- `dangerous`
- `conflicting`

## Legal Boundary

A witness proof is invalid if it used:

- private account access
- hacked data
- paywall bypass
- credentials
- surveillance of private persons
- access-control circumvention

## Non-Value Boundary

This schema does not create a token.

This schema does not create a reward.

This schema does not create market value.

This schema is not an investment offer.

This schema is not legal clearance.

Legal review is required before any public token launch, listing, sale, transferability or market-value communication.

## Files

- `schemas/auneya-witness-proof-v0.1.schema.json`
- `fixtures/auneya/witness-proofs/valid-release-reality-prooflet.json`
- `fixtures/auneya/witness-proofs/valid-download-integrity-prooflet.json`
- `fixtures/auneya/witness-proofs/invalid-private-data-proof.json`
- `conformance/auneya-witness-proof-schema-v0.1.sh`
