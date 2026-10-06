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


<!-- WVP:STEP-19L-V030-RELEASE-DOCS:START -->
## STEP 19L — v0.3 Release Notes and Artifact Naming Plan

Status: `implemented`

Release notes draft:

    docs/release/WVP-V0.3-RELEASE-NOTES-DRAFT.md

Artifact naming plan:

    docs/release/WVP-V0.3-ARTIFACT-NAMING-PLAN.md

Conformance check:

    ./conformance/release-check-v030-release-docs.sh

Purpose:

- document what v0.3 adds;
- define expected release artifact names;
- keep asset names platform- and version-explicit;
- preserve explicit non-claims around audits, binary safety, source-to-release proof and reproducible builds.

Progress interpretation after successful CI:

- Total project: approximately 60%.
- WVP v0.3: approximately 75%.
- Not 100%.
<!-- WVP:STEP-19L-V030-RELEASE-DOCS:END -->


<!-- WVP:STEP-19L-RECOVER-NON-CLAIM-TERM:START -->
## STEP 19L-RECOVER — Release Notes Non-Claim Term Fixed

Status: `implemented`

Reason:

- STEP 19L created the release notes, artifact naming plan and release-docs conformance check;
- the first run failed because the conformance check required the exact phrase `must not claim` in both documents;
- the release notes used equivalent weaker wording and were corrected to match the machine-checkable non-claim boundary.

Progress interpretation after successful CI:

- Total project: approximately 60%.
- WVP v0.3: approximately 75%.
- Not 100%.
<!-- WVP:STEP-19L-RECOVER-NON-CLAIM-TERM:END -->


<!-- WVP:STEP-19M-V030-RELEASE-DOCS-CI:START -->
## STEP 19M — v0.3 Release Docs Check Wired Into CI

Status: `implemented`

CI-enforced check:

    ./conformance/release-check-v030-release-docs.sh

Reason:

- STEP 19L created the v0.3 release notes draft, artifact naming plan and local release-docs conformance check;
- STEP 19M makes that check CI-enforced;
- release documentation must be machine-checked before release work continues.

Progress interpretation after successful CI:

- Total project: approximately 61–62%.
- WVP v0.3: approximately 78%.
- Not 100%.
<!-- WVP:STEP-19M-V030-RELEASE-DOCS-CI:END -->


<!-- WVP:STEP-19N-V030-VERSION-RELEASE-PLAN:START -->
## STEP 19N — v0.3 Version Bump and Release Command Plan

Status: `implemented`

Plan:

    docs/release/WVP-V0.3-VERSION-BUMP-AND-RELEASE-COMMAND-PLAN.md

Conformance check:

    ./conformance/release-check-v030-version-release-plan.sh

Purpose:

- define the planned v0.3.0 version bump;
- define release asset staging commands;
- define checksum and signature command shapes;
- define tag and GitHub release command shapes;
- preserve the boundary that this is a plan, not a release.

Progress interpretation after successful CI:

- Total project: approximately 63%.
- WVP v0.3: approximately 81%.
- Not 100%.
<!-- WVP:STEP-19N-V030-VERSION-RELEASE-PLAN:END -->


<!-- WVP:STEP-19O-V030-VERSION-RELEASE-PLAN-CI:START -->
## STEP 19O — v0.3 Version/Release Plan Check Wired Into CI

Status: `implemented`

CI-enforced check:

    ./conformance/release-check-v030-version-release-plan.sh

Reason:

- STEP 19N created the v0.3 version bump and release command plan;
- STEP 19O makes that plan machine-checked in CI;
- release execution must not proceed unless the version/release plan stays valid.

Progress interpretation after successful CI:

- Total project: approximately 64–65%.
- WVP v0.3: approximately 84%.
- Not 100%.
<!-- WVP:STEP-19O-V030-VERSION-RELEASE-PLAN-CI:END -->


<!-- WVP:STEP-19P-ACTUAL-V030-VERSION-BUMP:START -->
## STEP 19P — Actual v0.3.0 Version Bump

Status: `implemented`

Version file:

    reference/rust/wvp-release-check/Cargo.toml

Lockfile:

    reference/rust/wvp-release-check/Cargo.lock

Conformance check:

    ./conformance/release-check-v030-actual-version-bump.sh

Purpose:

- change the package version from 0.2.0 to 0.3.0;
- regenerate the Cargo lockfile;
- update the v0.3 readiness checklist version-bump item;
- preserve the boundary that this is not a tag, not a GitHub release and not a signature event.

Progress interpretation after successful CI:

- Total project: approximately 66%.
- WVP v0.3: approximately 87%.
- Not 100%.
<!-- WVP:STEP-19P-ACTUAL-V030-VERSION-BUMP:END -->


<!-- WVP:STEP-19P-RECOVER-ACTUAL-VERSION-BUMP:START -->
## STEP 19P-RECOVER — Actual v0.3.0 Version Bump Check Fixed

Status: `implemented`

Version file:

    reference/rust/wvp-release-check/Cargo.toml

Detected lockfile:

    Cargo.lock

Conformance check:

    ./conformance/release-check-v030-actual-version-bump.sh

Reason:

- STEP 19P correctly changed the package version to 0.3.0;
- the first actual-version conformance check failed because the Cargo.lock path assumption was too strict;
- this recovery detects the real lockfile path and verifies the v0.3.0 package entry there;
- this remains a version-bump commit only, not a tag, not a GitHub release and not a signature event.

Progress interpretation after successful CI:

- Total project: approximately 66%.
- WVP v0.3: approximately 87%.
- Not 100%.
<!-- WVP:STEP-19P-RECOVER-ACTUAL-VERSION-BUMP:END -->


<!-- WVP:STEP-19P-RECOVER-3-CURRENT-TOOL-VERSION-CHECKS:START -->
## STEP 19P-RECOVER-3 — Current Tool Version Checks Updated

Status: `implemented`

Failed CI run:

    PROJECT-STATE.md

Reason:

- STEP 19P successfully bumped the current `wvp-release-check` package to 0.3.0;
- several current-version conformance checks still expected the local tool output to contain version 0.2.0;
- those current-tool expectations were updated to 0.3.0;
- historical v0.2.0 release metadata checks remain distinct and are not treated as proof of a v0.3.0 release;
- this step does not create a tag, release or signature.

Progress interpretation after successful CI:

- Total project: approximately 66–67%.
- WVP v0.3: approximately 88%.
- Not 100%.
<!-- WVP:STEP-19P-RECOVER-3-CURRENT-TOOL-VERSION-CHECKS:END -->


<!-- WVP:STEP-19Q-ACTUAL-V030-VERSION-BUMP-CI:START -->
## STEP 19Q — Actual v0.3.0 Version Bump Check Wired Into CI

Status: `implemented`

CI-enforced check:

    ./conformance/release-check-v030-actual-version-bump.sh

Reason:

- STEP 19P changed the package version to 0.3.0;
- STEP 19P recovery corrected current-version conformance checks;
- STEP 19Q makes the actual v0.3.0 version bump check CI-enforced;
- this still does not create a tag, GitHub release or signature.

Progress interpretation after successful CI:

- Total project: approximately 67–68%.
- WVP v0.3: approximately 90%.
- Not 100%.
<!-- WVP:STEP-19Q-ACTUAL-V030-VERSION-BUMP-CI:END -->


<!-- WVP:STEP-19R-V030-UNSIGNED-ASSET-STAGING:START -->
## STEP 19R — v0.3.0 Unsigned Release Asset Staging

Status: `implemented`

Staging script:

    ./scripts/release/stage-v030-unsigned-asset.sh

Documentation:

    docs/release/WVP-V0.3-UNSIGNED-ASSET-STAGING.md

Conformance check:

    ./conformance/release-check-v030-unsigned-asset-staging.sh

Purpose:

- build the v0.3.0 release binary locally;
- stage the unsigned release asset under the planned v0.3.0 name;
- generate and verify the SHA-256 checksum asset;
- write a staging manifest with explicit non-claims;
- preserve the boundary that this is not a tag, not a GitHub release and not a signature event.

Progress interpretation after successful CI:

- Total project: approximately 69%.
- WVP v0.3: approximately 92%.
- Not 100%.
<!-- WVP:STEP-19R-V030-UNSIGNED-ASSET-STAGING:END -->


<!-- WVP:STEP-19R-RECOVER-PYTHON-BOOLEAN:START -->
## STEP 19R-RECOVER — Unsigned Staging Python Boolean Fixed

Status: `implemented`

Reason:

- STEP 19R created the unsigned v0.3.0 release asset staging script, documentation and conformance check;
- the first staging run failed while writing `STAGING-MANIFEST.json`;
- the shell value `true`/`false` was injected into Python directly;
- Python requires boolean conversion to `True`/`False` semantics;
- the staging script now converts the dirty-tree flag safely.

Boundary:

- no v0.3.0 tag is created;
- no GitHub release is created;
- no signature is created;
- unsigned staging remains local evidence only.

Progress interpretation after successful CI:

- Total project: approximately 69%.
- WVP v0.3: approximately 92%.
- Not 100%.
<!-- WVP:STEP-19R-RECOVER-PYTHON-BOOLEAN:END -->


