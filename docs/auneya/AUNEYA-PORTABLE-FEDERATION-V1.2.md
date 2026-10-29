# AUNEYA/WVP v1.2 — Portable Offline Federation Verification

Status: additive offline non-value research.

This is not a mainnet or distributed consensus protocol.

## What this adds

A v1.1 SQLite federation can be exported as a private
directory containing canonical v0.9 evidence capsules
and one canonical v1.2 manifest.

The manifest includes:

- canonical capsule hashes
- capsule lengths
- complete v1.1 reconciliation report
- explicit security limitations

Export independently re-verifies the evidence.

A second device can reproduce the same report without
the originating SQLite database.

This requires independently retained SHA-256 pins for:

- the registry checkpoint
- the original challenge
- the exported manifest

## Export

python3 tools/auneya/auneya_portable_v12.py export \
  --store private-federation.sqlite \
  --pin INDEPENDENT_CHECKPOINT_SHA256 \
  --challenge-sha256 ORIGINAL_CHALLENGE_SHA256 \
  --out private-export-directory

## Verify

python3 tools/auneya/auneya_portable_v12.py verify \
  --bundle private-export-directory \
  --pin INDEPENDENT_CHECKPOINT_SHA256 \
  --challenge-sha256 ORIGINAL_CHALLENGE_SHA256 \
  --expected-manifest-sha256 INDEPENDENTLY_RETAINED_MANIFEST_SHA256

The manifest SHA-256 is printed during export.

Record it using a separately trusted channel.

Copying the bundle and its digest from the same
compromised device does not create independent trust.

## Storage boundaries

Private directories require mode 0700.

Included files require mode 0600.

Output paths must not already exist.

Preserve the original federation database,
checkpoint and challenge evidence.

Private evidence bundles must not be committed to Git.

## Security properties

- Existing v1.1 signature validation is reused.
- Existing v0.9 evidence validation is reused.
- Manifest and capsule hashes are checked.
- Canonical JSON is required.
- Undeclared files are rejected.
- Symlink inputs are rejected.
- Altered bytes are rejected.
- Missing capsules are rejected.
- Duplicate references are rejected.
- Forged report summaries are rejected.
- Database export uses one consistent SQLite snapshot.
- Export does not intentionally modify the database.

## Trust limitations

A matching digest proves byte identity relative
to an independently trusted digest.

It does not prove actual observation truth.

This implementation does not prove:

- independent devices
- independent people
- Sybil resistance
- historical freshness
- Nightfall consensus
- actual blockchain ownership
- independent implementation diversity
- absence of filesystem compromise

It is not an audit or security certification.

It does not activate a network or mainnet.

It creates no token, reward or transferable value.

It does not grant legal clearance.

## Next engineering gates

1. Independent second-language verifier and
   differential interoperability suite.

2. Signed transport acknowledgments, replay expiry,
   denial-of-service budgets and adversarial P2P tests.

3. Independent external review and long-running
   multi-device experiments before any live network.

## Testing

python3 -m unittest discover \
  -s tests \
  -p 'test_auneya_portable_v12.py' -v

Existing v0.8 through v1.1 regression tests
remain mandatory.
