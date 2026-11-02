# Project State

## Current milestone

WVP-SEC-001 - Nightfall Verification Pack

## Status

Scaffold implemented.

## Completed

- security model
- verification profiles
- Nightfall report pack
- traceability matrix
- limitation register
- negative fixtures
- local verifier
- unit test
- GitHub Actions workflow

## Not complete yet

- real code-level binding into Nightfall internals
- real generated test vectors from Nightfall code
- fuzzing corpus
- independent cryptographic review
- reproducible binary verification
- signed release verification
- long-term maintenance evidence

## Next milestone

WVP-SEC-002 - bind fixtures to executable tests.


## WVP-SEC-002

Status: implemented.

Completed:

- codepath binding report
- JSON binding evidence
- markdown binding evidence
- binding method documentation
- binding checker
- unit tests

Boundary:

This step binds fixtures to observable paths. It does not prove implementation correctness.

Next milestone:

WVP-SEC-003 - convert selected bindings into executable semantic regression checks.


## WVP-SEC-003

Status: implemented.

Completed:

- semantic regression report
- executable semantic regression checker
- semantic regression method documentation
- JSON evidence artifact
- Markdown evidence artifact
- unit tests
- CI integration

Boundary:

This step creates static semantic regression evidence.
It does not prove runtime correctness.

Next milestone:

WVP-SEC-004 - generate executable Nightfall command probes
and capture reproducible command evidence.


## WVP-SEC-004

Status: implemented.

Completed:

- command probe report
- JSON command evidence
- Markdown command evidence
- command probe method documentation
- executable command probe checker
- unit tests
- CI integration

Boundary:

This step captures reproducible local command evidence.
It does not prove runtime consensus correctness.

Next milestone:

WVP-SEC-005 - create release integrity evidence and
reproducible artifact verification scaffolding.


## WVP-SEC-005

Status: implemented.

Completed:

- release integrity report
- JSON release evidence
- Markdown release evidence
- key file hashes
- release integrity method documentation
- executable release integrity checker
- unit tests
- CI integration

Boundary:

This step captures local release-integrity evidence.
It does not prove signed or reproducible binaries.

Next milestone:

WVP-SEC-006 - create supply-invariant evidence map and
runtime-safe invariant probe scaffolding.


## WVP-SEC-006

Status: implemented.

Completed:

- supply invariant evidence map
- JSON invariant evidence
- Markdown invariant evidence
- runtime-safe invariant probes
- supply invariant method documentation
- executable supply invariant checker
- unit tests
- CI integration

Boundary:

This step maps and probes invariant evidence.
It does not prove mathematical or consensus correctness.

Next milestone:

WVP-SEC-007 - create fuzzing and negative-vector
scaffolding for invariant-related failure classes.


## WVP-SEC-007

Status: implemented.

Completed:

- negative vector report
- safe abstract negative vector files
- fuzzing scaffold directory
- negative vector method documentation
- executable negative vector checker
- unit tests
- CI integration

Boundary:

This step creates defensive scaffolding only.
It does not publish exploit payloads and does not prove runtime rejection.

Next milestone:

WVP-SEC-008 - create private-disclosure and findings-triage workflow
for security-relevant observations.


## WVP-SEC-008

Status: implemented.

Completed:

- private disclosure workflow
- findings triage policy
- JSON triage evidence
- Markdown triage evidence
- repository security policy
- finding templates
- executable triage checker
- unit tests
- CI integration

Boundary:

This step creates a disclosure and triage process.
It is not legal advice, not an audit, and not proof that vulnerabilities exist.

Next milestone:

WVP-SEC-009 - create conformance scoring and public report
generation for Nightfall evidence packs.


## WVP-SEC-009

Status: implemented.

Completed:

- conformance score report
- public sanitized report
- conformance scoring method documentation
- public report method documentation
- executable conformance checker
- unit tests
- CI integration

Boundary:

This step scores evidence completeness only.
It is not an audit, not a certification, and not proof of project safety.

Next milestone:

WVP-SEC-010 - create final release-pack builder and
versioned evidence bundle manifest.


## WVP-SEC-010

Status: implemented.

Completed:

- release pack manifest
- markdown bundle manifest
- deterministic evidence archive
- SHA-256 checksum file
- release pack report
- release pack method documentation
- executable release pack checker
- unit tests
- CI integration

Boundary:

This step builds a versioned evidence bundle.
It is not an audit, not a certification, and not proof of project safety.

Next milestone:

WVP-SEC-011 - create CI hardening and required-check
gate documentation for WVP branches.


