# WVP Security Evidence Matrix

## Purpose

This matrix maps WVP security invariants to concrete evidence.

A security claim is only treated as meaningful when it is connected to:

1. a documented invariant,
2. a negative fixture,
3. an executable test,
4. an automated CI gate.

The purpose is to make WVP reviewable, auditable, and resistant to silent regression.

---

## Evidence Matrix

| Invariant | Risk Class | Negative Fixture | Executable Test | CI Gate | Status |
|---|---|---|---|---|---|
| WVP-INV-001 | Missing, empty, malformed, truncated, duplicated, or ambiguous digest material | `test-vectors/release-check/negative/FRC-SEC-001-missing-digest.json` | `security_negative_fixtures` | `wvp-security-invariants.yml` | Covered |
| WVP-INV-002 | Unsafe artifact paths, traversal, absolute paths, or unsafe platform paths | `test-vectors/release-check/negative/FRC-SEC-002-path-traversal.json` | `security_negative_fixtures` | `wvp-security-invariants.yml` | Covered |
| WVP-INV-003 | Duplicate artifact identity or conflicting metadata | `test-vectors/release-check/negative/FRC-SEC-003-duplicate-artifact.json` | `security_negative_fixtures` | `wvp-security-invariants.yml` | Covered |
| WVP-INV-004 | Artifact marked verified without verifiable signature state | `test-vectors/release-check/negative/FRC-SEC-004-missing-signature.json` | `security_negative_fixtures` | `wvp-security-invariants.yml` | Covered |
| WVP-INV-005 | Network-dependent core verification result | `test-vectors/release-check/negative/FRC-SEC-005-network-dependent-verification.json` | `security_negative_fixtures` | `wvp-security-invariants.yml` | Covered |
| WVP-INV-006 | Silent downgrade from stronger to weaker verification | `test-vectors/release-check/negative/FRC-SEC-006-silent-downgrade.json` | `security_negative_fixtures` | `wvp-security-invariants.yml` | Covered |
| WVP-INV-007 | Ambiguous network, chain, or environment context | `test-vectors/release-check/negative/FRC-SEC-007-ambiguous-network-context.json` | `security_negative_fixtures` | `wvp-security-invariants.yml` | Covered |

---

## Current Security Evidence

### Documented invariants

- `docs/security/SECURITY-INVARIANTS.md`

### Negative fixtures

- `test-vectors/release-check/negative/FRC-SEC-001-missing-digest.json`
- `test-vectors/release-check/negative/FRC-SEC-002-path-traversal.json`
- `test-vectors/release-check/negative/FRC-SEC-003-duplicate-artifact.json`
- `test-vectors/release-check/negative/FRC-SEC-004-missing-signature.json`
- `test-vectors/release-check/negative/FRC-SEC-005-network-dependent-verification.json`
- `test-vectors/release-check/negative/FRC-SEC-006-silent-downgrade.json`
- `test-vectors/release-check/negative/FRC-SEC-007-ambiguous-network-context.json`

### Executable tests

- `reference/rust/wvp-release-check/tests/security_negative_fixtures.rs`

### CI gates

- `tools/check_security_invariants.sh`
- `tools/check_security_evidence_matrix.sh`
- `.github/workflows/wvp-security-invariants.yml`
- `cargo test --all`

---

## Review Rule

A new security invariant is not accepted unless it has:

1. one documented invariant,
2. one negative fixture,
3. one executable test path,
4. one CI-covered check,
5. one entry in this matrix.

---

## Maintenance Rule

If a security-relevant bug is found, the fix is incomplete until this matrix is updated.

