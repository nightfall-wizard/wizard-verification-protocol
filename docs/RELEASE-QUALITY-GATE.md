# WVP Release Quality Gate

## Purpose

This document defines the minimum quality gate for WVP release-readiness.

A change is not considered release-ready unless it passes all security, evidence, threat-model, defensive-code, supply-chain, formatting, and test gates.

The goal is to make release quality explicit, repeatable, and enforceable.

---

## Required Gates

| Gate | Required Check |
|---|---|
| Security invariants | `tools/check_security_invariants.sh` |
| Security evidence matrix | `tools/check_security_evidence_matrix.sh` |
| Security threat model | `tools/check_security_threat_model.sh` |
| Defensive Rust code baseline | `tools/check_rust_defensive_code.sh` |
| Cargo supply-chain reproducibility | `tools/check_cargo_supply_chain.sh` |
| Rust formatting | `cargo fmt --all -- --check` |
| Rust test suite | `cargo test --all` |

---

## Release-Readiness Rule

A WVP change is release-ready only when all required gates pass.

No single passing test suite is enough.

No single document is enough.

No single security check is enough.

Release-readiness requires the full quality gate.

---

## Fail-Closed Rule

If any required gate fails, the release state is not acceptable.

The correct response is to fix the failing gate, not to bypass the gate.

---

## Maintenance Rule

Any new required security or quality check must be added to:

1. this document,
2. `tools/check_release_quality_gate.sh`,
3. the GitHub Actions workflow.

---

## Non-Goals

This gate does not prove that WVP is externally audited.

This gate does not prove that upstream projects are safe.

This gate does not replace cryptographic review.

This gate proves only that WVP's internal release-readiness checks are complete and currently passing.

