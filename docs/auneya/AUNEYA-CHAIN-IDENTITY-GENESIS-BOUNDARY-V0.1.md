# AUNEYA Chain Identity and Genesis Boundary v0.1

AUNEYA is documented as a permissionless Layer One research implementation and phone-first witness network.

This document defines research-mode chain identity and genesis boundaries for future AUNEYA Layer One protocol work.

It is compatible with AUNEYA L1 Legal Boundary v0.1 and AUNEYA Adversarial Invariant Matrix v0.1.

This document does not activate mainnet, does not define a public token offer, does not define transferable economic launch, does not request exchange listing, and does not make a market-value claim.

## Status

- Research-mode chain identity boundary
- Genesis immutability boundary
- Chain-id collision prevention boundary
- Non-value protocol safety document
- No token sale
- No presale
- No allocation sale
- No market-value claim
- No custody, broker, exchange, advice or third-party transfer-service framing

## Purpose

The purpose of this document is to define the minimum identity rules that must exist before AUNEYA can safely discuss future devnet, testnet, simulation or implementation work.

These rules prevent accidental chain confusion, replay across environments, mutable genesis definitions, hidden economic activation and undocumented migration paths.

## Definitions

- Chain identity: the complete protocol identity that separates one AUNEYA environment from another.
- Chain id: the explicit identifier used by clients, nodes, witnesses and signatures.
- Genesis configuration: the first canonical configuration for a chain environment.
- Genesis hash: the cryptographic digest of the genesis configuration.
- Environment: research, simulation, devnet, testnet or future legally reviewed network context.
- Research mode: a non-value mode that must not present sale, presale, allocation sale, market-value claim or transferable economic launch.
- Compatibility boundary: the rule that stricter non-value interpretation controls until separate legal review approves a change.

## Chain identity rules

| ID | Rule | Required property | Failure condition | Test hook |
|---|---|---|---|---|
| AUNEYA-CHAIN-001 | Chain id required | Every environment must define an explicit chain id | A node, witness or client accepts missing chain id | Missing-chain-id fixture |
| AUNEYA-CHAIN-002 | Chain id uniqueness | Research, devnet, testnet and any future network must use distinct chain ids | Two environments share the same chain id | Chain-id-collision fixture |
| AUNEYA-CHAIN-003 | Genesis hash required | Every chain id must bind to one genesis hash | A chain id is accepted without genesis hash binding | Genesis-hash fixture |
| AUNEYA-CHAIN-004 | Genesis immutability | A chain id must not accept multiple incompatible genesis configurations | Same chain id accepts different genesis configuration | Genesis-immutability fixture |
| AUNEYA-CHAIN-005 | Signature domain separation | Signatures and attestations must bind to chain id and context | A signature or attestation is valid across environments | Domain-separation fixture |
| AUNEYA-CHAIN-006 | Replay isolation | Transactions, attestations and witness messages must not replay across chain ids | Message from one environment is accepted in another | Replay-isolation fixture |
| AUNEYA-CHAIN-007 | Research-mode default | New chain work starts in research mode unless separate legal review approves another path | New chain work starts with public economic framing | Research-default fixture |
| AUNEYA-CHAIN-008 | No silent economic activation | Genesis configuration must not silently activate sale, presale, allocation sale, market-value claim or transferable economic launch | Genesis config enables economic launch framing without explicit review | Economic-activation fixture |
| AUNEYA-CHAIN-009 | Witness role separation | Chain identity must not make witness role into custody, broker, exchange, advice or third-party transfer authority | Witness identity grants third-party asset control | Witness-role fixture |
| AUNEYA-CHAIN-010 | Environment label required | User-facing outputs must label research, simulation, devnet, testnet or reviewed environment status | Client output hides environment status | Environment-label fixture |
| AUNEYA-CHAIN-011 | Migration explicitness | Migration between environments must require explicit documented mapping | State migrates between environments without documented mapping | Migration-mapping fixture |
| AUNEYA-CHAIN-012 | Legal-boundary compatibility | Chain identity and genesis work must remain compatible with AUNEYA L1 Legal Boundary v0.1 | A chain identity step conflicts with the stricter non-value interpretation | Legal-boundary fixture |

## Required genesis fields

A future research genesis configuration must define:

1. chain_id
2. environment_label
3. genesis_hash
4. protocol_version
5. created_at
6. consensus_profile
7. signature_domain
8. witness_domain
9. replay_domain
10. research_mode_enabled
11. economic_activation_enabled
12. legal_boundary_reference

## Required research-mode values

A research-mode genesis configuration must use:

1. research_mode_enabled equals true.
2. economic_activation_enabled equals false.
3. legal_boundary_reference equals AUNEYA L1 Legal Boundary v0.1.
4. environment_label equals research, simulation, devnet or testnet.
5. signature_domain includes chain_id.
6. witness_domain includes chain_id.
7. replay_domain includes chain_id.

## Hard stops

A future AUNEYA technical step must stop before release promotion if any of the following is true:

1. Chain id is missing.
2. Genesis hash is missing.
3. Genesis configuration is mutable for the same chain id.
4. Signature domain does not bind to chain id.
5. Witness domain does not bind to chain id.
6. Replay domain does not bind to chain id.
7. Environment label is hidden from user-facing output.
8. Research mode enables sale, presale, allocation sale, market-value claim or transferable economic launch.
9. Witness role becomes custody, broker, exchange, advice or third-party transfer authority.
10. The step conflicts with AUNEYA L1 Legal Boundary v0.1.

## Non-goals

This document does not define a public mainnet launch, token sale, presale, allocation sale, exchange listing, custody service, broker service, advisory service, transfer service or market-value communication.

## Implementation rule

Future AUNEYA protocol work must reference this document before introducing chain id logic, genesis files, signature domains, witness domains, replay domains, migration logic, devnet labels, testnet labels or research-mode controls.
