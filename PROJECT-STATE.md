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
