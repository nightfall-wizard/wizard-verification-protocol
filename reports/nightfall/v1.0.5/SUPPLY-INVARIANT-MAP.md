# WVP-SEC-006 - Supply Invariant Evidence Map

This report maps Nightfall supply-invariant claims to
observable source and documentation evidence.

Boundary: this is read-only evidence mapping, not an audit.

Source files scanned: 119
Claims: 9
Claim PASS: 9
Claim WARN: 0
Runtime-safe probes: 5
Probe PASS: 5
Probe WARN: 0

## Claim summary

| ID | Name | Class | Status | Missing terms |
|---|---|---|---|---|
| SUPPLY-001 | `supply_invariant_declared` | inflation | `PASS` | `-` |
| SUPPLY-002 | `utxo_accounting_surface` | inflation | `PASS` | `-` |
| SUPPLY-003 | `kernel_excess_surface` | inflation | `PASS` | `-` |
| SUPPLY-004 | `mint_burn_accounting_surface` | inflation | `PASS` | `-` |
| SUPPLY-005 | `coinbase_maturity_surface` | consensus | `PASS` | `-` |
| SUPPLY-006 | `emission_schedule_surface` | monetary_policy | `PASS` | `-` |
| SUPPLY-007 | `max_supply_cap_surface` | monetary_policy | `PASS` | `-` |
| SUPPLY-008 | `fee_burn_surface` | monetary_policy | `PASS` | `-` |
| SUPPLY-009 | `range_proof_surface` | inflation | `PASS` | `-` |

## SUPPLY-001 - supply_invariant_declared

Status: `PASS`

Class: `inflation`

Risk: accepted blocks may create value outside accounting

Required terms: `supply`, `invariant`

Found terms: `invariant`, `supply`

| Score | Path |
|---:|---|
| 2 | `SECURITY.md` |
| 2 | `crates/nightfall-consensus/src/lib.rs` |
| 2 | `crates/nightfall-consensus/tests/chain_rules.rs` |
| 2 | `crates/nightfall-core/src/views.rs` |
| 2 | `crates/nightfall-ledger/src/lib.rs` |
| 2 | `crates/nightfall-ledger/src/utxo.rs` |
| 2 | `crates/nightfall-ledger/tests/ledger_flow.rs` |
| 2 | `crates/nightfall-node/src/rpc.rs` |
| 2 | `crates/nightfall-node/tests/multi_node_reorg.rs` |
| 2 | `crates/nightfall-p2p/src/lib.rs` |
| 2 | `crates/nightfall-storage/src/lib.rs` |
| 2 | `crates/nightfall-wallet/src/main.rs` |

## SUPPLY-002 - utxo_accounting_surface

Status: `PASS`

Class: `inflation`

Risk: supply accounting cannot be tied to spendable outputs

Required terms: `utxo`

Found terms: `utxo`

| Score | Path |
|---:|---|
| 1 | `SECURITY.md` |
| 1 | `crates/nightfall-consensus/src/lib.rs` |
| 1 | `crates/nightfall-consensus/tests/chain_rules.rs` |
| 1 | `crates/nightfall-core/src/app.rs` |
| 1 | `crates/nightfall-core/src/vault_ui.rs` |
| 1 | `crates/nightfall-core/src/view_layout_tests.rs` |
| 1 | `crates/nightfall-core/src/views.rs` |
| 1 | `crates/nightfall-crypto/src/lib.rs` |
| 1 | `crates/nightfall-crypto/src/stealth.rs` |
| 1 | `crates/nightfall-ledger/Cargo.toml` |
| 1 | `crates/nightfall-ledger/src/builder.rs` |
| 1 | `crates/nightfall-ledger/src/lib.rs` |

## SUPPLY-003 - kernel_excess_surface

Status: `PASS`

Class: `inflation`

Risk: kernel excess validation may not protect hidden value

Required terms: `kernel`, `excess`

Found terms: `excess`, `kernel`

