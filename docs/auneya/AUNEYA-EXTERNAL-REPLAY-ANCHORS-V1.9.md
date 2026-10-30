# AUNEYA/WVP v1.9 — Signed External Replay State Checkpoints

Status: local research sub-step toward Gate 3.

This is not a completed external witness network.

## Security goal

AUNEYA v1.6 stores counters and accepted evidence in local SQLite.

Restoring an older SQLite file can also restore older counters.

AUNEYA v1.8 authenticated acknowledgments do not detect that attack.

Version 1.9 adds signed, canonical, state-complete checkpoints.

The operator must independently retain the latest signed checkpoint
and the signer's SHA-256 public-key pin outside the device/storage
rollback domain.

A file stored beside the local SQLite database is NOT external anchoring.

## Snapshot semantics

Format:

auneya-external-replay-anchor-v1.9

Each snapshot commits to:

- one research chain_id
- all ordered v1.6 replay messages for that chain
- all current peer tips
- message count
- signer SHA-256 pin
- predecessor checkpoint hash
- monotonic checkpoint sequence

Hash:

SHA-256 over canonical ASCII JSON.

Signature:

Ed25519.

Domain:

AUNEYA/WVP:EXTERNAL-ANCHOR:V1.9 followed by NUL.

The signing key is operator-controlled.

A signing key does not establish physical-device uniqueness.

## Verification

Read-only inspection checks SQLite integrity and contiguous sender history.

Fresh checkpoints require:

- complete previously anchored message history
- nondecreasing peer tips
- strictly increasing message count
- valid previous checkpoint
- valid signer pin
- valid Ed25519 signature

Old outputs cannot be overwritten.

Signed checkpoint verification requires an exact match
with the present database.

After new admissions, create and independently retain
a newer checkpoint before relying on the new state.

## External-trust boundary

A successfully signed file does not prove external storage.

The verifier reports:

externally_retained_proven: false

Independent storage, out-of-band pin distribution and
trusted latest-checkpoint selection remain operational requirements.

## Termux CLI

Use an existing v1.6 replay ledger and operator-provided
PEM keys.

Private directories require permissions 0700.

Private key and checkpoint files require permissions 0600.

Never commit private keys.

Capture:

    python3 tools/auneya/auneya_anchor_v19.py capture \
      --ledger /private/replay.sqlite \
      --chain auneya-research-v1 \
      --private /private/anchor-private.pem \
      --public /private/anchor-public.pem \
      --pin 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef \
      --output /private/anchor-0001.json

Verify:

    python3 tools/auneya/auneya_anchor_v19.py verify \
      --ledger /private/replay.sqlite \
      --public /private/anchor-public.pem \
      --pin 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef \
      --anchor /private/anchor-0001.json

For subsequent captures, provide:

    --previous /private/anchor-0001.json

Choose a new exclusive output path.

The example pin is NOT a real pin.

The actual public-key fingerprint must be independently authenticated.

## Tested failure classes

- Signature forgery
- Incorrect signer pin
- Modified checkpoint body
- Duplicate JSON fields
- Database truncation
- Restoration of earlier SQLite state
- Modified evidence history
- Noncontiguous counters
- Invalid checkpoint chain
- Accidental checkpoint overwrite
- New witnesses added after existing checkpoints

Tests use real Ed25519 keys and SQLite transactions.

## Explicit limitations

This implementation is not integrated into
public peer transport or automatic v1.8 admission.

Checkpoint export and independent retention require
an operator workflow.

An attacker controlling both the database and the
only retained anchor may restore both.

A compromised signing key can counterfeit checkpoints.

This implementation does not prove:

- trusted global time
- independent physical devices
- external witness availability
- Sybil resistance
- network consensus
- finality
- privacy compliance
- legal approval
- independent audit
- production readiness
- mainnet activation
- token issuance
- real rewards

## Next engineering milestone

Implement authenticated independent checkpoint storage
with external anti-rollback high-water marks.

Add:

- recovery tests
- ledger migration tests
- independent second-device validation
- adversarial outage testing
- signing-key compromise recovery
- external witness consistency checks

Gate 3 must not be declared complete until
those requirements have been independently validated.
