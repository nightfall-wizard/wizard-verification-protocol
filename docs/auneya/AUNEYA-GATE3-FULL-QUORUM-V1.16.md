# AUNEYA/WVP v1.16 — Independent Full-Quorum Cross-Language Verification

Status: experimental offline research. No economic or public-network activation.

## Engineering advance

Node.js re-verifies an original v1.12 portable capsule independently of the
Python quorum implementation, without npm dependencies. It checks canonical
bytes, exact field sets, bounded sizes, Ed25519 signatures of the v1.9 anchor
and every v1.10 keeper receipt, separately configured PEM SHA-256 pins,
keeper threshold and sorted uniqueness, all anchor/receipt bindings, sequence
and signed predecessor continuity, capsule metadata, and the exact Python
v1.11 WVP report SHA-256 commitment. 63-bit integers are parsed losslessly.

Optionally it invokes the existing independent Node v1.15 recipient ACK
verifier to bind recipient signature, externally provided ACK head, and
recipient floor to the newly verified full quorum in one read-only command.

## Termux verification

The expected capsule hash must be retained independently of the producer.

```sh
node tools/auneya/auneya_gate3_full_v116.js \
  --trust "$HOME/.auneya-keeper/trust.json" \
  --capsule "$HOME/.auneya-keeper/capsule.json" \
  --expected-capsule "$INDEPENDENT_CAPSULE_SHA256"
```

Optional ACK verification additionally accepts `--receipt`,
`--recipient-public`, `--recipient-pin`, `--expected-head` and `--floor`.

The first four ACK arguments must be supplied together. `--floor` is optional.

The trust configuration and PEM files must be regular mode 0600 files inside
mode 0700 directories. The capsule is read-only. Private keys are never read.

## Reproduce and falsify

```sh
python3 -m unittest discover -s tests -p 'test_auneya_gate3_full_v116.py' -v
python3 -m unittest discover -s tests -p 'test_auneya_gate3_interop_v115.py' -v
python3 tools/readme_truth.py --check
```

Tests include real Python-generated signed two-keeper evidence, two contiguous
checkpoints, positive Python/Node report commitment parity, optional recipient
ACK integration, forged signatures, mismatched pins and hashes, missing quorum,
duplicate keepers, noncanonical nested JSON, and symlink rejection.

## Explicit trust boundary

`expected_capsule_matched` means only that caller-supplied digest matched.

If the digest, trust pins, and evidence are all copied from the same compromised
device, this does NOT prove independence.

It does not prove external durable retention, time freshness, physical device
diversity, consensus, Sybil resistance, production safety, audit completion,
or legal compliance.

The v1.4 lossless parser limits individual JSON inputs to 3 MiB, even though
the Python capsule format allows up to 4 MiB. This validator intentionally
fails closed on larger capsules; full size-range parity remains open.

Gate 3 remains PARTIALLY IMPLEMENTED.

Gate 4 remains INCOMPLETE.

Gate 5 is NOT COMPLETED.

Gate 6 remains BLOCKED.

No mainnet, token, reward, transfer, price, economic activation, or public
P2P network is created.

Real second-device acceptance requires genuinely separate physical devices,
independent operator-controlled pins and storage, a transferred capsule,
rollback/outage experiments, signed trace retention and independent review.

Automated local tests cannot substitute for those requirements.