| Score | Path |
|---:|---|
| 2 | `SECURITY.md` |
| 2 | `crates/nightfall-consensus/src/lib.rs` |
| 2 | `crates/nightfall-crypto/src/kernel.rs` |
| 2 | `crates/nightfall-crypto/src/lib.rs` |
| 2 | `crates/nightfall-crypto/src/schnorr.rs` |
| 2 | `crates/nightfall-ledger/src/aggregate.rs` |
| 2 | `crates/nightfall-ledger/src/builder.rs` |
| 2 | `crates/nightfall-ledger/src/lib.rs` |
| 2 | `crates/nightfall-ledger/src/tx.rs` |
| 2 | `crates/nightfall-ledger/src/utxo.rs` |
| 2 | `crates/nightfall-ledger/tests/exploit_regression.rs` |
| 2 | `crates/nightfall-node/src/main.rs` |

## SUPPLY-004 - mint_burn_accounting_surface

Status: `PASS`

Class: `inflation`

Risk: minted and burned value may not be traceable

Required terms: `mint`, `burn`

Found terms: `burn`, `mint`

| Score | Path |
|---:|---|
| 2 | `SECURITY.md` |
| 2 | `crates/nightfall-consensus/src/lib.rs` |
| 2 | `crates/nightfall-core/src/app.rs` |
| 2 | `crates/nightfall-core/src/views.rs` |
| 2 | `crates/nightfall-crypto/src/kernel.rs` |
| 2 | `crates/nightfall-ledger/src/lib.rs` |
| 2 | `crates/nightfall-ledger/src/utxo.rs` |
| 2 | `crates/nightfall-ledger/tests/ledger_flow.rs` |
| 2 | `crates/nightfall-node/src/main.rs` |
| 2 | `crates/nightfall-node/src/rpc.rs` |
| 2 | `crates/nightfall-node/src/runtime.rs` |
| 2 | `crates/nightfall-node/tests/multi_node_reorg.rs` |

## SUPPLY-005 - coinbase_maturity_surface

Status: `PASS`

Class: `consensus`

Risk: miner rewards may become spendable too early

Required terms: `coinbase`, `maturity`

Found terms: `coinbase`, `maturity`

| Score | Path |
|---:|---|
| 2 | `crates/nightfall-consensus/src/lib.rs` |
| 2 | `crates/nightfall-core/src/app.rs` |
| 2 | `crates/nightfall-core/src/views.rs` |
| 2 | `crates/nightfall-core/src/wallet_state.rs` |
| 2 | `crates/nightfall-crypto/src/stealth.rs` |
| 2 | `crates/nightfall-ledger/src/lib.rs` |
| 2 | `crates/nightfall-ledger/src/utxo.rs` |
| 2 | `crates/nightfall-ledger/tests/exploit_regression.rs` |
| 2 | `crates/nightfall-ledger/tests/ledger_flow.rs` |
| 2 | `crates/nightfall-mobile/src/lib.rs` |
| 2 | `crates/nightfall-node/src/runtime.rs` |
| 2 | `crates/nightfall-storage/src/lib.rs` |

## SUPPLY-006 - emission_schedule_surface

Status: `PASS`

Class: `monetary_policy`

Risk: monetary schedule may not be explicitly traceable

Required terms: `emission`

Found terms: `emission`

| Score | Path |
|---:|---|
| 1 | `SECURITY.md` |
| 1 | `crates/nightfall-consensus/Cargo.toml` |
| 1 | `crates/nightfall-consensus/src/lib.rs` |
| 1 | `crates/nightfall-consensus/tests/chain_rules.rs` |
| 1 | `docs/ATTRIBUTES.md` |
| 1 | `docs/AUDIT-2026-08-12.md` |
| 1 | `docs/AUDIT-2026-08-16.md` |
| 1 | `docs/AUDIT-2026-09-08.md` |
| 1 | `docs/DECISIONS.md` |
| 1 | `docs/HISTORY.md` |
| 1 | `docs/INTERNAL-SWAP-REVIEW-2026-09-13.md` |
| 1 | `docs/MAINNET.md` |

