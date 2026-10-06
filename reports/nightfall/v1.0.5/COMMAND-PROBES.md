# WVP-SEC-004 - Nightfall Command Probes

This report captures reproducible local command evidence.

Boundary: this is not an audit.

Probe count: 10
PASS: 9
WARN: 1

| ID | Name | Class | Status | Return code |
|---|---|---|---|---:|
| NF-PROBE-001 | `nightfall_repo_exists` | repository | `PASS` | 0 |
| NF-PROBE-002 | `nightfall_git_head` | repository | `PASS` | 0 |
| NF-PROBE-003 | `nightfall_git_status` | repository | `PASS` | 0 |
| NF-PROBE-004 | `spec_exists` | documentation | `PASS` | 0 |
| NF-PROBE-005 | `security_policy_exists` | documentation | `PASS` | 0 |
| NF-PROBE-006 | `supply_terms_present` | inflation | `PASS` | 0 |
| NF-PROBE-007 | `coinbase_maturity_terms_present` | consensus | `PASS` | 0 |
| NF-PROBE-008 | `cargo_workspace_metadata` | build | `PASS` | 0 |
| NF-PROBE-009 | `cargo_test_no_run` | build | `WARN` | 124 |
| NF-PROBE-010 | `release_workflows_present` | release_integrity | `PASS` | 0 |

## NF-PROBE-001 - nightfall_repo_exists

Status: `PASS`

Class: `repository`

Command:

```bash
test -d "$HOME/nightfall"
```

Stdout:

```text

```


## NF-PROBE-002 - nightfall_git_head

Status: `PASS`

Class: `repository`

Command:

```bash
git rev-parse HEAD
```

Stdout:

```text
f477b69f189054f09cbef84d6ac6c2ec5e36ff3c

```


## NF-PROBE-003 - nightfall_git_status

Status: `PASS`

Class: `repository`

Command:

```bash
git status --short
```

Stdout:

```text

```


## NF-PROBE-004 - spec_exists

Status: `PASS`

Class: `documentation`

Command:

```bash
test -f docs/SPEC.md
```

Stdout:

```text

```


## NF-PROBE-005 - security_policy_exists

Status: `PASS`

Class: `documentation`

Command:

```bash
test -f SECURITY.md
```

Stdout:

```text

```


## NF-PROBE-006 - supply_terms_present

Status: `PASS`

Class: `inflation`

Command:

```bash
grep -RniE 'supply|invariant|kernel_excess|minted|burned' docs SECURITY.md crates 2>/dev/null | head -80
```

Stdout:

