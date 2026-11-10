# AUNEYA v1.19 — Adversarial dual-runtime capsule conformance

Status: experimental, non-value, offline research. No published v1.19 release.

## Contribution

v1.18 creates and re-verifies canonical schema-bound evidence after independent
Python and Node.js Ed25519 quorum verification. v1.19 adds a deterministic,
15-vector adversarial campaign against the actual v1.12 signed capsule verifier.

Each mutant is checked twice: by the existing Python quorum verifier and the
separately implemented Node.js full-quorum verifier. The mutant SHA-256 is
recomputed before calling Node, deliberately eliminating the trivial external
hash-mismatch defense so signature, pin, framing, quorum and commitment rules
must reject the attack. **Both implementations must return an explicit reject.**
An unexpected acceptance, runtime disagreement, or Node crash fails the run.

The report commits to the original v1.18 evidence bundle and records SHA-256s
of each mutant, deterministic names and exact rejection verdicts. Inputs are
rechecked against the original bytes after testing, and the tool never modifies
the original trust file, capsule or high-water floor. Optional output must be a
new file in a private 0700 directory and is written with 0600 permissions.

## Reproduction in Termux

With a real capsule and an independently supplied expected capsule hash:

```sh
mkdir -p "$HOME/.auneya-v119"
chmod 700 "$HOME/.auneya-v119"
python3 tools/auneya/auneya_gate4_adversarial_v119.py \
  --trust "$HOME/.auneya-keeper/trust.json" \
  --capsule "$HOME/.auneya-keeper/capsule.json" \
  --expected "$INDEPENDENT_CAPSULE_SHA256" \
  --output "$HOME/.auneya-v119/campaign.json"
```

For fully local, generated **test-only** Ed25519 evidence:

```sh
python3 -m unittest discover -s tests -p 'test_auneya_gate4_adversarial_v119.py' -v
python3 tools/readme_truth.py --check
```

The fixed campaign includes tampered envelope metadata, quorum/report hashes,
removed and duplicated keepers, wrong keeper pin, forged anchor/keeper signed
bodies and signatures, a duplicate JSON key, noncanonical framing and
truncation. No private key material is placed in the output report.

## Boundaries and missing acceptance

Two implementations **on one phone** are not two independent witnesses.
No physical-device separation, trusted time, external immutable retention,
public network, economic activity, token, mainnet, complete formal normative
protocol, independent audit or legal clearance is established by these tests.

Gate 3 remains partial until actual independently controlled physical devices
run rollback, outage and recovery trials and preserve authenticated logs.
Gate 4 remains incomplete pending normative wire schemas, external reproducible
replication and independent review. Gates 5 and 6 remain blocked.
