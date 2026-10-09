# WVP Supply-Chain Policy

## Purpose

This policy defines minimum supply-chain controls for WVP Rust release-verification code.

WVP is security-sensitive tooling. Its own dependency graph must be reproducible, reviewable, and protected against silent dependency drift.

---

## Scope

This policy applies to Rust code under:

- `reference/rust/wvp-release-check`

---

## Required Controls

| Control | Requirement |
|---|---|
| Lockfile | `Cargo.lock` must exist |
| Locked metadata | `cargo metadata --locked` must succeed |
| Git dependencies | Direct Cargo `git =` dependencies are not allowed without explicit review |
| Release gate | Supply-chain checks must run in the central release quality gate |
| CI | The GitHub Actions workflow must run the central release quality gate |

---

## Rationale

A verifier cannot be treated as release-ready when its own dependency graph is not reproducible.

`Cargo.lock` makes dependency resolution reviewable.

`cargo metadata --locked` ensures dependency metadata is consistent with the lockfile.

Blocking direct Git dependencies prevents unpinned or moving external dependency sources from silently entering release-verification code.

---

## Review Rule

A change that modifies Rust dependencies must pass the supply-chain gate.

A change that adds a direct Git dependency must be rejected unless a future policy explicitly allows it with review evidence.

---

## Maintenance Rule

Any future package-management system added to WVP must define equivalent controls for:

1. lockfile presence,
2. deterministic dependency metadata,
3. CI enforcement,
4. documented review policy.

