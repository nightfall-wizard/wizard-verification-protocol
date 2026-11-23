# AUNEYA v1.24 — compact Merkle consistency (offline research)

**Status:** experimental, non-value, non-normative; no network or economy.

## Problem and implementation

v1.23 proves membership using an externally pinned Merkle root but compares
old/new full journals for prefix consistency. v1.24 adds the RFC 9162
section 2.1.4 compact Merkle consistency proof to the **same** domain-separated
SHA-256 tree (`0x00` leaves, `0x01` branches), without altering v1.23 data.

- A valid v1.23 journal generates a minimal proof for old size `m` and new
  size `n`, `1 <= m <= n <= 256`; proof is at most nine hashes.
- Python generates and verifies it; a separate read-only Node.js implementation
  verifies independently using only the proof and separately pinned heads.
- Both readers reject size/root mismatch, fork, truncated or reordered paths,
  duplicate or noncanonical JSON, oversized proofs and equal-size equivocation.
- Proofs are private canonical JSON; new files are exclusive in mode 0600
  under existing private (0700) directories.
- A proof conveys append-only **hash continuity**, not underlying claim truth.

## Termux operation

First initialize and fill an actual v1.23 journal by following
[AUNEYA-TRANSPARENCY-V1.23.md](AUNEYA-TRANSPARENCY-V1.23.md). In a separately
trusted medium **retain old size and root before the journal grows**.
For a journal with a previously known old root:

~~~sh
python3 tools/auneya/auneya_consistency_v124.py prove \
  --journal "$HOME/.auneya-transparency/journal.json" \
  --old-size "$OLD_SIZE" --expected-old-root "$OLD_ROOT" \
  --out "$HOME/.auneya-transparency/consistency.json"

python3 tools/auneya/auneya_consistency_v124.py verify \
  --proof "$HOME/.auneya-transparency/consistency.json" \
  --expected-old-root "$OLD_ROOT" --expected-new-root "$NEW_ROOT" \
  --expected-old-size "$OLD_SIZE" --expected-new-size "$NEW_SIZE"

node tools/auneya/auneya_consistency_v124.js \
  --proof "$HOME/.auneya-transparency/consistency.json" \
  --expected-old-root "$OLD_ROOT" --expected-new-root "$NEW_ROOT" \
  --expected-old-size "$OLD_SIZE" --expected-new-size "$NEW_SIZE"
~~~

For verification, all four expected values MUST be supplied from an
independently controlled and previously retained source, not trusted simply
because they accompany the proof. The producing phone cannot attest to
physical separation or independent storage. Rollback of both the journal and
its pins remains possible within a shared compromise/rollback domain.

## Security and project acceptance boundaries

Real Gate 3 still needs two actually separate devices, independently managed
anchors and trust, outage/rollback/recovery measurements, adversarial peer
experiments and external review. Gate 3 remains PARTIAL, Gate 4 INCOMPLETE,
Gate 5 NOT COMPLETED, Gate 6 BLOCKED. The whitepaper is a research draft.
No mainnet, real token, transferability, audit, consensus or legal approval.

Repeat with `python3 -m unittest discover -s tests -p
"test_auneya_consistency_v124.py" -v` and
`python3 tools/readme_truth.py --check`.
