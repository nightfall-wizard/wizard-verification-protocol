# AUNEYA Pulse and Prooflet Flow v0.1

Status: protocol research  
Scope: provable web  
Value status: non-value simulation only

## Purpose

This document defines the first phone-first AUNEYA witness loop.

It models how a phone can turn lawful public claim checks into pulses, micro-proofs and prooflets.

This is simulation only.

## Flow

Claim
-> Pulse
-> Micro-Proof
-> Prooflet
-> later Witness Proof
-> later Auneya Event

## Pulse

A Pulse is the smallest visible witness activity.

Examples:

- public HTTP status observation
- release metadata observation
- public content hash observation
- public page snapshot hash observation
- DNS observation
- TLS observation

## Micro-Proof

A Micro-Proof groups one or more Pulses into a small evidence object.

## Prooflet

A Prooflet groups one or more Micro-Proofs into a claim-specific witness-flow output.

A Prooflet is not a token.

A Prooflet is not a reward.

A Prooflet is not market value.

## Simulated Reward Entry

The flow may include a simulated reward entry.

The simulated reward entry is non-transferable.

It has no market value.

It is not a token.

It is not a promise of future value.

## Legal Boundary

The flow is invalid if it requires:

- private account access
- private messages
- hacked data
- paywall bypass
- credential use
- surveillance of private persons
- access-control circumvention

## Non-Value Boundary

This schema does not create a token.

This schema does not create a real reward.

This schema does not create market value.

This schema is not an investment offer.

This schema is not legal clearance.

Legal review is required before any public token launch, listing, sale, transferability or market-value communication.

## Files

- `schemas/auneya-pulse-flow-v0.1.schema.json`
- `fixtures/auneya/pulse-flow/valid-phone-release-reality-flow.json`
- `fixtures/auneya/pulse-flow/invalid-private-target-flow.json`
- `fixtures/auneya/pulse-flow/invalid-value-reward-flow.json`
- `conformance/auneya-pulse-flow-v0.1.sh`
