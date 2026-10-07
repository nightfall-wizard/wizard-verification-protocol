# Rust Risk Pattern Baseline

## Purpose

This file records the current defensive-code baseline for WVP production Rust code.

The CI gate fails if any tracked risk-pattern count increases.

## Scope

- `reference/rust/wvp-release-check/src`

## Current Baseline

| Pattern | Count |
|---|---:|
| unwrap calls | 17 |
| .unwrap calls | 17 |
| expect calls | 5 |
| .expect calls | 5 |
| panic calls | 0 |
| todo calls | 0 |
| unimplemented calls | 0 |
| dbg calls | 0 |
| unsafe markers | 0 |
| allow unused | 0 |
| allow dead_code | 0 |

## Maintenance Rule

A later PR improves the repository when it reduces one or more counts without weakening behavior.

A later PR must not increase these counts unless the change is explicitly justified and reviewed.

