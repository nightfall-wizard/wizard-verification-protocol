# WVP Signature Tooling Capability

## Purpose

WVP v0.2 adds real release-signature verification.

The goal is to verify not only byte integrity through SHA256 checksums, but also release authenticity through detached cryptographic signatures.

## Current local capability

Selected signature path:

`openssl-rsa-sha256`

Detected tools:

- openssl: /data/data/com.termux/files/usr/bin/openssl
- gpg: not-found
- minisign: not-found
- ssh-keygen: /data/data/com.termux/files/usr/bin/ssh-keygen

## Required safety rule

Private signing keys must never be committed to this repository.

Private signing keys must never be printed into CI logs.

Private signing keys must never be uploaded as release assets.

Only public verification material may be committed.

## WVP v0.2 target

WVP v0.2 should add:

- public release verification key
- detached release signature asset
- signature asset discovery
- signature verification execution
- JSON fields for signature verification result
- status upgrade rules

## Intended status logic

- checksum failed: FAIL
- signature failed: FAIL
- checksum passed but signature missing: WARN
- checksum passed and signature passed: eligible for INFO
- signature tool unavailable: WARN or FAIL depending on context

## Current state

WVP v0.1.1 has checksum verification only.

WVP v0.2 starts here.
