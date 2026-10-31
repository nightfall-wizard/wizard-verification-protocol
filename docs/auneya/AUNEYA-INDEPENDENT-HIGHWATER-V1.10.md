# AUNEYA/WVP v1.10: Independent High-Water Witness Research

Status: experimental Gate 3 research.
Not production.

## Security objective

A v1.9 Ed25519-signed replay checkpoint is not
independent retention by itself.

A local SQLite database and its local anchor can
be rolled back together.

v1.10 adds a separately pinned keeper identity
and a monotonic keeper state.

Every new v1.9 checkpoint receives an
Ed25519-authenticated witness receipt.

Receipts form a hash-linked sequence.

## Independent retention

The keeper SHOULD run on a separate physical
device and storage domain.

Local tests use separate directories on one
test machine.

This does not prove physical independence.

The implementation does not transmit files
or provision remote devices.

Checkpoints and receipts must be transferred
through a separately authenticated channel.

Public keys and their SHA-256 pins must be
authenticated independently.

Never commit private keys.

## Security properties

The keeper checks:

- Valid v1.9 anchor signature.
- Independently pinned anchor signer.
- Distinct witness signer identity.
- Valid witness signing key.
- Exact checkpoint sequence.
- Previous anchor linkage.
- Previous witness receipt linkage.
- Increasing message count.
- Nondecreasing peer replay tips.
- Existing keeper state consistency.
- External high-water receipt consistency.
- Private local file permissions.
- Canonical authenticated receipts.

A previously accepted checkpoint cannot
silently replace a newer accepted checkpoint
while the keeper's current state survives.

A restored keeper database is rejected when
the client presents a separately retained
newer receipt.

## First acceptance

The v1.9 checkpoint must be created first.

Run the keeper on its own private storage.

Example:

python3 tools/auneya/auneya_witness_v110.py accept \
  --store /private/keeper.sqlite \
  --anchor /private/anchor-1.json \
  --anchor-public /private/anchor-public.pem \
  --anchor-pin YOUR_INDEPENDENT_64_HEX_PIN \
  --witness-private /private/keeper-private.pem \
  --witness-public /private/keeper-public.pem \
  --witness-pin YOUR_KEEPER_64_HEX_PIN \
  --output /private/receipt-1.json

The example fingerprints are placeholders.

All directories must have permissions 0700.

All private files require permissions 0600.

## Subsequent acceptance

For every subsequent signed checkpoint:

- Use a new exclusive output filename.
- Provide the previous witness receipt.
- Preserve the outside high-water receipt.
- Never replace or rewrite the old receipt.

Additional argument:

--previous-receipt /private/receipt-1.json

## Independent verification

Use the verify command with:

--anchor
--receipt
--anchor-public
--anchor-pin
--witness-public
--witness-pin

Optionally supply:

--previous-receipt

The verification checks both cryptographic
signatures and their exact binding.

## Interrupted export recovery

The database transaction commits before
the signed receipt is exported.

If the export fails after commit, the
receipt can be recovered using:

python3 tools/auneya/auneya_witness_v110.py export \
  --store /private/keeper.sqlite \
  --chain auneya-research-v1 \
  --witness-public /private/keeper-public.pem \
  --witness-pin YOUR_KEEPER_64_HEX_PIN \
  --output /private/recovered.json

A separately retained current receipt can
be supplied with:

--expected-floor /private/last-receipt.json

This rejects a keeper database that is
older than the supplied outside receipt.

## Security limitations

A signed receipt is not proof of independent
physical-device operation.

A signed receipt is not proof that storage
cannot be rolled back.

A compromised witness signing key can
fabricate confirmations.

An adversary controlling both keeper storage
and the only retained receipt can roll back
both together.

Local signatures do not prove:

- Network-wide replay resistance.
- Physical witness independence.
- Trusted global time.
- Sybil resistance.
- Decentralized consensus.
- Finality.
- Remote availability.
- Immutable retention.
- Independent auditing.
- Production interoperability.

A crash between database commitment and
receipt export requires explicit recovery.

Never interpret a failed client request as
proof that no keeper state was committed.

## Roadmap status

Gate 3 remains PARTIALLY IMPLEMENTED.

Remaining:

- Real second-device validation.
- External retention verification.
- Remote outage tests.
- Ledger migration tests.
- Signing-key compromise recovery.
- Witness equivocation testing.
- Independent cryptographic review.
- Independent operational review.

No token issuance.

No real rewards.

No transferability.

No mainnet activation.

No independent security audit claimed.

No economic or legal approval claimed.
