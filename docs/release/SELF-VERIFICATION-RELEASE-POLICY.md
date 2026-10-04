# WVP Self-Verification Release Policy

## Purpose

WVP must be able to inspect its own public release artifacts.

## Rule

Every public WVP release should provide at least:

- a release tag
- at least one release asset
- a checksum asset
- explicit limitations

## Current State

WVP v0.1.0 provides checksum discovery but not signature verification.

## Limitation

A checksum asset is integrity metadata, not a security guarantee.

Missing signature material must remain visible as WARN until implemented.
