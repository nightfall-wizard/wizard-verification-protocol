# WVP Release Integrity Method

WVP-SEC-005 captures release-integrity evidence from the local
Nightfall repository.

The method records:

- repository identity
- git HEAD
- configured remotes
- local tags
- release workflow presence
- CI workflow presence
- Cargo lockfile presence
- release/checksum/security terms
- hashes of key release-related files

A PASS means:

- the expected command returned successfully
- output was captured
- evidence is reproducible locally

A WARN means:

- evidence is missing
- a command failed
- the local repository or toolchain is incomplete
- manual review is required

This method does not prove:

- signed releases
- reproducible binary identity
- trusted build infrastructure
- absence of supply-chain compromise
- correctness of release artifacts
