
# WVP Maintainer Handoff

This document hands WVP Nightfall evidence work over to maintainers and reviewers.

## Scope

WVP is a verification and evidence framework.

It is not:

- an audit
- a safety certification
- legal advice
- investment advice
- proof that Nightfall is safe
- proof that Nightfall has no vulnerabilities

## Current evidence areas

The Nightfall v1.0.5 evidence pack currently contains:

- security model documentation
- verification profiles
- traceability report
- codepath bindings
- semantic regression checks
- command probes
- release integrity evidence
- supply invariant evidence map
- safe negative-vector scaffolding
- private disclosure and triage workflow
- conformance score
- sanitized public report
- release-pack manifest
- CI hardening and required-check gate
- maintainer handoff and merge-readiness checklist

## Local verification commands

Run these commands from the repository root:

- python3 -m unittest discover -s tests -v
- python3 wvp/nightfall/verifier.py
- python3 wvp/nightfall/codepath_binding.py
- python3 wvp/nightfall/semantic_regression.py
- python3 wvp/nightfall/command_probes.py
- python3 wvp/nightfall/release_integrity.py
- python3 wvp/nightfall/supply_invariant.py
- python3 wvp/nightfall/negative_vectors.py
- python3 wvp/nightfall/triage_workflow.py
- python3 wvp/nightfall/conformance_score.py
- python3 wvp/nightfall/release_pack.py
- python3 wvp/nightfall/ci_hardening.py
- python3 wvp/nightfall/handoff_readiness.py

## Required reviewer checks

Reviewers should verify:

- no private keys
- no seeds
- no live funds
- no exploit payloads
- no undisclosed vulnerability detail
- non-audit boundary is present
- generated release pack passes
- CI hardening passes
- public report is sanitized
- branch-protection guidance is documented

## Handoff boundary

This handoff makes the evidence pack maintainable. It does not prove Nightfall safety.