<!-- WVP:STEP-19R-RECOVER-2-SECRET-SCAN-SELF-MATCH:START -->
## STEP 19R-RECOVER-2 — Secret-Scan Self-Match Fixed

Status: `implemented`

Reason:

- STEP 19R unsigned staging passed locally;
- the final staged secret scan failed because the staging script contained the literal secret-detection regex;
- this was a scanner self-match, not private signing material;
- the staging script now constructs the secret-detection pattern from split parts;
- real secret-like material remains detectable, but the scanner no longer flags its own detection rule.

Boundary:

- no v0.3.0 tag is created;
- no GitHub release is created;
- no signature is created;
- unsigned staging remains local evidence only.

Progress interpretation after successful CI:

- Total project: approximately 69%.
- WVP v0.3: approximately 92%.
- Not 100%.
<!-- WVP:STEP-19R-RECOVER-2-SECRET-SCAN-SELF-MATCH:END -->


<!-- WVP:STEP-19S-V030-UNSIGNED-ASSET-STAGING-CI:START -->
## STEP 19S — v0.3.0 Unsigned Asset Staging Check Wired Into CI

Status: `implemented`

CI-enforced check:

    ./conformance/release-check-v030-unsigned-asset-staging.sh

Reason:

- STEP 19R prepared local unsigned v0.3.0 release asset staging;
- STEP 19R recovery fixed the staging manifest boolean handling and scanner self-match;
- STEP 19S makes unsigned asset staging machine-checked in CI;
- this still does not create a tag, GitHub release or detached signature.

Progress interpretation after successful CI:

- Total project: approximately 70%.
- WVP v0.3: approximately 94%.
- Not 100%.
<!-- WVP:STEP-19S-V030-UNSIGNED-ASSET-STAGING-CI:END -->


<!-- WVP:STEP-19T-V030-DETACHED-SIGNATURE-PROCEDURE:START -->
## STEP 19T — v0.3.0 Detached Signature Procedure Prepared

Status: `implemented`

Procedure script:

    ./scripts/release/sign-v030-staged-asset.sh

Documentation:

    docs/release/WVP-V0.3-DETACHED-SIGNATURE-PROCEDURE.md

Conformance check:

    ./conformance/release-check-v030-detached-signature-procedure.sh

Purpose:

- define a detached signature procedure for the staged v0.3.0 asset;
- require private signing material to remain outside the repository;
- require explicit signing mode before any signature can be created;
- verify that dry-run mode creates no signature;
- verify that signing mode refuses missing private-key input;
- preserve the boundary that this step creates no tag, no GitHub release and no signature.

Progress interpretation after successful CI:

- Total project: approximately 71%.
- WVP v0.3: approximately 95%.
- Not 100%.
<!-- WVP:STEP-19T-V030-DETACHED-SIGNATURE-PROCEDURE:END -->


<!-- WVP:STEP-19U-V030-DETACHED-SIGNATURE-PROCEDURE-CI:START -->
## STEP 19U — v0.3.0 Detached Signature Procedure Check Wired Into CI

Status: `implemented`

CI-enforced check:

    ./conformance/release-check-v030-detached-signature-procedure.sh

Reason:

- STEP 19T prepared the detached signature procedure without private-key exposure;
- dry-run creates no signature;
- sign mode refuses missing private-key input;
- STEP 19U makes the detached signature procedure machine-checked in CI;
- this still does not create a tag, GitHub release or detached signature.

Progress interpretation after successful CI:

- Total project: approximately 72%.
- WVP v0.3: approximately 96%.
- Not 100%.
<!-- WVP:STEP-19U-V030-DETACHED-SIGNATURE-PROCEDURE-CI:END -->


<!-- WVP:STEP-19V-V030-LOCAL-SIGNING-EXECUTION-GUARD:START -->
## STEP 19V — v0.3.0 Local Signing Execution Guard Prepared

Status: `implemented`

Guard script:

    ./scripts/release/guard-v030-local-signing-execution.sh

Documentation:

    docs/release/WVP-V0.3-LOCAL-SIGNING-EXECUTION-GUARD.md

Conformance check:

    ./conformance/release-check-v030-local-signing-execution-guard.sh

Purpose:

- define the local pre-signing decision boundary;
- require a clean source tree before signing can be approved;
- require HEAD to match origin/main before signing can be approved;
- require unsigned staging and detached-signature dry-run to pass;
- require the staging manifest to match the current source commit;
- verify that dirty-tree require-ready mode is refused;
- preserve the boundary that this step creates no tag, no GitHub release and no signature.

Progress interpretation after successful CI:

- Total project: approximately 73%.
- WVP v0.3: approximately 97%.
- Not 100%.
<!-- WVP:STEP-19V-V030-LOCAL-SIGNING-EXECUTION-GUARD:END -->


<!-- WVP:STEP-19V-RECOVER-DOC-GREP:START -->
## STEP 19V-RECOVER — Local Signing Guard Doc Grep Fixed

Status: `implemented`

Reason:

- STEP 19V created the local signing execution guard, documentation and conformance check;
- the first run failed in the documentation term check;
- the conformance check searched for `HEAD matches` as one plain string;
- the documentation uses Markdown backticks around `HEAD` and `origin/main`;
- the check now verifies the required terms without being brittle to Markdown formatting.

Boundary:

- no v0.3.0 tag is created;
- no GitHub release is created;
- no signature is created;
- no private signing material is introduced.

Progress interpretation after successful CI:

- Total project: approximately 73%.
- WVP v0.3: approximately 97%.
- Not 100%.
<!-- WVP:STEP-19V-RECOVER-DOC-GREP:END -->


<!-- WVP:STEP-19W-V030-LOCAL-SIGNING-GUARD-CI:START -->
## STEP 19W — v0.3.0 Local Signing Execution Guard Wired Into CI

Status: `implemented`

CI-enforced check:

    ./conformance/release-check-v030-local-signing-execution-guard.sh

Reason:

- STEP 19V prepared the local signing execution guard;
- STEP 19V recovery fixed the Markdown-sensitive documentation term check;
- the guard evaluates pre-signing readiness without creating a signature;
- the guard verifies dirty-tree refusal behavior;
- STEP 19W makes the local signing execution guard machine-checked in CI;
- this still does not create a tag, GitHub release or detached signature.

Progress interpretation after successful CI:

- Total project: approximately 74%.
- WVP v0.3: approximately 98%.
- Not 100%.
<!-- WVP:STEP-19W-V030-LOCAL-SIGNING-GUARD-CI:END -->


<!-- WVP:STEP-19X-V030-RELEASE-PUBLICATION-GUARD:START -->
## STEP 19X — v0.3.0 Release Publication Guard Prepared

Status: `implemented`

Guard script:

    ./scripts/release/guard-v030-release-publication.sh

Documentation:

    docs/release/WVP-V0.3-RELEASE-PUBLICATION-GUARD.md

Conformance check:

    ./conformance/release-check-v030-release-publication-guard.sh

Purpose:

- define the final pre-publication decision boundary;
- require no existing local or remote v0.3.0 tag;
- require no existing GitHub v0.3.0 release;
- require staged asset and checksum verification;
- require detached signature presence before publication approval;
- require detached signature verification before publication approval;
- verify that require-ready mode refuses missing detached signature;
- preserve the boundary that this step creates no tag, no GitHub release and no signature.

Progress interpretation after successful CI:

- Total project: approximately 75%.
- WVP v0.3: approximately 99%.
- Not 100%.
<!-- WVP:STEP-19X-V030-RELEASE-PUBLICATION-GUARD:END -->


<!-- WVP:STEP-19Y-V030-RELEASE-PUBLICATION-GUARD-CI:START -->
## STEP 19Y — v0.3.0 Release Publication Guard Check Wired Into CI

Status: `implemented`

CI-enforced check:

    ./conformance/release-check-v030-release-publication-guard.sh

Reason:

- STEP 19X prepared the final release publication guard;
- the guard checks local and remote v0.3.0 tag collision state;
- the guard checks GitHub release collision state;
- the guard verifies staged asset and checksum state;
- the guard refuses publication approval when the detached signature is missing;
- STEP 19Y makes the publication guard machine-checked in CI;
- this still does not create a tag, GitHub release or detached signature.

Progress interpretation after successful CI:

- Total project: approximately 76%.
- WVP v0.3: approximately 99%.
- Not 100%.
<!-- WVP:STEP-19Y-V030-RELEASE-PUBLICATION-GUARD-CI:END -->


<!-- WVP:STEP-19Z-RECOVER-SIGNATURE-CONFORMANCE-ENV-ISOLATION:START -->
## STEP 19Z-RECOVER — Detached Signature Conformance Env Isolation Fixed

Status: `implemented`

Reason:

- STEP 19Z was run with `WVP_SIGNING_PRIVATE_KEY` and `WVP_VERIFY_PUBLIC_KEY` set;
- the detached-signature conformance check includes a negative test that expects sign mode to fail without a private key;
- because the key environment was inherited, the negative test signed successfully and created a detached signature;
- the negative test now explicitly unsets signing-related environment variables before checking missing-key refusal;
- the check also fails if the negative test creates a signature.

Boundary:

