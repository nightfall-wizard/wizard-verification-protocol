# Independent-Environment Evidence Separation

## Status

This document defines how WVP separates build evidence by environment class.

This is not a reproducible-build proof.

This is not independent reproducibility evidence by itself.

This is not a binary-safety proof.

This is not an audit.

## Purpose

Single-environment build evidence and same-environment repeat-build evidence are useful, but they must not be confused with independent-environment reproducibility.

WVP therefore separates evidence into explicit environment classes before comparing build outputs.

## Environment classes

### android-termux-aarch64

Evidence produced on Android through Termux on an aarch64 device.

This is the mobile-built WVP reference path.

### github-actions-linux-x86_64

Evidence produced inside GitHub Actions on Linux x86_64 runners.

This is a CI evidence path.

### linux-aarch64

Evidence produced on Linux aarch64 outside Android/Termux.

### linux-x86_64

Evidence produced on Linux x86_64 outside GitHub Actions.

### unknown

Evidence where the environment cannot be classified reliably.

Unknown environment evidence must not be used for strong reproducibility claims.

## Separation rule

Evidence from one environment class must not be treated as equivalent to evidence from another environment class unless a comparison document explicitly records:

- both environment classes
- both source commits
- both toolchains
- both Cargo.lock hashes
- both binary hashes
- whether binary hashes match
- whether binary sizes match
- limitations

## Independent evidence requirement

Independent-environment evidence requires at least two separately classified environments.

A same-environment repeat-build match is not enough.

A CI-only build is not enough.

A Termux-only build is not enough.

## Required claim state

Until independent matching builds exist, the required claim remains:

- `reproducible_build_claim: false`

The environment separation evidence type is:

- `independent-environment-evidence-separation`

## Limitations

Environment classification is not a reproducible-build proof.

Environment classification does not prove source-build correspondence.

Environment classification does not prove binary safety.

Environment classification only prevents evidence categories from being mixed incorrectly.

## Android/Termux detection note

Android through Termux may report:

- `uname_s`: `Linux`
- `uname_m`: `aarch64`
- `uname -a`: a string containing both `aarch64` and `Android`
- `PREFIX`: `/data/data/com.termux/files/usr`
- `TERMUX_VERSION`: a Termux version string

Therefore Android/Termux evidence must be classified before the generic `linux-aarch64` fallback.
