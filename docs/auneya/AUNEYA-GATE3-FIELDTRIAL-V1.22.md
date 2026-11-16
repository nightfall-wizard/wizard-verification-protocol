# AUNEYA/WVP v1.22 — Offline Gate 3 Field-Trial Verification

**Status:** experimental, non-value research; NOT proof that real-device Gate 3 passed.

## Problem this closes

WVP/AUNEYA already has authenticated v1.12 keeper-quorum capsules,
v1.13 recipient-signed ACKs, a durable recipient floor, and independent
Python/Node verification. Previously a field trial required coordinating
these separate checks without one strict, reproducible evidence contract.

v1.22 is a **read-only** composition of the existing implementations:

1. Requires external, lower-case SHA-256 commitments for the recipient
   trust policy, quorum capsule, recipient ACK and persisted floor.
2. Requires an independently selected, SHA-256-pinned recipient Ed25519
   public key; no private signing key is needed to verify.
3. Re-verifies the full signed keeper quorum in Python and Node.js.
4. Independently checks the signed ACK in Python and Node.js.
5. Matches chain, sequence, capsule, anchor, trust, floor, key and ACK.
6. Refuses unexpected mutations, forged signatures or disagreement.
7. Emits canonical deterministic JSON with deliberately false production,
   physical-device, audit, remote-retention and economic claims.
8. Never mutates the recipient floor; exclusive report creation is optional.

## Real device procedure (not executable on one physical phone alone)

- Device A: create a real signed quorum capsule using v1.11/v1.12.
- Device B: separately provision and pin trust and the recipient key;
  independently retain monotonic high-water evidence; accept and sign
  an ACK using the existing v1.12/v1.13 tools.
- Independently preserve expected SHA-256 digests outside Device A's
  rollback domain. Never acquire the expected hashes from the same
  untrusted capsule/ACK transfer and call them independent.
- On the recipient, run this read-only verifier against the actual
  capsule, actual signed ACK, trust, pinned public key, and floor.
- Experimentally replay stale and conflicting capsules, simulate a
  producer rollback and a genuine remote outage/recovery while preserving
  the recipient floor. Preserve actual negative verdicts and sanitized logs.
- Obtain an independent reviewer assessment of physical separation,
  operator identity, retention, rollback and recovery. Source code cannot
  establish any of those facts from self-reported fields.

## Verifier command

```sh
python3 tools/auneya/auneya_fieldtrial_v122.py \
  --trust "$HOME/.auneya-keeper/trust.json" \
  --capsule "$HOME/exchange-1.json" \
  --ack "$HOME/.auneya-keeper/ack-1.json" \
  --floor "$HOME/.auneya-keeper/floor.json" \
  --recipient-public "$HOME/.auneya-keeper/recipient-public.pem" \
  --recipient-pin RECIPIENT_PUBLIC_KEY_SHA256 \
  --expected-trust EXTERNALLY_PINNED_TRUST_SHA256 \
  --expected-capsule EXTERNALLY_PINNED_CAPSULE_SHA256 \
  --expected-ack EXTERNALLY_PINNED_ACK_SHA256 \
  --expected-floor EXTERNALLY_PINNED_FLOOR_SHA256
```

An optional `--report path` writes a new 0600 file in an existing private
0700 directory. A successful report verifies **cryptographic artifacts**,
not independence of devices or witnesses.

## Reproduce in Termux

```sh
python3 -m unittest discover -s tests -p 'test_auneya_fieldtrial_v122.py' -v
python3 tools/readme_truth.py --check
```

The tests use authentic Ed25519 signatures but only local test fixtures.
They cannot complete real-device experiments. Gate 3 remains PARTIAL;
Gate 4 INCOMPLETE; Gate 5 NOT COMPLETED; Gate 6 BLOCKED.

No network launch, token issuance, mainnet, transferability, value, independent
audit or economic activation is claimed or enabled.