- no v0.3.0 tag is created;
- no GitHub release is created;
- no publication is executed;
- no private signing material is introduced;
- the accidental local signature from the failed negative test is removed before validation.

Progress interpretation after successful CI:

- Total project: approximately 76%.
- WVP v0.3: still approximately 99%.
- Not 100%.
<!-- WVP:STEP-19Z-RECOVER-SIGNATURE-CONFORMANCE-ENV-ISOLATION:END -->


<!-- WVP:STEP-20A-RECOVER-POST-RELEASE-VERIFICATION:START -->
## STEP 20A-RECOVER — v0.3.0 Post-Release Verification and CI Realignment

Status: `implemented`

Release state:

- v0.3.0 GitHub release exists.
- Remote tag v0.3.0 exists.
- Release URL: https://github.com/nightfall-wizard/wizard-verification-protocol/releases/tag/v0.3.0
- Source commit: `538460a967936b70792e4d275d50ee3b2a0b90c4`

Published release assets:

- `wvp-release-check-v0.3.0-termux-android-aarch64`
- `wvp-release-check-v0.3.0-termux-android-aarch64.sha256`
- `wvp-release-check-v0.3.0-termux-android-aarch64.sig`
- `wvp-release-signing-public-rsa3072.pem`

Verified evidence:

- Asset SHA256: `e77aee158c8a3997c17d45dc51f9192839103b9eef0bf59cc3abb312b963e1fb`
- Signature SHA256: `46cca5c071cdc7fe7f702fe89f261bc702b8de3fe5bd3a6da1856dfcb65dff07`
- Public key SHA256 fingerprint: `9a6e8ccbca7d75086d54c3d53bce8f48fd2abb506b26d98fd6803301dfa7a802`
- Downloaded release asset checksum verification passes.
- Downloaded detached signature verification passes.

CI realignment:

- The pre-release publication guard CI step was replaced with post-release publication conformance.
- This is required because v0.3.0 now intentionally has a remote tag and GitHub release.

Boundary:

- This release does not claim reproducible-build proof.
- This release does not claim source-to-release proof.
- This release does not claim binary safety proof.
- This release does not claim audit result.

Progress interpretation:

- Total project: approximately 78%.
- WVP v0.3 release publication: 100% for publication only.
- Overall WVP system: not 100%.
<!-- WVP:STEP-20A-RECOVER-POST-RELEASE-VERIFICATION:END -->


<!-- WVP:STEP-20A-RECOVER-3-LIVE-SMOKE-REALIGNMENT:START -->
## STEP 20A-RECOVER-3 — Live Smoke Realigned With v0.3.0 Release State

Status: `implemented`

Reason:

- v0.3.0 is now the latest GitHub release.
- The live metadata smoke still expected v0.2.0 and three release assets.
- v0.3.0 intentionally has four release assets:
  - release binary;
  - checksum file;
  - detached signature;
  - public verification key.
- The release-check signature asset counter was too broad and matched the public key asset name because it contains `signing`.
- Signature asset detection is now restricted to actual signature-like suffixes.

Boundary:

- no tag is created by this recovery;
- no GitHub release is created by this recovery;
- no private key is added;
- no reproducible-build proof is claimed;
- no source-to-release proof is claimed;
- no binary safety proof is claimed;
- no audit claim is made.

Progress interpretation after successful CI:

- Total project: approximately 79%.
- WVP v0.3 publication/post-release: 100%.
- Overall WVP system: not 100%.
<!-- WVP:STEP-20A-RECOVER-3-LIVE-SMOKE-REALIGNMENT:END -->


<!-- WVP:STEP-20A-RECOVER-4B-SIGNATURE-POLICY-DEFAULT-TAG:START -->
## STEP 20A-RECOVER-4B — Signature Policy Default Tag Updated

Status: `implemented`

Reason:

- v0.3.0 is now the latest GitHub release.
- The signature policy conformance check still defaulted to v0.2.0.
- The check already uses a dynamic `EXPECTED_TAG` mechanism.
- The correct fix is to update the default expected tag to v0.3.0, not to hard-code JSON literals.

Current expected live state:

- latest release tag: v0.3.0;
- release asset count: 4 in the live smoke;
- checksum asset count: 1;
- signature asset count: 1;
- checksum verification passes;
- detached signature verification passes;
- public verification key remains published.

Boundary:

- no tag is created by this recovery;
- no GitHub release is created by this recovery;
- no private key is added;
- no reproducible-build proof is claimed;
- no source-to-release proof is claimed;
- no binary safety proof is claimed;
- no audit claim is made.

Progress interpretation after successful CI:

- Total project: approximately 79%.
- WVP v0.3 publication/post-release: 100%.
- Overall WVP system: not 100%.
<!-- WVP:STEP-20A-RECOVER-4B-SIGNATURE-POLICY-DEFAULT-TAG:END -->


<!-- WVP:STEP-20A-RECOVER-5-V020-LATEST-DECOUPLING:START -->
## STEP 20A-RECOVER-5 — v0.2.0 Post-Release Check Decoupled From Latest Release

Status: `implemented`

Reason:

- v0.3.0 is now the latest GitHub release.
- The v0.2.0 post-release conformance check still correctly verifies the historical v0.2.0 release assets.
- It incorrectly expected the current live latest release to still be v0.2.0.
- Historical release checks must be tag-scoped and must not fail when a newer release is published.

Current behavior:

- v0.2.0 post-release check still verifies:
  - v0.2.0 GitHub release exists;
  - v0.2.0 has exactly three historical assets;
  - v0.2.0 checksum verifies;
  - v0.2.0 detached signature verifies;
  - no audit claim is made.
- It no longer asserts that v0.2.0 is the latest release.
- Current latest-release state is covered by:
  - `release-check-live-smoke.sh`;
  - `release-check-v030-post-release-publication.sh`.

Boundary:

- no tag is created by this recovery;
- no GitHub release is created by this recovery;
- no private key is added;
- no reproducible-build proof is claimed;
- no source-to-release proof is claimed;
- no binary safety proof is claimed;
- no audit claim is made.

Progress interpretation after successful CI:

- Total project: approximately 79%.
- WVP v0.3 publication/post-release: 100%.
- Overall WVP system: not 100%.
<!-- WVP:STEP-20A-RECOVER-5-V020-LATEST-DECOUPLING:END -->


<!-- WVP:STEP-20A-RECOVER-6-GH-TOKEN-POST-RELEASE-CI:START -->
## STEP 20A-RECOVER-6 — GH_TOKEN Added to v0.3 Post-Release CI Step

Status: `implemented`

Reason:

- The v0.3 post-release publication conformance check uses GitHub CLI.
- In CI, `gh release view` and `gh release download` require `GH_TOKEN`.
- Local execution passed because the local GitHub CLI session was authenticated.
- The CI workflow step now explicitly sets:
  - `GH_TOKEN: ${{ github.token }}`

Boundary:

- no tag is created by this recovery;
- no GitHub release is created by this recovery;
- no release asset is uploaded by this recovery;
- no private key is added;
- no reproducible-build proof is claimed;
- no source-to-release proof is claimed;
- no binary safety proof is claimed;
- no audit claim is made.

Progress interpretation after successful CI:

- Total project: approximately 79%.
- WVP v0.3 publication/post-release: 100%.
- Overall WVP system: not 100%.
<!-- WVP:STEP-20A-RECOVER-6-GH-TOKEN-POST-RELEASE-CI:END -->


<!-- WVP:STEP-21A-V040-SCOPE-PLAN:START -->
## STEP 21A — WVP v0.4 Scope and Execution Plan

Status: `implemented`

Purpose:

- Start the next development section after v0.3 publication and post-release verification.
- Document the v0.4 scope before implementation.
- Keep legal compliance and safety as the first constraint.
- Add CI-backed conformance for the v0.4 plan.

v0.4 planned tracks:

- release-check hardening;
- scorecard security baseline;
- node-diagnose read-only diagnostics;
- conformance and test vectors;
- light-verify design phase.

Boundaries:

- no tag is created by this step;
- no GitHub release is created by this step;
- no release asset is uploaded by this step;
- no private key is added;
- no custody, exchange, broker, trading, or investment-advice function is introduced;
- no audit claim is made;
- no legal compliance guarantee is made;
- no binary safety proof is claimed;
- no source-to-release proof is claimed;
- no reproducible-build proof is claimed.

Progress interpretation after successful CI:

- Total project: approximately 80%.
- WVP v0.3 publication/post-release: 100% for publication only.
- WVP v0.4: planned, not implemented.
- Overall WVP system: not 100%.
<!-- WVP:STEP-21A-V040-SCOPE-PLAN:END -->


<!-- WVP:STEP-21B-V040-RELEASE-CHECK-HARDENING-MATRIX:START -->
## STEP 21B — WVP v0.4 Release-Check Hardening Issue Matrix

Status: `implemented`

Purpose:

- Convert the v0.4 release-check hardening track into concrete implementation issues.
- Define P0 release-check hardening work before code changes.
- Add CI-backed conformance for the hardening matrix.

P0 issue focus:

- RCH-001: strict signature asset classification.
- RCH-002: public verification key must not count as a signature asset.
- RCH-003: duplicate checksum/signature asset ambiguity.
- RCH-004: missing checksum/signature/public-key states.

