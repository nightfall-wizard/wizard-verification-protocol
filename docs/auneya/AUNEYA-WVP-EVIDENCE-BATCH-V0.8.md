# AUNEYA/WVP v0.8
## Pinned Multi-Witness Evidence Batch

Status: offline non-value research.

No token.
No mainnet activation.
No financial claim.
No consensus modification.

## Purpose

This capability extends the existing AUNEYA
v0.5, v0.6 and v0.7 verification stack.

It processes 2 to 16 independently keyed
operator-signed Nightfall status observations.

All observations must:

- reference one common valid challenge;
- use pre-enrolled identities;
- carry valid Ed25519 signatures;
- match the pinned chain context;
- pass existing freshness requirements;
- match one externally pinned registry state;
- use distinct operator identities;
- use distinct public-key fingerprints.

## Transactional replay protection

Verification must finish before the replay
ledger is updated.

The existing v0.5 SQLite transaction is used
to reject duplicate observations.

A failed verification must not partially
accept a batch.

## Conflict classification

Supported observation verdicts:

- MATCHING_SIGNED_TIP_CLAIMS
- CONFLICTING_SAME_HEIGHT_SIGNED_CLAIMS
- INCONSISTENT_SIGNED_CLAIMS
- DIVERGENT_SIGNED_CLAIMS_NOT_FORK_PROOF

These verdicts describe signed statements.

They do not establish which statement is true.

## Deterministic commitment

The evidence digest commits to:

- externally pinned checkpoint SHA-256;
- challenge SHA-256;
- sorted signed-receipt SHA-256 values.

Input argument ordering cannot alter the digest.

The JSON report itself is not digitally signed.
Original receipts and checkpoint evidence
must be retained for independent reproduction.

## WVP claim boundary

WVP may classify authenticated and pinned
operator statements as verified evidence
of those statements.

WVP must not transform them into claims of:

- verified consensus;
- independently verified chain selection;
- proven cumulative proof of work;
- verified confidential monetary supply;
- uncompromised operator software;
- physically independent devices;
- Sybil resistance;
- independent security audit.

## Research boundary

This is a read-only, offline verifier.

It does not connect to remote RPC endpoints.

It does not create or transfer value.

It does not access wallet private keys.

It does not activate an AUNEYA mainnet.

A corrupt initial checkpoint pin or compromised
operator signing keys can defeat the assumptions.

Local replay protection is not distributed.

The verifier cannot prove that different
public keys belong to independent people.

## Example

Run using an independently retained checkpoint
hash and existing signed receipt files:

python3 tools/auneya/auneya_wvp_evidence_batch_v08.py \
  --challenge challenge.json \
  --receipt operator-a.json \
  --receipt operator-b.json \
  --receipt operator-c.json \
  --registry registry.sqlite \
  --seal checkpoint.json \
  --expected-sha256 INDEPENDENT_PIN \
  --replay-db replay.sqlite

## Verification

python3 -m unittest discover \
  -s tests \
  -p test_auneya_wvp_evidence_batch_v08.py \
  -v

## Compatibility

This additive implementation reuses the existing
v0.5 challenge verification, v0.6 checkpoint and
v0.7 frozen registry snapshot.

Existing protocol formats remain unchanged.

No public economic functionality is introduced.
