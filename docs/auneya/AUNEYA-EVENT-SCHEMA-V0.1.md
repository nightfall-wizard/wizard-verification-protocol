# AUNEYA Event Schema v0.1

Status: protocol research  
Scope: provable web  
Value status: non-value simulation only

## Purpose

This document defines the first machine-readable AUNEYA Event format.

An Auneya Event is formed when multiple lawful witness proofs refer to the same public claim and satisfy the event quorum rules.

AUNEYA does not claim absolute truth.

AUNEYA records structured agreement or conflict between lawful public witness proofs.

## Relationship to Previous Schemas

AUNEYA Claim Schema v0.1 defines what may be checked.

AUNEYA Witness Proof Schema v0.1 defines the proof created by a witness.

AUNEYA Event Schema v0.1 defines how multiple witness proofs form an event.

Formula:

Claim
-> Witness Proofs
-> Auneya Event

## Event Status Values

Initial event status values:

- `observed`
- `witnessed`
- `sealed`
- `disputed`
- `expired`

## Quorum Principle

A valid witnessed event requires:

- a lawful public or authorized claim
- multiple lawful witness proofs
- matching claim identifiers
- matching claim hashes
- independent witness identifiers
- sufficient witness count
- matching observed status for non-dispute events

## Legal Boundary

An Auneya Event is invalid if any forming proof used:

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

- `schemas/auneya-event-v0.1.schema.json`
- `fixtures/auneya/events/valid-witnessed-release-reality-event.json`
- `fixtures/auneya/events/invalid-duplicate-witness-event.json`
- `fixtures/auneya/events/invalid-private-data-event.json`
- `conformance/auneya-event-schema-v0.1.sh`