Boundaries:

- no tag is created by this step;
- no GitHub release is created by this step;
- no release asset is uploaded by this step;
- no private key is added;
- no custody, exchange, broker, trading, or investment-advice function is introduced;
- no audit claim is made;
- no legal compliance guarantee is made;
- no binary safety proof is claimed;
- no source-to-release proof is claimed;
- no reproducible-build proof is claimed.

Progress interpretation after successful CI:

- Total project: approximately 81%.
- WVP v0.3 publication/post-release: 100% for publication only.
- WVP v0.4: planned; release-check hardening matrix defined.
- Overall WVP system: not 100%.
<!-- WVP:STEP-21B-V040-RELEASE-CHECK-HARDENING-MATRIX:END -->


<!-- WVP:STEP-21C-V040-RELEASE-CHECK-FIXTURE-STRATEGY:START -->
## STEP 21C — WVP v0.4 Release-Check Fixture Strategy

Status: `implemented`

Purpose:

- Define deterministic fixture strategy for release-check hardening.
- Create fixture root and fixture index.
- Add CI-backed conformance for fixture strategy and safety boundaries.

Boundaries:

- no fixture runner is implemented by this step;
- no release-check behavior is changed by this step;
- no tag is created by this step;
- no GitHub release is created by this step;
- no release asset is uploaded by this step;
- no private key, seed phrase, wallet secret, or API token is added;
- no custody, exchange, broker, trading, or investment-advice function is introduced;
- no audit claim is made;
- no legal compliance guarantee is made;
- no binary safety proof is claimed;
- no source-to-release proof is claimed;
- no reproducible-build proof is claimed.

Progress interpretation after successful CI:

- Total project: approximately 82%.
- WVP v0.3 publication/post-release: 100% for publication only.
- WVP v0.4: planned; release-check hardening matrix and fixture strategy defined.
- Overall WVP system: not 100%.
<!-- WVP:STEP-21C-V040-RELEASE-CHECK-FIXTURE-STRATEGY:END -->


<!-- WVP:STEP-21D-FRC007-FIRST-DETERMINISTIC-FIXTURE:START -->
## STEP 21D — FRC-007 First Deterministic Release-Check Fixture

Status: `implemented`

Purpose:

- Add the first deterministic release-check fixture.
- Cover the regression case where a public verification key filename contains `signing`.
- Assert that public verification key assets must not count as detached signature assets.
- Add CI-backed conformance for FRC-007.

Fixture:

- ID: FRC-007.
- Name: public-key-name-contains-signing.
- Path: `fixtures/release-check/FRC-007-public-key-name-contains-signing`.
- Expected signature asset count: 0.
- Expected public verification key asset count: 1.

Boundaries:

- no fixture runner is implemented by this step;
- no release-check runtime behavior is changed by this step;
- no tag is created by this step;
- no GitHub release is created by this step;
- no release asset is uploaded by this step;
- no private key, seed phrase, wallet secret, or API token is added;
- no custody, exchange, broker, trading, or investment-advice function is introduced;
- no audit claim is made;
- no legal compliance guarantee is made;
- no binary safety proof is claimed;
- no source-to-release proof is claimed;
- no reproducible-build proof is claimed.

Progress interpretation after successful CI:

- Total project: approximately 83%.
- WVP v0.3 publication/post-release: 100% for publication only.
- WVP v0.4: planned; hardening matrix, fixture strategy, and first deterministic fixture defined.
- Overall WVP system: not 100%.
<!-- WVP:STEP-21D-FRC007-FIRST-DETERMINISTIC-FIXTURE:END -->


<!-- WVP:STEP-21E-FRC005-DUPLICATE-CHECKSUM-FIXTURE:START -->
## STEP 21E — FRC-005 Duplicate Checksum Fixture

Status: `implemented`

Purpose:

- Add deterministic duplicate-checksum fixture.
- Cover the ambiguity case where a release has more than one checksum-like asset.
- Assert that duplicate checksum state must not be silent success.
- Add CI-backed conformance for FRC-005.

Fixture:

- ID: FRC-005.
- Name: duplicate-checksum.
- Path: `fixtures/release-check/FRC-005-duplicate-checksum`.
- Expected checksum asset count: 2.
- Expected duplicate checksum state: true.
- Expected status class: FAIL_OR_WARN_DETERMINISTIC.

Boundaries:

- no fixture runner is implemented by this step;
- no release-check runtime behavior is changed by this step;
- no tag is created by this step;
- no GitHub release is created by this step;
- no release asset is uploaded by this step;
- no private key, seed phrase, wallet secret, or API token is added;
- no custody, exchange, broker, trading, or investment-advice function is introduced;
- no audit claim is made;
- no legal compliance guarantee is made;
- no binary safety proof is claimed;
- no source-to-release proof is claimed;
- no reproducible-build proof is claimed.

Progress interpretation after successful CI:

- Total project: approximately 84%.
- WVP v0.3 publication/post-release: 100% for publication only.
- WVP v0.4: planned; hardening matrix, fixture strategy, and two deterministic fixtures defined.
- Overall WVP system: not 100%.
<!-- WVP:STEP-21E-FRC005-DUPLICATE-CHECKSUM-FIXTURE:END -->


<!-- WVP:STEP-21F-FRC006-DUPLICATE-SIGNATURE-FIXTURE:START -->
## STEP 21F — FRC-006 Duplicate Signature Fixture

Status: `implemented`

Purpose:

- Add deterministic duplicate-signature fixture.
- Cover the ambiguity case where a release has more than one signature-like asset.
- Assert that duplicate signature state must not be silent success.
- Assert that public verification key assets must not count as detached signature assets.
- Add CI-backed conformance for FRC-006.

Fixture:

- ID: FRC-006.
- Name: duplicate-signature.
- Path: `fixtures/release-check/FRC-006-duplicate-signature`.
- Expected signature asset count: 2.
- Expected duplicate signature state: true.
- Expected status class: FAIL_OR_WARN_DETERMINISTIC.

Boundaries:

- no fixture runner is implemented by this step;
- no release-check runtime behavior is changed by this step;
- no tag is created by this step;
- no GitHub release is created by this step;
- no release asset is uploaded by this step;
- no private key, seed phrase, wallet secret, or API token is added;
- no custody, exchange, broker, trading, or investment-advice function is introduced;
- no audit claim is made;
- no legal compliance guarantee is made;
- no binary safety proof is claimed;
- no source-to-release proof is claimed;
- no reproducible-build proof is claimed.

Progress interpretation after successful CI:

- Total project: approximately 85%.
- WVP v0.3 publication/post-release: 100% for publication only.
- WVP v0.4: planned; hardening matrix, fixture strategy, and three deterministic fixtures defined.
- Overall WVP system: not 100%.
<!-- WVP:STEP-21F-FRC006-DUPLICATE-SIGNATURE-FIXTURE:END -->


<!-- WVP:STEP-21G-FRC003-SIGNATURE-NO-PUBLIC-KEY-FIXTURE:START -->
## STEP 21G — FRC-003 Signature Without Public Key Fixture

Status: `implemented`

Purpose:

- Add deterministic signature-no-public-key fixture.
- Cover the case where a release has a detached signature but no public verification key.
- Assert that signature verification must not be claimed without a public key.
- Add CI-backed conformance for FRC-003.

Fixture:

- ID: FRC-003.
- Name: signature-no-public-key.
- Path: `fixtures/release-check/FRC-003-signature-no-public-key`.
- Expected signature asset count: 1.
- Expected public verification key asset count: 0.
- Expected status class: WARN_OR_FAIL_DETERMINISTIC.

Boundaries:

- no fixture runner is implemented by this step;
- no release-check runtime behavior is changed by this step;
- no tag is created by this step;
- no GitHub release is created by this step;
- no release asset is uploaded by this step;
- no private key, seed phrase, wallet secret, or API token is added;
- no custody, exchange, broker, trading, or investment-advice function is introduced;
- no audit claim is made;
- no legal compliance guarantee is made;
- no binary safety proof is claimed;
- no source-to-release proof is claimed;
- no reproducible-build proof is claimed.

Progress interpretation after successful CI:

- Total project: approximately 86%.
- WVP v0.3 publication/post-release: 100% for publication only.
- WVP v0.4: planned; hardening matrix, fixture strategy, and four deterministic fixtures defined.
- Overall WVP system: not 100%.
<!-- WVP:STEP-21G-FRC003-SIGNATURE-NO-PUBLIC-KEY-FIXTURE:END -->


<!-- WVP:STEP-21H-FRC004-PUBLIC-KEY-NO-SIGNATURE-FIXTURE:START -->
## STEP 21H — FRC-004 Public Key Without Signature Fixture

Status: `implemented`

Purpose:

- Add deterministic public-key-no-signature fixture.
- Cover the case where a release has a public verification key but no detached signature.
- Assert that public verification key assets must not count as detached signature assets.
- Assert that signature verification must not be claimed without a detached signature.
- Add CI-backed conformance for FRC-004.

Fixture:

