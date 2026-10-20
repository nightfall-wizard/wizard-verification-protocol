# AUNEYA v0.6 — externally pinned identity-registry checkpoints

Status: local-research verification utility; no protocol or token release.

## Threat and capability

The existing v0.4 SQLite trusted-node registry validates individual public-key fingerprints and authorized lifecycle events. This optional WVP-style read-only verification step captures a **consistent SQLite snapshot** (including active WAL state), checks its table schema, node fingerprints, ordered enrollment/rotation/revocation event epochs, and produces a deterministic private checkpoint. Its SHA-256 must be copied to an independently trusted location. Later verification compares **both** the checkpoint's externally supplied digest and the live registry state. Advancing a checkpoint preserves the old event history, disallows epoch rollback, identity deletion, key changes without rotation, and revoked-key resurrection. Refuses to overwrite prior checkpoints.

## Run in Termux (Python 3 standard library)

```sh
python3 tools/auneya/auneya_registry_checkpoint_v06.py init --registry /private/path/registry.sqlite --out /private/path/checkpoint-001.json
# Record the printed CHECKPOINT_SHA256 somewhere independently trusted, offline.
python3 tools/auneya/auneya_registry_checkpoint_v06.py verify --registry /private/path/registry.sqlite --seal /private/path/checkpoint-001.json --expected-sha256 THE_RECORDED_64_CHARACTER_HASH
# Only AFTER a legitimate enrollment, rotation, or revocation:
python3 tools/auneya/auneya_registry_checkpoint_v06.py advance --registry /private/path/registry.sqlite --seal /private/path/checkpoint-001.json --expected-sha256 THE_RECORDED_64_CHARACTER_HASH --out /private/path/checkpoint-002.json
```

Old pins/checkpoints must be retained for an audit trail. Never accept a replacement hash supplied by the same compromised machine as independent evidence. Never commit a real registry, checkpoint, or operator IDs. Use a private directory: both inputs must be regular files with mode 0600. Run `python3 -m unittest discover -s tests -p 'test_auneya_registry_checkpoint_v06.py' -v` for eleven deterministic adversarial tests.

## Boundaries

This does not stop an adversary who controls the current registry, pins and checkpoint storage; it cannot certify a checkpoint initialized from an already compromised registry. Neither the event-digest fields nor this verifier reconstruct or cryptographically recheck all historical v0.4 Ed25519 signatures. Concurrent changes after the snapshot may occur; the wrapper does not lock external consumers or automatically gate v0.4/v0.5 calls. The file is a **local detection mechanism**, not a distributed transparency log, hardware monotonic counter, independent security audit, anti-Sybil proof, Nightfall consensus proof, balance proof, mainnet/token/transfer feature, or rollback prevention without external anchoring.

Roadmap alignment: verifiable evidence, recovery rehearsals and independent scrutiny with explicit failure and trust boundaries. Existing WVP v0.5 and AUNEYA v0.4/v0.5 code remain unchanged.
