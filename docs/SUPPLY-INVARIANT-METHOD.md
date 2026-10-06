# WVP Supply Invariant Evidence Method

WVP-SEC-006 maps supply-invariant evidence and creates
runtime-safe probes.

Runtime-safe means:

- no seed is read
- no private key is read
- no wallet transaction is created
- no node state is mutated
- no network action is required
- only local files and read-only commands are inspected

The method records:

- supply-invariant wording
- UTXO accounting surface
- kernel excess surface
- mint and burn accounting surface
- coinbase maturity surface
- emission schedule surface
- maximum supply cap surface
- fee burn surface
- range proof surface

A PASS means:

- the required evidence terms are visible
- at least one source or documentation path supports review
- evidence can be reproduced locally

A WARN means:

- evidence was not visible
- wording may have changed
- a stronger binding is needed

This method does not prove:

- the invariant is mathematically correct
- every consensus path enforces the invariant
- inflation bugs are impossible
- wallet or node software is safe
- Nightfall has been audited
