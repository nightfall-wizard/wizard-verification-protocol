# WVP v0.5-RC1 Public Verification Guide

## Purpose

This guide explains how an external reviewer can verify WVP v0.5-RC1 locally.

The goal is reproducibility.

A reviewer should not need to trust a screenshot, a claim, or a single passing test. The reviewer should be able to run the same release-readiness gate directly.

## Verification Scope

This guide applies to:

- WVP v0.5-RC1
- branch: `wvp-incident-001-nightfall-040-043-20261007-062725`
- evidence base commit: `a573149`
- generated: `2026-10-07T08:55:22Z`
- primary crate: `reference/rust/wvp-release-check`

## Minimum Verification Command

Run from the repository root:

```bash
bash tools/check_release_quality_gate.sh
```

A successful verification must end with:

```text
PASS: release quality gate passed
```

## Individual Verification Commands

The central release quality gate runs these checks:

```bash
bash tools/check_security_invariants.sh
bash tools/check_security_evidence_matrix.sh
bash tools/check_security_threat_model.sh
bash tools/check_rust_defensive_code.sh
bash tools/check_cargo_supply_chain.sh
bash tools/check_dependency_inventory.sh
bash tools/check_release_evidence_bundle.sh
bash tools/check_public_verification_guide.sh
bash tools/check_security_artifact_manifest.sh
cargo fmt --all -- --check
cargo test --all
```

## Expected Evidence

A successful local verification proves that:

1. security invariants exist,
2. negative fixtures exist,
3. executable security tests exist,
4. the threat model is linked to evidence,
5. defensive-code risk patterns did not increase,
6. Cargo dependency resolution is locked,
7. dependency inventory is current,
8. release evidence is present,
9. public verification instructions are present,
10. security-critical artifacts match committed hashes,
11. Rust formatting passes,
12. the full Rust test suite passes.

## Failure Rule

If any command fails, WVP v0.5-RC1 is not locally verified.

The correct response is to fix the failing gate, not to bypass it.

## Non-Goals

This guide does not prove that WVP is externally audited.

This guide does not prove that Nightfall or any upstream project is safe.

This guide does not replace cryptographic review.

This guide proves only that WVP's internal release-readiness evidence is reproducible by a reviewer.