```text
docs/RESET.md:17:| 89 M minted | ~7 years | **~23.5 years** |
docs/RESET.md:18:| Terminal supply | 89,999,999.7075 | **89,999,999.25** (0.75 NIGHT short of the cap) |
docs/RESET.md:19:| Fees while subsidy > 0 | burned | **burned** |
docs/RESET.md:20:| Fees after subsidy | burned (miner unpaid) | **paid to the miner**, not minted, not burned |
docs/SWAP-ATTACKS.md:47:  same invariant, hundreds of ticks, not weeks.
docs/GETTING-NIGHT.md:39:Fees stop being burned and go to the miner once the subsidy runs out.
docs/GETTING-NIGHT.md:44:The practical horizon is much nearer: 89 million are minted in about
docs/DECISIONS.md:13:| 3 | Supply verification | Global invariant `Σ UTXO − Σ kernel_excess = (minted − burned)·G`, checked after every block, on startup, and via RPC. Supply is now *provable*, not asserted. |
docs/whitepaper-en.json:3:  "subtitle": "Private settlement. Verifiable supply.",
docs/whitepaper-en.json:23:          "text": "The central design choice is to combine private payment amounts with an explicit supply invariant. Nodes check a relationship between unspent commitments, accumulated kernel excesses, issuance and burned fees. That relationship is useful only together with valid range proofs, signatures, authorization and correct state transitions. An equation by itself is not a security proof."
docs/whitepaper-en.json:255:      "label": "05 / The supply invariant",
docs/whitepaper-en.json:274:            "= (total minted - total burned fees) G"
docs/whitepaper-en.json:276:          "caption": "Global invariant. UTXO commitments and kernel excesses are group elements; minted and burned values are integer accounting totals."
docs/whitepaper-en.json:280:          "text": "Starting from the defined genesis state, accepted transitions preserve this invariant. Range proofs exclude invalid value encodings; input signatures establish spending authority; UTXO checks prevent double spending; emission rules bound coinbase issuance. Removing any of these checks changes the security argument."
docs/whitepaper-en.json:288:          "text": "The network page displays a node's reported totals and invariant result. The browser does not independently replay the ledger or verify the full cryptographic statement. Independent verification requires a validating implementation and an understood policy for trusted local state and historical checkpoints."
docs/whitepaper-en.json:351:          "text": "A miner's proposed block must satisfy shape, ordering, parent linkage, timing, difficulty, proof-of-work, authorization, commitment and issuance checks. Rejected transitions must not partially alter ledger state. Transaction selection in the current mempool sorts candidates by fee and skips conflicts; fees are nevertheless burned during subsidy eras."
docs/whitepaper-en.json:385:          "caption": "Height h is zero-based. One NIGHT is 100,000,000 darks. The implementation also enforces the remaining supply ceiling."
docs/whitepaper-en.json:390:          "caption": "Share of the 90 million ceiling at the end of each era. These are supply shares, not returns. Heights determine issuance; calendar dates do not."
docs/whitepaper-en.json:407:              "Fees are destroyed; circulation decreases by the burned amount."
docs/whitepaper-en.json:438:          "text": "Era e covers heights e x 7,500,000 through (e + 1) x 7,500,000 - 1. At height 225,000,000 the scheduled subsidy is zero. Fees burned in earlier eras are not reissued. Actual circulating supply can therefore be lower than the cumulative issuance shown."
docs/CORE_WALLET.md:29:wallet payment fee is 0.001 NIGHT, burned while subsidy remains. An outgoing
docs/MOBILE.md:278:- **Fees are burned, not paid to a miner.** Worth one line in the UI, because
docs/AUDIT-2026-08-16.md:13:the supply. The new risk is not a tautological balance proof — it is
docs/AUDIT-2026-08-16.md:41:| C-06 | 90 M cap not enforced | Critical | **Closed.** Emission + invariant. |
docs/AUDIT-2026-08-16.md:72:| **S-01** |
```


## NF-PROBE-007 - coinbase_maturity_terms_present

Status: `PASS`

Class: `consensus`

Command:

```bash
grep -RniE 'coinbase|maturity|1440' docs SECURITY.md crates 2>/dev/null | head -80
```

Stdout:

