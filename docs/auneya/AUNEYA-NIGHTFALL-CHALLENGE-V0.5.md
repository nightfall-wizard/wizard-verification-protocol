# AUNEYA v0.5 — Challenge-bound Nightfall operator observations

## Capability

One challenger creates a short-lived unpredictable 256-bit request. Independently configured operators obtain **public, read-only** data from **their own** Nightfall v8 mainnet RPC on `127.0.0.1` and sign a bounded JSON observation with Ed25519. The verifier checks the precise request, freshness, static mainnet genesis, key from the **pre-enrolled** AUNEYA v0.4 registry, and signature. A private SQLite ledger rejects repeated observations. Two verified operator receipts can be compared for matching tips, same-height fork discrepancies, or differing-height observations that **do not prove a fork**.

This is a portable file-exchange format. It does not open a TCP listener, expose a remote RPC port, or initiate any network access other than local loopback RPC. Do not use private wallet keys for AUNEYA signing. The external channel for exchanging files is out of scope; it must separately protect operator privacy and the integrity of the initial key pinning.

## Commands

Use `python3 tools/auneya/auneya_nightfall_challenge_v05.py` with:

- `challenge --out challenge.json`
- `attest --challenge challenge.json --node-id node_research_operator_a --private OPERATOR.private.pem --rpc-port 17881 --out witness.json`
- `verify --challenge challenge.json --receipt witness.json --registry pinned.sqlite --replay-db verified.sqlite`
- `compare --challenge challenge.json --receipt-a a.json --receipt-b b.json --registry pinned.sqlite --replay-db compared.sqlite`

The verifier must enroll each operator's public key separately in the v0.4 registry using `auneya_trusted_node_identity_v04.py enroll` and independently confirm its SHA-256 fingerprint. A recipient cannot be enrolled by the submitted receipt. The signature is domain-separated from v0.4 identity events and includes the challenge, reporting node ID, observation time and strict public status fields.

**Choose a new replay database for a new verifier workflow, not to bypass replay rejection for a previously processed claim.** `compare` consumes both receipts together; do not preconsume either with `verify` against the same replay database. The replay ledger is local and does not prevent someone creating a fresh verifier state.

## Tests

`python3 -m unittest discover -s tests -p test_auneya_nightfall_challenge_v05.py -v`

## Deliberate non-claims

- Signed RPC observations **do not independently verify consensus, accumulated proof of work, the confidential supply equation, or the correctness of a remote operator's software**.
- Different public keys **do not prove distinct devices, locations, or independent owners**. This is not Sybil resistance or a decentralization certificate.
- Same-height differing tips demonstrate conflicting claims at overlapping times, not which chain is valid or that an attack occurred.
- Verification does not authorize transfers, mining, peer control, protocol changes, wallet scanning, financial claims, or independent security-audit claims.
- This tool does not implement AUNEYA mainnet, tokens, transferable rewards, market value, or legal clearance.

Designed to complement Nightfall's September 2026 roadmap emphasis on independently checked operator evidence, and not to supersede Nightfall's own node verification.
