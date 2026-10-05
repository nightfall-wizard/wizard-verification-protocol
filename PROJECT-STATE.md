# PROJECT-STATE

Updated: 2026-10-05 00:55:59 CEST

## Project

Wizard Verification Protocol — WVP

## Builder

nightfall-wizard

## Category

Proof-of-Project-Reality

## Current stage

WVP v0.3 Linux-vs-Android build evidence comparison format implemented.

## Completed

- WVP v0.1.1 release baseline is complete
- checksum verification is implemented
- release checksum verification is end-to-end proven
- OpenSSL signature tooling path is detected
- no-secret scan excludes detector scripts containing intentional sentinel patterns
- signature discovery is separated from signature verification
- JSON fields for signature verification status are implemented
- INFO now requires checksum verification and signature verification to pass
- public release verification key is committed
- private release signing key is kept outside the repository
- public key fingerprint conformance is implemented
- detached release signature asset exists for v0.1.1
- detached release signature is verified by conformance using the committed public key
- wvp-release-check internally verifies detached release signatures
- wvp-release-check reaches INFO when checksum and signature verification both pass
- release asset matching now requires exactly one .sha256 asset
- release asset matching now requires exactly one .sig asset
- negative unit tests cover missing and duplicate signature/checksum assets
- tamper-negative tests reject modified signed assets
- tamper-negative tests reject modified detached signatures
- tamper-negative tests reject wrong public verification keys
- v0.2 release-candidate documentation exists
- v0.2 release checklist exists
- v0.2 release-candidate documentation is covered by CI conformance
- wvp-release-check package version is 0.2.0
- local v0.2 release build script exists
- local release build script creates binary, checksum and detached signature without upload
- v0.2 version and build script conformance is covered by CI
- Git tag v0.2.0 exists
- GitHub release v0.2.0 exists
- v0.2.0 release includes binary, checksum and detached signature assets
- published v0.2.0 checksum verification passes
- published v0.2.0 detached signature verification passes
- wvp-release-check self-verifies v0.2.0 as INFO
- v0.2.0 post-release verification is covered by CI conformance
- v0.3 reproducible-build evidence model exists
- v0.3 build provenance script exists
- v0.3 single-environment build provenance conformance exists
- v0.3 same-environment repeat-build comparison exists
- v0.3 same-environment repeat-build conformance is covered by CI
- v0.3 independent-environment evidence separation exists
- v0.3 environment classification conformance is covered by CI
- v0.3 CI build provenance artifact generation exists
- v0.3 CI build provenance artifact upload is configured in GitHub Actions
- v0.3 build provenance artifact comparison format exists
- v0.3 Linux-vs-Android comparison wording is explicitly non-proof

## Current progress

WVP v0.1 baseline: 100 percent.

WVP v0.2 signature verification: 100 percent.

WVP v0.3 reproducible-build evidence: 50 percent after commit, push and CI verification.

## Next target

Add actual CI-artifact download and Android-vs-CI comparison command.

## Safety state

No seeds, wallet files, tokens or private signing keys are stored in this repository.

<!-- WVP:STEP-19F-ANDROID-VS-CI:START -->
## STEP 19F / 19G — Android vs CI Build Provenance Evidence

Date: 2026-10-05  
Commit: `75a777b37e23bf350057dfc8917ef9d29396a184`  
GitHub Actions Run ID: `37242108764`  
Evidence report: `docs/release/ANDROID-VS-CI-BUILD-EVIDENCE-2026-10-05.md`  
Machine-readable comparison: `target/wvp-android-vs-ci-build-provenance-comparison-75a777b/BUILD-PROVENANCE-COMPARISON.json`

### Result

`PASS`

### Verified / observed

- `verified`: Android-Termux artifact exists.
- `verified`: GitHub Actions artifact exists.
- `verified`: both artifacts contain build provenance JSON, environment classification JSON, manifest, native binary and SHA256 file.
- `verified`: both artifact-local SHA256 checks pass.
- `verified`: source commit matches.
- `verified`: package version matches.
- `verified`: Cargo.lock hash matches.
- `observed`: Android-Termux environment class differs from GitHub Actions environment class.
- `observed`: binary SHA256 differs.
- `observed`: binary size differs.
- `observed`: Rust/Cargo versions differ.

### Limits

- No reproducible-build claim.
- No source-to-release proof.
- No binary-safety proof.
- No audit claim.
- Cross-architecture native binaries are not expected to be byte-identical.

### Current interpretation

This is valid cross-environment build-provenance evidence.  
It strengthens WVP release-integrity documentation but remains below reproducible-build proof level.
<!-- WVP:STEP-19F-ANDROID-VS-CI:END -->


<!-- WVP:STEP-19H-REUSABLE-ANDROID-VS-CI-CONFORMANCE:START -->
## STEP 19H — Reusable Android vs CI Build Provenance Conformance

