# WVP v0.3.0 Local Signing Execution Guard

Status: guard prepared
Scope: `wvp-release-check` v0.3.0
Date: 2026-10-05

## Purpose

This document defines the local signing execution guard for the staged `wvp-release-check` v0.3.0 asset.

This guard does not create a signature.
This guard does not create a tag.
This guard does not create a GitHub release.
This guard does not expose private signing material.
This guard does not prove source-to-release correspondence.
This guard does not prove reproducible builds.
This guard does not prove binary safety.
This guard is not an audit.

## Guard Script

    ./scripts/release/guard-v030-local-signing-execution.sh

## Evaluation Mode

Safe evaluation mode:

    ./scripts/release/guard-v030-local-signing-execution.sh --evaluate

Evaluation mode writes:

    target/wvp-v0.3.0-local-signing-execution-guard/GUARD-REPORT.json

Evaluation mode must not create:

- detached signature;
- `v0.3.0` tag;
- GitHub release.

## Required Ready Conditions

The guard may only approve local signing when:

- the source tree is clean;
- `HEAD` matches `origin/main`;
- no local `v0.3.0` tag exists;
- no detached signature file already exists;
- unsigned staging succeeds;
- detached-signature dry-run succeeds;
- the staged asset exists;
- the staged checksum exists;
- the staging manifest exists;
- the staging manifest source commit matches `HEAD`;
- the staging manifest says source tree dirty is `false`;
- the staging manifest says no signature was created;
- the staging manifest says no tag was created;
- the staging manifest says no GitHub release was created;
- the staging manifest says staging-only is `true`.

## Require-Ready Mode

Strict local gate:

    ./scripts/release/guard-v030-local-signing-execution.sh --require-ready

This mode exits non-zero unless all ready conditions pass.

## Boundary

No v0.3.0 tag is created by this document.
No GitHub release is created by this document.
No signature is created by this document.
No private signing material is committed by this document.

The guard prepares the local decision boundary before signing, but signing and publishing are still separate steps.
