# Wizard Verification Protocol v0.4.0

This release adds deterministic release-check fixtures FRC-003 through FRC-007,
semantic fixture-runner coverage, release-evidence reports, a version 0.4.0
reference checker, and CI-backed conformance checks.

This release does not require independent reviewer approval. Historical
pre-release gates are retained as records but are no longer run as current
release-state gates. Security, test, and adversarial fixture checks remain.

## Evidence boundary

WVP has not been independently audited. Internal tests do not prove binary
safety, source-to-release equivalence, complete reproducibility, protocol
security, legal clearance, financial suitability, or wallet safety.

See the attached assets for build-platform and signing status. If only the
GitHub-generated source archives appear, no new compiled binary is supplied.
