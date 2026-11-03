# Gate 3: real-device acceptance contract

**OPEN: not yet independently demonstrated.**

1. Operate producer and recipient on two truly separate physical devices, with recipient-controlled trust pins and storage.
2. Transfer an authenticated v1.12 capsule from the v1.11 quorum and independently verify it against the recipient high-water floor.
3. Attack stale replay, forged signatures, bad pins, insufficient quorum, same-height conflicts and producer rollback; keep recipient state intact.
4. Record actual commit IDs, hashes, device separation, expected and observed verdicts, and sanitized logs for independent review.

Local Termux tests and multiple signing keys cannot prove independent physical storage. Gate 3 remains partial; Gates 4/5 open; Gate 6 blocked. No economic activation.

[Independent governance](../PROJECT-INDEPENDENCE.md).

## v1.15 Cross-Language Verification Requirement

A real Gate 3 acceptance experiment must use
genuinely separate physical devices and independently
controlled recipient trust and storage.

The recipient must verify the complete v1.12 quorum
and maintain its durable high-water floor.

The v1.15 Node.js verifier provides an additional,
independently implemented v1.13 ACK signature check.

The externally supplied expected ACK SHA-256 must
be retained outside the producer rollback domain.

Record actual device separation, immutable source
commit IDs, transferred artifacts, observed verdicts
and sanitized logs.

Simulated devices and test signing keys cannot
establish independent physical-device acceptance.

Independent review remains required.
