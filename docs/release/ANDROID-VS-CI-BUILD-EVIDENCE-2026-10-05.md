# Android vs CI Build Provenance Evidence

Date: 2026-10-05  
Module: `wvp-release-check`  
Commit: `75a777b37e23bf350057dfc8917ef9d29396a184`  
GitHub Actions Run ID: `37242108764`  
Evidence file: `target/wvp-android-vs-ci-build-provenance-comparison-75a777b/BUILD-PROVENANCE-COMPARISON.json`

## Status

Observed result: `PASS`

This document records one Android-Termux vs GitHub-Actions build-provenance comparison.

## Observed Evidence

| Field | Android-Termux | GitHub Actions |
|---|---:|---:|
| Environment class | `android-termux-aarch64` | `github-actions-linux-x86_64` |
| Git commit | `75a777b37e23bf350057dfc8917ef9d29396a184` | `75a777b37e23bf350057dfc8917ef9d29396a184` |
| Package version | `0.2.0` | `0.2.0` |
| Cargo.lock SHA256 | `ee77c281371c917af18cf52e06201f3b11ed15228e90fc2ae0763cbd7421b6e2` | `ee77c281371c917af18cf52e06201f3b11ed15228e90fc2ae0763cbd7421b6e2` |
| Rustc | `rustc 1.99.0 (b940084d7 2026-09-28) (built from a source tarball)` | `rustc 1.98.1 (48a229cea 2026-09-01)` |
| Cargo | `cargo 1.99.0 (5f94df478 2026-08-27) (built from a source tarball)` | `cargo 1.98.1 (797e8a9bc 2026-08-05)` |
| Binary SHA256 | `ec614692da779bd3d535eb3f7c0c2d0a5d0c94d8a7074e4a559171f001273ad9` | `29780484ea617e202d90374e38f0041feb3c2c6b5234c4fe52cb64950b6cbc18` |
| Binary size bytes | `676880` | `604832` |

## Comparison Results

| Check | Result |
|---|---:|
| Same environment class | `False` |
| Independent environment comparison performed | `True` |
| Linux vs Android comparison detected | `True` |
| Source commit match | `True` |
| Package version match | `True` |
| Cargo.lock hash match | `True` |
| Rustc version match | `False` |
| Cargo version match | `False` |
| Binary SHA256 match | `False` |
| Binary size match | `False` |

## Interpretation

- `verified`: same source commit.
- `verified`: same `Cargo.lock` hash.
- `verified`: same package version.
- `verified`: Android-Termux and GitHub Actions are treated as separate environment classes.
- `observed`: native binaries differ across architecture/toolchain.
- `observed`: binary hash mismatch is not treated as failure for this cross-environment comparison.
- `limitation`: this is not a reproducible-build proof.
- `limitation`: this is not a binary-safety proof.
- `limitation`: this does not prove the published release asset was built from source.

## Explicit Non-Claims

WVP does not claim from this evidence:

- that the binary is safe;
- that the release asset was built from source;
- that the build is reproducible;
- that cross-architecture binaries must be byte-identical;
- that this is an audit.

## Machine-Readable Source

The canonical machine-readable comparison is:

`target/wvp-android-vs-ci-build-provenance-comparison-75a777b/BUILD-PROVENANCE-COMPARISON.json`

