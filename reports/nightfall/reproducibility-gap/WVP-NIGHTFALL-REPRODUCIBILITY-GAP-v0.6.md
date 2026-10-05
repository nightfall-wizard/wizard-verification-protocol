# WVP Nightfall Reproducibility Gap v0.6

Generated UTC: `2026-10-05T15:08:03Z`

## Scope

This report checks reproducibility-related build metadata for Nightfall.

Repository checked:

- `Instinctes/nightfall`

Release:

- tag: `v1.0.5`
- name: `NIGHTFALLCOIN Core 1.0.5`
- published at: `2026-09-22T03:34:27Z`
- release author: `Instinctes`
- tag commit: `9591ac0a3a58f734883f8b248b7b05aac88ee8f0`

This report is stacked after:

- `WVP Nightfall Source-to-Release Boundary v0.5`

## Safety boundary

No release binary is executed.

No local release build is performed.

This report checks metadata and reproducibility gaps only.

## Reproducibility evidence

| Field | Value |
|---|---:|
| Cargo.lock present | `yes` |
| Cargo.lock SHA256 | `f95730fdfeec1e1651aeba5fc0017aff3443dc206ffd0f94fd4ba08dc1d82014` |
| Toolchain file | `none` |
| Exact Rust toolchain pinned | `unknown_or_absent` |
| Release workflow present | `yes` |
| GitHub Actions uses lines | `12` |
| GitHub Actions SHA-pinned uses lines | `0` |
| GitHub Actions non-SHA uses lines | `12` |
| Actions pinning status | `some_or_all_actions_not_sha_pinned` |
| Runner lines | `4` |
| Floating runner lines | `3` |
| Runner pinning status | `floating_runner_detected` |
| Build command surface count | `19` |
| Reproducibility gap level | `material_reproducibility_gap` |

## GitHub Actions dependency lines

```text
- uses: actions/checkout@v4
- uses: dtolnay/rust-toolchain@stable
- uses: Swatinem/rust-cache@v2
- uses: actions/checkout@v4
- uses: dtolnay/rust-toolchain@stable
- uses: Swatinem/rust-cache@v2
- uses: actions/checkout@v4
- uses: dtolnay/rust-toolchain@stable
- uses: Swatinem/rust-cache@v2
- uses: actions/checkout@v4
- uses: dtolnay/rust-toolchain@stable
- uses: Swatinem/rust-cache@v2
```

## Runner lines

```text
- runs-on: ubuntu-latest
- runs-on: ${{ matrix.os }}
- runs-on: windows-latest
- runs-on: ubuntu-latest
```

## Build command surface

```text
- /data/data/com.termux/files/home/.tmp/wvp-nightfall-v06/nightfall/README.md:99:cargo build --release -p nightfall-core
- /data/data/com.termux/files/home/.tmp/wvp-nightfall-v06/nightfall/README.md:260:cargo run --release -p nightfall-crypto --example powbench
- /data/data/com.termux/files/home/.tmp/wvp-nightfall-v06/nightfall/README.md:273:`cargo run --release -p nightfall-node --example checkpoint -- <height>`.
- /data/data/com.termux/files/home/.tmp/wvp-nightfall-v06/nightfall/README.md:281:cargo build --release -p nightfall-node -p nightfall-wallet
- /data/data/com.termux/files/home/.tmp/wvp-nightfall-v06/nightfall/README.md:385:cargo test --workspace
- /data/data/com.termux/files/home/.tmp/wvp-nightfall-v06/nightfall/CONTRIBUTING.md:25:cargo fmt --all
- /data/data/com.termux/files/home/.tmp/wvp-nightfall-v06/nightfall/CONTRIBUTING.md:26:cargo clippy --workspace --all-targets    # must be clean, not "mostly clean"
- /data/data/com.termux/files/home/.tmp/wvp-nightfall-v06/nightfall/CONTRIBUTING.md:27:cargo test --workspace
- /data/data/com.termux/files/home/.tmp/wvp-nightfall-v06/nightfall/.github/workflows/ci.yml:33:        run: cargo fmt --all --check
- /data/data/com.termux/files/home/.tmp/wvp-nightfall-v06/nightfall/.github/workflows/ci.yml:38:        run: cargo clippy --workspace --all-targets -- -D warnings
- /data/data/com.termux/files/home/.tmp/wvp-nightfall-v06/nightfall/.github/workflows/ci.yml:41:        run: cargo test --workspace
- /data/data/com.termux/files/home/.tmp/wvp-nightfall-v06/nightfall/.github/workflows/ci.yml:73:        run: cargo test -p nightfall-ledger --test exploit_regression -- --nocapture
- /data/data/com.termux/files/home/.tmp/wvp-nightfall-v06/nightfall/.github/workflows/ci.yml:78:        run: cargo test -p nightfall-storage --test reorg_persistence
- /data/data/com.termux/files/home/.tmp/wvp-nightfall-v06/nightfall/.github/workflows/ci.yml:100:        run: cargo build --release -p nightfall-node -p nightfall-wallet -p nightfall-core
- /data/data/com.termux/files/home/.tmp/wvp-nightfall-v06/nightfall/.github/workflows/ci.yml:111:        run: cargo test -p nightfall-wallet --lib
- /data/data/com.termux/files/home/.tmp/wvp-nightfall-v06/nightfall/.github/workflows/release.yml:48:        run: cargo test --workspace
- /data/data/com.termux/files/home/.tmp/wvp-nightfall-v06/nightfall/.github/workflows/release.yml:51:        run: cargo build --release -p nightfall-core -p nightfall-node -p nightfall-wallet
- /data/data/com.termux/files/home/.tmp/wvp-nightfall-v06/nightfall/.github/workflows/release.yml:173:        run: cargo test --workspace
- /data/data/com.termux/files/home/.tmp/wvp-nightfall-v06/nightfall/.github/workflows/release.yml:176:        run: cargo build --release -p nightfall-core -p nightfall-node -p nightfall-wallet
```

## Verdict

```text
cargo-lock-present: yes
exact-rust-toolchain-pinned: unknown_or_absent
actions-sha-pinning-status: some_or_all_actions_not_sha_pinned
runner-pinning-status: floating_runner_detected
build-command-surface-present: yes
local-build-performed: no
byte-identical-rebuild-performed: no
source-to-binary-proven: no
reproducible-build-proven: no
binary-safety-proven: no
reproducibility-gap-level: material_reproducibility_gap
```

## Interpretation

This v0.6 report checks whether the public source tree contains enough build metadata to move toward reproducible build verification.

It does not prove:

- that release binaries match source;
- that binaries were built by GitHub Actions;
- that builds are byte-identical reproducible;
- that the build environment is fully pinned;
- that binaries are safe;
- that Nightfall is externally audited.

## Hard boundary

A project can have Cargo.lock, release workflows and checksum files and still not have reproducible builds.

WVP must not treat build metadata as source-to-binary proof.

No legal, custody or investment claim is made.

## Next correct step

The next WVP step should be:

```text
wvp-nightfall-build-attestation-gap-v0.7
```

It should check:

1. whether GitHub provenance attestations exist;
2. whether release assets have build provenance;
3. whether workflow run IDs can be linked to release assets;
4. whether artifacts can be traced to a specific commit;
5. whether SLSA-style provenance is present or absent;
6. whether source-to-binary remains unproven.
