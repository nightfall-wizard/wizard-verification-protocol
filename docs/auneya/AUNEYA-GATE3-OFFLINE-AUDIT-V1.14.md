# AUNEYA/WVP v1.14 — Independent Offline Recipient-History Audit

**Status: experimental non-value research only. Gate 3 remains PARTIALLY IMPLEMENTED.**

## Purpose

The recipient's chronological history is no longer accepted merely because it
contains v1.13 ACKs. An independent read-only auditor re-runs the **complete**
v1.12 Ed25519 quorum verification for every capsule and validates every v1.13
recipient signature against a separately pinned public key.

It checks exact recipient-to-quorum commitments, consistent independent trust
configuration, sequence 1 bootstrap, contiguous signed predecessor anchors,
non-replayed capsule and ACK digests, and the last recipient ACK against an
**independently retained, externally supplied** 64-character lowercase SHA-256
head pin.

The head pin MUST be communicated or recorded separately from the producer's
storage. A head copied from the same potentially compromised directory does
not prove rollback resistance.

No private keys belong in an audit manifest.

## Manifest

Canonical ASCII JSON with exactly one terminating LF.

Maximum 64 KiB, maximum 64 entries.

Place the manifest, capsules and ACKs in a recipient-controlled private
directory. All entry file names are basenames, never absolute paths.

    {"entries":[{"ack":"ack1.json","capsule":"capsule1.json"}],"format":"auneya-gate3-audit-manifest-v1.14"}

The manifest's ordering is chronological; it must start at sequence 1.

For a second entry, the recipient ACK must be `advanced`, not `unchanged`.

## Independent offline command

Run in Termux at repository root, with separately enrolled trust policy,
recipient key pin and retained final ACK hash:

    python3 tools/auneya/auneya_gate3_audit_v114.py \
      --trust "$HOME/.auneya-keeper/trust.json" \
      --manifest "$HOME/.auneya-keeper/audit-manifest.json" \
      --recipient-public "$HOME/.auneya-keeper/recipient-public.pem" \
      --recipient-pin 'INDEPENDENT_RECIPIENT_PEM_SHA256' \
      --expected-head 'INDEPENDENT_LATEST_ACK_SHA256' \
      --floor "$HOME/.auneya-keeper/floor.json" \
      --output "$HOME/.auneya-keeper/verified-audit.json"

`--floor` is optional and refers to the current floor at the last ACK, not
a historical floor.

`--output` is optional, exclusive creation (no overwrite), mode 0600 in
an existing mode-0700 directory.

The audit is read-only without that option.

Nothing is uploaded. No automatic network service is started.

## Adversarial reproduction

    python3 -m unittest discover -s tests -p 'test_auneya_gate3_audit_v114.py' -v
    python3 -m unittest discover -s tests -p 'test_auneya_gate3_receipt_v113.py' -v
    python3 tools/readme_truth.py --check

Real Ed25519 keys are used in local fixtures.

Tests cover signed two-sequence continuity, dropped/reordered/replayed
evidence, manipulated ACK signatures, wrong pins, path traversal, symlinks,
noncanonical manifests, mismatching head and exclusive output.

**No real device separation is simulated as proof.**

## Remaining Gate 3 acceptance

Two independently controlled physical devices; isolated storage and trust
roots; actual transfer, producer restore/rollback, remote outage and recovery;
reproducible packet or file traces, key compromise/rotation recovery,
independent reviewers and published sanitized acceptance records.

Gate 4: INCOMPLETE.

Gate 5: NOT COMPLETED.

Gate 6: BLOCKED.

No consensus, Sybil resistance, independent audit, mainnet, token, economic
activation, profits, rewards, or transferability are claimed or enabled.