Status: `implemented`

Reusable local conformance command:

    ./conformance/release-check-android-vs-ci-build-provenance.sh

Purpose:

- Download the GitHub Actions build-provenance artifact for the checked-out commit.
- Generate a fresh Android-Termux build-provenance artifact locally.
- Compare both artifact sets.
- Validate that Android-Termux and GitHub Actions are treated as separate environment classes.
- Validate that source commit, package version and Cargo.lock hash match.
- Preserve the explicit non-claim that this is not a reproducible-build proof.

Required preconditions:

- clean Git source tree;
- authenticated GitHub CLI;
- successful GitHub Actions run for the checked-out commit;
- downloadable `wvp-ci-build-provenance-<commit>` artifact.

Limits:

- not an audit;
- not a binary-safety proof;
- not a source-to-release proof;
- not a reproducible-build proof;
- not intended to run as part of normal CI because it depends on an already-uploaded GitHub Actions artifact.
<!-- WVP:STEP-19H-REUSABLE-ANDROID-VS-CI-CONFORMANCE:END -->


<!-- WVP:STEP-19I-DOCS-REFERENCE:START -->
## STEP 19I — README/SPEC/LIMITATIONS Reference Android vs CI Conformance

Status: `implemented`

The reusable Android-vs-CI build-provenance conformance command is now referenced from the main documentation surface.

Progress interpretation:

- Total project: approximately 54–55%.
- WVP v0.3: approximately 65%.
- Not 100%; the remaining work still includes v0.3 release publication, stronger source-to-release documentation, broader WVP module completion and final release evidence.
<!-- WVP:STEP-19I-DOCS-REFERENCE:END -->


<!-- WVP:STEP-19J-V030-READINESS-CHECKLIST:START -->
## STEP 19J — v0.3 Release Readiness Checklist

Status: `implemented`

Release readiness document:

    docs/release/WVP-V0.3-RELEASE-READINESS-CHECKLIST.md

Conformance check:

    ./conformance/release-check-v030-readiness-checklist.sh

Purpose:

- define what remains before WVP v0.3 can be published;
- separate completed evidence from missing release requirements;
- prevent false 100% completion claims;
- preserve the explicit non-claims around audits, binary safety, source-to-release proof and reproducible builds.

Progress interpretation after successful CI:

- Total project: approximately 56–58%.
- WVP v0.3: approximately 70%.
- Not 100%.
<!-- WVP:STEP-19J-V030-READINESS-CHECKLIST:END -->


<!-- WVP:STEP-19K-V030-READINESS-CI:START -->
## STEP 19K — v0.3 Readiness Check Wired Into CI

Status: `implemented`

Workflow:

    .github/workflows/ci.yml

CI-enforced readiness check:

    ./conformance/release-check-v030-readiness-checklist.sh

CI syntax-only check for local Android-vs-CI command:

    bash -n ./conformance/release-check-android-vs-ci-build-provenance.sh

Reason:

- the v0.3 readiness checklist must be checked by CI, not only manually;
- the Android-vs-CI command depends on GitHub CLI and an already-created artifact, so CI only verifies shell syntax for that command;
- this keeps local/manual evidence separate from CI-enforced checks.

Progress interpretation after successful CI:

- Total project: approximately 58–59%.
- WVP v0.3: approximately 72%.
- Not 100%.
<!-- WVP:STEP-19K-V030-READINESS-CI:END -->


<!-- WVP:STEP-19K-RECOVER-WORKFLOW-YAML:START -->
## STEP 19K-RECOVER — Workflow YAML Recovery

Status: `implemented`

Failed run:

    37289978792

Recovered workflow:

    .github/workflows/ci.yml

Reason:

- STEP 19K correctly added the v0.3 readiness check conceptually;
- the first CI attempt failed at workflow-file level;
- the workflow block was reinserted using marker-derived indentation;
- CI must be green again before any further release work.

Progress interpretation after successful CI:

- Total project: approximately 58–59%.
- WVP v0.3: approximately 72%.
- Not 100%.
<!-- WVP:STEP-19K-RECOVER-WORKFLOW-YAML:END -->


<!-- WVP:STEP-19K-RECOVER-2-WORKFLOW-INDENT:START -->
## STEP 19K-RECOVER-2 — Workflow Step Indentation Fixed

Status: `implemented`

Reason:

- the first 19K recovery recorded state but did not modify the workflow file;
- the workflow still had malformed step indentation;
- this recovery force-rewrites the affected GitHub Actions steps with six-space step indentation and eight-space `run:` indentation;
- CI must be green before release work continues.

Progress interpretation after successful CI:

- Total project: approximately 58–59%.
- WVP v0.3: approximately 72%.
- Not 100%.
<!-- WVP:STEP-19K-RECOVER-2-WORKFLOW-INDENT:END -->

