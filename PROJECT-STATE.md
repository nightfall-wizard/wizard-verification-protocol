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
