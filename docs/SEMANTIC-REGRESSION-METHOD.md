# WVP Semantic Regression Method

WVP-SEC-003 converts fixture-to-codepath bindings into
automated static semantic regression checks.

The method checks whether bound source/documentation paths
still contain security-critical terms required by a fixture.

This provides regression evidence that a later change did not
silently remove or move the visible implementation surface
without WVP noticing.

A PASS means:

- the fixture is bound to readable paths
- required semantic terms were found
- the evidence is reproducible

A PASS does not mean:

- the implementation is correct
- the cryptography is sound
- the project is audited
- user funds are safe

A WARN means:

- WVP found a gap in the semantic evidence
- the fixture may need a stronger binding
- the implementation path may have changed
