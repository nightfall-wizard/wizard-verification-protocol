# WVP Security Artifact Manifest

## Purpose

This manifest defines the security-critical files that must not drift silently.

WVP is security-sensitive release-verification tooling. Its own security documents, fixtures, checks, baselines, and release gates must be treated as controlled artifacts.

## Controlled Artifact Classes

| Class | Examples |
|---|---|
| Security policy | invariants, threat model, defensive coding policy |
| Evidence | evidence matrix, dependency inventory, baselines |
| Executable checks | shell gates under tools/ |
| CI gate | GitHub Actions release-readiness workflow |
| Negative fixtures | adversarial release-check fixtures |
| Rust executable specification | security fixture integration tests |
| Supply-chain state | Cargo.lock, dependency inventory hash |

## Rule

A security-relevant artifact change is incomplete unless the security artifact manifest is updated.

This prevents silent drift in the files that define WVP's security posture.

## Required Gate

The central release quality gate must run:

- tools/check_security_artifact_manifest.sh

## Maintenance Rule

When a controlled artifact intentionally changes:

1. run the full release quality gate,
2. regenerate security-baselines/security-artifact-manifest.sha256,
3. commit the artifact change and manifest update together.

## Non-Goals

This manifest does not prove that WVP is externally audited.

This manifest does not prove that upstream projects are safe.

This manifest does not replace cryptographic review.

It only proves that WVP's own security-critical repository artifacts are tracked against a committed hash baseline.
