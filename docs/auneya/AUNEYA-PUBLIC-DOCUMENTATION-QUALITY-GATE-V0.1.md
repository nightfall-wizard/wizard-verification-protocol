# AUNEYA Public Documentation Quality Gate v0.1

Status: protocol research
Scope: public documentation quality gate
Network: none
Mainnet active: false
Token created: false
Market value claimed: false
Transferable: false

## Purpose

This quality gate defines minimum public documentation standards for AUNEYA before external review.

It protects the project from unclear language, accidental value claims, premature launch language and legal ambiguity.

## Quality gate

AUNEYA public documentation must pass all of the following checks:

- protocol purpose is understandable
- review scope is explicit
- reviewer checklist is present
- public documentation links to core artifacts
- open questions are visible
- known limitations are visible
- non-value simulation boundary is repeated
- launch-related language is avoided
- market-value language is avoided
- investment framing is avoided
- legal review requirement is explicit

## Required boundary terms

Public documentation must preserve these statements or equivalent wording:

- no token
- no market value
- no transferability
- no mainnet
- not investment advice
- not legal advice
- not a custody, broker, exchange or financial service
- legal review required before launch
- non-value simulation

## Disallowed claims

AUNEYA public documentation must not claim:

- AUNEYA is launched
- neya is a transferable asset
- rewards have monetary value
- users can profit
- future listings are planned or guaranteed
- legal approval exists
- audits are complete
- mainnet is active
- regulators have approved the design
- AUNEYA is a financial product

## External review packet

A minimal external review packet should include:

- AUNEYA protocol charter
- AUNEYA provable web scope
- AUNEYA non-value simulation notice
- claim schema
- witness proof schema
- event schema
- pulse and prooflet flow
- local witness runner
- local simulation evidence pack
- external review readiness report
- public documentation quality gate

## Machine-checkable evidence

This gate is checked by:

    python3 tools/auneya/auneya_external_review_readiness.py

Conformance is checked by:

    bash conformance/auneya-external-review-readiness-v0.1.sh

## Boundary

This quality gate is not a launch.
It is not a legal review.
It is not investment advice.
It is not a financial service.
It is not a token issuance.
It creates no token, no market value, no transferability and no mainnet activity.

Legal review is required before any public token launch, listing, sale, transferability or market-value communication.

