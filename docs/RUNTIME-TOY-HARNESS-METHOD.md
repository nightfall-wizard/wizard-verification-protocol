
# WVP Runtime Toy Harness Method

WVP-SEC-014 adds a safe local runtime toy harness.

The harness executes small deterministic toy inputs that model evidence classes without touching real Nightfall funds, wallets, seeds, keys, nodes, or live chain state.

## Purpose

The purpose is to move beyond static evidence into safe executable behavior checks.

The harness checks:

- deterministic toy supply accounting
- duplicate toy input rejection
- canonical toy ordering
- coinbase maturity boundary behavior
- toy release digest presence
- toy public-report sanitation
- toy private-disclosure routing
- toy issue-quality gate behavior

## Safety boundary

The runtime toy harness must not use:

- real seeds
- private keys
- wallet files
- live funds
- live RPC mutation
- exploit payloads
- weaponized reproduction steps
- undisclosed vulnerability detail

## What PASS means

A PASS means the WVP toy harness and toy vectors behave consistently.

## What PASS does not mean

A PASS does not prove:

- Nightfall consensus correctness
- cryptographic soundness
- absence of inflation bugs
- absence of theft bugs
- real-world anonymity
- production safety
- audit status

## Non-audit rule

This harness is evidence automation. It is not an audit.
