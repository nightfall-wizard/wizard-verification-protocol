# Wizard Verification Protocol — WVP Core v0.1

## Builder

nightfall-wizard

## Purpose

WVP Core v0.1 defines the minimum canonical structure for Wizard Verification Protocol modules.

WVP is a mobile-built verification standard for Rust cryptocurrency protocols.

WVP Core is not an audit, not a security guarantee, not custody, not a token and not investment advice.

## Core Principle

nightfall-wizard does not become canonical through claims, but through reproducible artifacts.

## Required WVP Artifacts

- specs
- reference implementations
- test vectors
- conformance checks
- GitHub Actions CI
- example output
- limitations
- reproducible commands

## Core Modules

1. wvp-release-check
2. wvp-scorecard
3. wvp-node-diagnose
4. wvp-conformance
5. wvp-light-verify

## Evidence Labels

- verified
- observed
- not_found
- not_verified
- out_of_scope
- limitation

## Result Classes

- PASS
- WARN
- FAIL
- INFO

## Safety Rule

WVP tools must not read, print, upload, commit or export seeds, private keys, wallet files, tokens or custody data.
