# AUNEYA/WVP v1.5 — Temporal Evidence Admission

Status: additive offline/local research.

Not a token, economic or network release.

## Vision alignment

WVP verifies reproducible technical evidence.

AUNEYA is the proposed phone-first network for
witnessing lawful public digital claims.

This module adds a local admission security gate
on top of independently verified v1.4 evidence.

Existing v0.5-v1.4 formats remain unchanged.

## Security properties

1. Three independently supplied SHA-256 anchors.
2. Independent Node.js v1.4 signature verification.
3. Private filesystem permissions.
4. Maximum 8 MiB bundle budget.
5. Maximum 16 evidence capsules.
6. Strict challenge admission window.
7. Maximum observation age of 600 seconds.
8. Persistent SQLite replay protection.
9. Unique challenge and manifest identities.
10. Clock rollback detection.
11. Atomic ledger updates.
12. No silent ledger reset.
13. Fail-closed ledger capacity limit.
14. Regression tests with real Ed25519 evidence.

## CLI

Run against a genuine v1.2 evidence bundle:

    python3 tools/auneya/auneya_admission_v15.py admit \
      --bundle PRIVATE_V12_BUNDLE \
      --pin INDEPENDENT_CHECKPOINT_SHA256 \
      --challenge-sha256 INDEPENDENT_CHALLENGE_SHA256 \
      --expected-manifest-sha256 INDEPENDENT_MANIFEST_SHA256 \
      --ledger PRIVATE_DIR/auneya-admission.sqlite

The ledger parent directory must have private
0700 permissions.

The evidence must remain private.

The three hashes must originate from independently
trusted sources.

## Successful result

LOCALLY_ADMITTED_ONCE

The result confirms only that the signed,
pinned evidence passed this local policy.

It does not prove the truth of observations.

## Failure behavior

The verifier rejects:

- Invalid signatures.
- Incorrect trusted pins.
- Modified evidence.
- Expired challenges.
- Future challenges outside the allowed skew.
- Stale observations.
- Duplicate challenges.
- Duplicate manifests.
- Local clock rollback.
- Excessive bundle size.
- Unsafe ledger permissions.
- Unsafe symlink inputs.
- Exhausted replay-ledger capacity.

## Limitations

The local clock is not a trusted time source.

The ledger is not a distributed transparency log.

A storage-controlling attacker may roll back local
state unless it is externally anchored.

This is not network-wide replay protection.

Signatures authenticate statements but cannot
establish whether the statements are true.

No independent devices, Sybil resistance,
historical freshness, blockchain consensus,
actual monetary correctness or independent
audit are proven.

Protection against all filesystem races is
not established.

No wallet, transferable value, token, real
reward or mainnet activation is introduced.

## Next roadmap gates

1. Authenticated, bounded peer transport.
2. Externally anchored replay epochs.
3. Stronger trusted-time policies.
4. Adversarial multi-device experiments.
5. Independent operators and external reviewers.
6. Privacy and threat-model review.
7. Versioned formal AUNEYA whitepaper.
8. Reproducible public acceptance evidence.
9. Independent security audit.
10. Explicit governance and release decisions.

The project must not claim these gates are
complete merely because this module exists.

## Tests

    python3 -m unittest discover \
      -s tests \
      -p 'test_auneya_admission_v15.py' -v

The suite is also integrated into WVP
Required Checks.
