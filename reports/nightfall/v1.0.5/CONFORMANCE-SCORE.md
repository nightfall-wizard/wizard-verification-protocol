# WVP-SEC-009 - Nightfall Conformance Score

This report scores WVP evidence completeness for Nightfall v1.0.5.

Boundary: this is not an audit, not a certification, and not proof of safety.

Score: **100.0%**

Grade: **A**

Verdict: **LIMITED CONFORMANCE PASS**

## Requirement summary

| ID | Area | Status | Weight | Points |
|---|---|---|---:|---:|
| CONF-001 | `security_model` | `PASS` | 6 | 6.0 |
| CONF-002 | `verification_pack` | `PASS` | 8 | 8.0 |
| CONF-003 | `codepath_bindings` | `PASS` | 10 | 10.0 |
| CONF-004 | `semantic_regression` | `PASS` | 10 | 10.0 |
| CONF-005 | `command_probes` | `PASS` | 10 | 10.0 |
| CONF-006 | `release_integrity` | `PASS` | 10 | 10.0 |
| CONF-007 | `supply_invariant` | `PASS` | 12 | 12.0 |
| CONF-008 | `negative_vectors` | `PASS` | 10 | 10.0 |
| CONF-009 | `disclosure_triage` | `PASS` | 10 | 10.0 |
| CONF-010 | `automation_checks` | `PASS` | 14 | 14.0 |

## Missing evidence

No required WVP evidence file is missing.

## Non-audit boundary

A high score means WVP evidence coverage is present.

It does not mean:

- Nightfall is safe
- the implementation is correct
- cryptography is sound
- vulnerabilities are absent
- an independent audit was performed
