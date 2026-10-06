
# WVP Reviewer Guide

This guide helps a reviewer understand what to check.

## What a reviewer should look for

- evidence files exist
- JSON reports are machine-readable
- Markdown reports are readable
- safety boundaries are explicit
- checkers pass locally
- release pack hash is current
- public report is sanitized
- branch-protection instructions are present

## What a reviewer should not assume

A passing WVP check does not prove:

- consensus correctness
- cryptographic soundness
- absence of inflation bugs
- absence of theft bugs
- real-world anonymity
- production safety
- audit status

## Security handling

If a review discovers a security-relevant observation, use the private disclosure and triage workflow.
