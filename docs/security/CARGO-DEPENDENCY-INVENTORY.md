# WVP Cargo Dependency Inventory

## Purpose

This document records the current Rust dependency inventory for WVP release-verification code.

The goal is to make dependency drift visible and reviewable.

A change to `Cargo.lock` is security-relevant because WVP is verification software.

---

## Scope

Inventory scope:

- `Cargo.toml`
- `reference/rust/wvp-release-check/Cargo.toml`
- `Cargo.lock`

---

## Current Cargo.lock Hash

```text
78cf87b89da0009d8742cebd829b6463d154d29be882c684f38635675c427e8e  Cargo.lock
```

---

## Required Checks

| Check | Required |
|---|---|
| Cargo.lock exists | yes |
| Cargo.lock hash recorded | yes |
| cargo metadata locked | yes |
| cargo tree locked | yes |
| direct Cargo git dependencies blocked | yes |
| release quality gate enforces dependency inventory | yes |

---

## Current Dependency Tree

Generated with:

```bash
cargo tree --locked --manifest-path "reference/rust/wvp-release-check/Cargo.toml"
```

Summary:

- direct root-package lines detected: 1
- total dependency-tree lines: 57

```text
wvp-release-check v0.3.0 (/data/data/com.termux/files/home/wizard-verification-protocol/reference/rust/wvp-release-check)
├── serde v1.0.229
│   ├── serde_core v1.0.229
│   └── serde_derive v1.0.229 (proc-macro)
│       ├── proc-macro2 v1.0.107
│       │   └── unicode-ident v1.0.26
│       ├── quote v1.0.47
│       │   └── proc-macro2 v1.0.107 (*)
│       └── syn v3.0.6
│           ├── proc-macro2 v1.0.107 (*)
│           ├── quote v1.0.47 (*)
│           └── unicode-ident v1.0.26
└── serde_json v1.0.151
    ├── itoa v1.0.18
    ├── memchr v2.8.3
    ├── serde_core v1.0.229
    └── zmij v1.0.23
[dev-dependencies]
└── proptest v1.11.0
    ├── bit-set v0.8.0
    │   └── bit-vec v0.8.0
    ├── bit-vec v0.8.0
    ├── bitflags v2.13.2
    ├── num-traits v0.2.19
    │   [build-dependencies]
    │   └── autocfg v1.5.1
    ├── rand v0.9.5
    │   └── rand_core v0.9.5
    │       └── getrandom v0.3.4
    │           ├── cfg-if v1.0.5
    │           └── libc v0.2.190
    ├── rand_chacha v0.9.0
    │   ├── ppv-lite86 v0.2.21
    │   │   └── zerocopy v0.8.60
    │   └── rand_core v0.9.5 (*)
    ├── rand_xorshift v0.4.0
    │   └── rand_core v0.9.5 (*)
    ├── regex-syntax v0.8.11
    ├── rusty-fork v0.3.1
    │   ├── fnv v1.0.7
    │   ├── quick-error v1.2.3
    │   ├── tempfile v3.27.0
    │   │   ├── fastrand v2.5.0
    │   │   ├── getrandom v0.4.3
    │   │   │   ├── cfg-if v1.0.5
    │   │   │   └── libc v0.2.190
    │   │   ├── once_cell v1.21.4
    │   │   └── rustix v1.1.5
    │   │       ├── bitflags v2.13.2
    │   │       ├── errno v0.3.14
    │   │       │   └── libc v0.2.190
    │   │       ├── libc v0.2.190
    │   │       └── linux-raw-sys v0.12.1
    │   └── wait-timeout v0.2.1
    │       └── libc v0.2.190
    ├── tempfile v3.27.0 (*)
    └── unarray v0.1.4
```

---

## Review Rule

A pull request that changes `Cargo.lock` must update this inventory.

A pull request that changes dependencies but does not update this file is incomplete.

---

## Security Rule

Direct Cargo `git =` dependencies are not allowed unless a future policy explicitly defines review evidence, pinning requirements, and reproducibility controls.

---

## Maintenance Rule

When dependencies change, update:

1. `Cargo.lock`,
2. `security-baselines/cargo-lock.sha256`,
3. `docs/security/CARGO-DEPENDENCY-INVENTORY.md`,
4. the release quality gate result.

