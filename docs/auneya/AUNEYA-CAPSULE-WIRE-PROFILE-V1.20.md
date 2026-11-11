# AUNEYA v1.20 — capsule wire research candidate

Adds JSON Schema 2020-12 structural profile for existing v1.12
signed capsules, 3 MiB bound matching current Node parser,
canonical nested encoding and signed dual-runtime adversarial
conformance. Python and Node independently reject all 15 v1.19
attacks. Reports are deterministic; input hashes must be pinned
independently of an untrusted capsule.

Run `python3 -m unittest discover -s tests -p test_auneya_wire_v120.py -v`.
For real externally pinned evidence: `python3 tools/auneya/auneya_wire_v120.py
create --trust TRUST --capsule CAPSULE --expected EXTERNAL_SHA256
--output NEW_PRIVATE_REPORT`. Recheck using `verify --input REPORT`.

Not proven: independent physical devices, external durable
retention, formally ratified normative schema, trusted time,
network consensus, independent audit or lawful economic activity.
Gate 3 partial, Gate 4 incomplete, Gates 5/6 blocked.
No token, mainnet, transferability or reward activation.
