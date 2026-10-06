# WVP-SEC-002 - Nightfall Codepath Bindings

This file binds WVP fixtures to observable Nightfall source/documentation paths.

Boundary: this is not an audit and does not prove the implementation correct.

Target files scanned: 118
Fixtures bound: 8/8

## thin_air_mint

Status: `bound`

Terms: `supply`, `invariant`, `mint`, `burn`, `kernel`

| Score | Path |
|---:|---|
| 5 | `crates/nightfall-consensus/src/lib.rs` |
| 5 | `crates/nightfall-core/src/views.rs` |
| 5 | `crates/nightfall-ledger/src/lib.rs` |
| 5 | `crates/nightfall-ledger/src/utxo.rs` |
| 5 | `crates/nightfall-ledger/tests/ledger_flow.rs` |
| 5 | `crates/nightfall-node/src/rpc.rs` |
| 5 | `crates/nightfall-node/tests/multi_node_reorg.rs` |
| 5 | `crates/nightfall-storage/src/lib.rs` |

## negative_amount_attempt

Status: `bound`

Terms: `range`, `proof`, `amount`, `bulletproof`

| Score | Path |
|---:|---|
| 4 | `crates/nightfall-crypto/src/commit.rs` |
| 4 | `crates/nightfall-crypto/src/rangeproof.rs` |
| 4 | `crates/nightfall-ledger/tests/exploit_regression.rs` |
| 4 | `crates/nightfall-node/src/rpc.rs` |
| 4 | `docs/AUDIT-2026-08-12.md` |
| 4 | `docs/AUDIT-2026-08-16.md` |
| 4 | `docs/DECISIONS.md` |
| 4 | `docs/MAINNET.md` |

## fake_input_spend

Status: `bound`

Terms: `input`, `utxo`, `spend`, `signature`

| Score | Path |
|---:|---|
| 4 | `crates/nightfall-core/src/views.rs` |
| 4 | `crates/nightfall-crypto/src/lib.rs` |
| 4 | `crates/nightfall-ledger/src/lib.rs` |
| 4 | `crates/nightfall-ledger/src/tx.rs` |
| 4 | `crates/nightfall-ledger/tests/exploit_regression.rs` |
| 4 | `crates/nightfall-wallet/src/lib.rs` |
| 4 | `docs/AUDIT-2026-08-12.md` |
| 4 | `docs/AUDIT-2026-08-16.md` |

## immature_coinbase_spend

Status: `bound`

Terms: `coinbase`, `maturity`, `1440`

| Score | Path |
|---:|---|
| 3 | `crates/nightfall-wallet/src/lib.rs` |
| 2 | `crates/nightfall-consensus/src/lib.rs` |
| 2 | `crates/nightfall-core/src/app.rs` |
| 2 | `crates/nightfall-core/src/views.rs` |
| 2 | `crates/nightfall-core/src/wallet_state.rs` |
| 2 | `crates/nightfall-crypto/src/stealth.rs` |
| 2 | `crates/nightfall-ledger/src/lib.rs` |
| 2 | `crates/nightfall-ledger/src/utxo.rs` |

## duplicate_input

Status: `bound`

Terms: `duplicate`, `input`, `reject`

| Score | Path |
|---:|---|
| 3 | `crates/nightfall-consensus/src/lib.rs` |
| 3 | `crates/nightfall-consensus/tests/chain_rules.rs` |
| 3 | `crates/nightfall-wallet/src/lib.rs` |
| 3 | `crates/nightfall-wallet/src/vault.rs` |
| 3 | `crates/nightfall-web/src/vault.rs` |
| 3 | `docs/SPEC.md` |
| 3 | `docs/VAULT-FORMAT.md` |
| 2 | `crates/nightfall-core/src/app.rs` |

## unsorted_block_body

Status: `bound`

Terms: `sort`, `canonical`, `order`

| Score | Path |
|---:|---|
| 3 | `crates/nightfall-consensus/src/lib.rs` |
| 3 | `crates/nightfall-ledger/src/aggregate.rs` |
| 3 | `crates/nightfall-ledger/src/utxo.rs` |
| 3 | `crates/nightfall-wallet/src/lib.rs` |
| 3 | `docs/SPEC.md` |
| 2 | `crates/nightfall-consensus/src/difficulty.rs` |
| 2 | `crates/nightfall-consensus/tests/chain_rules.rs` |
| 2 | `crates/nightfall-core/src/app.rs` |

## invalid_kernel_excess

Status: `bound`

Terms: `kernel`, `excess`, `signature`

| Score | Path |
|---:|---|
| 3 | `crates/nightfall-consensus/src/lib.rs` |
| 3 | `crates/nightfall-crypto/src/kernel.rs` |
| 3 | `crates/nightfall-crypto/src/lib.rs` |
| 3 | `crates/nightfall-crypto/src/schnorr.rs` |
| 3 | `crates/nightfall-ledger/src/aggregate.rs` |
| 3 | `crates/nightfall-ledger/src/lib.rs` |
| 3 | `crates/nightfall-ledger/src/tx.rs` |
| 3 | `crates/nightfall-ledger/tests/exploit_regression.rs` |

## block_apply_atomicity_case

Status: `bound`

Terms: `atomic`, `staged`, `commit`, `reject`

| Score | Path |
|---:|---|
| 4 | `docs/AUDIT-2026-08-12.md` |
| 4 | `docs/DECISIONS.md` |
| 3 | `crates/nightfall-consensus/src/lib.rs` |
| 3 | `crates/nightfall-core/src/app.rs` |
| 3 | `crates/nightfall-core/src/vault_ui.rs` |
| 3 | `crates/nightfall-core/src/views.rs` |
| 3 | `crates/nightfall-core/src/wallet_state.rs` |
| 3 | `crates/nightfall-ledger/src/lib.rs` |
