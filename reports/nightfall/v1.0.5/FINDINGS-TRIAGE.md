# WVP-SEC-008 - Private Disclosure and Findings Triage

This report defines how WVP handles security-relevant observations.

Boundary: this is not legal advice and not an audit.

Security classes: 9
Severity levels: 5
Workflow states: 9
Triage rules: 8

## Safety boundary

- no_real_seed: `True`
- no_private_key: `True`
- no_live_funds: `True`
- no_exploit_payloads: `True`
- no_public_zero_day_details: `True`
- non_audit_label_required: `True`
- sanitized_public_reports: `True`

## Security classes

| ID | Class | Private default | Public detail |
|---|---|---:|---|
| CLASS-001 | Inflation | `True` | only after fix or maintainer clearance |
| CLASS-002 | Theft | `True` | only after fix or maintainer clearance |
| CLASS-003 | Fund destruction | `True` | only after fix or maintainer clearance |
| CLASS-004 | Consensus split | `True` | only after fix or maintainer clearance |
| CLASS-005 | Remote crash or resource exhaustion | `True` | only after fix or maintainer clearance |
| CLASS-006 | Privacy break | `True` | only after fix or maintainer clearance |
| CLASS-007 | Key recovery | `True` | only after fix or maintainer clearance |
| CLASS-008 | Release integrity failure | `True` | only after fix or maintainer clearance |
| CLASS-009 | Documentation-to-code mismatch | `False` | sanitized summary allowed |

## Severity levels

| Level | Private default | Definition |
|---|---:|---|
| INFO | `False` | No direct security impact; improves clarity. |
| LOW | `False` | Limited impact or hard-to-trigger issue. |
| MEDIUM | `True` | Meaningful security impact requiring maintainer review. |
| HIGH | `True` | Likely serious impact on funds, consensus, privacy, or availability. |
| CRITICAL | `True` | Potential catastrophic impact or easy exploitation. |

## Workflow states

- `observed`
- `classified`
- `evidence_captured`
- `private_hold`
- `maintainer_contact_ready`
- `maintainer_contacted`
- `fix_or_response_pending`
- `resolved`
- `sanitized_public_summary`

## Triage rules

- **TRIAGE-001**: Do not publish exploit steps.
- **TRIAGE-002**: Do not publish payloads that enable theft, inflation, fund destruction, or consensus split.
- **TRIAGE-003**: Do not request or store seeds, private keys, wallet files, or live funds.
- **TRIAGE-004**: Use sanitized summaries for public reports until fix or maintainer clearance.
- **TRIAGE-005**: Keep reproducible local evidence but redact secrets and exploit-enabling detail.
- **TRIAGE-006**: Mark WVP outputs as non-audit unless an independent audit exists.
- **TRIAGE-007**: Escalate HIGH and CRITICAL observations to private disclosure workflow.
- **TRIAGE-008**: When uncertain, classify conservatively and withhold exploit detail.
