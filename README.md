# Wizard Verification Protocol — WVP

Built by nightfall-wizard.

## Category

Proof-of-Project-Reality

## Core Sentence

Wizard Verification Protocol turns project claims into verifiable reality.

## Adversarial Principle

No claim without proof. No proof without reproduction. No verification without adversarial testing.

## Purpose

WVP is a mobile-built, zero-budget verification standard for checking whether crypto and open-source projects are technically, organizationally and economically real.

## Schelling Point Goal

When someone wants to verify whether a project is real, they should think of WVP.

Without WVP, a project check is incomplete.

## Current Status

Bootstrap implementation in progress.

## Current Modules

- wvp-release-check
- wvp-scorecard
- wvp-node-diagnose
- wvp-conformance
- wvp-light-verify

<!-- WVP:ANDROID-VS-CI-CONFORMANCE:START -->
## Android vs CI Build Provenance Conformance

WVP includes a local, authenticated Android-vs-CI conformance command:

    ./conformance/release-check-android-vs-ci-build-provenance.sh

This command downloads the GitHub Actions build-provenance artifact for the checked-out commit, generates a fresh Android-Termux artifact locally, compares both artifacts, and validates that the result stays within the correct claim boundary.

It verifies:

- same source commit;
- same package version;
- same Cargo.lock hash;
- Android-Termux and GitHub Actions are separate environment classes;
- cross-architecture binary differences are not treated as failure;
- no reproducible-build claim is made.

It does not prove:

- binary safety;
- source-to-release correspondence;
- full reproducible builds;
- audit status.
<!-- WVP:ANDROID-VS-CI-CONFORMANCE:END -->