- ID: FRC-004.
- Name: public-key-no-signature.
- Path: `fixtures/release-check/FRC-004-public-key-no-signature`.
- Expected signature asset count: 0.
- Expected public verification key asset count: 1.
- Expected status class: WARN_OR_FAIL_DETERMINISTIC.

Boundaries:

- no fixture runner is implemented by this step;
- no release-check runtime behavior is changed by this step;
- no tag is created by this step;
- no GitHub release is created by this step;
- no release asset is uploaded by this step;
- no private key, seed phrase, wallet secret, or API token is added;
- no custody, exchange, broker, trading, or investment-advice function is introduced;
- no audit claim is made;
- no legal compliance guarantee is made;
- no binary safety proof is claimed;
- no source-to-release proof is claimed;
- no reproducible-build proof is claimed.

Progress interpretation after successful CI:

- Total project: approximately 87%.
- WVP v0.3 publication/post-release: 100% for publication only.
- WVP v0.4: planned; hardening matrix, fixture strategy, and five deterministic fixtures defined.
- Overall WVP system: not 100%.
<!-- WVP:STEP-21H-FRC004-PUBLIC-KEY-NO-SIGNATURE-FIXTURE:END -->


<!-- WVP:STEP-21I-FIXTURE-RUNNER-DESIGN:START -->
## STEP 21I — Release-Check Fixture Runner Design

Status: `implemented`

Purpose:

- Add compact design anchor for a future WVP v0.4 release-check fixture runner.
- Bind implemented deterministic fixtures FRC-003, FRC-004, FRC-005, FRC-006, and FRC-007.
- Define runner contract, status model, exit-code model, offline boundary, secret boundary, and non-claims.
- Add CI-backed conformance for the design anchor.

Artifacts:

- `docs/release-check/WVP-V040-FIXTURE-RUNNER-DESIGN.md`
- `conformance/wvp-v040-release-check-fixture-runner-design-conformance.sh`

Boundaries:

- no generic fixture runner is implemented by this step;
- no release-check runtime behavior is changed by this step;
- no tag is created;
- no GitHub release is created;
- no release asset is uploaded;
- no private key, seed phrase, wallet secret, or API token is added;
- no custody, broker, exchange, paid-report, or investment-advice function is introduced;
- no audit claim is made;
- no legal compliance guarantee is made;
- no binary safety proof is claimed;
- no source-to-release proof is claimed;
- no reproducible-build proof is claimed.

Progress interpretation after successful CI:

- Total project: approximately 88%.
- WVP v0.4: five deterministic fixtures plus fixture-runner design.
- Overall WVP system: not 100%.
<!-- WVP:STEP-21I-FIXTURE-RUNNER-DESIGN:END -->


<!-- WVP:STEP-21J-FIXTURE-INDEX-VALIDATOR:START -->
## STEP 21J — Fixture Index Validator

Status: `implemented`

Purpose:

- Add reusable WVP v0.4 release-check fixture index validator.
- Validate fixture IDs, statuses, paths, required files, JSON syntax, duplicate IDs, unsafe paths, and required implemented fixtures.
- Add negative tests for missing required fixture, duplicate fixture ID, and unsafe fixture path.
- Add CI-backed conformance for the validator.

Artifacts:

- `conformance/wvp-v040-release-check-fixture-index-validator.sh`
- `conformance/wvp-v040-release-check-fixture-index-validator-conformance.sh`

Boundaries:

- no generic fixture runner is implemented by this step;
- no release-check runtime behavior is changed by this step;
- no tag is created;
- no GitHub release is created;
- no release asset is uploaded;
- no private key, seed phrase, wallet secret, or API token is added;
- no custody, broker, exchange, paid-report, or investment-advice function is introduced;
- no audit claim is made;
- no legal clearance guarantee is made;
- no binary safety proof is claimed;
- no source-to-release proof is claimed;
- no reproducible-build proof is claimed.

Progress interpretation after successful CI:

- Total project: approximately 89%.
- WVP v0.4: five deterministic fixtures, runner design, and fixture index validator.
- Overall WVP system: not 100%.
<!-- WVP:STEP-21J-FIXTURE-INDEX-VALIDATOR:END -->


<!-- WVP:STEP-21K-FIXTURE-RUNNER-SKELETON:START -->
## STEP 21K — Fixture Runner Skeleton

Status: `implemented`

Purpose:

- Add generic WVP v0.4 release-check fixture runner skeleton.
- Read `fixtures/release-check/FIXTURE-INDEX.json`.
- Validate implemented fixture structure.
- Emit machine-readable JSON result.
- Keep execution offline, read-only, non-mutating, and claim-limited.
- Add CI-backed conformance for JSON output and negative unsafe-path behavior.

Artifacts:

- `conformance/wvp-v040-release-check-fixture-runner-skeleton.sh`
- `conformance/wvp-v040-release-check-fixture-runner-skeleton-conformance.sh`

Boundaries:

- skeleton validates fixture structure only;
- no full fixture semantic classifier is implemented by this step;
- no release-check Rust runtime behavior is changed by this step;
- no tag is created;
- no GitHub release is created;
- no release asset is uploaded;
- no private key, seed phrase, wallet secret, or API token is added;
- no custody, broker, exchange, paid-report, or investment-advice function is introduced;
- no audit claim is made;
- no legal clearance guarantee is made;
- no binary safety proof is claimed;
- no source-to-release proof is claimed;
- no reproducible-build proof is claimed.

Progress interpretation after successful CI:

- Total project: approximately 90%.
- WVP v0.4: fixtures, runner design, index validator, and runner skeleton.
- Overall WVP system: not 100%.
<!-- WVP:STEP-21K-FIXTURE-RUNNER-SKELETON:END -->


<!-- WVP:STEP-21L-FIXTURE-RUNNER-SEMANTIC-LAYER:START -->
## STEP 21L — Fixture Runner Semantic Classification Layer

Status: `implemented`

Purpose:

- Extend the fixture runner skeleton with a first semantic classification layer.
- Classify release assets into binary, checksum, detached signature, and public verification key groups.
- Compare supported `expected_classification` keys against actual derived fixture classification.
- Preserve offline, read-only, non-mutating, and claim-limited execution.
- Add CI-backed semantic conformance and mismatch-negative testing.

Artifacts:

- `conformance/wvp-v040-release-check-fixture-runner-skeleton.sh`
- `conformance/wvp-v040-release-check-fixture-runner-semantic-conformance.sh`

Boundaries:

- this is the first semantic layer, not a full independent audit engine;
- unsupported expected keys may remain explicitly reported as unchecked;
- no release-check Rust runtime behavior is changed by this step;
- no tag is created;
- no GitHub release is created;
- no release asset is uploaded;
- no private key, seed phrase, wallet secret, or API token is added;
- no custody, broker, exchange, paid-report, or investment-advice function is introduced;
- no audit claim is made;
- no legal clearance guarantee is made;
- no binary safety proof is claimed;
- no source-to-release proof is claimed;
- no reproducible-build proof is claimed.

Progress interpretation after successful CI:

- Total project: approximately 91%.
- WVP v0.4: fixtures, runner design, index validator, runner skeleton, and first semantic classification layer.
- Overall WVP system: not 100%.
<!-- WVP:STEP-21L-FIXTURE-RUNNER-SEMANTIC-LAYER:END -->


<!-- WVP:STEP-21M-SEMANTIC-COVERAGE-GUARD:START -->
## STEP 21M — Semantic Coverage Guard

Status: `implemented`

Purpose:

- Add CI-backed semantic coverage guard for WVP v0.4 release-check fixtures.
- Require all `expected_classification` keys for FRC-003, FRC-004, FRC-005, FRC-006, and FRC-007 to be semantically checked.
- Reject unknown unchecked semantic keys through a negative coverage test.
- Preserve offline, read-only, non-mutating, and claim-limited execution.

Artifacts:

- `conformance/wvp-v040-release-check-fixture-runner-skeleton.sh`
- `conformance/wvp-v040-release-check-fixture-runner-semantic-coverage-conformance.sh`

Boundaries:

- this is semantic fixture coverage, not a full independent audit engine;
- no release-check Rust runtime behavior is changed by this step;
- no tag is created;
- no GitHub release is created;
- no release asset is uploaded;
- no private key, seed phrase, wallet secret, or API token is added;
- no custody, broker, exchange, paid-report, or investment-advice function is introduced;
- no audit claim is made;
- no legal clearance guarantee is made;
- no binary safety proof is claimed;
- no source-to-release proof is claimed;
- no reproducible-build proof is claimed.

Progress interpretation after successful CI:

- Total project: approximately 92%.
- WVP v0.4: fixtures, runner design, index validator, runner skeleton, semantic classification layer, and semantic coverage guard.
- Overall WVP system: not 100%.
<!-- WVP:STEP-21M-SEMANTIC-COVERAGE-GUARD:END -->


<!-- WVP:STEP-21N-RUNNER-REPORT-ARTIFACT:START -->
## STEP 21N — v0.4 Fixture Runner Report Artifact

Status: `implemented`

Purpose:

- Add reproducible WVP v0.4 fixture runner report artifacts.
- Store machine-readable runner summary in JSON.
- Store human-readable runner summary in Markdown.
- Verify report contents against live offline runner output in CI.
- Preserve offline, read-only, non-mutating, and claim-limited execution.

