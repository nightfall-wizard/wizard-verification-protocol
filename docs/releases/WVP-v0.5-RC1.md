# WVP v0.5-RC1 Release Evidence Bundle

## Purpose

This document records the release-readiness evidence for WVP v0.5-RC1.

WVP v0.5-RC1 is a release-candidate evidence bundle for the Rust release-check reference implementation and its security gates.

## Release Candidate Identity

| Field | Value |
|---|---|
| Release candidate | WVP v0.5-RC1 |
| Branch | `wvp-incident-001-nightfall-040-043-20261007-062725` |
| Evidence base commit | `a573149` |
| Evidence generated | `2026-10-07T08:55:22Z` |
| Primary crate | `reference/rust/wvp-release-check` |

## Required Gates

WVP v0.5-RC1 is release-ready only when the central release quality gate passes.

Required checks:

- `tools/check_security_invariants.sh`
- `tools/check_security_evidence_matrix.sh`
- `tools/check_security_threat_model.sh`
- `tools/check_rust_defensive_code.sh`
- `tools/check_cargo_supply_chain.sh`
- `tools/check_dependency_inventory.sh`
- `tools/check_release_evidence_bundle.sh`
- `tools/check_public_verification_guide.sh`
- `tools/check_security_artifact_manifest.sh`
- `cargo fmt --all -- --check`
- `cargo test --all`

## Evidence Summary

| Evidence Area | Status |
|---|---|
| Security invariants | Covered |
| Negative fixtures | Covered |
| Executable fixture tests | Covered |
| Evidence matrix | Covered |
| Threat model | Covered |
| Defensive Rust baseline | Covered |
| Cargo supply-chain reproducibility | Covered |
| Cargo dependency inventory | Covered |
| Release evidence bundle | Covered |
| Public verification guide | Covered |
| Security artifact manifest | Covered |
| Central release quality gate | Covered |
| Rust formatting | Covered |
| Full Rust test suite | Covered |

## Security Posture

WVP v0.5-RC1 has internal controls for:

1. fail-closed release verification behavior,
2. negative fixture coverage,
3. executable security specification tests,
4. documented threat model,
5. defensive-code drift prevention,
6. dependency reproducibility,
7. dependency inventory drift detection,
8. release evidence verification,
9. public reviewer verification guidance,
10. security artifact hash control,
11. centralized release-readiness enforcement.

## Non-Goals

WVP v0.5-RC1 does not prove that WVP is externally audited.

WVP v0.5-RC1 does not prove that Nightfall or any upstream project is safe.

WVP v0.5-RC1 does not replace cryptographic review.

WVP v0.5-RC1 proves only that WVP's internal release-readiness evidence is complete and currently passing.

## Release Rule

A release candidate is incomplete unless this document, the public verification guide, the central release quality gate, and all security-controlled artifacts pass together.