## WVP-SEC-011

Status: implemented.

Completed:

- CI hardening report
- required-check workflow
- branch protection template
- required-check gate documentation
- executable CI hardening checker
- unit tests
- CI integration guidance

Boundary:

This step documents and checks CI hardening.
It does not itself enable GitHub branch protection and does not prove project safety.

Next milestone:

WVP-SEC-012 - create maintainer handoff, final roadmap, and merge-readiness checklist.


## WVP-SEC-012

Status: implemented.

Completed:

- maintainer handoff documentation
- merge-readiness checklist
- final roadmap
- post-merge operations guide
- reviewer guide
- handoff templates
- handoff readiness report
- merge-readiness report
- executable handoff readiness checker
- unit tests
- CI integration
- release-pack refresh

Boundary:

This step makes the project maintainable and locally merge-ready.
It does not merge PRs, enable GitHub branch protection, provide independent review, or prove project safety.

Next milestone:

WVP-SEC-013 - external review preparation and issue-quality gate.


## WVP-SEC-013

Status: implemented.

Completed:

- external review preparation documentation
- issue-quality gate method
- external review request document
- review scope document
- reviewer response log
- public issue templates
- review request templates
- external review report
- issue-quality gate report
- executable external-review gate checker
- unit tests
- CI integration
- release-pack refresh

Boundary:

This step prepares external review and improves issue hygiene.
It does not provide independent review, merge PRs, enable branch protection, or prove project safety.

Next milestone:

WVP-SEC-014 - runtime test-harness expansion for safe local toy inputs.


## WVP-SEC-014

Status: implemented.

Completed:

- runtime toy harness method documentation
- toy input safety boundary
- runtime harness limitations
- 10 safe local toy vectors
- runtime toy harness report
- runtime toy harness checker
- runtime templates
- unit tests
- CI integration
- release-pack refresh

Boundary:

This step executes safe local toy inputs only.
It does not execute real Nightfall consensus, mutate live node state, use funds, use seeds, or prove project safety.

Next milestone:

WVP-SEC-015 - repository governance and versioned release process.


## WVP-SEC-015

Status: implemented.

Completed:

- governance documentation
- versioning policy
- release process
- changelog policy
- evidence refresh cadence
- maintainer roles
- governance templates
- governance release report
- executable governance release checker
- unit tests
- CI integration
- release-pack refresh

Boundary:

This step creates repository governance and a versioned release process.
It does not merge PRs, enable GitHub branch protection, obtain independent external review, or prove project safety.

Progress:

Local evidence/project completion after this milestone: 98%.
Remaining external completion: 2%.

Remaining external work:

- open and review PRs
- run GitHub Actions
- merge accepted PRs
- enable or verify branch protection
- obtain independent external review or maintainer feedback
- maintain recurring evidence refresh history

Next milestone:

External completion checklist, PR merge workflow, and branch-protection verification.


## WVP-SEC-016

Status: implemented.

Completed:

- external completion checklist
- PR merge workflow
- branch-protection verification method
- CI history verification method
- independent review tracker
- final completion boundary
- external completion templates
- external completion report
- executable external completion checker
- unit tests
- CI integration
- release-pack refresh

Boundary:

This step documents and checks external completion readiness.
It does not open PRs, merge PRs, enable GitHub branch protection, obtain independent review, or prove project safety.

Progress:

Local evidence/project completion after this milestone: 99%.
Remaining external completion: 1%.

100 percent rule:

Only mark the project 100 percent complete after merged PRs, green GitHub Actions, verified branch protection, reviewer or maintainer feedback, and recurring maintenance evidence are recorded.


## AUNEYA-LOCAL-SIM-EVIDENCE-001

Status: implemented.

Completed:

- local simulation evidence pack
- JSON evidence report
- Markdown evidence report
- existing AUNEYA conformance orchestration
- one-command local demo boundary validation
- invalid private-data claim rejection validation
- non-value simulation boundary preservation
- CI-compatible conformance script

Boundary:

This step binds existing AUNEYA local simulation artifacts into one reproducible evidence pack.
It does not create AUNEYA, neya, a token, market value, transferability, mainnet activity, financial claims, legal clearance or investment advice.

Next milestone:

AUNEYA external review readiness and public documentation quality gate.


## AUNEYA-EXTERNAL-REVIEW-READY-001

Status: implemented.

Completed:

- external review readiness document
- public documentation quality gate
- machine-checkable readiness report
- JSON evidence report
- Markdown evidence report
- public boundary validation
- reviewer checklist validation
- CI-compatible conformance script