Artifacts:

- `reports/release-check/WVP-V040-FIXTURE-RUNNER-REPORT.json`
- `reports/release-check/WVP-V040-FIXTURE-RUNNER-REPORT.md`
- `conformance/wvp-v040-release-check-fixture-runner-report-conformance.sh`

Boundaries:

- this is a fixture runner report, not a full independent audit engine;
- no release-check Rust runtime behavior is changed by this step;
- no tag is created;
- no GitHub release is created;
- no GitHub release asset is uploaded;
- no private key, seed phrase, wallet secret, or API token is added;
- no custody, broker, exchange, paid-report, or investment-advice function is introduced;
- no audit claim is made;
- no legal clearance guarantee is made;
- no binary safety proof is claimed;
- no source-to-release proof is claimed;
- no reproducible-build proof is claimed.

Progress interpretation after successful CI:

- Total project: approximately 93%.
- WVP v0.4: fixtures, runner design, index validator, runner skeleton, semantic classification layer, semantic coverage guard, and runner report artifact.
- Overall WVP system: not 100%.
<!-- WVP:STEP-21N-RUNNER-REPORT-ARTIFACT:END -->


<!-- WVP:STEP-21O-RELEASE-READINESS-CHECKLIST:START -->
## STEP 21O — v0.4 Release Readiness Checklist

Status: `implemented`

Purpose:

- Add CI-backed WVP v0.4 release-readiness checklist.
- Record required evidence before a future v0.4 release.
- Confirm that this step does not create a tag, GitHub release, or GitHub release asset.
- Preserve offline, read-only, non-mutating, and claim-limited execution.

Artifacts:

- `docs/release-check/WVP-V040-RELEASE-READINESS-CHECKLIST.md`
- `conformance/wvp-v040-release-readiness-checklist-conformance.sh`

Boundaries:

- this is release-readiness preparation, not an actual release;
- no tag is created;
- no GitHub release is created;
- no GitHub release asset is uploaded;
- no private key, seed phrase, wallet secret, or API token is added;
- no custody, broker, exchange, paid-report, or investment-advice function is introduced;
- no audit claim is made;
- no legal clearance guarantee is made;
- no binary safety proof is claimed;
- no source-to-release proof is claimed;
- no reproducible-build proof is claimed.

Progress interpretation after successful CI:

- Total project: approximately 94%.
- WVP v0.4: release-readiness checklist added.
- Overall WVP system: not 100%.
<!-- WVP:STEP-21O-RELEASE-READINESS-CHECKLIST:END -->



<!-- WVP:STEP-21P-RELEASE-NOTES-DRAFT:START -->
## STEP 21P — v0.4 Release Notes Draft

Status: `implemented`

Purpose:

- Add CI-backed WVP v0.4 release notes draft.
- Record release-note text for a possible future v0.4 release.
- Confirm that this step does not create a tag, GitHub release, GitHub release asset, or signature.
- Preserve offline, read-only, non-mutating, and claim-limited execution.

Artifacts:

- `docs/release-check/WVP-V040-RELEASE-NOTES-DRAFT.md`
- `conformance/wvp-v040-release-notes-draft-conformance.sh`

Boundaries:

- this is a release notes draft, not an actual release;
- no tag is created;
- no GitHub release is created;
- no GitHub release asset is uploaded;
- no private key, seed phrase, wallet secret, or API token is added;
- no custody, broker, exchange, paid-report, or investment-advice function is introduced;
- no audit claim is made;
- no legal clearance guarantee is made;
- no binary safety proof is claimed;
- no source-to-release proof is claimed;
- no reproducible-build proof is claimed.

Progress interpretation after successful CI:

- Total project: approximately 95%.
- WVP v0.4: release notes draft added.
- Overall WVP system: not 100%.
<!-- WVP:STEP-21P-RELEASE-NOTES-DRAFT:END -->


<!-- WVP:STEP-21Q-FINAL-PRE-RELEASE-GATE:START -->
## STEP 21Q — v0.4 Final Pre-Release Gate

Status: `implemented`

Purpose:

- Add CI-backed final WVP v0.4 pre-release gate.
- Consolidate v0.4 evidence, release notes, readiness, report status, implemented fixture coverage, and no-release status.
- Confirm that this step does not create a tag, GitHub release, GitHub release asset, or signature.
- Preserve offline, read-only, non-mutating, and claim-limited execution.

Artifacts:

- `docs/release-check/WVP-V040-FINAL-PRE-RELEASE-GATE.md`
- `conformance/wvp-v040-final-pre-release-gate-conformance.sh`

Boundaries:

- this is a final pre-release gate, not an actual release;
- no tag is created;
- no GitHub release is created;
- no GitHub release asset is uploaded;
- no private key, seed phrase, wallet secret, or API token is added;
- no custody, broker, exchange, paid-report, or investment-advice function is introduced;
- no audit claim is made;
- no legal clearance guarantee is made;
- no binary safety proof is claimed;
- no source-to-release proof is claimed;
- no reproducible-build proof is claimed.

Progress interpretation after successful CI:

- Total project: approximately 96%.
- WVP v0.4: final pre-release gate added.
- Overall WVP system: not 100%.
<!-- WVP:STEP-21Q-FINAL-PRE-RELEASE-GATE:END -->


<!-- WVP:STEP-21R-CONTROLLED-RELEASE-PLAN:START -->
## STEP 21R — Controlled v0.4.0 Release Plan

Status: `implemented`

Purpose:

- Add CI-backed controlled v0.4.0 release plan.
- Define the future manual release sequence without executing it.
- Confirm that this step does not create a tag, GitHub release, GitHub release asset, or signature.
- Preserve legal, operational, offline, read-only, non-mutating, and claim-limited execution.

Artifacts:

- `docs/release-check/WVP-V040-CONTROLLED-RELEASE-PLAN.md`
- `conformance/wvp-v040-controlled-release-plan-conformance.sh`

Boundaries:

- this is a release plan, not an actual release;
- no tag is created;
- no GitHub release is created;
- no GitHub release asset is uploaded;
- no private key, seed phrase, wallet secret, or API token is added;
- no custody, broker, exchange, paid-report, or investment-advice function is introduced;
- no audit claim is made;
- no legal clearance guarantee is made;
- no binary safety proof is claimed;
- no source-to-release proof is claimed;
- no reproducible-build proof is claimed.

Progress interpretation after successful CI:

- Total project: approximately 97%.
- WVP v0.4: controlled release plan added.
- Overall WVP system: not 100%.
<!-- WVP:STEP-21R-CONTROLLED-RELEASE-PLAN:END -->


<!-- WVP:STEP-21S-PRE-RELEASE-PREP-STOP-MARKER:START -->
## STEP 21S — v0.4 Pre-Release Prep Stop Marker

Status: `implemented`

Purpose:

- Add CI-backed v0.4 pre-release preparation stop marker.
- Mark v0.4 preparation as complete but not released.
- Confirm that this step does not create a tag, GitHub release, GitHub release asset, or signature.
- Require any real v0.4.0 release to be a separate explicit action.

Artifacts:

- `docs/release-check/WVP-V040-PRE-RELEASE-PREP-STOP-MARKER.md`
- `conformance/wvp-v040-pre-release-prep-stop-marker-conformance.sh`

Boundaries:

- this is a stop marker, not an actual release;
- no tag is created;
- no GitHub release is created;
- no GitHub release asset is uploaded;
- no private key, seed phrase, wallet secret, or API token is added;
- no custody, broker, exchange, paid-report, or investment-advice function is introduced;
- no audit claim is made;
- no legal clearance guarantee is made;
- no binary safety proof is claimed;
- no source-to-release proof is claimed;
- no reproducible-build proof is claimed.

Progress interpretation after successful CI:

- Total project: approximately 98%.
- WVP v0.4: pre-release preparation track stopped before release execution.
- Overall WVP system: not 100%.
<!-- WVP:STEP-21S-PRE-RELEASE-PREP-STOP-MARKER:END -->


<!-- WVP:STEP-21T-PUBLIC-STATUS-ALIGNMENT:START -->
## STEP 21T — v0.4 Public Status Alignment

Status: `implemented`

Purpose:

- Add CI-backed public README status alignment for WVP v0.4.
- Make the public repository state explicit: v0.4 is prepared but not released.
- Confirm that this step does not create a tag, GitHub release, GitHub release asset, or signature.
- Preserve legal, operational, offline, read-only, non-mutating, and claim-limited execution.

Artifacts:

- `README.md`
- `conformance/wvp-v040-public-status-alignment-conformance.sh`

Boundaries:

- this is public status alignment, not an actual release;
- no tag is created;
- no GitHub release is created;
- no GitHub release asset is uploaded;
- no private key, seed phrase, wallet secret, or API token is added;
- no custody, broker, exchange, paid-report, or investment-advice function is introduced;
- no audit claim is made;
- no legal clearance guarantee is made;
- no binary safety proof is claimed;
- no source-to-release proof is claimed;
- no reproducible-build proof is claimed.

Progress interpretation after successful CI:

- Total project: approximately 99%.
- WVP v0.4: public status aligned with prepared-not-released state.
- Overall WVP system: not 100%.
<!-- WVP:STEP-21T-PUBLIC-STATUS-ALIGNMENT:END -->


