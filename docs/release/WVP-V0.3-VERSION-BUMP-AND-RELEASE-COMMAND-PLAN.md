# WVP v0.3 Version Bump and Release Command Plan

Status: draft command plan  
Scope: `wvp-release-check` v0.3 release preparation  
Date: 2026-10-05

## Purpose

This document defines the planned version bump and release commands for WVP v0.3.

It is not a release execution log.  
It is not a tag.  
It is not a published release.  
It is not a source-to-release proof.  
It is not a reproducible-build proof.  
It is not an audit.

## Planned Version

Planned release tag:

    v0.3.0

Planned package version:

    0.3.0

Current pre-bump package version:

    0.2.0

## Planned Version Bump File

Primary version file:

    reference/rust/wvp-release-check/Cargo.toml

Required change:

    version = "0.2.0"

to:

    version = "0.3.0"

## Pre-Bump Verification Commands

Before applying the version bump:

    git status --short --branch
    cargo fmt --manifest-path reference/rust/wvp-release-check/Cargo.toml -- --check
    cargo clippy --manifest-path reference/rust/wvp-release-check/Cargo.toml -- -D warnings
    cargo test --manifest-path reference/rust/wvp-release-check/Cargo.toml
    ./conformance/release-check-v030-readiness-checklist.sh
    ./conformance/release-check-v030-release-docs.sh

## Planned Build Command

After the version bump commit:

    cargo build --release --locked --manifest-path reference/rust/wvp-release-check/Cargo.toml

## Planned Release Directory

Expected local release staging directory:

    target/wvp-release-v0.3.0

## Planned Android-Termux Asset Name

Expected binary asset:

    wvp-release-check-v0.3.0-termux-android-aarch64

Expected checksum asset:

    wvp-release-check-v0.3.0-termux-android-aarch64.sha256

Expected signature asset:

    wvp-release-check-v0.3.0-termux-android-aarch64.sig

## Planned Asset Staging Commands

After building:

    mkdir -p target/wvp-release-v0.3.0
    cp -f reference/rust/wvp-release-check/target/release/wvp-release-check target/wvp-release-v0.3.0/wvp-release-check-v0.3.0-termux-android-aarch64
    cd target/wvp-release-v0.3.0
    sha256sum wvp-release-check-v0.3.0-termux-android-aarch64 > wvp-release-check-v0.3.0-termux-android-aarch64.sha256

## Planned Signature Command

Signature creation requires private signing material.

Private signing material must not be committed.  
Private signing material must not be copied into the repository.  
Private signing material must not be printed into logs.

Planned command shape:

    openssl dgst -sha256 -sign <private-key-file-outside-repo> -out wvp-release-check-v0.3.0-termux-android-aarch64.sig wvp-release-check-v0.3.0-termux-android-aarch64

## Planned Public Verification Commands

Checksum verification:

    sha256sum -c wvp-release-check-v0.3.0-termux-android-aarch64.sha256

Signature verification:

    openssl dgst -sha256 -verify <public-key-file> -signature wvp-release-check-v0.3.0-termux-android-aarch64.sig wvp-release-check-v0.3.0-termux-android-aarch64

## Planned Tag Command

Only after all checks pass:

    git tag -a v0.3.0 -m "WVP v0.3.0"
    git push origin v0.3.0

## Planned GitHub Release Command Shape

Only after tag creation and final local verification:

    gh release create v0.3.0 \
      target/wvp-release-v0.3.0/wvp-release-check-v0.3.0-termux-android-aarch64 \
      target/wvp-release-v0.3.0/wvp-release-check-v0.3.0-termux-android-aarch64.sha256 \
      target/wvp-release-v0.3.0/wvp-release-check-v0.3.0-termux-android-aarch64.sig \
      --repo nightfall-wizard/wizard-verification-protocol \
      --title "WVP v0.3.0" \
      --notes-file docs/release/WVP-V0.3-RELEASE-NOTES-DRAFT.md

## Planned Post-Release Verification

After publishing:

    ./target/release/wvp-release-check --target nightfall-wizard/wizard-verification-protocol --json

Expected post-release checks:

- release exists;
- tag exists;
- binary asset exists;
- checksum asset exists;
- signature asset exists;
- checksum verification passes;
- signature verification passes;
- no private signing material is tracked;
- no audit claim is made;
- no binary-safety claim is made;
- no full reproducible-build claim is made;
- no source-to-release-proof claim is made unless separately proven.

## Explicit Non-Claims

This plan must not claim:

- that v0.3.0 has already been released;
- that the release binary is safe;
- that the release asset was built from source;
- that full reproducible builds are proven;
- that the project has been audited;
- that any third-party cryptocurrency project is secure.

## Current Status

Draft only.  
No v0.3.0 release has been published by this document.  
No tag is created by this document.  
No signature is created by this document.