```text
docs/DECISIONS.md:20:| 10 | Coinbase maturity | 1,440 mainnet / 60 testnet / 10 devnet. v4 had none. |
docs/DECISIONS.md:57:| 9 | Coinbase | Shielded miner note bound by emission schedule and Pedersen balance. — **The binding did not exist.** |
docs/whitepaper-en.json:264:          "caption": "Local balance equation. The reward term includes the permitted coinbase value; after subsidy ends, coinbase value is funded by fees rather than new issuance."
docs/whitepaper-en.json:280:          "text": "Starting from the defined genesis state, accepted transitions preserve this invariant. Range proofs exclude invalid value encodings; input signatures establish spending authority; UTXO checks prevent double spending; emission rules bound coinbase issuance. Removing any of these checks changes the security argument."
docs/whitepaper-en.json:336:              "Coinbase maturity",
docs/whitepaper-en.json:412:              "Fees fund the miner's coinbase; no additional issuance or fee burn."
docs/whitepaper-en.json:463:              "Input/output structure, public fees, block timing, coinbase flags and graph information."
docs/whitepaper-en.json:1110:              "Target block time / coinbase maturity",
docs/whitepaper-en.json:1137:          "text": "UTXO: an unspent output recorded by the ledger. Commitment: a group element representing a hidden value and blinding factor. Kernel: a signed record of public transaction terms and excess. Range proof: evidence that a committed value is within the allowed interval. Coinbase: the miner's permitted output, subject to maturity. Reorganization: replacement of a suffix of accepted history. Checkpoint: a compiled height/hash constraint. Bootstrap: a delivery format for historical chain data, not a new consensus authority."
docs/MOBILE.md:264:2. Select coins, excluding immature coinbase outputs. **Mined coins are locked
docs/AUDIT-2026-08-16.md:52:| E-02 | No coinbase maturity | Medium | **Closed.** 1,440 mainnet. |
docs/AUDIT-2026-08-16.md:147:A reorg deeper than coinbase maturity (1,440 blocks, ~6 hours) can
docs/AUDIT-2026-08-16.md:202:one coinbase and nothing else has an anonymity set of one.
docs/AUDIT-2026-08-16.md:309:- mint NIGHT without a coinbase that pays the schedule
docs/SPEC.md:64:features:     Plain | Coinbase   public; drives maturity
docs/SPEC.md:95:feature:     Plain | Coinbase
docs/SPEC.md:97:reward_darks:u64        coinbase only
docs/SPEC.md:215:### 2.4 Coinbase maturity
docs/SPEC.md:327:the subsidy. After the subsidy is zero, the coinbase kernel carries the block's
docs/SPEC.md:343:- coinbase kernels carry no fee; plain kernels carry no reward
docs/SPEC.md:344:- a coinbase spends no inputs
docs/SPEC.md:354:- coinbase is transaction 0 and the only one
docs/MAINNET.md:260:Coinbase outputs mature after **1,440 blocks** (~6 h) before they can be spent.
docs/MAINNET.md:288:| Coinbase maturity | 1,440 blocks |
docs/AUDIT-2026-08-12.md:8:At the time of the audit the live mainnet datadir held 84 blocks, 1,680 NIGHT, exactly one non-coinbase transaction and two distinct recipient keys — i.e. only the operator's own machine. **The vulnerability had not been exploited.**
docs/AUDIT-2026-08-12.md:41:| **E-02** | No coinbase maturity — reorgs cascade | **Medium** | Fixed |
docs/AUDIT-2026-08-12.md:234:| **E-02** | No coinbase maturity, so a reorg orphaning a block invalidated every transaction spending its subsidy, cascading arbitrarily. | 1,440 blocks on mainnet, 60 on testnet, 10 on devnet. |
docs/AUDIT-2026-08-12.md:284:* `crates/nightfall-ledger/tests/ledger_flow.rs` — coinbase, transfer, fee burn, double-spend, maturity, atomicity, supply invariant.
docs/DEV-WALLET-1.0.0-dev.2.md:45:3. **Lokale Coins:** Mining starten. Devnet-Coinbase wird nach zehn Blöcken
docs/DEV-WALLET-1.0.0.md:32:3. Mining starten, um lokale Testcoins zu erzeugen. Coinbase-Ausgänge werden
docs/emission/NIGHTFALL-emission-schedule.html:494:      <p>Once the subsidy reaches zero the coinbase kernel carries the block'
```


## NF-PROBE-008 - cargo_workspace_metadata

Status: `PASS`

Class: `build`

Command:

```bash
cargo metadata --no-deps --format-version 1
```

Stdout:

