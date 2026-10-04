# WVP v0.2 Release Checklist

## Pre-release checks

- [ ] Repository is clean.
- [ ] Main branch is synced with origin.
- [ ] Private signing key exists outside the repository.
- [ ] Public verification key exists in the repository.
- [ ] Public key fingerprint conformance passes.
- [ ] No private signing material is committed.
- [ ] `cargo fmt --all -- --check` passes.
- [ ] `cargo clippy --workspace --all-targets -- -D warnings` passes.
- [ ] `cargo test --workspace --locked` passes.

## Conformance checks

- [ ] Release-check smoke conformance passes.
- [ ] Live GitHub metadata smoke conformance passes.
- [ ] Self-release checksum conformance passes.
- [ ] Self-release signature conformance passes.
- [ ] Signature verified policy conformance passes.
- [ ] No-secret signing material conformance passes.
- [ ] Signature tooling capability conformance passes.
- [ ] Signature status model conformance passes.
- [ ] Public release verification key conformance passes.
- [ ] Signature asset matching conformance passes.
- [ ] Signature tamper-negative conformance passes.

## Release build steps

- [ ] Bump package version to `0.2.0`.
- [ ] Build release binary.
- [ ] Generate `.sha256` checksum asset.
- [ ] Generate detached `.sig` signature asset.
- [ ] Verify checksum locally.
- [ ] Verify detached signature locally.
- [ ] Create GitHub release tag `v0.2.0`.
- [ ] Upload binary.
- [ ] Upload `.sha256`.
- [ ] Upload `.sig`.

## Post-release checks

- [ ] Download published binary.
- [ ] Download published `.sha256`.
- [ ] Download published `.sig`.
- [ ] Verify published checksum.
- [ ] Verify published detached signature.
- [ ] Run `wvp-release-check --target nightfall-wizard/wizard-verification-protocol --json --live`.
- [ ] Confirm status is `INFO`.
- [ ] Confirm `checksum_verification_passed` is `true`.
- [ ] Confirm `signature_verification_passed` is `true`.
- [ ] Confirm `signature_verification_error` is `null`.
- [ ] Confirm CI passes on the release-preparation commit.

## Release notes must say

- This is not an audit.
- This does not prove reproducible builds.
- This does not prove binary safety.
- This verifies release checksum and detached signature integrity.
- Private signing material is not included.
- Public verification material is included.

## Stop conditions

Stop the release if any of the following occurs:

- repository is dirty unexpectedly
- private key path is inside the repository
- private key material is detected in staged files
- checksum verification fails
- signature verification fails
- CI fails
- more than one `.sha256` asset is present
- more than one `.sig` asset is present
