# AUNEYA v1.18 — offline Gate 4 dual-verification evidence contract

**Scope:** Independently reproducible research evidence; not a live network.

The v1.18 CLI re-executes the existing v1.17 Python+Node dual full-quorum
verification, enforces exact report fields and typed non-claims, and produces
one bounded canonical ASCII JSON artifact.

An exact JSON Schema 2020-12 contract is published at:

`schemas/auneya-gate4-evidence-v1.18.schema.json`

The artifact commits to its schema bytes, underlying dual report, the expected
capsule digest and an independently configured trust file digest.

Cryptographic verification occurs before generating or accepting the artifact.

## Termux / offline

First obtain the v1.12 capsule, private mode-0600 trust configuration and
expected capsule SHA-256 from independently controlled sources.

Never treat a digest delivered with the same untrusted capsule as an
independent anti-rollback anchor.

```sh
mkdir -p "$HOME/.auneya-gate4"
chmod 700 "$HOME/.auneya-gate4"

python3 tools/auneya/auneya_gate4_bundle_v118.py create \
  --trust "$HOME/.auneya-keeper/trust.json" \
  --capsule "$HOME/.auneya-keeper/capsule.json" \
  --expected "$INDEPENDENT_CAPSULE_SHA256" \
  --output "$HOME/.auneya-gate4/evidence.json"

python3 tools/auneya/auneya_gate4_bundle_v118.py verify \
  --trust "$HOME/.auneya-keeper/trust.json" \
  --capsule "$HOME/.auneya-keeper/capsule.json" \
  --expected "$INDEPENDENT_CAPSULE_SHA256" \
  --input "$HOME/.auneya-gate4/evidence.json"
```

`create` fails if the output already exists.

`verify` re-executes both cryptographic implementations and compares the
complete byte-for-byte artifact.

It never accepts a report purely because its own hashes look consistent.

The schema is a consumer contract, not an audit certificate or normative
consensus protocol.

All output is unsigned; subsequent edits are detectable only by
re-verification or independently trusted external retention.

## Reproduction and adversarial regression

```sh
python3 -m unittest discover \
  -s tests \
  -p 'test_auneya_gate4_bundle_v118.py' \
  -v

python3 tools/readme_truth.py --check
```

Tests exercise valid two-keeper Ed25519 quorum artifacts,
deterministic output, exclusive private writes, re-verification,
forged status, wrong external hash, duplicate JSON keys,
symlinks, noncanonical bytes and resource limits.

## Unmet acceptance criteria

Gate 3 is still partial.

Two genuinely separate physical devices, independent recipient-controlled
pins/storage, adversarial producer rollback and recorded recovery must
be demonstrated, with external review.

Gate 4 gains a machine-readable contract, but independent reproduction
and a formal protocol-level normative schema remain incomplete.

Gates 5 and 6 remain blocked.

No token, economy, public mainnet, audit, physical independence,
trusted time, network consensus or release is created by this step.
