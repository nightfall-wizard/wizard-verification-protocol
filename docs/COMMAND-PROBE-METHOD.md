# WVP Command Probe Method

WVP-SEC-004 captures reproducible command evidence from
the local Nightfall repository.

The goal is to move beyond documentation-only evidence.

A probe can check:

- repository presence
- git identity
- specification presence
- security policy presence
- consensus-related search terms
- cargo workspace metadata
- build/test command availability
- release workflow presence

A PASS means:

- the command ran with the expected return code
- the output was captured
- the evidence can be inspected later

A WARN means:

- the command failed
- the local repository is missing
- the toolchain is missing
- the evidence requires manual review

A probe does not prove:

- cryptographic correctness
- consensus correctness
- absence of inflation
- absence of theft bugs
- production safety
