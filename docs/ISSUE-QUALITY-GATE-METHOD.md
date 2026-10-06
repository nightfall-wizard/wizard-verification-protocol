
# WVP Issue-Quality Gate Method

This method defines the minimum quality bar for public WVP issues.

## Required issue fields

Every public issue should include:

- issue type
- affected evidence area
- expected behavior
- observed behavior
- reproduction boundary
- safety boundary
- non-audit boundary
- proposed action
- whether private detail was withheld

## Allowed public issue types

- documentation gap
- evidence gap
- checker failure
- release-pack drift
- unclear limitation
- reviewer question
- sanitized security observation
- CI or workflow issue
- template improvement

## Public issue must not include

- private key
- seed
- wallet file
- live funds
- exploit payload
- weaponized reproduction
- undisclosed vulnerability detail

## Quality decision

PASS:
The issue is clear, bounded, reproducible, and safe to publish.

HOLD:
The issue may contain security-sensitive details and needs private triage.

FAIL:
The issue is ambiguous, unsafe, or missing required fields.

## Boundary

The issue-quality gate protects review hygiene. It does not certify project safety.
