# WVP v0.3.0 Release Publication Guard

Status: guard prepared
Scope: `wvp-release-check` v0.3.0
Date: 2026-10-05

## Purpose

This document defines the release publication guard for the staged `wvp-release-check` v0.3.0 asset.

This guard does not create a signature.
This guard does not create a tag.
This guard does not create a GitHub release.
This guard does not expose private signing material.
This guard does not prove source-to-release correspondence.
This guard does not prove reproducible builds.
This guard does not prove binary safety.
This guard is not an audit.

## Guard Script

    ./scripts/release/guard-v030-release-publication.sh

## Evaluation Mode

Safe evaluation mode:

    ./scripts/release/guard-v030-release-publication.sh --evaluate

Evaluation mode writes:

    target/wvp-v0.3.0-release-publication-guard/PUBLICATION-GUARD-REPORT.json

Evaluation mode must not create:

- detached signature;
- `v0.3.0` tag;
- GitHub release.

## Required Ready Conditions

The guard may only approve release publication when:

- the source tree is clean;
- `HEAD` matches `origin/main`;
- no local `v0.3.0` tag exists;
- no remote `v0.3.0` tag exists;
- no GitHub `v0.3.0` release exists;
- the staged asset exists;
- the staged checksum exists;
- the staged checksum verifies;
- the detached signature exists;
- the detached signature verifies with the supplied public verification key;
- the staging manifest exists;
- the staging manifest source commit matches `HEAD`;
- the staging manifest says source tree dirty is `false`;
- the staging manifest says no tag was created;
- the staging manifest says no GitHub release was created;
- the staging manifest says staging-only is `true`.

## Require-Ready Mode

Strict release publication gate:

    ./scripts/release/guard-v030-release-publication.sh --require-ready

This mode exits non-zero unless all ready conditions pass.

## Boundary

No v0.3.0 tag is created by this document.
No GitHub release is created by this document.
No signature is created by this document.
No private signing material is committed by this document.

The guard prepares the final publication decision boundary, but signing, tagging and publishing remain separate explicit steps.