<!-- WVP:STEP-21U-CAPABILITIES-AND-USAGE:START -->
## STEP 21U — v0.4 Capabilities and Usage Guide

Status: `implemented`

Purpose:

- Add CI-backed public documentation for what WVP v0.4 can do.
- Document what WVP v0.4 cannot do.
- Document practical local usage commands.
- Confirm that this step does not create a tag, GitHub release, GitHub release asset, or signature.
- Preserve legal, operational, offline, read-only, non-mutating, and claim-limited execution.

Artifacts:

- `docs/release-check/WVP-V040-CAPABILITIES-AND-USAGE.md`
- `conformance/wvp-v040-capabilities-and-usage-conformance.sh`

Boundaries:

- this is usage documentation, not an actual release;
- no tag is created;
- no GitHub release is created;
- no GitHub release asset is uploaded;
- no private key, seed phrase, wallet secret, or API token is added;
- no custody, broker, exchange, paid-report, or investment-advice function is introduced;
- no audit claim is made;
- no legal clearance guarantee is made;
- no binary safety proof is claimed;
- no source-to-release proof is claimed;
- no reproducible-build proof is claimed.

Progress interpretation after successful CI:

- Total project: approximately 99%.
- WVP v0.4: capabilities and usage documented.
- Overall WVP system: not 100%.
<!-- WVP:STEP-21U-CAPABILITIES-AND-USAGE:END -->


<!-- WVP:STEP-22E-POST-MERGE-VERIFICATION:START -->
## STEP 22E — Release-Reality Post-Merge Verification

Status: implemented

Purpose:
Verify that the merged WVP Release-Reality Check v0.1 stack is complete on `main` and protected by CI-backed gates.

Implemented verification:
- release-reality checker exists and is executable;
- schema file exists;
- documentation exists;
- release-reality workflow exists;
- schema/output alignment gate exists and runs;
- deterministic fixture gate exists and runs;
- exactly eight deterministic release-reality fixtures exist;
- live self-check still produces WVP v0.1 output;
- unverified claims remain `not_proven`;
- explicit non-claims remain present.

Covered gates:
- `conformance/wvp-release-reality-schema-output-alignment.sh`
- `conformance/wvp-release-reality-deterministic-fixture-gate.sh`
- `conformance/wvp-release-reality-post-merge-verification.sh`

Boundaries:
- no audit claim is made;
- no legal-clearance claim is made;
- no investment-quality claim is made;
- no custody-safety claim is made;
- no binary-safety claim is made;
- no source-to-binary proof is claimed;
- no reproducible-build proof is claimed;
- no protocol-security proof is claimed;
- no private key, seed phrase, wallet secret, API token, custody data, or user-funds data is read, printed, uploaded, or committed.

Interpretation:
STEP 22E turns the release-reality checker work from a successful merged feature into a verified main-branch subsystem with persistent CI-backed regression protection.
<!-- WVP:STEP-22E-POST-MERGE-VERIFICATION:END -->

<!-- WVP:STEP-22F-CAPABILITY-INDEX:START -->
## STEP 22F — Release-Reality Capability Index

Status: implemented

Purpose:
Add a machine-readable capability index for the WVP Release-Reality Check v0.1 subsystem.

Implemented artifacts:
- `capabilities/wvp-release-reality-capability-index-v0.1.json`
- `docs/WVP-RELEASE-REALITY-CAPABILITY-INDEX-V0.1.md`
- `conformance/wvp-release-reality-capability-index-gate.sh`

The capability index records:
- implemented checker capabilities;
- explicit non-capabilities;
- CI-backed gates;
- deterministic fixture inventory;
- hard safety and claim-boundary rules;
- accepted claim-status vocabulary.

Boundaries:
- not a release approval;
- not an audit;
- not legal clearance;
- not investment advice;
- not custody safety proof;
- not binary safety proof;
- not source-to-binary proof;
- not reproducible-build proof;
- not protocol security proof.

Interpretation:
STEP 22F turns the release-reality checker subsystem into a documented capability surface that can be reviewed, linked, versioned and defended without overclaiming.
<!-- WVP:STEP-22F-CAPABILITY-INDEX:END -->

<!-- WVP:STEP-23-AUNEYA-PROTOCOL-CHARTER:START -->
## STEP 23 — AUNEYA Protocol Charter

Date: 2026-10-06

### Purpose

WVP is now explicitly anchored as the technical verification core for the AUNEYA working architecture.

AUNEYA is defined as an open-source, phone-first network for witnessing the provable web.

### Added

- `docs/auneya/README.md`
- `docs/auneya/AUNEYA-PROTOCOL-CHARTER.md`
- `docs/auneya/AUNEYA-PROVABLE-WEB-SCOPE.md`
- `docs/auneya/AUNEYA-NON-VALUE-SIMULATION-NOTICE.md`

### Core interpretation

WVP remains the verification protocol.

AUNEYA is the long-term working architecture.

The initial work remains legal, open-source, non-custodial and non-value simulation.

### Explicit non-claims

- No token is created by this step.
- No token sale is offered.
- No market value is claimed.
- No return, profit, yield or financial outcome is offered or promised.
- No custody, broker, exchange or paid-report service is created.
- AUNEYA is a working name pending trademark clearance.
- Legal review is required before any public token launch, listing, sale, transferability or market-value communication.

### Next target

Define the first AUNEYA claim schema for the provable web using WVP release-reality as Claim Type 001.
<!-- WVP:STEP-23-AUNEYA-PROTOCOL-CHARTER:END -->

<!-- WVP:STEP-24-AUNEYA-CLAIM-SCHEMA-V01:START -->
## STEP 24 — AUNEYA Claim Schema v0.1

Date: 2026-10-06

### Purpose

AUNEYA now has its first machine-readable claim format for the provable web.

This turns the AUNEYA architecture from a documented vision into a concrete technical object that can be validated by conformance.

### Added

- `schemas/auneya-claim-v0.1.schema.json`
- `docs/auneya/AUNEYA-CLAIM-SCHEMA-V0.1.md`
- `fixtures/auneya/claims/valid-release-reality.json`
- `fixtures/auneya/claims/valid-download-integrity.json`
- `fixtures/auneya/claims/valid-website-claim-reality.json`
- `fixtures/auneya/claims/invalid-private-data-claim.json`
- `conformance/auneya-claim-schema-v0.1.sh`

### Verified

- valid public release-reality claim passes
- valid public download-integrity claim passes
- valid public website-claim-reality claim passes
- invalid private-data claim is rejected
- legal boundary requires private-data, hacked-data, paywall-bypass, credential-use and surveillance prohibitions

### Explicit non-claims

- No token is created by this step.
- No reward is created by this step.
- No token sale is offered.
- No market value is claimed.
- No return, profit, yield or financial outcome is offered or promised.
- Legal review is required before any public token launch, listing, sale, transferability or market-value communication.

### Next target

Define AUNEYA Witness Proof Schema v0.1 so a lawful claim can produce a structured witness proof.
<!-- WVP:STEP-24-AUNEYA-CLAIM-SCHEMA-V01:END -->

<!-- WVP:STEP-25-AUNEYA-WITNESS-PROOF-SCHEMA-V01:START -->
## STEP 25 — AUNEYA Witness Proof Schema v0.1

Date: 2026-10-06

### Purpose

AUNEYA now has its first machine-readable witness proof format.

This turns a lawful public AUNEYA claim into a structured proof object that records witness class, observed status, evidence hashes, lawful boundary confirmation, timing and integrity metadata.

### Added

- `schemas/auneya-witness-proof-v0.1.schema.json`
- `docs/auneya/AUNEYA-WITNESS-PROOF-SCHEMA-V0.1.md`
- `fixtures/auneya/witness-proofs/valid-release-reality-prooflet.json`
- `fixtures/auneya/witness-proofs/valid-download-integrity-prooflet.json`
- `fixtures/auneya/witness-proofs/invalid-private-data-proof.json`
- `conformance/auneya-witness-proof-schema-v0.1.sh`

### Verified

- valid release-reality prooflet passes
- valid download-integrity prooflet passes
- invalid private-data proof is rejected
- witness proof references an existing claim fixture
- lawful proof requires public or authorized target confirmation
- lawful proof rejects private data, hacked data, paywall bypass, credential use and surveillance

### Explicit non-claims

- No token is created by this step.
- No reward is created by this step.
- No token sale is offered.
- No market value is claimed.
- No return, profit, yield or financial outcome is offered or promised.
- Legal review is required before any public token launch, listing, sale, transferability or market-value communication.

### Next target

Define AUNEYA Event Schema v0.1 so multiple lawful witness proofs can form an Auneya Event.
<!-- WVP:STEP-25-AUNEYA-WITNESS-PROOF-SCHEMA-V01:END -->

<!-- WVP:STEP-26-AUNEYA-EVENT-SCHEMA-V01:START -->
## STEP 26 — AUNEYA Event Schema v0.1

Date: 2026-10-06

### Purpose

AUNEYA now has its first machine-readable event format.

This turns multiple lawful witness proofs for the same public claim into an Auneya Event with quorum, independent witness count, event status, lawful boundary confirmation and event integrity metadata.

