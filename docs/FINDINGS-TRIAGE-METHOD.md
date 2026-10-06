# WVP Findings Triage Method

WVP findings are classified by:

1. security class
2. severity
3. evidence quality
4. exploitability
5. publication risk
6. disclosure state

## Severity

INFO:
No direct security impact.

LOW:
Limited impact or hard-to-trigger issue.

MEDIUM:
Meaningful security impact that requires maintainer review.

HIGH:
Likely serious impact on funds, consensus, privacy, or availability.

CRITICAL:
Potential catastrophic impact or easy exploitation.

## States

- observed
- classified
- evidence_captured
- private_hold
- maintainer_contact_ready
- maintainer_contacted
- fix_or_response_pending
- resolved
- sanitized_public_summary

## Non-audit rule

A WVP finding is not an audit finding unless an actual
independent audit exists.
