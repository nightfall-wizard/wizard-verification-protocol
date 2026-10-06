# ADR 0001: Release-Reality Core Boundary

## Status

Accepted for PR review.

## Context

The release checker had useful behavior, tests, and conformance gates, but core policy was less reviewable while concentrated in the executable entrypoint.

## Decision

Move release-reality behavior into a typed Rust library boundary:

- CLI remains thin.
- I/O is isolated behind provider code.
- Classification is pure and testable.
- Reporting is separate from verification logic.
- Checksum and signature verification are separate modules.

## Consequences

Positive:

- smaller review surface
- stronger regression tests
- easier fixture-driven checks
- clearer audit preparation

Tradeoff:

- more files
- slightly more module structure
- dependency on serde/serde_json for safer JSON rendering
