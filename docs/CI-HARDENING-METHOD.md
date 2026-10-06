
# WVP CI Hardening Method

WVP-SEC-011 defines CI hardening for WVP evidence branches.

The goal is to make every pull request pass a stable required-check gate before merge.

## Controls

The CI hardening method requires:

- least-privilege workflow permissions
- checkout credentials not persisted
- job timeout
- concurrency control
- unit tests
- all WVP Nightfall checkers
- release-pack verification
- CI hardening self-check
- no secrets
- no live funds
- non-audit boundary

## Required workflow

The canonical required workflow is:

`.github/workflows/wvp-required-checks.yml`

The required job is:

`required`

Recommended GitHub required check name:

`WVP Required Checks / required`

## Boundary

CI passing does not prove implementation correctness, cryptographic soundness, consensus safety, or audit status.
