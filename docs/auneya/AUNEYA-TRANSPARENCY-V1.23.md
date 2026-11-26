# AUNEYA v1.23 — Evidence Transparency Journal (research)

**Status:** offline non-value research. No external retention, physical device
independence, production network, distributed consensus, audit or token claim.

## Distinct capability

A privacy-minimal local journal of **hash-only commitments** generated from
**freshly reverified** AUNEYA v1.22 signed Gate 3 artifacts. Records bind the
full v1.22 deterministic report digest, chain, strictly contiguous positive
sequence, recipient key pin, capsule, ACK, persisted floor and anchor hashes.
Records never contain private Ed25519 signing keys or original evidence bodies.

RFC 6962-style domain-separated SHA-256 Merkle hashing uses
`leaf = SHA256(0x00 || canonical(record))`,
`branch = SHA256(0x01 || left || right)`, and
`empty = SHA256(empty bytes)`. Internal nodes split at the greatest power
of two strictly smaller than the number of leaves. Canonical representation:
ASCII JSON, sorted keys, no insignificant whitespace, one trailing LF.

The journal is bounded to 256 entries, canonical, backed by 0600 files in
0700 directories; serialized modifications use an advisory file lock and
atomic fsync + rename. The inclusion proof is checked in separate Python and
Node.js implementations with an externally pinned **size and root**.

## Operator commands (private Termux directory)

```sh
mkdir -p "$HOME/.auneya-transparency"
chmod 700 "$HOME/.auneya-transparency"
J="$HOME/.auneya-transparency/journal.json"
python3 tools/auneya/auneya_transparency_v123.py init --journal "$J"
```

To append, provide **actual** v1.22 signed artifacts and **independently
obtained** hashes, as in `AUNEYA-GATE3-FIELDTRIAL-V1.22.md`:

```sh
python3 tools/auneya/auneya_transparency_v123.py append --journal "$J" \
  --trust "$TRUST" --capsule "$CAPSULE" --ack "$ACK" --floor "$FLOOR" \
  --recipient-public "$RECIPIENT_PUBLIC" --recipient-pin "$RECIPIENT_PIN" \
  --expected-trust "$TRUST_SHA" --expected-capsule "$CAPSULE_SHA" \
  --expected-ack "$ACK_SHA" --expected-floor "$FLOOR_SHA"

python3 tools/auneya/auneya_transparency_v123.py inspect --journal "$J"
```

A sequence gap is refused. Export an inclusion proof using `prove --index 0
--out "$HOME/.auneya-transparency/proof.json" --journal "$J"` (new output
only). Verify it with **both** `verify-proof --proof ... --expected-root SHA
--expected-size N` (Python) and `node tools/auneya/auneya_transparency_v123.js
--proof ... --expected-root SHA --expected-size N` (Node).

Retain old/new journal snapshots in separate private files and use
`compare --old ... --new ... --old-root EXTERNALLY_RETAINED_ROOT
--new-root EXTERNALLY_RETAINED_ROOT`.

## Honest trust boundary

A locally computed root or copy of an old journal **does not** establish an
independent checkpoint. Inclusion proves **membership in the supplied pinned
root**, not an observation's real-world truth or the integrity of the
journal author.

Comparing two entire journal snapshots detects truncation, prefix rewrites
and forks **only if** both head commitments were independently retained
outside an attacker's rollback domain.

This is **not** a compact Merkle consistency proof, gossip service,
public transparency log or signed checkpoint service.
Operator compromise can forge a new log plus new root.

The remaining priority is real two-device Gate 3 acceptance and independently
controlled durable commitments, rollback/outage/recovery experiments, privacy
review and external security review.

Gate 3 stays PARTIAL, Gate 4 INCOMPLETE, Gate 5 NOT COMPLETED,
Gate 6 BLOCKED. No mainnet/economic activation.

## Bounded file input

Both Merkle readers use a single checked file descriptor, reject nonregular
files, final-component symlinks and multiply linked files, and read at most
512 KiB plus one byte. Metadata is checked again after reading. This is local
input hardening, not proof of immutable storage or independent retention.
