# AUNEYA/WVP v1.13 — Signed Recipient Acceptance

Status: **experimental local research**.

Gate 3 remains **partially implemented**.

No public network, independent audit, token issuance
or economic activation.

## Goal

A recipient verifies a v1.12 portable signed quorum
capsule using independently configured trust anchors
and a monotonic high-water floor.

The recipient then signs an Ed25519 acceptance
statement.

The statement binds:

- Research chain identity
- Anchor sequence and SHA-256
- Portable capsule SHA-256
- Recipient trust-policy SHA-256
- Recipient high-water floor SHA-256
- Recipient public-key fingerprint

The canonical bounded JSON acknowledgment
contains no private keys.

## Security contract

- A v1.13 ACK requires successful v1.12 verification.
- The existing monotonic high-water admission must pass.
- Recipient signatures use Ed25519 domain separation.
- Public-key fingerprints must match trusted pins.
- Invalid signatures and altered commitments are rejected.
- Output files are created exclusively.
- An interrupted signing operation may leave an advanced
  floor without a signed ACK.
- Historical floor states require separate retention.
- A signature does not prove independent physical hardware.
- Real second-device Gate 3 acceptance remains mandatory.

## Recipient command

Run from the repository root.

The recipient must already possess independently
configured trust anchors and a signing keypair.

    python3 tools/auneya/auneya_gate3_receipt_v113.py issue --trust "$HOME/.auneya-keeper/trust.json" --capsule "$HOME/exchange-1.json" --floor "$HOME/.auneya-keeper/floor.json" --recipient-private "$HOME/.auneya-keeper/recipient-private.pem" --recipient-public "$HOME/.auneya-keeper/recipient-public.pem" --pin "RECIPIENT_PUBLIC_KEY_SHA256" --output "$HOME/.auneya-keeper/ack-1.json"

## Independent signature verification

    python3 tools/auneya/auneya_gate3_receipt_v113.py verify --receipt "$HOME/.auneya-keeper/ack-1.json" --recipient-public "$HOME/.auneya-keeper/recipient-public.pem" --pin "RECIPIENT_PUBLIC_KEY_SHA256" --capsule "$HOME/exchange-1.json"

A matching historical floor snapshot can optionally
be supplied using --floor.

## Reproduction

    python3 -m unittest discover -s tests -p 'test_auneya_gate3_receipt_v113.py' -v
    python3 -m unittest discover -s tests -p 'test_auneya_capsule_v112.py' -v
    python3 tools/readme_truth.py --check

## Remaining requirements

Independent recipient physical device.

Separate recipient-controlled durable storage.

Actual producer rollback and outage experiments.

Real recovery evidence.

Independent protocol replication.

Key rotation and revocation validation.

Independent cryptographic, privacy and legal reviews.

Gate 4: INCOMPLETE.

Gate 5: NOT COMPLETED.

Gate 6: BLOCKED.

No network or economic activation.
