# Negative Release-Check Fixtures

These fixtures are intentionally invalid.

They prove that WVP does not merely recognize valid release metadata, but also rejects dangerous release states.

## Fixture Matrix

| Fixture | Invariant | Expected |
|---|---:|---|
| FRC-SEC-001-missing-digest.json | WVP-INV-001 | reject |
| FRC-SEC-002-path-traversal.json | WVP-INV-002 | reject |
| FRC-SEC-003-duplicate-artifact.json | WVP-INV-003 | reject |
| FRC-SEC-004-missing-signature.json | WVP-INV-004 | reject |
| FRC-SEC-005-network-dependent-verification.json | WVP-INV-005 | reject |
| FRC-SEC-006-silent-downgrade.json | WVP-INV-006 | reject |
| FRC-SEC-007-ambiguous-network-context.json | WVP-INV-007 | reject |

## Maintenance Rule

Every security-relevant release-check bug must add:

1. one invariant or invariant clarification,
2. one negative fixture,
3. one regression test,
4. one changelog entry if user-visible behavior changes.

