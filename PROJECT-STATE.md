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