Boundary:

This step checks AUNEYA documentation readiness for external review.
It does not create AUNEYA, neya, a token, market value, transferability, mainnet activity, legal clearance, financial claims or investment advice.

Next milestone:

AUNEYA external reviewer packet and issue-template workflow.


## AUNEYA-REVIEWER-PACKET-001

Status: implemented.

Completed:

- external reviewer packet
- review feedback workflow
- AUNEYA external review issue template
- machine-checkable reviewer packet report
- JSON evidence report
- Markdown evidence report
- public boundary validation
- review category validation
- CI-compatible conformance script

Boundary:

This step makes AUNEYA externally reviewable through structured documentation and issue-based feedback.
It does not create AUNEYA, neya, a token, market value, transferability, mainnet activity, legal clearance, financial claims or investment advice.

Next milestone:

AUNEYA review intake evidence and maintainer response log.


## AUNEYA-REVIEW-INTAKE-LOG-001

Status: implemented.

Completed:

- review intake evidence model
- zero-intake state documentation
- maintainer response log
- AUNEYA maintainer response issue template
- machine-checkable review intake report
- JSON evidence report
- Markdown evidence report
- public boundary validation
- maintainer triage-state validation
- CI-compatible conformance script

Boundary:

This step records review intake readiness and maintainer response structure.
It does not create fake external review, AUNEYA, neya, a token, market value, transferability, mainnet activity, legal clearance, financial claims or investment advice.

Next milestone:

AUNEYA recurring review evidence refresh and external feedback trail.


## AUNEYA-RECURRING-REVIEW-EVIDENCE-001

Status: implemented.

Completed:

- recurring review evidence refresh document
- external feedback trail document
- scheduled GitHub Actions workflow
- manual workflow_dispatch support
- machine-checkable recurring review evidence report
- JSON evidence report
- Markdown evidence report
- zero-feedback state validation
- fake-feedback rejection rule
- public boundary validation
- CI-compatible conformance script

Boundary:

This step adds recurring review evidence refresh and an external feedback trail.
It does not create fake external review, AUNEYA, neya, a token, market value, transferability, mainnet activity, legal clearance, financial claims or investment advice.

Next milestone:

AUNEYA first real external review request and public reviewer outreach log.


## AUNEYA-LOCAL-LEDGER-WALLET-001

Status: implemented.

Completed:

- local ledger simulator
- local wallet simulator
- local wallet address display
- simulated non-value balance display
- append-only local simulation entries
- visible terminal wallet view
- JSON export
- Markdown export
- wallet-view text export
- machine-checkable ledger and wallet report
- CI-compatible conformance script
- GitHub Actions workflow

Boundary:

This step creates a tangible local ledger and local wallet simulator.
It does not create a real wallet, private key, seed phrase, custody, AUNEYA, neya, a token, market value, transferability, mainnet activity, legal clearance, financial claims or investment advice.

Next milestone:

AUNEYA local browser dashboard and mobile-first read-only UI.


## AUNEYA-LOCAL-DASHBOARD-001

Status: implemented.

Completed:

- local browser dashboard
- mobile-first read-only UI
- static HTML export
- local dashboard JSON report
- local dashboard Markdown report
- wallet snapshot display
- balance display
- ledger entry display
- ledger hash display
- boundary display
- machine-checkable dashboard report
- CI-compatible conformance script
- GitHub Actions workflow

Boundary:

This step creates a local browser dashboard for the local ledger and wallet simulator.
It does not create a real wallet, private key, seed phrase, custody, AUNEYA, neya, a token, market value, transferability, mainnet activity, legal clearance, financial claims or investment advice.

Next milestone:

AUNEYA local claim composer and dashboard live-refresh sandbox.


## AUNEYA-LOCAL-CLAIM-COMPOSER-001

Status: implemented.

Completed:

- local claim composer
- dashboard live-refresh sandbox
- local claim form
- local state API
- local claim POST endpoint
- local claim validation
- simulated prooflet generation
- simulated event finalization
- simulated ledger update
- simulated balance update
- local composer state JSON
- local composer evidence JSON
- local composer Markdown report
- mobile-first composer HTML
- machine-checkable composer report
- CI-compatible conformance script
- GitHub Actions workflow

Boundary:

This step creates a local claim composer and dashboard live-refresh sandbox.
It does not create a real wallet, private key, seed phrase, custody, AUNEYA, neya, a token, market value, transferability, mainnet activity, legal clearance, financial claims or investment advice.

Next milestone:

AUNEYA local witness prooflet inspector and event detail explorer.