```text
s_default_features":true,"features":["derive"],"target":null,"registry":null},{"name":"serde_json","source":"registry+https://github.com/rust-lang/crates.io-index","req":"^1","kind":null,"rename":null,"optional":false,"uses_default_features":true,"features":[],"target":null,"registry":null},{"name":"tracing","source":"registry+https://github.com/rust-lang/crates.io-index","req":"^0.1","kind":null,"rename":null,"optional":false,"uses_default_features":true,"features":[],"target":null,"registry":null},{"name":"tracing-subscriber","source":"registry+https://github.com/rust-lang/crates.io-index","req":"^0.3","kind":null,"rename":null,"optional":false,"uses_default_features":true,"features":["env-filter"],"target":null,"registry":null},{"name":"ureq","source":"registry+https://github.com/rust-lang/crates.io-index","req":"^2","kind":null,"rename":null,"optional":false,"uses_default_features":false,"features":["json","tls"],"target":null,"registry":null},{"name":"zeroize","source":"registry+https://github.com/rust-lang/crates.io-index","req":"^1","kind":null,"rename":null,"optional":false,"uses_default_features":true,"features":["derive"],"target":null,"registry":null},{"name":"tray-icon","source":"registry+https://github.com/rust-lang/crates.io-index","req":"^0.19","kind":null,"rename":null,"optional":false,"uses_default_features":true,"features":[],"target":"cfg(any(target_os = \"windows\", target_os = \"macos\"))","registry":null},{"name":"objc2-app-kit","source":"registry+https://github.com/rust-lang/crates.io-index","req":"^0.2.2","kind":null,"rename":null,"optional":false,"uses_default_features":true,"features":["NSApplication","NSResponder","NSView","NSWindow"],"target":"cfg(target_os = \"macos\")","registry":null},{"name":"objc2-foundation","source":"registry+https://github.com/rust-lang/crates.io-index","req":"^0.2.2","kind":null,"rename":null,"optional":false,"uses_default_features":true,"features":[],"target":"cfg(target_os = \"macos\")","registry":null}],"targets":[{"kind":["bin"],"crate_types":["bin"],"name":"nightfall-core","src_path":"/data/data/com.termux/files/home/nightfall/crates/nightfall-core/src/main.rs","edition":"2021","doc":true,"doctest":false,"test":true}],"features":{},"manifest_path":"/data/data/com.termux/files/home/nightfall/crates/nightfall-core/Cargo.toml","metadata":null,"publish":null,"authors":[],"categories":[],"keywords":[],"readme":null,"repository":null,"homepage":null,"documentation":null,"edition":"2021","links":null,"default_run":null,"rust_version":null},{"name":"nightfall-mobile","version":"1.0.5","id":"path+file:///data/data/com.termux/files/home/nightfall/crates/nightfall-mobile#1.0.5","license":"MIT OR Apache-2.0","license_file":null,"description":"FFI surface for the Nightfall phone wallets","source":null,"dependencies":[{"name":"anyhow","source":"registry+https://github.com/rust-lang/crates.io-index","req":"^1","kind":null,"rename":null,"optional":false,"uses_default_features":true,"features":[],"target":null,"registry":null},{"name":"hex","source":"registry+https://github.com/rust-lang/crates.io-index","req":"^0.4","kind":null,"rename":null,"optional":false,"uses_default_features":true,"features":[],"target":null,"registry":null},{"name":"nightfall-crypto","source":null,"req":"*","kind":null,"rename":null,"optional":false,"uses_default_features":true,"features":[],"target":null,"registry":null,"path":"/data/data/com.termux/files/home/nightfall/crates/nightfall-crypto"},{"name":"nightfall-ledger","source":null,"req":"*","kind":null,"rename":null,"optional":false,"uses_default_features":true,"features":[],"target":null,"registry":null,"path":"/data/data/com.termux/files/home/nightfall/crates/nightfall-ledger"},{"name":"nightfall-types","source":null,"req":"*","kind":null,"rename":null,"optional":false,"uses_default_features":true,"features":[],"target":null,"registry":null,"path":"/data/data/com.termux/files/home/nightfall/crates/nightfall-types"},{"name":"nightfall-wallet","source":nu
```


## NF-PROBE-009 - cargo_test_no_run

Status: `WARN`

Class: `build`

Command:

```bash
cargo test --workspace --no-run
```

Stdout:

```text

```

Stderr:

```text
timeout
```

## NF-PROBE-010 - release_workflows_present

Status: `PASS`

Class: `release_integrity`

Command:

```bash
find .github/workflows -maxdepth 1 -type f -print
```

Stdout:

```text
.github/workflows/ci.yml
.github/workflows/release.yml

```
