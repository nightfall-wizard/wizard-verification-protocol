# WVP v0.3.0 Post-Release Verification

Status: published and post-release verified.

## Release

- Repository: `nightfall-wizard/wizard-verification-protocol`
- Tag: `v0.3.0`
- Source commit: `538460a967936b70792e4d275d50ee3b2a0b90c4`
- Release URL: https://github.com/nightfall-wizard/wizard-verification-protocol/releases/tag/v0.3.0

## Required release assets

- `wvp-release-check-v0.3.0-termux-android-aarch64`
- `wvp-release-check-v0.3.0-termux-android-aarch64.sha256`
- `wvp-release-check-v0.3.0-termux-android-aarch64.sig`
- `wvp-release-signing-public-rsa3072.pem`

## Verified hashes

- Asset SHA256: `e77aee158c8a3997c17d45dc51f9192839103b9eef0bf59cc3abb312b963e1fb`
- Checksum file SHA256: `9a41870b1946e3443a41f9dce3c9e5c1be75653c9d3e2517a2c09d9da717f861`
- Signature SHA256: `46cca5c071cdc7fe7f702fe89f261bc702b8de3fe5bd3a6da1856dfcb65dff07`
- Public key SHA256 fingerprint: `9a6e8ccbca7d75086d54c3d53bce8f48fd2abb506b26d98fd6803301dfa7a802`

## Verification commands

```bash
sha256sum -c wvp-release-check-v0.3.0-termux-android-aarch64.sha256
openssl dgst -sha256 -verify wvp-release-signing-public-rsa3072.pem -signature wvp-release-check-v0.3.0-termux-android-aarch64.sig wvp-release-check-v0.3.0-termux-android-aarch64
```

## Evidence boundary

The v0.3.0 release is published with checksum evidence, a detached signature, and a public verification key.

This does not prove:

- reproducible build;
- source-to-release correspondence;
- binary safety;
- audit result.
