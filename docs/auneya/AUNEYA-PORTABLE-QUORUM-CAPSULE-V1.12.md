# AUNEYA/WVP v1.12

## Portable Authenticated Quorum Evidence

Status: Experimental research.

Production readiness: Not established.

Economic activation: Disabled.

Independent audit: Not completed.

## Objective

AUNEYA v1.12 extends v1.11 with portable
authenticated quorum evidence.

Signed anchor and keeper evidence can be
serialized into a canonical bounded capsule.

An independent verifier must provide its
own separately pinned trust policy.

The exported capsule does not include
private signing keys or trusted identity
configuration.

## Security properties

- Canonical ASCII JSON.
- Exactly one LF-terminated JSON object.
- Strict duplicate-key rejection.
- Four MiB total resource limit.
- Bounded signed anchors.
- Maximum sixteen keeper receipts.
- Existing v1.11 Ed25519 verification.
- Quorum threshold enforcement.
- Signed predecessor verification.
- Deterministic evidence classification.
- Content-addressed capsule SHA256.
- No trusted filesystem paths from capsules.
- Atomic recipient-side high-water updates.
- Exclusive file locking.
- Durable fsync before success.
- Stale sequence rejection.
- Same-height conflicting anchor rejection.
- Trust-policy digest binding.
- No automatic overwriting of output.

## Export

Use an existing authenticated v1.11 bundle.

```sh
python3 tools/auneya/auneya_capsule_v112.py export \
  --trust /private/trust.json \
  --bundle /private/bundle-1.json \
  --output /private/exchange-1.json
```

For sequence greater than one, add:

`--previous /private/bundle-previous.json`

## Independent verification

The receiving Termux device must already
possess its own trusted signer policy.

```sh
mkdir -p "$HOME/.auneya-keeper"
chmod 700 "$HOME/.auneya-keeper"

python3 tools/auneya/auneya_capsule_v112.py verify \
  --trust "$HOME/.auneya-keeper/trust.json" \
  --capsule /private/exchange-1.json \
  --floor "$HOME/.auneya-keeper/floor.json"
```

The receiving device must receive the capsule
through an independently selected transfer method.

The software does not itself create a public
network service.

The floor must be stored outside the producer's
rollback domain to provide meaningful external
retention.

## Conformance

```sh
python3 -m unittest discover \
  -s tests \
  -p 'test_auneya_capsule_v112.py' \
  -v

python3 tools/readme_truth.py --check
```

## Security boundaries

This implementation does not prove:

- Independent physical devices.
- Independent human operators.
- Global latest checkpoints.
- Network-wide rollback immunity.
- External storage availability.
- Trusted global time.
- Sybil resistance.
- Distributed consensus.
- Public peer discovery.
- Production safety.
- Independent security auditing.
- Legal authorization.

No token is created.

No value is promised.

No mainnet is activated.

No economic mechanism is enabled.

The independent physical-device acceptance
gate remains open.