## SUPPLY-007 - max_supply_cap_surface

Status: `PASS`

Class: `monetary_policy`

Risk: maximum supply cap may not be traceable

Required terms: `supply`, `cap`

Found terms: `cap`, `supply`

| Score | Path |
|---:|---|
| 2 | `crates/nightfall-consensus/src/lib.rs` |
| 2 | `crates/nightfall-consensus/tests/chain_rules.rs` |
| 2 | `crates/nightfall-core/src/app.rs` |
| 2 | `crates/nightfall-core/src/view_layout_tests.rs` |
| 2 | `crates/nightfall-core/src/views.rs` |
| 2 | `crates/nightfall-crypto/src/pow.rs` |
| 2 | `crates/nightfall-ledger/src/lib.rs` |
| 2 | `crates/nightfall-ledger/src/utxo.rs` |
| 2 | `crates/nightfall-ledger/tests/ledger_flow.rs` |
| 2 | `crates/nightfall-node/src/main.rs` |
| 2 | `crates/nightfall-node/src/rpc.rs` |
| 2 | `crates/nightfall-node/src/runtime.rs` |

## SUPPLY-008 - fee_burn_surface

Status: `PASS`

Class: `monetary_policy`

Risk: fee handling may alter supply accounting

Required terms: `fee`, `burn`

Found terms: `burn`, `fee`

| Score | Path |
|---:|---|
| 2 | `crates/nightfall-consensus/src/lib.rs` |
| 2 | `crates/nightfall-core/src/app.rs` |
| 2 | `crates/nightfall-core/src/views.rs` |
| 2 | `crates/nightfall-crypto/src/kernel.rs` |
| 2 | `crates/nightfall-ledger/src/builder.rs` |
| 2 | `crates/nightfall-ledger/src/lib.rs` |
| 2 | `crates/nightfall-ledger/src/utxo.rs` |
| 2 | `crates/nightfall-ledger/tests/ledger_flow.rs` |
| 2 | `crates/nightfall-node/src/main.rs` |
| 2 | `crates/nightfall-node/src/rpc.rs` |
| 2 | `crates/nightfall-node/src/runtime.rs` |
| 2 | `crates/nightfall-node/tests/multi_node_reorg.rs` |

## SUPPLY-009 - range_proof_surface

Status: `PASS`

Class: `inflation`

Risk: invalid confidential amounts may bypass limits

Required terms: `range`, `proof`

Found terms: `proof`, `range`

| Score | Path |
|---:|---|
| 2 | `crates/nightfall-consensus/src/lib.rs` |
| 2 | `crates/nightfall-crypto/examples/scanbench.rs` |
| 2 | `crates/nightfall-crypto/src/commit.rs` |
| 2 | `crates/nightfall-crypto/src/lib.rs` |
| 2 | `crates/nightfall-crypto/src/rangeproof.rs` |
| 2 | `crates/nightfall-crypto/src/stealth.rs` |
| 2 | `crates/nightfall-ledger/src/lib.rs` |
| 2 | `crates/nightfall-ledger/src/tx.rs` |
| 2 | `crates/nightfall-ledger/src/utxo.rs` |
| 2 | `crates/nightfall-ledger/tests/exploit_regression.rs` |
| 2 | `crates/nightfall-ledger/tests/ledger_flow.rs` |
| 2 | `crates/nightfall-node/src/main.rs` |

## Runtime-safe probe summary

| ID | Name | Status | Return code |
|---|---|---|---:|
| INV-PROBE-001 | `grep_supply_invariant` | `PASS` | 0 |
| INV-PROBE-002 | `grep_utxo_kernel` | `PASS` | 0 |
| INV-PROBE-003 | `grep_mint_burn` | `PASS` | 0 |
| INV-PROBE-004 | `grep_coinbase_maturity` | `PASS` | 0 |
| INV-PROBE-005 | `grep_emission_cap` | `PASS` | 0 |
