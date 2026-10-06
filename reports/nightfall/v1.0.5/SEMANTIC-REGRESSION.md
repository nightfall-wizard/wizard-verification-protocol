# WVP-SEC-003 - Semantic Regression Checks

This report converts WVP codepath bindings into executable
semantic checks against observable Nightfall files.

Boundary: this is static semantic evidence, not an audit.

Checks: 8
PASS: 8
WARN: 0

| Fixture | Status | Class | Missing terms |
|---|---|---|---|
| `thin_air_mint` | `PASS` | inflation | `-` |
| `negative_amount_attempt` | `PASS` | inflation | `-` |
| `fake_input_spend` | `PASS` | theft | `-` |
| `immature_coinbase_spend` | `PASS` | consensus | `-` |
| `duplicate_input` | `PASS` | consensus | `-` |
| `unsorted_block_body` | `PASS` | consensus | `-` |
| `invalid_kernel_excess` | `PASS` | inflation | `-` |
| `block_apply_atomicity_case` | `PASS` | consensus | `-` |

## thin_air_mint

Status: `PASS`

Risk: value creation outside valid accounting

Required terms: `supply`, `invariant`

Found terms: `invariant`, `supply`

Searched paths:

- `crates/nightfall-consensus/src/lib.rs`
- `crates/nightfall-core/src/views.rs`
- `crates/nightfall-ledger/src/lib.rs`
- `crates/nightfall-ledger/src/utxo.rs`
- `crates/nightfall-ledger/tests/ledger_flow.rs`
- `crates/nightfall-node/src/rpc.rs`
- `crates/nightfall-node/tests/multi_node_reorg.rs`
- `crates/nightfall-storage/src/lib.rs`

## negative_amount_attempt

Status: `PASS`

Risk: invalid amount accepted

Required terms: `range`, `proof`

Found terms: `proof`, `range`

Searched paths:

- `crates/nightfall-crypto/src/commit.rs`
- `crates/nightfall-crypto/src/rangeproof.rs`
- `crates/nightfall-ledger/tests/exploit_regression.rs`
- `crates/nightfall-node/src/rpc.rs`
- `docs/AUDIT-2026-08-12.md`
- `docs/AUDIT-2026-08-16.md`
- `docs/DECISIONS.md`
- `docs/MAINNET.md`

## fake_input_spend

Status: `PASS`

Risk: spending non-existing or unauthorized input

Required terms: `input`, `utxo`

Found terms: `input`, `utxo`

Searched paths:

- `crates/nightfall-core/src/views.rs`
- `crates/nightfall-crypto/src/lib.rs`
- `crates/nightfall-ledger/src/lib.rs`
- `crates/nightfall-ledger/src/tx.rs`
- `crates/nightfall-ledger/tests/exploit_regression.rs`
- `crates/nightfall-wallet/src/lib.rs`
- `docs/AUDIT-2026-08-12.md`
- `docs/AUDIT-2026-08-16.md`

## immature_coinbase_spend

Status: `PASS`

Risk: spending miner reward too early

Required terms: `coinbase`, `maturity`

Found terms: `coinbase`, `maturity`

Searched paths:

- `crates/nightfall-wallet/src/lib.rs`
- `crates/nightfall-consensus/src/lib.rs`
- `crates/nightfall-core/src/app.rs`
- `crates/nightfall-core/src/views.rs`
- `crates/nightfall-core/src/wallet_state.rs`
- `crates/nightfall-crypto/src/stealth.rs`
- `crates/nightfall-ledger/src/lib.rs`
- `crates/nightfall-ledger/src/utxo.rs`

## duplicate_input

Status: `PASS`

Risk: same input accepted twice

Required terms: `duplicate`, `input`

Found terms: `duplicate`, `input`

Searched paths:

- `crates/nightfall-consensus/src/lib.rs`
- `crates/nightfall-consensus/tests/chain_rules.rs`
- `crates/nightfall-wallet/src/lib.rs`
- `crates/nightfall-wallet/src/vault.rs`
- `crates/nightfall-web/src/vault.rs`
- `docs/SPEC.md`
- `docs/VAULT-FORMAT.md`
- `crates/nightfall-core/src/app.rs`

## unsorted_block_body

Status: `PASS`

Risk: canonical ordering not enforced

Required terms: `sort`

Found terms: `sort`

Searched paths:

- `crates/nightfall-consensus/src/lib.rs`
- `crates/nightfall-ledger/src/aggregate.rs`
- `crates/nightfall-ledger/src/utxo.rs`
- `crates/nightfall-wallet/src/lib.rs`
- `docs/SPEC.md`
- `crates/nightfall-consensus/src/difficulty.rs`
- `crates/nightfall-consensus/tests/chain_rules.rs`
- `crates/nightfall-core/src/app.rs`

## invalid_kernel_excess

Status: `PASS`

Risk: hidden value through invalid excess

Required terms: `kernel`, `excess`

Found terms: `excess`, `kernel`

Searched paths:

- `crates/nightfall-consensus/src/lib.rs`
- `crates/nightfall-crypto/src/kernel.rs`
- `crates/nightfall-crypto/src/lib.rs`
- `crates/nightfall-crypto/src/schnorr.rs`
- `crates/nightfall-ledger/src/aggregate.rs`
- `crates/nightfall-ledger/src/lib.rs`
- `crates/nightfall-ledger/src/tx.rs`
- `crates/nightfall-ledger/tests/exploit_regression.rs`

## block_apply_atomicity_case

Status: `PASS`

Risk: rejected block mutates state

Required terms: `atomic`

Found terms: `atomic`

Searched paths:

- `docs/AUDIT-2026-08-12.md`
- `docs/DECISIONS.md`
- `crates/nightfall-consensus/src/lib.rs`
- `crates/nightfall-core/src/app.rs`
- `crates/nightfall-core/src/vault_ui.rs`
- `crates/nightfall-core/src/views.rs`
- `crates/nightfall-core/src/wallet_state.rs`
- `crates/nightfall-ledger/src/lib.rs`
