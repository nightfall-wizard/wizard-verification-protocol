# WVP stable JSON report contract

## Purpose

`wvp-release-check --json` is a machine-readable interface.

This document defines the v1 stability boundary for the JSON report surface.

## Contract

The JSON report must include:

- `schema_version`
- `tool`
- `version`
- `target`
- `status`
- `classification`
- `live_inspection`
- `summary`
- `github`
- `limitations`

## Schema version

The current schema version is 1.

Breaking changes require a new schema version.

## Status values

Allowed status values are:

- `INFO`
- `WARN`
- `FAIL`

## Stability rule

Existing v1 fields must not be renamed, removed, or silently change meaning without a schema version change.

## Non-claims

This contract does not prove audit status, binary safety, reproducible builds, source-to-release equivalence, legal compliance, wallet safety, or investment suitability.

It only stabilizes the machine-readable report surface.
