# AUNEYA/WVP v1.0 — Transactional Evidence Archive

Status: additive local research capability.

This is not a token, network launch, audit, consensus proof,
security certification or economic activation.

## Problem

The v0.9 workflow consumes signed observations in a SQLite
replay database before writing a separate evidence capsule.

A crash between these operations can leave a consumed
observation without its corresponding durable archive.

## Solution

v1.0 stores:

1. v0.5-compatible replay records.
2. Complete canonical v0.9 evidence capsules.
3. External checkpoint pin references.

These are written in one private SQLite database.

The replay records and capsule are inserted in the same
SQLite transaction.

SQLite is configured with:

- BEGIN IMMEDIATE
- synchronous=FULL
- journal_mode=DELETE
- unique replay keys
- unique evidence commitments

On transaction failure, all evidence inserts are rolled back.

Schema initialization is separate and contains no observations.

## Compatibility

The following existing components remain unchanged:

- AUNEYA v0.5 challenge and signature format.
- AUNEYA v0.6 checkpoint format.
- AUNEYA v0.7 pinned observation model.
- AUNEYA/WVP v0.8 multi-witness commitment.
- AUNEYA v0.9 canonical archival capsule.

This is additive functionality.

## Capture

python3 tools/auneya/auneya_archive_v10.py capture \
  --challenge challenge.json \
  --receipt operator-a.json \
  --receipt operator-b.json \
  --registry registry.sqlite \
  --seal checkpoint.json \
  --expected-sha256 EXTERNALLY_RECORDED_PIN \
  --ledger private-replay-and-archive.sqlite

The command returns a deterministic evidence_sha256 value.

## Independent offline inspection

python3 tools/auneya/auneya_archive_v10.py inspect \
  --ledger private-replay-and-archive.sqlite \
  --evidence-sha256 EVIDENCE_SHA256 \
  --expected-sha256 EXTERNALLY_RECORDED_PIN

## Export

python3 tools/auneya/auneya_archive_v10.py export \
  --ledger private-replay-and-archive.sqlite \
  --evidence-sha256 EVIDENCE_SHA256 \
  --expected-sha256 EXTERNALLY_RECORDED_PIN \
  --out capsule.json

The export is a canonical v0.9-compatible capsule.

Existing files are never intentionally overwritten.

## Security properties

The implementation checks:

- Ed25519 signature validity.
- External registry checkpoint binding.
- Bounded input count.
- Capture-time challenge freshness.
- Deterministic evidence commitments.
- Duplicate observation rejection.
- Transaction rollback.
- Archive/replay consistency.
- Archived capsule integrity.

## Explicit limitations

Atomicity covers one local SQLite database.

It does not cover:

- separately exported files;
- external backups;
- independently stored checkpoint pins;
- multiple machines;
- distributed network consensus.

This implementation does not prove:

- historical freshness during later offline inspection;
- physical independence of signing devices;
- operator independence;
- Sybil resistance;
- accuracy of reported blockchain states;
- consensus validity;
- monetary supply correctness;
- independent security audit completion.

Concurrent malicious registry modification, compromised
operator keys, filesystem compromise, loss of the SQLite
database and an untrusted initial checkpoint pin remain
outside the solved threat model.

## Economic and legal boundary

No token is created.

No mainnet is activated.

No real rewards are issued.

No transferable units are created.

No wallet keys are accessed.

No economic, investment or legal-clearance claim is made.

## Tests

python3 -m unittest discover \
  -s tests \
  -p 'test_auneya_archive_v10.py' -v

python3 -m unittest discover \
  -s tests \
  -p 'test_auneya_archive_v09.py' -v

python3 -m unittest discover \
  -s tests \
  -p 'test_auneya_wvp_evidence_batch_v08.py' -v

The adversarial tests cover valid archival, duplicate replay,
injected precommit failure, signature tampering, incorrect
external pins, missing replay records and archive corruption.
