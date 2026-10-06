
# WVP Release Process

This document defines the WVP evidence release process.

## Local release steps

1. Run unit tests.
2. Run all WVP Nightfall checkers.
3. Rebuild the release pack.
4. Verify release-pack checksum.
5. Verify public-report sanitation.
6. Verify non-audit boundary.
7. Commit changes.
8. Push branch.
9. Open pull request.
10. Wait for CI.
11. Review feedback.
12. Merge only after required checks pass.

## Required local commands

Run:

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
- python3 wvp/nightfall/external_review_gate.py
- python3 wvp/nightfall/runtime_toy_harness.py
- python3 wvp/nightfall/governance_release.py

## External steps

A local Termux command cannot guarantee:

- PR merge
- GitHub branch protection
- independent external review
- maintainer approval
- long-term maintenance history

## Boundary

A WVP release is an evidence release. It is not an audit.
