# WVP v0.3 Release Readiness Checklist

Status: draft readiness checklist  
Scope: `wvp-release-check` release-integrity track  
Date: 2026-10-05

## Purpose

This checklist defines what must be true before WVP v0.3 can be published.

It is not a release announcement.  
It is not an audit.  
It is not a reproducible-build claim.  
It is not a source-to-release proof.

## Current Completed Evidence

- [x] v0.2.0 release exists.
- [x] release asset exists.
- [x] checksum asset exists.
- [x] signature asset exists.
- [x] public verification key is documented.
- [x] checksum verification passes.
- [x] signature verification passes.
- [x] signature tamper-negative tests pass.
- [x] signature asset matching tests pass.
- [x] no private signing material is tracked.
- [x] single-environment build provenance exists.
- [x] same-environment repeat-build evidence exists.
- [x] build environment classification exists.
- [x] CI build provenance artifact exists.
- [x] Android-vs-CI build provenance comparison exists.
- [x] reusable Android-vs-CI conformance command exists.
- [x] README/SPEC/LIMITATIONS reference the Android-vs-CI command.
- [x] CI is green on main.

## Required Before v0.3 Release

- [x] v0.3 version bump is prepared.
- [ ] v0.3 release notes are drafted.
- [ ] v0.3 release asset build command is documented.
- [ ] v0.3 checksum generation command is documented.
- [ ] v0.3 signature generation command is documented.
- [ ] v0.3 public verification command is documented.
- [ ] v0.3 release limitations are explicitly repeated.
- [ ] v0.3 tag plan is documented.
- [ ] v0.3 release artifact naming is documented.
- [ ] v0.3 post-release verification command is documented.
- [ ] v0.3 CI artifact retention limitation is documented.
- [ ] v0.3 does not claim full reproducible builds.
- [ ] v0.3 does not claim binary safety.
- [ ] v0.3 does not claim audit status.
- [ ] v0.3 does not claim source-to-release proof unless separately proven.

## Explicit Non-Claims

WVP v0.3 must not claim:

- that binaries are safe;
- that release assets were built from source;
- that cross-architecture binaries are byte-identical;
- that reproducible builds are fully proven;
- that WVP is an audit;
- that Nightfall or any third-party project has been audited.

## Release Readiness Interpretation

v0.3 can be considered release-ready only when:

1. all required pre-release documentation exists;
2. all local Rust checks pass;
3. all release-integrity conformance scripts pass;
4. GitHub Actions is green;
5. the release boundary is explicit;
6. no private signing material is tracked;
7. no stronger security claim is made than the evidence supports.

## Current State

Current status after STEP 19I:

- Total project: approximately 54–55%.
- WVP v0.3: approximately 65%.

Expected status after this checklist is committed and CI passes:

- Total project: approximately 56–58%.
- WVP v0.3: approximately 70%.

