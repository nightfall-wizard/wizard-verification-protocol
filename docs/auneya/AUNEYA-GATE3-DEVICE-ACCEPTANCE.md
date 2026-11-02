# Gate 3: real-device acceptance contract

**OPEN: not yet independently demonstrated.**

1. Operate producer and recipient on two truly separate physical devices, with recipient-controlled trust pins and storage.
2. Transfer an authenticated v1.12 capsule from the v1.11 quorum and independently verify it against the recipient high-water floor.
3. Attack stale replay, forged signatures, bad pins, insufficient quorum, same-height conflicts and producer rollback; keep recipient state intact.
4. Record actual commit IDs, hashes, device separation, expected and observed verdicts, and sanitized logs for independent review.

Local Termux tests and multiple signing keys cannot prove independent physical storage. Gate 3 remains partial; Gates 4/5 open; Gate 6 blocked. No economic activation.

[Independent governance](../PROJECT-INDEPENDENCE.md).
