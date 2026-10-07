# WVP Security Threat Model

## Purpose

This document defines the threat model for WVP release verification.

WVP exists to reduce the risk that users, maintainers, reviewers, or downstream projects trust a release artifact that is unverifiable, ambiguous, downgraded, tampered with, mislabeled, or unsafe to consume.

The threat model is intentionally conservative.

WVP assumes that release metadata, artifact names, checksums, signatures, network context, and verification claims may be malformed, incomplete, misleading, duplicated, or adversarial.

---

## Protected Assets

### ASSET-001: Release integrity

Users must be able to distinguish verified release artifacts from unverifiable or failed artifacts.

### ASSET-002: Verification determinism

The same supplied artifact metadata must produce the same core verification result without relying on live network state.

### ASSET-003: Artifact identity

Artifact name, version, digest, signature state, and network context must refer to one unambiguous release target.

### ASSET-004: User trust boundary

WVP must not represent weak, partial, missing, or failed verification as strong verification.

### ASSET-005: Reviewability

A reviewer must be able to trace security claims to invariants, fixtures, executable tests, and CI gates.

---

## Trust Boundaries

### TB-001: Repository boundary

Files inside the repository are reviewable inputs.

### TB-002: Release metadata boundary

Release metadata is untrusted until validated.

### TB-003: Artifact naming boundary

Artifact paths and names are untrusted until checked for traversal, absolute paths, and unsafe platform-specific forms.

### TB-004: Signature and digest boundary

Digest and signature material are untrusted until format, presence, uniqueness, and consistency are checked.

### TB-005: Network boundary

Live network state must not be required for the deterministic core verification result.

---

## Threat Matrix

| Threat | Asset | Attack Surface | Impact | Mitigation | Linked Invariant | Evidence |
|---|---|---|---|---|---|---|
| THREAT-001 | ASSET-001 | Missing or empty digest field | Unverifiable artifact may appear acceptable | Require digest material to be present and non-empty | WVP-INV-001 | FRC-SEC-001 |
| THREAT-002 | ASSET-003 | Path traversal or absolute artifact path | Verifier may trust or reference unsafe artifact location | Reject unsafe artifact paths | WVP-INV-002 | FRC-SEC-002 |
| THREAT-003 | ASSET-003 | Duplicate artifact identity | One artifact may be verified while another is consumed | Reject duplicate identity and conflicting metadata | WVP-INV-003 | FRC-SEC-003 |
| THREAT-004 | ASSET-004 | Claimed verified status without signature material | False trust in unverifiable artifact | Reject unverifiable signature state | WVP-INV-004 | FRC-SEC-004 |
| THREAT-005 | ASSET-002 | Live network dependency in core verification | Non-reproducible or externally influenced verification result | Keep core verification offline and deterministic | WVP-INV-005 | FRC-SEC-005 |
| THREAT-006 | ASSET-004 | Silent downgrade from strong to weak verification | User believes stronger verification happened | Fail closed on silent downgrade | WVP-INV-006 | FRC-SEC-006 |
| THREAT-007 | ASSET-003 | Ambiguous network, chain, or environment context | Testnet/mainnet confusion or wrong release context | Reject ambiguous network context | WVP-INV-007 | FRC-SEC-007 |

---

## Explicit Non-Goals

WVP does not claim to prove that an upstream project is safe.

WVP does not replace a cryptographic audit.

WVP does not guarantee that a release is free of vulnerabilities.

WVP does not depend on GitHub stars, maintainer reputation, popularity, market value, or external adoption.

WVP verifies only the evidence it is explicitly designed to verify.

---

## Fail-Closed Principle

If required verification evidence is missing, ambiguous, duplicated, downgraded, unsupported, malformed, or network-dependent, WVP must fail closed or mark the result explicitly as unverified.

It must not silently convert uncertainty into success.

---

## Review Rule

Any new verification feature must update this threat model when it changes:

1. protected assets,
2. trust boundaries,
3. attack surfaces,
4. failure modes,
5. linked invariants,
6. negative fixtures,
7. CI evidence.

---

## Maintenance Rule

A security-relevant bug fix is incomplete until the bug is mapped to:

1. one threat,
2. one invariant,
3. one negative fixture,
4. one executable test,
5. one CI gate.

