# AUNEYA/WVP v0.9: Offline archival verification

Research only. No token or mainnet activation.

Captures 2-16 observations accepted by v0.8.

Stores:
- Original challenge.
- Original signed observations.
- Pinned registry checkpoint.
- Ed25519 public keys.
- Original v0.8 report.

Historical inspection verifies signatures and
recomputes the evidence commitment offline.

A separately retained checkpoint SHA-256 is required.

This proves neither observation truth nor
historical freshness, independent operators,
Sybil resistance or Nightfall consensus validity.

No custody, economic activation or wallet access.

Cross-file atomicity between replay-ledger updates
and capsule storage is not guaranteed.

Capture:

python3 tools/auneya/auneya_archive_v09.py capture \
  --challenge challenge.json \
  --receipt a.json \
  --receipt b.json \
  --registry registry.sqlite \
  --seal seal.json \
  --pin INDEPENDENT_SHA256 \
  --ledger replay.sqlite \
  --out capsule.json

Inspect:

python3 tools/auneya/auneya_archive_v09.py inspect \
  --capsule capsule.json \
  --pin INDEPENDENT_SHA256
