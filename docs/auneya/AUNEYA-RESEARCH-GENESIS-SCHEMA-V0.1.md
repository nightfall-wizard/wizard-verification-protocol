# AUNEYA Research Genesis Schema v0.1

AUNEYA is documented as a permissionless Layer One research implementation and phone-first witness network.

This document defines the research-mode genesis schema used for AUNEYA chain identity and genesis test vectors.

It is compatible with AUNEYA L1 Legal Boundary v0.1, AUNEYA Adversarial Invariant Matrix v0.1 and AUNEYA Chain Identity and Genesis Boundary v0.1.

This document does not activate mainnet, does not define a public token offer, does not define transferable economic launch, does not request exchange listing, and does not make a market-value claim.

## Status

- Research-mode schema
- Genesis test-vector anchor
- Non-value protocol safety document
- No token sale
- No presale
- No allocation sale
- No market-value claim
- No custody, broker, exchange, advice or third-party transfer-service framing

## Schema files

- `specs/auneya/genesis/research-genesis.schema.json`
- `test-vectors/auneya/genesis/research-genesis.valid.json`
- `test-vectors/auneya/genesis/research-genesis.invalid-economic-activation.json`
- `conformance/auneya-research-genesis-schema-v0.1.sh`

## Required research-mode values

A valid research-mode genesis object must use:

1. `research_mode_enabled` equals `true`.
2. `economic_activation_enabled` equals `false`.
3. `legal_boundary_reference` equals `AUNEYA L1 Legal Boundary v0.1`.
4. `environment_label` equals `research`, `simulation`, `devnet` or `testnet`.
5. `signature_domain` includes `chain_id`.
6. `witness_domain` includes `chain_id`.
7. `replay_domain` includes `chain_id`.

## Required fields

A valid research-mode genesis object must define:

1. `chain_id`
2. `environment_label`
3. `genesis_hash`
4. `protocol_version`
5. `created_at`
6. `consensus_profile`
7. `signature_domain`
8. `witness_domain`
9. `replay_domain`
10. `research_mode_enabled`
11. `economic_activation_enabled`
12. `legal_boundary_reference`

## Hard stops

A future AUNEYA implementation must stop before release promotion if any of the following is true:

1. A genesis object omits `chain_id`.
2. A genesis object omits `genesis_hash`.
3. `research_mode_enabled` is not `true`.
4. `economic_activation_enabled` is not `false`.
5. `legal_boundary_reference` is not `AUNEYA L1 Legal Boundary v0.1`.
6. A domain field does not bind to `chain_id`.
7. A test vector contradicts the schema.
8. A schema permits token sale, presale, allocation sale, market-value claim or transferable economic launch.
9. A schema permits custody, broker, exchange, advice or third-party transfer-service framing.
10. The schema conflicts with AUNEYA Chain Identity and Genesis Boundary v0.1.

## Non-goals

This document does not define a public mainnet launch, token sale, presale, allocation sale, exchange listing, custody service, broker service, advisory service, transfer service or market-value communication.

## Implementation rule

Future AUNEYA genesis work must update this schema and its conformance gate before introducing additional chain identity, genesis, domain, witness, replay or research-mode fields.
