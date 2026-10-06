# WVP-SEC-007 - Negative Vector and Fuzzing Scaffolding

This report defines safe negative vectors for Nightfall invariant-related failure classes.

Boundary: this is defensive scaffolding, not an exploit release and not an audit.

Vectors: 11

## Safety boundary

- no real seed
- no private key
- no live funds
- no undisclosed exploit detail
- no network mutation
- no node state mutation

## Vector summary

| ID | Fixture | Class | Expected result |
|---|---|---|---|
| NV-INF-001 | `thin_air_mint` | inflation | `reject` |
| NV-INF-002 | `negative_amount_attempt` | inflation | `reject` |
| NV-THEFT-001 | `fake_input_spend` | theft | `reject` |
| NV-CONS-001 | `immature_coinbase_spend` | consensus | `reject` |
| NV-CONS-002 | `duplicate_input` | consensus | `reject` |
| NV-CONS-003 | `unsorted_block_body` | consensus | `reject` |
| NV-INF-003 | `invalid_kernel_excess` | inflation | `reject` |
| NV-CONS-004 | `block_apply_atomicity_case` | consensus | `reject_without_state_mutation` |
| NV-POL-001 | `fee_burn_mismatch` | monetary_policy | `reject_or_warn` |
| NV-REL-001 | `release_digest_missing` | release_integrity | `warn` |
| NV-WALLET-001 | `light_client_lie` | display_integrity | `documented_limitation` |

## NV-INF-001 - thin_air_mint

Class: `inflation`

Expected result: `reject`

Mutation target: `minted_without_valid_source`

Abstract vector for value creation without valid accounting source.

## NV-INF-002 - negative_amount_attempt

Class: `inflation`

Expected result: `reject`

Mutation target: `invalid_confidential_amount`

Abstract vector for invalid amount encoding or invalid range-proof surface.

## NV-THEFT-001 - fake_input_spend

Class: `theft`

Expected result: `reject`

Mutation target: `spend_nonexistent_input`

Abstract vector for attempting to spend an input not present in the UTXO set.

## NV-CONS-001 - immature_coinbase_spend

Class: `consensus`

Expected result: `reject`

Mutation target: `spend_coinbase_before_maturity`

Abstract vector for miner reward spend before configured maturity.

## NV-CONS-002 - duplicate_input

Class: `consensus`

Expected result: `reject`

Mutation target: `same_input_twice`

Abstract vector for duplicate input use inside one validation surface.

## NV-CONS-003 - unsorted_block_body

Class: `consensus`

Expected result: `reject`

Mutation target: `noncanonical_ordering`

Abstract vector for non-canonical ordering of block body elements.

## NV-INF-003 - invalid_kernel_excess

Class: `inflation`

Expected result: `reject`

Mutation target: `kernel_excess_mismatch`

Abstract vector for kernel excess mismatch against accounting equation.

## NV-CONS-004 - block_apply_atomicity_case

Class: `consensus`

Expected result: `reject_without_state_mutation`

Mutation target: `partial_state_apply_after_reject`

Abstract vector for rejected block mutating state partially.

## NV-POL-001 - fee_burn_mismatch

Class: `monetary_policy`

Expected result: `reject_or_warn`

Mutation target: `fee_burn_accounting_mismatch`

Abstract vector for fee accounting mismatch around burn logic.

## NV-REL-001 - release_digest_missing

Class: `release_integrity`

Expected result: `warn`

Mutation target: `missing_release_digest`

Abstract vector for missing release checksum or digest evidence.

## NV-WALLET-001 - light_client_lie

Class: `display_integrity`

Expected result: `documented_limitation`

Mutation target: `untrusted_node_display_state`

Abstract vector for light-client display state controlled by an untrusted node.
