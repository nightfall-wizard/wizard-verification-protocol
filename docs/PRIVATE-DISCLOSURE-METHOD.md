# WVP Private Disclosure Method

WVP-SEC-008 defines a private-disclosure workflow for
security-relevant observations.

The workflow exists because some findings must not be
published with full detail before maintainers have had a
reasonable opportunity to review and fix the issue.

## Default private classes

The following classes default to private handling:

- inflation
- theft
- fund destruction
- consensus split
- remote crash or resource exhaustion
- privacy break
- key recovery
- release integrity failure

Documentation-to-code mismatch may be public if the
summary is sanitized and does not reveal an exploit path.

## Public reporting rule

Public WVP reports should contain:

- sanitized summary
- affected class
- evidence boundary
- whether details were withheld
- non-audit disclaimer

Public WVP reports should not contain:

- exploit payloads
- weaponized reproduction steps
- private keys
- seeds
- live wallet details
- undisclosed vulnerability detail

## Triage principle

When uncertain, classify conservatively and withhold
exploit-enabling details.
