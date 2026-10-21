# AUNEYA v0.7 — checkpoint-bound Nightfall observation verification

Status: additive local research tool. No new AUNEYA token, mainnet or WVP release.

## Gap resolved

The v0.5 signature verifier accepts whatever public keys currently exist in a local v0.4 SQLite registry. The separate v0.6 verifier can detect a changed or rolled-back registry using an independently retained checkpoint SHA-256. This tool composes both primitives: it accepts **only** observations signed by keys in a frozen registry snapshot exactly matching the externally pinned v0.6 seal.

## Exact trust boundary

1. Read an existing canonical v0.6 seal; compare its SHA-256 to the caller-supplied value kept independently of the device/registry.
2. Make a read-only consistent SQLite backup of the registry (including committed WAL pages); validate this frozen copy using v0.6 schema and key-fingerprint checks. Require exact match to seal contents.
3. Run **unchanged** v0.5 challenge/freshness/chain-context/Ed25519 verification against that private temporary copy. Optional two-operator comparison remains a comparison of *claims*, not chain validation or independence proof.
4. Recheck the live registry and then atomically consume the v0.5 replay ledger. Failures before recording must not consume receipts. The temporary copy is automatically removed.

## Use (Termux, installed Python/OpenSSL)

First create and **independently retain** a pin using the existing v0.6 `init` command. Never use a digest supplied by the registry's publisher as an independent trust anchor.

```sh
python3 tools/auneya/auneya_pinned_observation_v07.py \
  --challenge /private/challenge.json --receipt /private/operator-a.json \
  --registry /private/registry.sqlite --seal /private/checkpoint.json \
  --expected-sha256 YOUR_INDEPENDENTLY_RECORDED_SHA256 \
  --replay-db /private/auneya-v07-replay.sqlite
```

For comparison, add `--receipt-b /private/operator-b.json`. Never reuse the same receipt with a fresh replay DB as a way to claim freshness.

Tests: `python3 -m unittest discover -s tests -p 'test_auneya_pinned_observation_v07.py' -v`.

## Limitations

A corrupt initial pin, compromise of the separate anchor, forged source attestations, adversarial operator key custody, or collusion remain out of scope. The pre/post live-registry comparison is **not** an atomic lock held across separate applications; a malicious concurrent writer could change and restore state, though individual signatures are verified against a frozen pinned snapshot. The replay DB is mutable verifier-local state, not a distributed anti-replay service. This does not verify the Nightfall chain, fork selection, supply, node software, external audit, or true independence of operators. No wallet keys, mainnet mutation, external connections, token creation, market value or legal approval.

**Roadmap / Whitepaper:** supports independent reproducible operator evidence and explicit trust boundaries in the 28 September 2026 Nightfall Roadmap and the 18 September 2026 Whitepaper. It does not modify Nightfall consensus or the published WVP v0.5.0 and AUNEYA v0.4–0.6 implementations.
