# WVP report v1 compatibility guard

## Purpose

The v1 JSON report is a machine-readable compatibility surface.

The compatibility guard prevents accidental report-shape changes from silently reaching users or downstream tools.

## What is guarded

The guard snapshots the rendered JSON report shape for `wvp-release-check --json`.

It checks:

- top-level field presence;
- nested `github` field presence;
- stable primitive JSON types;
- array surfaces;
- security-relevant verification fields;
- `schema_version: 1`.

## Breaking-change rule

If a field is renamed, removed, moved, or has its JSON type changed, the guard fails.

A real breaking change must be intentional and must either:

- update the report schema version; or
- update the snapshot with a clear compatibility explanation.

## Non-claims

This guard does not prove audit status, binary safety, reproducible builds, source-to-release equivalence, legal compliance, wallet safety, or investment suitability.

It only blocks accidental JSON v1 compatibility drift.
