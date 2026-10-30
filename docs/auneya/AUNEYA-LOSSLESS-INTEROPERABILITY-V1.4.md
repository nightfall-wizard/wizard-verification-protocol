# AUNEYA/WVP v1.4 — Lossless independent verification

Status: offline, non-value research only; not a protocol release.

## Previously documented gap
The v1.3 independent Node.js verifier uses JSON.parse, which cannot
exactly represent all unsigned 64-bit Python observations.

## v1.4
- Additive parser for canonical JSON with lossless BigInt representation.
- Duplicate-key, malformed UTF-8, float, trailing-token and size rejection.
- Correct comparison and signature canonicalization beyond 2^53-1.
- Differential Python/OpenSSL/Node.js tests on real signed evidence.
- Re-run v1.3 adversarial verification cases against the v1.4 implementation.
- Existing v1.3 code and old evidence formats remain unchanged.

## CLI
Run the v1.4 CLI with an existing private v1.2 evidence export and
three independently trusted SHA-256 anchors:

    node tools/auneya/auneya_independent_v14.js verify \
      --bundle PRIVATE_DIRECTORY \
      --pin INDEPENDENT_CHECKPOINT_SHA256 \
      --challenge-sha256 INDEPENDENT_CHALLENGE_SHA256 \
      --expected-manifest-sha256 INDEPENDENT_MANIFEST_SHA256

## Safety limitations
Signatures authenticate statements, not the truth of observations.
No Sybil resistance, human/device independence, historical freshness,
Nightfall consensus, independent audit, mainnet readiness or protection
against all filesystem races is proven. No token, wallet, transferable
value, real reward or mainnet activity is created.

## Next gates
Authenticated transport, replay expiration, resource budgets,
adversarial multi-device experiments and independent external review.
