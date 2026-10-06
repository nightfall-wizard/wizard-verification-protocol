# Nightfall Fuzzing Scaffold

This directory is a placeholder for future safe fuzzing work.

Current status:

- abstract negative vectors exist
- no exploit payloads are included
- no live chain mutation is performed
- no wallet seed or private key is used

Next steps:

1. bind each abstract vector to a public test harness
2. create deterministic toy inputs
3. run only local non-network tests
4. record crashes as private security reports when relevant
5. avoid publishing exploitable detail
