# WVP Codepath Binding Method

WVP-SEC-002 links each security fixture to likely implementation or specification paths.

The method is deliberately conservative:

1. scan selected source and documentation files
2. search for fixture-specific security terms
3. record matching paths and file hashes
4. mark fixtures as bound or unbound
5. avoid claiming correctness

A bound fixture means:

- WVP found relevant source or documentation paths
- future tests can target those paths
- the fixture is no longer only abstract documentation

A bound fixture does not mean:

- the code is correct
- the bug class is impossible
- the project is audited
- user funds are safe
