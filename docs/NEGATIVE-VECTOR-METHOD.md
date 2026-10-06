# WVP Negative Vector Method

WVP-SEC-007 creates safe negative-vector scaffolding for
security-critical failure classes.

The vectors are intentionally abstract.

They do not contain:

- real seeds
- private keys
- live funds
- exploit payloads
- undisclosed vulnerability details
- node-mutating commands
- network-mutating commands

The purpose is to make expected rejection behavior explicit.

A vector defines:

- failure class
- fixture name
- expected result
- mutation target
- safety boundary

A PASS means:

- vectors are present
- vectors are machine-readable
- safety fields are explicit
- expected rejection behavior is documented

A PASS does not mean:

- Nightfall rejects the concrete runtime case
- the implementation is safe
- the invariant is proven
- the project is audited