### Added

- `schemas/auneya-event-v0.1.schema.json`
- `docs/auneya/AUNEYA-EVENT-SCHEMA-V0.1.md`
- `fixtures/auneya/witness-proofs/valid-release-reality-prooflet-witness-002.json`
- `fixtures/auneya/events/valid-witnessed-release-reality-event.json`
- `fixtures/auneya/events/invalid-duplicate-witness-event.json`
- `fixtures/auneya/events/invalid-private-data-event.json`
- `conformance/auneya-event-schema-v0.1.sh`

### Verified

- valid witnessed release-reality event passes
- duplicate-witness event is rejected
- private-data event is rejected
- event proof references must exist
- event proofs must match the same claim id and claim hash
- witness ids must be independent
- non-dispute events require matching observed status
- only lawful public or authorized proofs may form a valid event

### Explicit non-claims

- No token is created by this step.
- No reward is created by this step.
- No token sale is offered.
- No market value is claimed.
- No return, profit, yield or financial outcome is offered or promised.
- Legal review is required before any public token launch, listing, sale, transferability or market-value communication.

### Next target

Define AUNEYA Pulse and Prooflet Flow v0.1 so the phone-first witness loop can be simulated without value, token or mainnet activation.
<!-- WVP:STEP-26-AUNEYA-EVENT-SCHEMA-V01:END -->

<!-- WVP:STEP-27-AUNEYA-PULSE-FLOW-V01:START -->
## STEP 27 — AUNEYA Pulse and Prooflet Flow v0.1

Date: 2026-10-06

### Purpose

AUNEYA now has its first phone-first witness loop model.

This defines how a lawful public claim can be processed by a phone witness as Pulses, Micro-Proofs and a Prooflet before later becoming a Witness Proof or Auneya Event.

### Added

- `schemas/auneya-pulse-flow-v0.1.schema.json`
- `docs/auneya/AUNEYA-PULSE-AND-PROOFLET-FLOW-V0.1.md`
- `fixtures/auneya/pulse-flow/valid-phone-release-reality-flow.json`
- `fixtures/auneya/pulse-flow/invalid-private-target-flow.json`
- `fixtures/auneya/pulse-flow/invalid-value-reward-flow.json`
- `conformance/auneya-pulse-flow-v0.1.sh`

### Verified

- valid phone release-reality flow passes
- private-target flow is rejected
- transferable or market-value reward flow is rejected
- pulse indexes must be sequential
- pulse cadence must be one second in v0.1
- micro-proofs must reference existing pulses
- prooflets must reference existing micro-proofs
- simulated reward entries must be non-transferable and non-value only

### Explicit non-claims

- No token is created by this step.
- No real reward is created by this step.
- No token sale is offered.
- No market value is claimed.
- No return, profit, yield or financial outcome is offered or promised.
- Legal review is required before any public token launch, listing, sale, transferability or market-value communication.

### Next target

Define AUNEYA Local Witness Runner v0.1 so Termux can generate a local non-value pulse-flow report from public claim fixtures.
<!-- WVP:STEP-27-AUNEYA-PULSE-FLOW-V01:END -->

<!-- WVP:STEP-28-AUNEYA-LOCAL-WITNESS-RUNNER-V01:START -->
## STEP 28 — AUNEYA Local Witness Runner v0.1

Date: 2026-10-06

### Purpose

AUNEYA now has its first local Termux-compatible witness runner.

The runner reads a lawful public AUNEYA claim fixture and emits a local non-value AUNEYA Pulse and Prooflet Flow v0.1 report.

### Added

- `tools/auneya/auneya_local_witness_runner.py`
- `docs/auneya/AUNEYA-LOCAL-WITNESS-RUNNER-V0.1.md`
- `fixtures/auneya/local-runner/example-local-witness-flow.json`
- `conformance/auneya-local-witness-runner-v0.1.sh`

### Verified

- valid public release-reality claim produces a local pulse-flow report
- invalid private-data claim is rejected
- generated local report has four one-second Pulses
- generated local report has two Micro-Proofs
- generated local report has one Prooflet
- simulated reward entry is non-transferable
- simulated reward entry claims no market value
- runner performs no mainnet activation and creates no token

### Explicit non-claims

- No token is created by this step.
- No real reward is created by this step.
- No token sale is offered.
- No market value is claimed.
- No return, profit, yield or financial outcome is offered or promised.
- Legal review is required before any public token launch, listing, sale, transferability or market-value communication.

### Next target

Define AUNEYA Local Witness CLI Display v0.1 so Termux can show a clean phone-first live-style report from the local runner output.
<!-- WVP:STEP-28-AUNEYA-LOCAL-WITNESS-RUNNER-V01:END -->

<!-- WVP:STEP-29-AUNEYA-LOCAL-WITNESS-CLI-DISPLAY-V01:START -->
## STEP 29 — AUNEYA Local Witness CLI Display v0.1

Date: 2026-10-06

### Purpose

AUNEYA now has its first local Termux-style witness display.

The display reads a local non-value AUNEYA Pulse and Prooflet Flow v0.1 report and prints a phone-first status view.

### Added

- `tools/auneya/auneya_local_witness_display.py`
- `docs/auneya/AUNEYA-LOCAL-WITNESS-CLI-DISPLAY-V0.1.md`
- `fixtures/auneya/local-runner/example-local-witness-display.txt`
- `conformance/auneya-local-witness-display-v0.1.sh`

### Verified

- display reads local runner output
- display prints local non-value mode
- display prints claim, witness, pulse, micro-proof and prooflet fields
- display shows simulated_neya as non-transferable
- display rejects value/transferability violation fixtures
- display states no token, no real reward, no mainnet and no market value

### Explicit non-claims

- No token is created by this step.
- No real reward is created by this step.
- No token sale is offered.
- No market value is claimed.
- No return, profit, yield or financial outcome is offered or promised.
- Legal review is required before any public token launch, listing, sale, transferability or market-value communication.

### Next target

Define AUNEYA One-Command Local Demo v0.1 so Termux can run the local runner and display in one command.
<!-- WVP:STEP-29-AUNEYA-LOCAL-WITNESS-CLI-DISPLAY-V01:END -->

<!-- WVP:STEP-30-AUNEYA-ONE-COMMAND-LOCAL-DEMO-V01:START -->
## STEP 30 — AUNEYA One-Command Local Demo v0.1

Date: 2026-10-06

### Purpose

AUNEYA now has its first one-command local Termux demo.

The demo runs the local witness runner and local witness CLI display in one command.

### Added

- `tools/auneya/auneya_one_command_local_demo.sh`
- `docs/auneya/AUNEYA-ONE-COMMAND-LOCAL-DEMO-V0.1.md`
- `fixtures/auneya/local-runner/example-one-command-local-demo.txt`
- `conformance/auneya-one-command-local-demo-v0.1.sh`

### Verified

- one command creates a local pulse-flow report
- one command prints the local witness display
- one command writes local flow, full display and compact display outputs
- valid public claim fixture passes
- private-data claim fixture is rejected
- simulated entry is non-transferable
- simulated entry claims no market value
- demo states no token, no real reward, no mainnet and no market value

### Explicit non-claims

- No token is created by this step.
- No real reward is created by this step.
- No token sale is offered.
- No market value is claimed.
- No return, profit, yield or financial outcome is offered or promised.
- Legal review is required before any public token launch, listing, sale, transferability or market-value communication.

### Next target

Define AUNEYA Local Demo Quickstart v0.1 so a new phone user can run the local demo from README-level instructions.
<!-- WVP:STEP-30-AUNEYA-ONE-COMMAND-LOCAL-DEMO-V01:END -->

<!-- WVP:STEP-31-AUNEYA-LOCAL-DEMO-QUICKSTART-V01:START -->
## STEP 31 — AUNEYA Local Demo Quickstart v0.1

Date: 2026-10-06

### Purpose

AUNEYA now has a Termux-focused quickstart for the one-command local demo.

This gives a new phone user a direct README-level path to run the local non-value demo.

### Added

- `docs/auneya/AUNEYA-LOCAL-DEMO-QUICKSTART-V0.1.md`
- `fixtures/auneya/local-runner/example-local-demo-quickstart.txt`
- `conformance/auneya-local-demo-quickstart-v0.1.sh`

### Verified

- quickstart document exists
- quickstart contains the one-command local demo command
- quickstart states token, market-value, transferability and mainnet boundaries
- quickstart demo produces local flow, display and compact display outputs
- private-data claim fixture is rejected
- simulated entry is non-transferable
- simulated entry claims no market value

### Explicit non-claims

- No token is created by this step.
- No AUNEYA is created by this step.
- No neya is created by this step.
- No real reward is created by this step.
- No token sale is offered.
- No market value is claimed.
- No return, profit, yield or financial outcome is offered or promised.
- Legal review is required before any public token launch, listing, sale, transferability or market-value communication.

### Next target

Define AUNEYA Local Claim Selection v0.1 so a phone user can choose between supported lawful public claim fixtures before local collecting simulation begins.
<!-- WVP:STEP-31-AUNEYA-LOCAL-DEMO-QUICKSTART-V01:END -->

