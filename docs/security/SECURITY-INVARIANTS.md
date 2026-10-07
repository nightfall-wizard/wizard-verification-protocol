# WVP Security Invariants

## Purpose

This document defines security properties that WVP release verification must preserve.

WVP must not only accept valid release metadata. It must also reject dangerous release states that could mislead users, weaken verification, or make release integrity ambiguous.

The goal is not cleverness. The goal is deterministic, reviewable, security-preserving behavior.

---

## WVP-INV-001: No missing digest material

A release artifact MUST NOT be accepted if required digest or checksum material is missing, empty, malformed, truncated, duplicated, or ambiguous.

### Security reason

A release verifier that tolerates missing or ambiguous digest material can give users false confidence in an unverifiable artifact.

### Expected behavior

Reject.

---

## WVP-INV-002: No unsafe artifact paths

A release manifest MUST NOT accept artifact paths containing path traversal, absolute paths, unsafe platform-specific paths, hidden directory escapes, or names that could resolve outside the expected release artifact boundary.

### Invalid examples

- `../nightfall-wallet`
- `/tmp/nightfall-wallet`
- `artifacts/../../wallet`
- `C:\Users\wallet`
- `././../../release`

### Security reason

Release verification must not normalize unsafe paths into trusted targets.

### Expected behavior

Reject.

---

## WVP-INV-003: No duplicate artifact identity

A release manifest MUST NOT accept duplicate artifact names, duplicate digest entries, or conflicting metadata for the same logical artifact identity.

### Security reason

Duplicate identity can allow one artifact to be verified while another artifact is consumed.

### Expected behavior

Reject.

---

## WVP-INV-004: No unverifiable signature state

A release artifact MUST NOT be marked as verified if signature information is absent, empty, malformed, unsupported, or detached from the artifact identity.

### Security reason

A verifier must clearly separate:

- verified
- unverified
- unsupported
- failed

No unverifiable artifact may be represented as verified.

### Expected behavior

Reject or mark explicitly unverified. Never mark verified.

---

## WVP-INV-005: No network-dependent core verification result

Release verification MUST NOT require live network access to produce the core verification result for already supplied artifacts, manifests, checksums, signatures, and test vectors.

### Security reason

Verification must be reproducible and reviewable. Network-dependent verification creates nondeterministic trust.

### Expected behavior

Core verification remains offline and deterministic.

---

## WVP-INV-006: No silent downgrade

A release verification process MUST NOT silently downgrade from a stronger verification mode to a weaker one.

Examples:

- signature expected, but only checksum checked
- checksum expected, but only file presence checked
- strict manifest expected, but unknown fields silently accepted as trusted
- mainnet artifact checked with testnet assumptions

### Security reason

Silent downgrade is one of the most dangerous verifier failure modes because users believe strong verification happened when it did not.

### Expected behavior

Reject or explicitly fail closed.

---

## WVP-INV-007: No ambiguous network or chain context

A release artifact MUST NOT be accepted if its network, chain, or environment context is missing, ambiguous, inconsistent, or mismatched.

### Security reason

For blockchain software, confusing testnet, mainnet, staging, or fork-specific artifacts can cause real user loss.

### Expected behavior

Reject.

---

## Rule for future security bugs

Every security-relevant bug found in WVP MUST result in:

1. one new or clarified invariant,
2. one negative fixture,
3. one regression test,
4. one changelog entry if user-visible behavior changes.

