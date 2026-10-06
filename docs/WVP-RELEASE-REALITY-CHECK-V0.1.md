<!-- WVP:RELEASE-REALITY-CHECK -->

# WVP Release-Reality Check v0.1

## Purpose

WVP Release-Reality Check v0.1 records public GitHub evidence for one repository release.

It answers one narrow question: which release-related claims are supported by public repository and release artifacts, and which claims remain not proven.

## Scope

The checker records repository existence, default branch, public release presence, release tag reference presence, release asset count and names, checksum asset presence, signature asset presence, SECURITY.md presence, README presence, license file presence and GitHub Actions workflow presence.

## Explicit non-claims

This tool does not prove protocol security, binary safety, legal clearance, investment quality, custody safety, external audit status, checksum correctness, cryptographic signature validity, source-to-binary correspondence or reproducible builds.

If a claim is not actually verified, the output must say not_proven, not_verifiable or not_enough_evidence.

## Usage

Run:

    tools/wvp-release-reality-check.sh owner/repo --out report.json

Example:

    tools/wvp-release-reality-check.sh nightfall-wizard/wizard-verification-protocol --out reports/release-reality/self.json

## Legal and safety boundary

The tool must not read, request, print, upload or commit seeds, private keys, wallet files, passwords, access tokens, API keys, custody data or user funds data.

It uses GitHub public/API metadata available to the authenticated GitHub CLI session. It must not print authentication material.

## v0.1 design rule

Small, verifiable, narrow.

The tool is intentionally not a general project rating, audit tool, investment screen, custody analyzer or legal review system.
